"""Tests for the Swarm autoscaler (ops/autoscaler/autoscaler.py).

The autoscaler is operations tooling, not an application module, so it is
loaded by path rather than imported as a package -- and the .dockerignore
assertions at the bottom guard the boundary that keeps it out of the
application image.
"""

import dataclasses
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOSCALER_PATH = REPO_ROOT / "ops" / "autoscaler" / "autoscaler.py"

_spec = importlib.util.spec_from_file_location("ayd_autoscaler", AUTOSCALER_PATH)
autoscaler = importlib.util.module_from_spec(_spec)
# Registered before exec: dataclasses resolves annotations via sys.modules.
sys.modules[_spec.name] = autoscaler
_spec.loader.exec_module(autoscaler)

Policy = autoscaler.Policy
State = autoscaler.State
decide = autoscaler.decide


# ---------------------------------------------------------------------------
# CPU sampling
# ---------------------------------------------------------------------------


def make_stats(cpu_delta, system_delta, online_cpus=4, percpu=None):
    """Stats payload shaped like the Engine API's /containers/{id}/stats."""
    cpu_usage = {"total_usage": 1_000_000_000 + cpu_delta}
    if percpu is not None:
        cpu_usage["percpu_usage"] = percpu
    stats = {
        "cpu_stats": {
            "cpu_usage": cpu_usage,
            "system_cpu_usage": 10_000_000_000 + system_delta,
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 1_000_000_000},
            "system_cpu_usage": 10_000_000_000,
        },
    }
    if online_cpus is not None:
        stats["cpu_stats"]["online_cpus"] = online_cpus
    return stats


def test_cpu_percent_relative_to_host_when_no_limit_set():
    # 1 core of 4 in use, no CPU limit -> 25% of the host allowance.
    stats = make_stats(cpu_delta=1_000_000_000, system_delta=4_000_000_000, online_cpus=4)
    assert autoscaler.cpu_percent_of_limit(stats) == pytest.approx(25.0)


def test_cpu_percent_relative_to_the_services_own_limit():
    # Same 1 core, but the service is capped at 1 CPU -> it is fully busy.
    stats = make_stats(cpu_delta=1_000_000_000, system_delta=4_000_000_000, online_cpus=4)
    assert autoscaler.cpu_percent_of_limit(stats, limit_nano_cpus=1_000_000_000) == pytest.approx(100.0)
    # Capped at 1.5 CPU, the same load is two thirds of the allowance.
    assert autoscaler.cpu_percent_of_limit(stats, limit_nano_cpus=1_500_000_000) == pytest.approx(66.67, rel=1e-3)


def test_cpu_percent_falls_back_to_percpu_length():
    stats = make_stats(cpu_delta=1_000_000_000, system_delta=4_000_000_000, online_cpus=None, percpu=[1, 2, 3, 4])
    assert autoscaler.cpu_percent_of_limit(stats) == pytest.approx(25.0)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda s: s["cpu_stats"].pop("system_cpu_usage"),
        lambda s: s["precpu_stats"]["cpu_usage"].pop("total_usage"),
        lambda s: s.update({"cpu_stats": {}}),
    ],
    ids=["no system usage", "no previous usage", "empty cpu_stats"],
)
def test_cpu_percent_returns_none_for_unusable_samples(mutate):
    stats = make_stats(cpu_delta=1_000_000_000, system_delta=4_000_000_000)
    mutate(stats)
    assert autoscaler.cpu_percent_of_limit(stats) is None


def test_cpu_percent_returns_none_when_the_counter_went_backwards():
    # A restarted container resets its counters; that sample is meaningless.
    stats = make_stats(cpu_delta=-500, system_delta=4_000_000_000)
    assert autoscaler.cpu_percent_of_limit(stats) is None


def test_cpu_percent_returns_none_when_system_did_not_advance():
    stats = make_stats(cpu_delta=1_000_000_000, system_delta=0)
    assert autoscaler.cpu_percent_of_limit(stats) is None


