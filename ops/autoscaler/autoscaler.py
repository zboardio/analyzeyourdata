"""Docker Swarm autoscaler for the Analyze Your Data stack.

Watches services labelled ``ayd.autoscale=true``, samples the CPU usage of their
running containers through the Docker Engine API, and moves the replica count
between the per-service minimum and maximum.

This is *operations* tooling for the Swarm deployment, not part of the
application. It is deliberately dependency-free -- the Engine API is spoken
directly over the unix socket -- so the image is a Python base layer plus this
one file, and nothing here ever reaches the published application image.

Runs as a Swarm service pinned to a manager node with /var/run/docker.sock
mounted. Anything able to rewrite service specs on a manager is effectively root
on that host; that is why this runs our own auditable code rather than a
third-party image.
"""

from __future__ import annotations

import dataclasses
import http.client
import json
import logging
import os
import signal
import socket
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

LABEL_PREFIX = os.environ.get("AUTOSCALER_LABEL_PREFIX", "ayd.autoscale")
HEARTBEAT_PATH = os.environ.get("AUTOSCALER_HEARTBEAT", "/tmp/autoscaler.heartbeat")

log = logging.getLogger("autoscaler")


# --------------------------------------------------------------------------
# Engine API transport
# --------------------------------------------------------------------------


class _UnixHTTPConnection(http.client.HTTPConnection):
    """HTTPConnection that talks to a unix domain socket."""

    def __init__(self, socket_path: str, timeout: float = 60.0) -> None:
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect(self.socket_path)
        self.sock = sock


class DockerError(RuntimeError):
    """Non-2xx response from the Engine API."""


class DockerAPI:
    """Minimal Engine API client: exactly the calls this autoscaler needs."""

    def __init__(self, socket_path: str = "/var/run/docker.sock", timeout: float = 60.0) -> None:
        self.socket_path = socket_path
        self.timeout = timeout
        self.prefix = ""

    def negotiate_version(self) -> str:
        """Pin requests to the daemon's own API version, so an older or newer
        daemon does not reject us over a hard-coded version string."""
        version = self.request("GET", "/version").get("ApiVersion")
        self.prefix = f"/v{version}" if version else ""
        return version or "unversioned"

    def request(self, method: str, path: str, params: dict | None = None, body=None):
        url = self.prefix + path
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        payload = None
        headers = {}
        if body is not None:
            payload = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        conn = _UnixHTTPConnection(self.socket_path, timeout=self.timeout)
        try:
            conn.request(method, url, body=payload, headers=headers)
            response = conn.getresponse()
            raw = response.read()
            if response.status >= 400:
                raise DockerError(f"{method} {url} -> {response.status}: {raw.decode(errors='replace')[:300]}")
            if not raw:
                return None
            return json.loads(raw)
        finally:
            conn.close()

    def autoscaled_services(self) -> list[dict]:
        filters = json.dumps({"label": [f"{LABEL_PREFIX}=true"]})
        return self.request("GET", "/services", params={"filters": filters}) or []

    def running_container_ids(self, service_id: str) -> list[str]:
        filters = json.dumps({"service": [service_id], "desired-state": ["running"]})
        tasks = self.request("GET", "/tasks", params={"filters": filters}) or []
        ids = []
        for task in tasks:
            status = task.get("Status") or {}
            if status.get("State") != "running":
                continue
            container_id = (status.get("ContainerStatus") or {}).get("ContainerID")
            if container_id:
                ids.append(container_id)
        return ids

    def container_stats(self, container_id: str) -> dict | None:
        try:
            return self.request(
                "GET", f"/containers/{container_id}/stats", params={"stream": "false"}
            )
        except (DockerError, OSError) as exc:
            log.warning("stats failed for %s: %s", container_id[:12], exc)
            return None

    def set_replicas(self, service: dict, target: int) -> None:
        spec = service["Spec"]
        spec["Mode"]["Replicated"]["Replicas"] = target
        self.request(
            "POST",
            f"/services/{service['ID']}/update",
            params={"version": service["Version"]["Index"]},
            body=spec,
        )


# --------------------------------------------------------------------------
# Pure decision logic -- no Docker, no clock, fully unit tested
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Policy:
    """Scaling rules for one service."""

    min_replicas: int = 1
    max_replicas: int = 3
    cpu_high: float = 75.0
    cpu_low: float = 25.0
    up_samples: int = 2
    down_samples: int = 5
    cooldown: float = 180.0


@dataclasses.dataclass(frozen=True)
class State:
    """What we remember about a service between ticks."""

    high_streak: int = 0
    low_streak: int = 0
    # -inf, not 0.0: time.monotonic() is small just after a host boot, and a
    # zero default would impose a phantom cooldown on the first ticks.
    last_change: float = float("-inf")


@dataclasses.dataclass(frozen=True)
class Decision:
    target: int
    state: State
    reason: str


