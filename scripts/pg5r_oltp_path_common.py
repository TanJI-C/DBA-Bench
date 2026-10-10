"""Shared harness for the pg5 OLTP instance three-path calibration scripts.

Encodes the batch resource lease (container/network/volume prefix `pg5r-oltp-`,
host ports 25100-25149, at most six live PostgreSQL containers), the path
matrix semantics from the production portfolio contract section 10, and the
report/evidence layout. The scripts under `scripts/` assemble instance
timelines from these pieces; real execution additionally requires the pg5
dataset images and the frozen core runtime, and is gated to the next phase.

This module contains no benchmark-subject session: healthy, zero-action and
wrong-action paths are fully scripted; the complete reference path runs the
scripted oracle remediation, which is one legitimate solution, not the only
accepted one.
"""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

PORT_RANGE = range(25100, 25150)
CONTAINER_PREFIX = "pg5r-oltp-"
MAX_LIVE_CONTAINERS = 6
REPORT_ROOT = Path("reports/pg5r-oltp")


def configure_port_range(lo: int, hi: int) -> None:
    """Narrows the lease range for a parallel sub-run (reference/zero split)."""

    global PORT_RANGE
    PORT_RANGE = range(lo, hi + 1)

PATHS = ("healthy", "reference", "zero", "wrong")


class PathError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ScheduledEvent:
    at_seconds: float
    event_id: str
    capability_id: str
    payload: Mapping[str, object]

    def with_origin(self, origin: float) -> float:
        return origin + self.at_seconds


@dataclass(frozen=True, slots=True)
class ScheduledAction:
    """A scripted oracle (reference path) or wrong-action SQL statement."""

    at_seconds: float
    label: str
    sql: str
    expect_failure: bool = False


def acquire_port() -> int:
    """Picks a free port inside the batch lease range; fails if the range is exhausted."""

    for port in PORT_RANGE:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind(("0.0.0.0", port))
            except OSError:
                continue
        return port
    raise PathError(
        f"No free host port left in the pg5r-oltp lease range {PORT_RANGE.start}-{PORT_RANGE.stop - 1}; "
        "another calibration run is holding the lease"
    )


def live_leased_containers() -> list[str]:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True, check=True,
    )
    return [name for name in result.stdout.splitlines() if name.startswith(CONTAINER_PREFIX)]


def assert_lease_capacity() -> None:
    live = live_leased_containers()
    if len(live) >= MAX_LIVE_CONTAINERS:
        raise PathError(
            f"pg5r-oltp lease already holds {len(live)} live containers (max {MAX_LIVE_CONTAINERS}): {live!r}"
        )


def cleanup_lease(container_name: str) -> Mapping[str, object]:
    """Stops and removes the run's container; returns the cleanup evidence."""

    result = subprocess.run(
        ["docker", "rm", "-f", container_name], capture_output=True, text=True
    )
    return {"container": container_name, "returncode": result.returncode, "stderr": result.stderr.strip(), "at": time.time()}


def deploy_container(spec: Mapping[str, object]) -> None:
    """Runs the dataset image under the batch lease; caller waits for readiness."""

    resources = spec["resources"]
    docker_args = [
        "docker", "run", "-d", "--name", str(spec["container_name"]),
        "-p", f"{spec['host_port']}:5432",
        "--cpus", str(resources["cpus"]),
        "--memory", f"{resources['memory_mb']}m",
        "--shm-size", str(resources["shm_size"]),
    ]
    if resources.get("cpuset"):
        docker_args += ["--cpuset-cpus", str(resources["cpuset"])]
    docker_args.append(str(spec["image"]))
    subprocess.run(docker_args, capture_output=True, text=True, check=True)


def wait_until_ready(port: int, *, timeout_seconds: float = 300.0) -> None:
    import psycopg2

    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            connection = psycopg2.connect(
                host="localhost", port=port, user="postgres", password="password",
                dbname="testdb", connect_timeout=2,
            )
            connection.close()
            return
        except psycopg2.Error as exc:
            last_error = exc
            time.sleep(2.0)
    raise PathError(f"Dataset container did not become ready within {timeout_seconds}s: error={last_error!r}")