def test_cpu_percent_returns_none_when_no_cpus_reported():
    stats = make_stats(cpu_delta=1_000_000_000, system_delta=4_000_000_000, online_cpus=0)
    assert autoscaler.cpu_percent_of_limit(stats) is None


# ---------------------------------------------------------------------------
# Label parsing
# ---------------------------------------------------------------------------


def test_policy_defaults_when_no_labels_present():
    defaults = Policy()
    assert autoscaler.policy_from_labels({}, defaults) == defaults


def test_policy_reads_overrides_from_labels():
    policy = autoscaler.policy_from_labels(
        {
            "ayd.autoscale": "true",
            "ayd.autoscale.min": "2",
            "ayd.autoscale.max": "5",
            "ayd.autoscale.cpu-high": "80",
            "ayd.autoscale.cpu-low": "20",
        },
        Policy(),
    )
    assert (policy.min_replicas, policy.max_replicas) == (2, 5)
    assert (policy.cpu_high, policy.cpu_low) == (80.0, 20.0)


def test_policy_never_lets_max_fall_below_min():
    policy = autoscaler.policy_from_labels(
        {"ayd.autoscale.min": "3", "ayd.autoscale.max": "1"}, Policy()
    )
    assert policy.max_replicas == policy.min_replicas == 3


def test_policy_ignores_unparsable_labels():
    policy = autoscaler.policy_from_labels(
        {"ayd.autoscale.max": "lots", "ayd.autoscale.cpu-high": ""}, Policy(max_replicas=3, cpu_high=75.0)
    )
    assert policy.max_replicas == 3
    assert policy.cpu_high == 75.0


# ---------------------------------------------------------------------------
# Scaling decisions
# ---------------------------------------------------------------------------


NO_COOLDOWN = Policy(cooldown=0.0)


def test_corrects_a_service_scaled_below_its_minimum():
    decision = decide(0, None, Policy(min_replicas=1), State(), now=100.0)
    assert decision.target == 1
    assert decision.reason == "below min"


def test_corrects_a_service_scaled_above_its_maximum():
    # A stack deploy or a manual scale can push past the ceiling.
    decision = decide(6, 10.0, Policy(max_replicas=3), State(), now=100.0)
    assert decision.target == 3
    assert decision.reason == "above max"


def test_out_of_band_correction_ignores_the_cooldown():
    recent = State(last_change=99.0)
    decision = decide(0, None, Policy(min_replicas=1, cooldown=180.0), recent, now=100.0)
    assert decision.target == 1


def test_missing_cpu_sample_holds_steady_and_clears_streaks():
    decision = decide(1, None, NO_COOLDOWN, State(high_streak=1, low_streak=1), now=100.0)
    assert decision.target == 1
    assert decision.reason == "no usable cpu sample"
    assert (decision.state.high_streak, decision.state.low_streak) == (0, 0)


def test_one_busy_sample_is_not_enough_to_scale_up():
    policy = dataclasses.replace(NO_COOLDOWN, cpu_high=75.0, up_samples=2)
    decision = decide(1, 90.0, policy, State(), now=100.0)
    assert decision.target == 1
    assert decision.state.high_streak == 1


def test_scales_up_once_the_busy_streak_is_met():
    policy = dataclasses.replace(NO_COOLDOWN, cpu_high=75.0, up_samples=2, max_replicas=3)
    decision = decide(1, 90.0, policy, State(high_streak=1), now=100.0)
    assert decision.target == 2
    assert decision.state.high_streak == 0
    assert decision.state.last_change == 100.0


def test_never_scales_above_the_maximum():
    policy = dataclasses.replace(NO_COOLDOWN, cpu_high=75.0, up_samples=2, max_replicas=3)
    decision = decide(3, 99.0, policy, State(high_streak=5), now=100.0)
    assert decision.target == 3
    assert decision.reason == "steady"