def cpu_percent_of_limit(stats: dict, limit_nano_cpus: int = 0) -> float | None:
    """CPU used by one container as a percentage of the CPU it is *allowed*.

    Measuring against the service's own CPU limit rather than the whole host
    means "80%" reads the same for a service capped at 1.5 CPU as for one
    capped at 1.0. Returns None when the sample is unusable.
    """
    cpu = stats.get("cpu_stats") or {}
    precpu = stats.get("precpu_stats") or {}
    usage = (cpu.get("cpu_usage") or {}).get("total_usage")
    pre_usage = (precpu.get("cpu_usage") or {}).get("total_usage")
    system = cpu.get("system_cpu_usage")
    pre_system = precpu.get("system_cpu_usage")
    if None in (usage, pre_usage, system, pre_system):
        return None

    cpu_delta = usage - pre_usage
    system_delta = system - pre_system
    if cpu_delta < 0 or system_delta <= 0:
        return None

    online = cpu.get("online_cpus") or len((cpu.get("cpu_usage") or {}).get("percpu_usage") or [])
    if not online:
        return None

    cores_used = (cpu_delta / system_delta) * online
    allowance = (limit_nano_cpus / 1e9) if limit_nano_cpus else float(online)
    if allowance <= 0:
        return None
    return (cores_used / allowance) * 100.0


def policy_from_labels(labels: dict, defaults: Policy) -> Policy:
    """Per-service overrides via `ayd.autoscale.*` labels; bad values are
    ignored in favour of the default rather than crashing the loop."""

    def _num(key, fallback, cast):
        raw = labels.get(f"{LABEL_PREFIX}.{key}")
        if raw is None:
            return fallback
        try:
            return cast(raw)
        except (TypeError, ValueError):
            log.warning("ignoring unparsable label %s.%s=%r", LABEL_PREFIX, key, raw)
            return fallback

    minimum = max(0, _num("min", defaults.min_replicas, int))
    maximum = max(minimum, _num("max", defaults.max_replicas, int))
    return dataclasses.replace(
        defaults,
        min_replicas=minimum,
        max_replicas=maximum,
        cpu_high=_num("cpu-high", defaults.cpu_high, float),
        cpu_low=_num("cpu-low", defaults.cpu_low, float),
    )


def decide(
    current: int,
    cpu: float | None,
    policy: Policy,
    state: State,
    now: float,
    can_grow: bool = True,
) -> Decision:
    """Choose the replica count for one service. Pure: same inputs, same output.

    Scaling up is deliberately quicker than scaling down -- a busy service
    should get help fast, an idle one can wait to be sure the lull is real.
    """
    reset = dataclasses.replace(state, high_streak=0, low_streak=0)

    # Drifted outside its own bounds (label edited, manual scale): correct at
    # once and do not let the cooldown hold a service below its minimum.
    if current < policy.min_replicas:
        return Decision(policy.min_replicas, dataclasses.replace(reset, last_change=now), "below min")
    if current > policy.max_replicas:
        return Decision(policy.max_replicas, dataclasses.replace(reset, last_change=now), "above max")

    if cpu is None:
        return Decision(current, reset, "no usable cpu sample")

    state = dataclasses.replace(
        state,
        high_streak=state.high_streak + 1 if cpu >= policy.cpu_high else 0,
        low_streak=state.low_streak + 1 if cpu <= policy.cpu_low else 0,
    )

    if now - state.last_change < policy.cooldown:
        return Decision(current, state, "cooling down")

    if state.high_streak >= policy.up_samples and current < policy.max_replicas:
        if not can_grow:
            return Decision(current, state, "stack replica budget reached")
        changed = dataclasses.replace(state, high_streak=0, low_streak=0, last_change=now)
        return Decision(current + 1, changed, f"cpu {cpu:.0f}% high for {state.high_streak} samples")

    if state.low_streak >= policy.down_samples and current > policy.min_replicas:
        changed = dataclasses.replace(state, high_streak=0, low_streak=0, last_change=now)
        return Decision(current - 1, changed, f"cpu {cpu:.0f}% low for {state.low_streak} samples")

    return Decision(current, state, "steady")


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def _env_bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclasses.dataclass
class Settings:
    interval: float = 60.0
    dry_run: bool = False
    max_total_replicas: int = 0  # 0 = no stack-wide cap
    socket_path: str = "/var/run/docker.sock"
    defaults: Policy = dataclasses.field(default_factory=Policy)

    @classmethod
    def from_env(cls) -> "Settings":
        env = os.environ
        defaults = Policy(
            min_replicas=int(env.get("AUTOSCALER_MIN", 1)),
            max_replicas=int(env.get("AUTOSCALER_MAX", 3)),
            cpu_high=float(env.get("AUTOSCALER_CPU_HIGH", 75)),
            cpu_low=float(env.get("AUTOSCALER_CPU_LOW", 25)),
            up_samples=int(env.get("AUTOSCALER_UP_SAMPLES", 2)),
            down_samples=int(env.get("AUTOSCALER_DOWN_SAMPLES", 5)),
            cooldown=float(env.get("AUTOSCALER_COOLDOWN", 180)),
        )
        return cls(
            interval=float(env.get("AUTOSCALER_INTERVAL", 60)),
            dry_run=_env_bool("AUTOSCALER_DRY_RUN", False),
            max_total_replicas=int(env.get("AUTOSCALER_MAX_TOTAL_REPLICAS", 0)),
            socket_path=env.get("DOCKER_SOCKET", "/var/run/docker.sock"),
            defaults=defaults,
        )