def run_timeline(
    *,
    origin: float,
    clock,
    schedule: Sequence[ScheduledEvent],
    actions: Sequence[ScheduledAction],
    activate: Callable[[ScheduledEvent], Mapping[str, object]],
    execute_action: Callable[[ScheduledAction], Mapping[str, object]],
) -> list[Mapping[str, object]]:
    """Fires scheduled events and actions at their monotonic offsets; returns observations."""

    stop = threading.Event()
    merged = sorted(
        [("event", item.at_seconds, item) for item in schedule]
        + [("action", item.at_seconds, item) for item in actions],
        key=lambda entry: entry[1],
    )
    observations: list[Mapping[str, object]] = []
    for kind, at_seconds, item in merged:
        clock.wait_until(origin + at_seconds, stop)
        if kind == "event":
            evidence = activate(item)
            observations.append({"kind": "event", "event_id": item.event_id, "at": clock.monotonic(), "evidence": evidence})
        else:
            evidence = execute_action(item)
            observations.append({"kind": "action", "label": item.label, "at": clock.monotonic(), "evidence": evidence})
    return observations


def write_report(run_id: str, report: Mapping[str, object]) -> Path:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    path = REPORT_ROOT / f"{run_id}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return path


def parse_common_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--path", choices=PATHS, required=True,
                        help="healthy | reference (scripted oracle) | zero | wrong")
    parser.add_argument("--image", required=True,
                        help="pg5 dataset image for this instance (built once per dataset build)")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cpu", type=float, default=2.0)
    parser.add_argument("--memory-mb", type=int, default=2048)
    parser.add_argument("--port-lo", type=int, default=25100,
                        help="inclusive lower bound of this run's lease sub-range")
    parser.add_argument("--port-hi", type=int, default=25149,
                        help="inclusive upper bound of this run's lease sub-range")
    parser.add_argument("--cpuset", default="",
                        help="optional --cpuset-cpus segment pinned to the run container")
    return parser.parse_args()


def require_path_schedule(schedules: Mapping[str, Sequence[ScheduledEvent]], path: str) -> Sequence[ScheduledEvent]:
    if path not in schedules:
        raise PathError(f"No event schedule registered for path: path={path!r}, known={sorted(schedules)!r}")
    return schedules[path]


def zero_action_budget_note() -> str:
    return (
        "The zero path must show, on the same seed/resources/clock as healthy and reference, "
        "at least one business objective measurably outside its budget (logical-op good fraction "
        "or delivery contract). A blocker that resolves on its own does not erase the loss "
        "recorded by the trusted ledger during the affected window."
    )


def job_terminal_records(evidence_path: Path) -> list[Mapping[str, object]]:
    """Reads the sealed evidence ledger for job terminal records (delivery deadline facts)."""

    terminals: list[Mapping[str, object]] = []
    with evidence_path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            envelope = json.loads(raw)
            record = envelope["record"]
            if record.get("kind") == "job_terminal":
                terminals.append(record)
    return terminals


def budget_assessment(items: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    """Renders one run's comparison against the provisional threshold ledger."""

    return {
        "provisional": True,
        "within_budget": all(bool(item["within_budget"]) for item in items),
        "items": list(items),
    }


def collect_guc_state(connection) -> list[Mapping[str, object]]:
    """Terminal instance/role GUC facts: wrong-action fallout and baseline integrity."""

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 'setting' AS kind, name, setting::text, NULL::text, NULL::text FROM pg_settings "
            "WHERE name IN ('synchronous_commit', 'max_connections', 'idle_in_transaction_session_timeout', 'fsync') "
            "UNION ALL "
            "SELECT 'role', NULL, NULL, rolname, array_to_string(rolconfig, ';') FROM pg_roles "
            "WHERE rolname IN ('shop_app', 'shop_auditor', 'report_client');"
        )
        rows = cursor.fetchall()
    state = []
    for kind, name, setting, rolname, rolconfig in rows:
        state.append({
            "kind": str(kind), "name": name, "setting": setting,
            "role": rolname, "rolconfig": rolconfig,
        })
    return state