def test_scales_down_only_after_a_longer_idle_streak():
    policy = dataclasses.replace(NO_COOLDOWN, cpu_low=25.0, down_samples=5, min_replicas=1)
    held = decide(2, 5.0, policy, State(low_streak=3), now=100.0)
    assert held.target == 2
    assert held.state.low_streak == 4

    shrunk = decide(2, 5.0, policy, State(low_streak=4), now=100.0)
    assert shrunk.target == 1
    assert shrunk.state.last_change == 100.0


def test_scaling_up_is_quicker_than_scaling_down():
    policy = Policy()
    assert policy.up_samples < policy.down_samples


def test_never_scales_below_the_minimum():
    policy = dataclasses.replace(NO_COOLDOWN, cpu_low=25.0, down_samples=1, min_replicas=1)
    decision = decide(1, 0.0, policy, State(low_streak=5), now=100.0)
    assert decision.target == 1
    assert decision.reason == "steady"


def test_cooldown_blocks_a_change_but_keeps_counting():
    policy = dataclasses.replace(Policy(cooldown=180.0), cpu_high=75.0, up_samples=1)
    decision = decide(1, 99.0, policy, State(last_change=50.0), now=100.0)
    assert decision.target == 1
    assert decision.reason == "cooling down"
    assert decision.state.high_streak == 1


def test_cooldown_expiry_lets_the_change_through():
    policy = dataclasses.replace(Policy(cooldown=180.0), cpu_high=75.0, up_samples=1, max_replicas=3)
    decision = decide(1, 99.0, policy, State(last_change=-100.0), now=100.0)
    assert decision.target == 2


def test_stack_wide_budget_blocks_scaling_up():
    policy = dataclasses.replace(NO_COOLDOWN, cpu_high=75.0, up_samples=1, max_replicas=3)
    decision = decide(1, 99.0, policy, State(), now=100.0, can_grow=False)
    assert decision.target == 1
    assert decision.reason == "stack replica budget reached"


def test_stack_wide_budget_does_not_block_scaling_down():
    policy = dataclasses.replace(NO_COOLDOWN, cpu_low=25.0, down_samples=1, min_replicas=1)
    decision = decide(2, 1.0, policy, State(low_streak=1), now=100.0, can_grow=False)
    assert decision.target == 1


def test_a_fresh_state_is_not_treated_as_just_changed():
    # time.monotonic() is small right after a host boot; a zero default would
    # wrongly read as "changed a moment ago" and stall the first ticks.
    policy = dataclasses.replace(Policy(cooldown=180.0), cpu_high=75.0, up_samples=1, max_replicas=3)
    decision = decide(1, 99.0, policy, State(), now=30.0)
    assert decision.target == 2


# ---------------------------------------------------------------------------
# Image boundary: ops/ must never reach the published application image
# ---------------------------------------------------------------------------


DOCKERIGNORE = REPO_ROOT / ".dockerignore"


def dockerignore_patterns():
    lines = DOCKERIGNORE.read_text().splitlines()
    return {line.strip() for line in lines if line.strip() and not line.strip().startswith("#")}


def test_dockerignore_exists():
    # Dockerfile ends in `COPY . .`; without this file everything ships.
    assert DOCKERIGNORE.is_file()


@pytest.mark.parametrize(
    "pattern",
    ["ops/", ".env", ".env.*", "env/", ".git", ".github/", "tests/", "docs/"],
)
def test_dockerignore_excludes_what_must_not_ship(pattern):
    assert pattern in dockerignore_patterns(), (
        f"{pattern!r} missing from .dockerignore -- it would be copied into the "
        "published application image by `COPY . .`"
    )


@pytest.mark.parametrize("needed", ["assets", "assets/", "i18n", "i18n/", "app.py", "config.py", "*.md", "*"])
def test_dockerignore_does_not_exclude_the_application(needed):
    assert needed not in dockerignore_patterns(), (
        f"{needed!r} in .dockerignore would strip application files out of the image"
    )


def test_autoscaler_is_not_importable_as_an_application_module():
    # It lives under ops/ precisely so the app never depends on it.
    assert not (REPO_ROOT / "autoscaler.py").exists()
    assert AUTOSCALER_PATH.is_file()


