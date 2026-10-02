# Swarm autoscaler

Operations tooling for the Docker Swarm deployment. It is **not** part of the
application and never ships inside `ghcr.io/zboardio/analyzeyourdata` — the
repository root `.dockerignore` excludes `ops/` from the application build
context, and this image is built from `ops/autoscaler/` as its own context.

Self-hosters running a single container (`docker-compose.single.yml`) do not
need any of this.

## What it does

Every interval it lists the services labelled `ayd.autoscale=true`, samples the
CPU usage of their running containers through the Docker Engine API, and moves
the replica count between the service's minimum and maximum. It also restores
a service that Swarm has left short of tasks — see [Healing](#healing).

CPU is measured **against the service's own CPU limit**, not the host, so "80%"
means the same thing for a service capped at 1.5 CPU as for one capped at 1.0.

Scaling up is quicker than scaling down: a busy service gets help after two
consecutive high samples, an idle one is only shrunk after five consecutive low
ones, and every change starts a cooldown.

### Healing

It also restores a service that has fewer live tasks than its spec asks for.
Swarm normally replaces a task that stops, but not always:

- under `restart_policy.condition: on-failure`, a container that exits `0` is
  never restarted — and gunicorn exits `0` on `SIGTERM`;
- `max_attempts` without a `window` is counted over the task slot's whole
  lifetime, so after that many restarts Swarm gives the slot up for good.

Either way the service sits at `0/1` until its next deploy. When a service is
short for three consecutive ticks, the autoscaler does what
`docker service update --force` does: it bumps the task template's
`ForceUpdate` counter, and Swarm rolls every slot of that service, the
abandoned ones included. Posting the spec back unchanged is not enough — Swarm
treats a slot whose last task should not be restarted as still occupied. A
surged service that lost one task therefore has its healthy tasks rolled too,
under the service's own `update_config` (`start-first` in the stack files, so
without downtime). While the service stays short the attempt is repeated once
per heal cooldown.

A task that is pending, starting or waiting out its restart delay counts as
live, and nothing is healed while a rolling update is in progress.

The stack files in this repository use `condition: any` with no `max_attempts`,
so Swarm should not leave a gap in the first place; healing is the safety net
behind that, and the per-service log line (`1/1 tasks alive`) makes a degraded
service visible.

## Service labels

Set as Swarm **service** labels (`deploy.labels` in a compose file):

| Label | Default | Meaning |
|---|---|---|
| `ayd.autoscale` | — | `true` opts the service in. Nothing else is watched. |
| `ayd.autoscale.min` | `1` | Never scale below this. |
| `ayd.autoscale.max` | `3` | Never scale above this. |
| `ayd.autoscale.cpu-high` | `75` | Percent of the CPU limit that counts as busy. |
| `ayd.autoscale.cpu-low` | `25` | Percent of the CPU limit that counts as idle. |

Unparsable label values are logged and ignored in favour of the default.

## Environment variables

Set in `.env.autoscaler` on the deployment host, wired in by `env_file:` in
the stack file. Copy `.env.example.autoscaler` from the repository root to
create it. The file must exist or `docker stack deploy` fails; it only needs the
lines you want to differ from the defaults below.

It is deliberately a separate file from the application's `.env`: the one
container holding the Docker socket has no reason to carry the app's
credentials. (Being honest about the limit of that argument — a process that can
rewrite service specs can also read every other service's environment through
the API. The separation is hygiene, not a security boundary.)

Note that `docker stack deploy` does **not** read `.env` for `${...}`
interpolation, so `env_file:` is the only way to get values into a stack
service short of exporting shell variables.

| Variable | Default | Description |
|---|---|---|
| `AUTOSCALER_INTERVAL` | `60` | Seconds between ticks. |
| `AUTOSCALER_DRY_RUN` | `false` | Log the decisions without applying them. |
| `AUTOSCALER_MAX_TOTAL_REPLICAS` | `0` | Stack-wide ceiling across all watched services; `0` disables it. |
| `AUTOSCALER_MIN` / `AUTOSCALER_MAX` | `1` / `3` | Defaults when a service carries no min/max label. |
| `AUTOSCALER_CPU_HIGH` / `AUTOSCALER_CPU_LOW` | `75` / `25` | Default thresholds. |
| `AUTOSCALER_UP_SAMPLES` | `2` | Consecutive busy samples before scaling up. |
| `AUTOSCALER_DOWN_SAMPLES` | `5` | Consecutive idle samples before scaling down. |
| `AUTOSCALER_COOLDOWN` | `180` | Seconds after a change before another is considered. |
| `AUTOSCALER_HEAL` | `true` | Force an update of a service that is short of live tasks. |
| `AUTOSCALER_HEAL_SAMPLES` | `3` | Consecutive short samples before healing. |
| `AUTOSCALER_HEAL_COOLDOWN` | `300` | Seconds between heal attempts on the same service. |
| `AUTOSCALER_LOG_LEVEL` | `INFO` | Python log level. |
| `DOCKER_SOCKET` | `/var/run/docker.sock` | Engine socket path. |

## Requirements and caveats

- Must run on a **manager** node with `/var/run/docker.sock` mounted. Write
  access to that socket is equivalent to root on the node — that is the reason
  this is our own auditable code rather than a third-party image.
- `docker stack deploy` always resets replica counts to the compose file's
  value. Omitting the `replicas` key does not help: the daemon substitutes `1`
  (`ServiceSpecToGRPC` in moby). So after every deploy a surged service drops to
  its baseline and the autoscaler raises it again within a couple of ticks.
- On a single-node Swarm, replicas share one host's cores. The autoscaler adds
  process-level parallelism, not hardware.

## Build and run

```bash
# Local image for the manual-build stack
docker build -t ayd-swarm-autoscaler:latest ops/autoscaler

# Tests (part of the repository suite)
pytest tests/test_autoscaler.py

# Watch it decide, in the deployed stack
docker service logs ayd_autoscaler --follow
```

Roll it out with `AUTOSCALER_DRY_RUN=true` first and read a few ticks of logs
before letting it act.