class Autoscaler:
    def __init__(self, api: DockerAPI, settings: Settings) -> None:
        self.api = api
        self.settings = settings
        self.states: dict[str, State] = {}
        self._stop = False

    def stop(self, *_args) -> None:
        log.info("shutdown requested")
        self._stop = True

    def service_cpu(self, service_id: str, limit_nano_cpus: int) -> float | None:
        """Mean CPU across the service's running containers, as a percentage of
        each container's allowance. Sampling is concurrent because a single
        stats read blocks for about a second."""
        container_ids = self.api.running_container_ids(service_id)
        if not container_ids:
            return None
        with ThreadPoolExecutor(max_workers=min(8, len(container_ids))) as pool:
            samples = list(pool.map(self.api.container_stats, container_ids))
        values = [
            pct
            for stats in samples
            if stats
            for pct in [cpu_percent_of_limit(stats, limit_nano_cpus)]
            if pct is not None
        ]
        if not values:
            return None
        return sum(values) / len(values)

    def tick(self, now: float) -> None:
        services = self.api.autoscaled_services()
        if not services:
            log.info("no services carry %s=true", LABEL_PREFIX)
            return

        total = 0
        plans = []
        for service in services:
            spec = service.get("Spec") or {}
            name = spec.get("Name", service.get("ID", "?"))
            replicated = (spec.get("Mode") or {}).get("Replicated")
            if replicated is None:
                log.warning("%s is not a replicated service, skipping", name)
                continue
            current = int(replicated.get("Replicas") or 0)
            total += current
            plans.append((service, name, spec, current))

        cap = self.settings.max_total_replicas
        for service, name, spec, current in plans:
            policy = policy_from_labels(spec.get("Labels") or {}, self.settings.defaults)
            limit = int(
                (((spec.get("TaskTemplate") or {}).get("Resources") or {}).get("Limits") or {})
                .get("NanoCPUs")
                or 0
            )
            cpu = self.service_cpu(service["ID"], limit)
            can_grow = cap <= 0 or total < cap
            state = self.states.get(name, State())
            decision = decide(current, cpu, policy, state, now, can_grow=can_grow)
            self.states[name] = decision.state

            shown = f"{cpu:.0f}%" if cpu is not None else "n/a"
            if decision.target == current:
                log.info("%s: %d replicas, cpu %s -- %s", name, current, shown, decision.reason)
                continue

            log.info(
                "%s: %d -> %d replicas, cpu %s -- %s%s",
                name, current, decision.target, shown, decision.reason,
                " [dry run]" if self.settings.dry_run else "",
            )
            if self.settings.dry_run:
                continue
            try:
                self.api.set_replicas(service, decision.target)
                total += decision.target - current
            except (DockerError, OSError) as exc:
                log.error("%s: scaling failed, will retry next tick: %s", name, exc)
                self.states[name] = state

    def run_forever(self) -> None:
        while not self._stop:
            started = time.monotonic()
            try:
                self.tick(started)
                _write_heartbeat()
            except (DockerError, OSError) as exc:
                log.error("tick failed: %s", exc)
            elapsed = time.monotonic() - started
            remaining = self.settings.interval - elapsed
            while remaining > 0 and not self._stop:
                nap = min(1.0, remaining)
                time.sleep(nap)
                remaining -= nap


def _write_heartbeat() -> None:
    try:
        with open(HEARTBEAT_PATH, "w") as handle:
            handle.write(str(time.time()))
    except OSError as exc:  # a wedged heartbeat must not kill the loop
        log.warning("heartbeat write failed: %s", exc)


def main() -> int:
    logging.basicConfig(
        level=os.environ.get("AUTOSCALER_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )
    settings = Settings.from_env()
    api = DockerAPI(settings.socket_path)
    try:
        version = api.negotiate_version()
    except (DockerError, OSError) as exc:
        log.error("cannot reach the Docker API at %s: %s", settings.socket_path, exc)
        return 1

    log.info(
        "autoscaler started (api %s, interval %.0fs, defaults min=%d max=%d high=%.0f%% low=%.0f%%%s%s)",
        version,
        settings.interval,
        settings.defaults.min_replicas,
        settings.defaults.max_replicas,
        settings.defaults.cpu_high,
        settings.defaults.cpu_low,
        f", stack cap {settings.max_total_replicas}" if settings.max_total_replicas else "",
        ", DRY RUN" if settings.dry_run else "",
    )

    autoscaler = Autoscaler(api, settings)
    signal.signal(signal.SIGTERM, autoscaler.stop)
    signal.signal(signal.SIGINT, autoscaler.stop)
    autoscaler.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