# ---------------------------------------------------------------------------
# Stack wiring: the autoscaler is ops tooling, configured by the host
# ---------------------------------------------------------------------------


import yaml  # noqa: E402  (declared in requirements-dev.txt)

STACK_FILES = ["docker-compose.cicd.yml", "docker-compose.local.yml"]
SELF_HOST_FILES = ["docker-compose.single.yml", "docker-compose.yml"]


def load_compose(name):
    return yaml.safe_load((REPO_ROOT / name).read_text())


@pytest.mark.parametrize("stack_file", STACK_FILES)
def test_every_language_service_is_labelled_for_autoscaling(stack_file):
    # Guards the case of adding a 16th language and forgetting the labels.
    services = load_compose(stack_file)["services"]
    apps = {k: v for k, v in services.items() if k.startswith("app-")}
    assert len(apps) == 15
    for name, service in apps.items():
        labels = service["deploy"].get("labels") or {}
        assert labels.get("ayd.autoscale") == "true", f"{name} is not labelled"
        assert int(labels["ayd.autoscale.min"]) >= 1
        assert int(labels["ayd.autoscale.max"]) >= int(labels["ayd.autoscale.min"])


@pytest.mark.parametrize("stack_file", STACK_FILES)
def test_language_services_keep_a_single_replica_baseline(stack_file):
    # docker stack deploy always resets to this value; surge is the
    # autoscaler's job, not the compose file's.
    services = load_compose(stack_file)["services"]
    replicas = {v["deploy"]["replicas"] for k, v in services.items() if k.startswith("app-")}
    assert replicas == {1}


@pytest.mark.parametrize("stack_file", STACK_FILES)
def test_autoscaler_never_scales_itself(stack_file):
    autoscaler_service = load_compose(stack_file)["services"]["autoscaler"]
    labels = (autoscaler_service.get("deploy") or {}).get("labels") or {}
    assert "ayd.autoscale" not in labels


@pytest.mark.parametrize("stack_file", STACK_FILES)
def test_autoscaler_runs_on_a_manager_with_the_docker_socket(stack_file):
    autoscaler_service = load_compose(stack_file)["services"]["autoscaler"]
    constraints = autoscaler_service["deploy"]["placement"]["constraints"]
    assert any("node.role == manager" in c for c in constraints)
    assert any("/var/run/docker.sock" in v for v in autoscaler_service["volumes"])


@pytest.mark.parametrize("stack_file", STACK_FILES)
def test_host_tuning_is_not_baked_into_the_committed_stack_file(stack_file):
    # Node-sized values and the dry-run toggle belong on the host: flipping
    # AUTOSCALER_DRY_RUN must not require a commit, a CI build and a deploy.
    autoscaler_service = load_compose(stack_file)["services"]["autoscaler"]
    assert autoscaler_service.get("env_file"), "autoscaler should be configured by env_file"
    inline = autoscaler_service.get("environment") or {}
    hardcoded = [k for k in inline if k.startswith("AUTOSCALER_")]
    assert not hardcoded, f"host tuning hardcoded in {stack_file}: {hardcoded}"


def test_autoscaler_env_template_is_committed():
    template = REPO_ROOT / ".env.example.autoscaler"
    assert template.is_file(), "env_file has no committed template to copy from"
    body = template.read_text()
    for key in ["AUTOSCALER_DRY_RUN", "AUTOSCALER_MAX_TOTAL_REPLICAS", "AUTOSCALER_INTERVAL"]:
        assert key in body


@pytest.mark.parametrize("compose_file", SELF_HOST_FILES)
def test_self_hosters_never_get_the_autoscaler(compose_file):
    # The single-container and local-dev stacks are what other people run.
    services = load_compose(compose_file)["services"]
    assert "autoscaler" not in services
    for service in services.values():
        assert "/var/run/docker.sock" not in str(service.get("volumes") or "")
