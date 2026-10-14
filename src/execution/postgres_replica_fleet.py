"""Execution support for the PostgreSQL read-replica cascade scenario.

The fleet is deliberately small, but it is a real primary/streaming-replica
topology.  Read traffic enters PgBouncer and an HAProxy router; the agent's
control connection remains on the primary so remediation SQL cannot be sent
to an asynchronous replica by accident.
"""

from __future__ import annotations

import json
import hashlib
import os
import random
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import uuid
from bisect import bisect_left
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.execution.deployments.base import BaseDeployment
from src.execution.environments.postgres import PGEnv
from src.execution.tools import Tool, lazy_agent_text
from src.execution.history.metrics import (
    MetricFrame,
    MetricQuery,
    MetricService,
    bound_metric_result,
    format_utc_timestamp,
    parse_utc_timestamp,
    render_metric_frame,
)
from src.execution.history.records import (
    CapturedRecords,
    HistoricalCoverage,
    HistoricalPointRecord,
    HistoricalRecordSource,
)
from src.execution.postgres_metrics import LivePostgresSamplerMetricProvider
from src.execution.postgres_replica_metrics import FLEET_METRIC_NAMES, REPLICA_FLEET_METRIC_CATALOG
from src.execution.specs import HostPortLayout, PostgresCaseRuntime
from src.execution.host_ports import claim_host_ports


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplicaFleetPorts:
    primary: int = 15851
    replica_0: int = 15852
    replica_1: int = 15853
    replica_2: int = 15854
    pgbouncer: int = 15855
    router: int = 15856
    metrics: int = 15857
    probe: int = 15858
    auxiliary: int = 15859

    @property
    def replicas(self) -> tuple[int, int, int]:
        return (self.replica_0, self.replica_1, self.replica_2)

    def as_dict(self) -> dict[str, int]:
        return {
            "primary": self.primary,
            "replica_0": self.replica_0,
            "replica_1": self.replica_1,
            "replica_2": self.replica_2,
            "pgbouncer": self.pgbouncer,
            "router": self.router,
            "metrics": self.metrics,
            "probe": self.probe,
            "auxiliary": self.auxiliary,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class PgReplicaFleetRuntime(PostgresCaseRuntime):
    host_ports: HostPortLayout = HostPortLayout(offsets=tuple(range(9)))
    ports: ReplicaFleetPorts = ReplicaFleetPorts()
    identity: str = "pg-composite-fault-lwlock-pgbouncer-cascade"


class PgReplicaFleetDeployment(BaseDeployment):
    """Docker deployment with task-scoped names and explicit teardown."""

    POSTGRES_IMAGE = "postgres:16"
    ROUTER_IMAGE = "haproxy:3.0-alpine"
    PGBOUNCER_IMAGE = "edoburu/pgbouncer:1.24.1"
    PGBOUNCER_LOCAL_FALLBACK = "aiopsbench-pgbouncer-fault:latest"
    PGDATA = "/var/lib/postgresql/data/pgdata"
    PRIMARY_RESTART_READY_TIMEOUT_SECONDS = 900

    def __init__(
        self,
        *,
        identity: str,
        ports: ReplicaFleetPorts = ReplicaFleetPorts(),
        image_name: str = "aiopsbench-pg-replica-cascade-base:latest",
        fault_image_name: str = "aiopsbench-pg-fault-replica-cascade:latest",
        resources: Mapping[str, Any] | None = None,
        postgres_user: str = "postgres",
        postgres_password: str = "password",
        postgres_db: str = "testdb",
    ):
        self.identity = self._safe_name(identity)
        self.ports = ports
        self._ports_are_explicit = ports != ReplicaFleetPorts()
        self._port_lease = None
        self.image_name = image_name
        self.fault_image_name = fault_image_name
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.postgres_db = postgres_db
        self.resources = dict(resources or {
            "cpus": 1.0,
            "memory_mb": 512,
            "shm_size": "256m",
        })
        self.container_name = f"{self.identity}-primary"
        self.replica_container_names = tuple(
            f"{self.identity}-replica-{index}" for index in range(3)
        )
        self.router_container_name = f"{self.identity}-router"
        self.pgbouncer_container_name = f"{self.identity}-pgbouncer"
        self.network_name = f"{self.identity}-network"
        self.volume_names = {
            "primary": f"{self.identity}-primary-data",
            **{
                f"replica_{index}": f"{self.identity}-replica-{index}-data"
                for index in range(3)
            },
        }
        self.pgdata = self.PGDATA
        self._runtime_dir = Path(tempfile.mkdtemp(prefix=f"{self.identity}-"))
        self._known_containers = (
            self.container_name,
            *self.replica_container_names,
            self.router_container_name,
            self.pgbouncer_container_name,
        )

    @staticmethod
    def _safe_name(value: str) -> str:
        value = "".join(char if char.isalnum() or char in "-_" else "-" for char in value)
        value = value.strip("-")
        if not value:
            raise ValueError("fleet identity must contain at least one safe character")
        if len(value) <= 72:
            return value
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
        return f"{value[:61].rstrip('-')}-{digest}"

    @property
    def all_ports(self) -> tuple[int, ...]:
        return tuple(self.ports.as_dict().values())

    def _run(self, args: list[str], *, check: bool = True, timeout: int = 300) -> subprocess.CompletedProcess:
        return subprocess.run(args, check=check, capture_output=True, text=True, timeout=timeout)

    def read_logs(self, lines: int = 200) -> str:
        result = self._run(
            ["docker", "logs", "--timestamps", "--tail", str(lines), self.container_name],
            check=False,
            timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL Docker log read failed: container={self.container_name!r}, "
                f"returncode={result.returncode}, stderr={result.stderr.strip()!r}"
            )
        return result.stdout + result.stderr

    def read_logs_at_range(self, start_epoch_ms: int, end_epoch_ms: int) -> str:
        """Read the bounded primary log streams used by frozen history."""
        if not isinstance(start_epoch_ms, int) or isinstance(start_epoch_ms, bool):
            raise TypeError(
                "PostgreSQL log start must be an epoch millisecond integer: "
                f"start_epoch_ms={start_epoch_ms!r}"
            )
        if not isinstance(end_epoch_ms, int) or isinstance(end_epoch_ms, bool):
            raise TypeError(
                "PostgreSQL log end must be an epoch millisecond integer: "
                f"end_epoch_ms={end_epoch_ms!r}"
            )
        if start_epoch_ms >= end_epoch_ms:
            raise ValueError(
                "PostgreSQL log capture range must be positive: "
                f"container={self.container_name!r}, start_epoch_ms={start_epoch_ms}, "
                f"end_epoch_ms={end_epoch_ms}"
            )
        start = datetime.fromtimestamp(start_epoch_ms / 1000, tz=timezone.utc).isoformat(
            timespec="milliseconds"
        ).replace("+00:00", "Z")
        end = datetime.fromtimestamp(end_epoch_ms / 1000, tz=timezone.utc).isoformat(
            timespec="milliseconds"
        ).replace("+00:00", "Z")
        docker_result = self._run(
            [
                "docker", "logs", "--timestamps",
                "--since", start,
                "--until", end,
                self.container_name,
            ],
            check=False,
            timeout=30,
        )
        if docker_result.returncode != 0:
            raise RuntimeError(
                "PostgreSQL Docker log range read failed: "
                f"container={self.container_name!r}, start_epoch_ms={start_epoch_ms}, "
                f"end_epoch_ms={end_epoch_ms}, returncode={docker_result.returncode}, "
                f"stderr={docker_result.stderr.strip()!r}"
            )
        paths_result = self._run(
            [
                "docker", "exec", self.container_name, "sh", "-c",
                f"find {self.PGDATA}/log -maxdepth 1 -type f -name '*.log' -print | sort",
            ],
            check=False,
            timeout=30,
        )
        if paths_result.returncode != 0:
            raise RuntimeError(
                "PostgreSQL log file enumeration failed: "
                f"container={self.container_name!r}, returncode={paths_result.returncode}, "
                f"stderr={paths_result.stderr.strip()!r}"
            )
        paths = tuple(path for path in paths_result.stdout.splitlines() if path)
        if not paths:
            raise RuntimeError(
                "PostgreSQL log file enumeration returned no files: "
                f"container={self.container_name!r}, directory={self.PGDATA + '/log'!r}"
            )
        file_result = self._run(
            ["docker", "exec", self.container_name, "cat", *paths],
            check=False,
            timeout=30,
        )
        if file_result.returncode != 0:
            raise RuntimeError(
                "PostgreSQL log file read failed: "
                f"container={self.container_name!r}, files={paths!r}, "
                f"returncode={file_result.returncode}, stderr={file_result.stderr.strip()!r}"
            )
        return docker_result.stdout + docker_result.stderr + file_result.stdout

    def postgres_log_sizes(self) -> dict[str, int]:
        """Expose one stable primary log stream to PGEnv's visible-log API."""
        output = self.read_logs(lines=10000)
        return {"docker://primary": len(output.encode("utf-8"))}

    def read_postgres_logs_after(self, offsets: dict[str, int]) -> tuple[str, dict[str, int]]:
        """Read bytes appended since the last bounded PostgreSQL log snapshot."""
        key = "docker://primary"
        if set(offsets) - {key}:
            raise RuntimeError(f"unknown PostgreSQL log offsets: {sorted(offsets)}")
        raw = self.read_logs(lines=10000).encode("utf-8")
        offset = int(offsets.get(key, 0))
        if offset < 0 or offset > len(raw):
            raise RuntimeError(
                f"PostgreSQL log offset is outside the current stream: offset={offset}, size={len(raw)}"
            )
        return raw[offset:].decode("utf-8", errors="replace"), {key: len(raw)}

    def _container_exists(self, name: str) -> bool:
        result = self._run(["docker", "container", "inspect", name], check=False, timeout=60)
        return result.returncode == 0

    def _image_exists(self, name: str) -> bool:
        result = self._run(["docker", "image", "inspect", name], check=False, timeout=60)
        return result.returncode == 0

    def _assert_ports_available(self) -> None:
        if len(set(self.all_ports)) != len(self.all_ports):
            raise ValueError(f"replica fleet ports must be unique: {self.ports.as_dict()}")
        ss = self._run(["ss", "-ltnH"], check=False, timeout=10)
        listeners = set()
        for line in ss.stdout.splitlines():
            address = line.split()[3] if len(line.split()) > 3 else ""
            try:
                listeners.add(int(address.rsplit(":", 1)[1]))
            except (IndexError, ValueError):
                continue
        for port in self.all_ports:
            if port in listeners:
                raise RuntimeError(f"configured replica-fleet port is already listening: port={port}")
            with socket.socket() as probe:
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    probe.bind(("127.0.0.1", port))
                except OSError as exc:
                    raise RuntimeError(f"configured replica-fleet port is unavailable: port={port}") from exc

    def _ensure_image(self) -> None:
        if self._image_exists(self.image_name):
            return
        project_root = Path(__file__).resolve().parents[2]
        dockerfile = project_root / "config" / "docker" / "pg-replica-cascade" / "Dockerfile"
        self._run(["docker", "build", "--tag", self.image_name, "--file", str(dockerfile), str(dockerfile.parent)], timeout=900)

    def _ensure_network(self) -> None:
        if self._run(["docker", "network", "inspect", self.network_name], check=False, timeout=60).returncode != 0:
            self._run(["docker", "network", "create", "--driver", "bridge", self.network_name])

    def _ensure_volume(self, name: str) -> None:
        if self._run(["docker", "volume", "inspect", name], check=False, timeout=60).returncode != 0:
            self._run(["docker", "volume", "create", name])

    @staticmethod
    def _worker_cpuset_args() -> list[str]:
        cpuset_cpus = os.environ.get("AIOPS_CPUSET_CPUS")
        cpuset_mems = os.environ.get("AIOPS_CPUSET_MEMS")
        if bool(cpuset_cpus) != bool(cpuset_mems):
            raise RuntimeError(
                "PostgreSQL replica-fleet worker isolation requires both cpuset values: "
                f"AIOPS_CPUSET_CPUS={cpuset_cpus!r}, AIOPS_CPUSET_MEMS={cpuset_mems!r}"
            )
        if not cpuset_cpus:
            return []
        return ["--cpuset-cpus", cpuset_cpus, "--cpuset-mems", cpuset_mems]

    def _start_primary(self) -> None:
        if self._container_exists(self.container_name):
            self._run(["docker", "start", self.container_name], check=False)
            return
        self._seed_volume_from_image(self.volume_names["primary"])
        self._run([
            "docker", "run", "--detach", "--name", self.container_name,
            "--network", self.network_name, "--network-alias", "primary",
            "--publish", f"{self.ports.primary}:5432",
            "--env", f"POSTGRES_USER={self.postgres_user}",
            "--env", f"POSTGRES_PASSWORD={self.postgres_password}",
            "--env", f"POSTGRES_DB={self.postgres_db}",
            "--env", f"PGDATA={self.PGDATA}",
            "--env", "POSTGRES_INITDB_ARGS=--no-sync",
            "--volume", f"{self.volume_names['primary']}:{self.PGDATA}",
            "--cpus", str(self.resources.get("cpus", 1.0)),
            "--memory", f"{self.resources.get('memory_mb', 512)}m",
            "--shm-size", str(self.resources.get("shm_size", "256m")),
            *self._worker_cpuset_args(),
            self.image_name,
            "postgres", "-c", "wal_level=replica", "-c", "max_wal_senders=8",
            "-c", "max_replication_slots=8", "-c", "shared_preload_libraries=pg_stat_statements",
            "-c", "logging_collector=on", "-c", "log_destination=stderr",
        ])

    def _seed_volume_from_image(self, volume: str) -> None:
        """Restore the optional primary-data archive carried by a fault image."""
        probe = self._run([
            "docker", "image", "inspect", "--format", "{{json .Config.Labels}}", self.image_name,
        ], check=False, timeout=30)
        try:
            labels = json.loads(probe.stdout) if probe.returncode == 0 else {}
        except json.JSONDecodeError:
            labels = {}
        if not isinstance(labels, dict):
            labels = {}
        if labels.get("aiopsbench.image_kind") != "fault":
            return
        self._run([
            "docker", "run", "--rm", "--user", "root", "--entrypoint", "bash",
            "--env", f"PGDATA={self.PGDATA}", "--volume", f"{volume}:{self.PGDATA}",
            *self._worker_cpuset_args(),
            self.image_name, "-lc",
            "rm -rf \"$PGDATA\"/* \"$PGDATA\"/.[!.]* 2>/dev/null || true; "
            "tar -xpf /opt/aiopsbench/replica-cascade/primary-data.tar -C \"$PGDATA\"; "
            "rm -f \"$PGDATA\"/postmaster.pid \"$PGDATA\"/postmaster.opts; "
            "chown -R postgres:postgres \"$PGDATA\"",
        ], timeout=300)

    def _psql(self, sql: str) -> str:
        result = self._run([
            "docker", "exec", self.container_name, "psql", "-X", "-v", "ON_ERROR_STOP=1",
            "-U", self.postgres_user, "-d", self.postgres_db, "-At", "-c", sql,
        ], check=False, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"PostgreSQL command failed: {result.stderr.strip()}")
        return result.stdout.strip()

    def _wait_primary(self, timeout: int = 300) -> None:
        deadline = time.time() + timeout
        initdb_shutdown_retry = False
        while time.time() < deadline:
            try:
                state = self._run([
                    "docker", "inspect", "--format", "{{.State.Status}} {{.State.ExitCode}}",
                    self.container_name,
                ], check=False, timeout=30)
            except subprocess.TimeoutExpired:
                # A busy Docker daemon can delay an inspect even after the
                # container has been created. Keep readiness bounded by the
                # fleet-wide timeout instead of turning a transient delay into
                # an infrastructure failure.
                continue
            if state.returncode != 0:
                raise RuntimeError(f"primary container disappeared before readiness: {self.container_name}")
            if not state.stdout.startswith("running "):
                logs = self._run(
                    ["docker", "logs", "--tail", "80", self.container_name],
                    check=False,
                    timeout=30,
                )
                log_tail = (logs.stdout + logs.stderr).strip()
                if (
                    not initdb_shutdown_retry
                    and state.stdout.startswith("exited 1")
                    and (
                        ("initdb:" in log_tail and "pg_ctl: server does not shut down" in log_tail)
                        or "pg_ctl: server did not start in time" in log_tail
                    )
                ):
                    # Docker/PostgreSQL can lose an initdb post-bootstrap
                    # shutdown or startup race under daemon contention. The
                    # volume is initialized at this point, so one bounded
                    # restart is safe; repeated or different exits remain
                    # infrastructure failures.
                    retry = self._run(
                        ["docker", "start", self.container_name],
                        check=False,
                        timeout=120,
                    )
                    initdb_shutdown_retry = True
                    if retry.returncode == 0:
                        continue
                raise RuntimeError(
                    f"primary container is not running: {self.container_name} "
                    f"state={state.stdout.strip()} logs={log_tail!r}"
                )
            result = self._run([
                "docker", "exec", self.container_name, "pg_isready", "-U", self.postgres_user,
                "-d", self.postgres_db,
            ], check=False, timeout=60)
            if result.returncode == 0:
                database = self._run([
                    "docker", "exec", self.container_name, "psql", "-X", "-At",
                    "-U", self.postgres_user, "-d", self.postgres_db, "-c", "SELECT 1",
                ], check=False, timeout=60)
                if database.returncode == 0 and database.stdout.strip() == "1":
                    return
            time.sleep(1)
        raise RuntimeError(f"primary did not become ready: container={self.container_name}")

    def _wait_postgres_container(self, name: str, timeout: int = 180) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            # Unrelated benchmark containers can delay Docker exec. Keep the
            # fleet readiness deadline bounded while allowing the control
            # plane more than one short scheduling slice.
            command_timeout = max(5, min(60, timeout))
            result = self._run([
                "docker", "exec", name, "pg_isready", "-U", self.postgres_user,
                "-d", self.postgres_db,
            ], check=False, timeout=command_timeout)
            if result.returncode == 0:
                database = self._run([
                    "docker", "exec", name, "psql", "-X", "-At",
                    "-U", self.postgres_user, "-d", self.postgres_db, "-c", "SELECT 1",
                ], check=False, timeout=command_timeout)
                if database.returncode == 0 and database.stdout.strip() == "1":
                    return True
            time.sleep(1)
        return False

    def _tcp_ready(self, port: int, timeout: float = 1.0) -> bool:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=timeout):
                return True
        except OSError:
            return False

    def _wait_fleet_ready(self, timeout: int = 300) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            check_timeout = min(60, max(1, int(deadline - time.time())))
            if not self._wait_postgres_container(self.container_name, timeout=check_timeout):
                continue
            replicas_ready = all(
                self._wait_postgres_container(
                    name,
                    timeout=min(60, max(1, int(deadline - time.time()))),
                )
                for name in self.replica_container_names
            )
            if replicas_ready and self._tcp_ready(self.ports.router) and self._tcp_ready(self.ports.pgbouncer):
                return True
            time.sleep(1)
        return False

    def _configure_primary(self) -> None:
        self._run([
            "docker", "exec", self.container_name, "bash", "-lc",
            "hba=/var/lib/postgresql/data/pgdata/pg_hba.conf; "
            "for line in "
            "'host replication replica_user 0.0.0.0/0 scram-sha-256' "
            "'host all all 0.0.0.0/0 scram-sha-256'; do "
            "grep -Fqx \"$line\" \"$hba\" || printf '%s\\n' \"$line\" >> \"$hba\"; "
            "done",
        ])
        if not self._psql("SELECT 1 FROM pg_roles WHERE rolname = 'replica_user'"):
            self._psql("CREATE ROLE replica_user WITH REPLICATION LOGIN PASSWORD 'replica_password'")
        else:
            self._psql("ALTER ROLE replica_user WITH REPLICATION LOGIN PASSWORD 'replica_password'")
        if not self._psql("SELECT 1 FROM pg_roles WHERE rolname = 'report'"):
            self._psql("CREATE ROLE report WITH LOGIN PASSWORD 'report_password'")
        else:
            self._psql("ALTER ROLE report WITH LOGIN PASSWORD 'report_password'")
        for setting, value in (
            ("wal_level", "'replica'"),
            ("max_wal_senders", "'8'"),
            ("max_replication_slots", "'8'"),
        ):
            self._psql(f"ALTER SYSTEM SET {setting} = {value}")
        self._psql("SELECT pg_reload_conf()")
        self._run(["docker", "restart", self.container_name], timeout=self.PRIMARY_RESTART_READY_TIMEOUT_SECONDS)
        self._wait_primary(timeout=self.PRIMARY_RESTART_READY_TIMEOUT_SECONDS)
        self._psql(
            "CREATE EXTENSION IF NOT EXISTS pg_stat_statements; "
            "CREATE TABLE IF NOT EXISTS rc_customers(id bigint PRIMARY KEY, region integer NOT NULL, tier integer NOT NULL); "
            "CREATE TABLE IF NOT EXISTS rc_orders(id bigint PRIMARY KEY, customer_id bigint NOT NULL, status integer NOT NULL, amount numeric NOT NULL); "
            "CREATE TABLE IF NOT EXISTS rc_order_items(id bigint PRIMARY KEY, order_id bigint NOT NULL, sku integer NOT NULL, quantity integer NOT NULL); "
            "CREATE TABLE IF NOT EXISTS rc_products(id bigint PRIMARY KEY, category integer NOT NULL, price numeric NOT NULL); "
            "CREATE TABLE IF NOT EXISTS rc_write_probe(id integer PRIMARY KEY, writes bigint NOT NULL, touched_at timestamptz NOT NULL); "
            "INSERT INTO rc_customers SELECT i, i % 64, i % 8 FROM generate_series(1, 2000) i ON CONFLICT DO NOTHING; "
            "INSERT INTO rc_orders SELECT i, ((i - 1) % 2000) + 1, i % 5, (i % 900) + 10 FROM generate_series(1, 10000) i ON CONFLICT DO NOTHING; "
            "INSERT INTO rc_order_items SELECT i, ((i - 1) % 10000) + 1, i % 300, (i % 4) + 1 FROM generate_series(1, 40000) i ON CONFLICT DO NOTHING; "
            "INSERT INTO rc_products SELECT i, i % 32, (i % 900) + 10 FROM generate_series(1, 300) i ON CONFLICT DO NOTHING; "
            "INSERT INTO rc_write_probe VALUES (1, 0, clock_timestamp()) ON CONFLICT DO NOTHING; "
            "CREATE INDEX IF NOT EXISTS rc_orders_customer_status_idx ON rc_orders(customer_id, status); "
            "CREATE INDEX IF NOT EXISTS rc_items_order_sku_idx ON rc_order_items(order_id, sku); "
            "CREATE INDEX IF NOT EXISTS rc_products_category_idx ON rc_products(category); "
            "GRANT USAGE ON SCHEMA public TO report; "
            "GRANT SELECT ON rc_orders TO report;"
        )
        footprint = " ".join(
            f"CREATE TABLE IF NOT EXISTS rc_footprint_{index:02d}(id integer PRIMARY KEY, value integer);"
            f" INSERT INTO rc_footprint_{index:02d} VALUES (1, {index}) ON CONFLICT DO NOTHING;"
            for index in range(96)
        )
        self._psql(footprint)

    def _start_replica_container(self, index: int) -> None:
        name = self.replica_container_names[index]
        volume = self.volume_names[f"replica_{index}"]
        try:
            self._run([
                "docker", "run", "--detach", "--name", name,
                "--network", self.network_name, "--network-alias", f"replica-{index}",
                "--publish", f"{self.ports.replicas[index]}:5432",
                "--env", f"PGDATA={self.PGDATA}", "--volume", f"{volume}:{self.PGDATA}",
                "--cpus", str(self.resources.get("cpus", 1.0)),
                "--memory", f"{self.resources.get('memory_mb', 512)}m",
                "--shm-size", str(self.resources.get("shm_size", "256m")),
                *self._worker_cpuset_args(),
                self.image_name, "postgres", "-c", "hot_standby=on",
                "-c", "shared_preload_libraries=pg_stat_statements",
                "-c", "logging_collector=on", "-c", "log_destination=stderr",
            ])
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"replica container failed to start: name={name!r}, "
                f"stderr={exc.stderr.strip()!r}, stdout={exc.stdout.strip()!r}"
            ) from exc

    def _clone_replica_volume(self, source: str, target: str) -> None:
        result = self._run([
            "docker", "run", "--rm", "--user", "root", "--entrypoint", "bash",
            "--volume", f"{source}:/source:ro", "--volume", f"{target}:/target",
            *self._worker_cpuset_args(),
            self.POSTGRES_IMAGE, "-lc",
            "rm -rf /target/* /target/.[!.]* 2>/dev/null || true; "
            "cp -a /source/. /target/; "
            "rm -f /target/postmaster.pid /target/postmaster.opts; "
            "chown -R postgres:postgres /target",
        ], check=False, timeout=900)
        if result.returncode != 0:
            raise RuntimeError(f"replica volume clone failed: {result.stderr.strip()}")

    def _create_replica(self, index: int, *, start: bool = True) -> None:
        name = self.replica_container_names[index]
        volume = self.volume_names[f"replica_{index}"]
        self._ensure_volume(volume)
        if self._container_exists(name):
            if start:
                self._run(["docker", "start", name], check=False)
            return
        if index == 0:
            backup_command = (
                f"rm -rf {self.PGDATA}/* {self.PGDATA}/.[!.]* 2>/dev/null || true; "
                f"chown -R postgres:postgres {self.PGDATA}; "
                f"PGPASSWORD=replica_password gosu postgres pg_basebackup -h primary -D {self.PGDATA} "
                "-U replica_user -Fp -Xs -P -R -c fast"
            )
            result = self._run([
                "docker", "run", "--rm", "--user", "root", "--entrypoint", "bash",
                "--network", self.network_name, "--volume", f"{volume}:{self.PGDATA}",
                *self._worker_cpuset_args(),
                self.POSTGRES_IMAGE, "-lc", backup_command,
            ], check=False, timeout=900)
        else:
            result = None
            self._clone_replica_volume(self.volume_names["replica_0"], volume)
        if result is not None and result.returncode != 0:
            raise RuntimeError(f"replica basebackup failed for replica_{index}: {result.stderr.strip()}")
        if start:
            self._start_replica_container(index)

    def _write_router_configs(self, excluded_replicas: set[int] | None = None) -> tuple[Path, Path, Path]:
        excluded_replicas = excluded_replicas or set()
        haproxy = self._runtime_dir / "haproxy.cfg"
        haproxy.write_text(
            "global\n  maxconn 512\ndefaults\n  mode tcp\n  timeout connect 500ms\n  timeout client 30s\n  timeout server 30s\n"
            "frontend postgres_read\n  bind *:5433\n  default_backend replicas\nbackend replicas\n  balance roundrobin\n  option tcp-check\n  default-server inter 250ms fall 2 rise 2\n"
            + "".join(
                f"  server replica_{i} replica-{i}:5432 check\n"
                for i in range(3) if i not in excluded_replicas
            ),
            encoding="utf-8",
        )
        pgbouncer = self._runtime_dir / "pgbouncer.ini"
        pgbouncer.write_text(
            "[databases]\n"
            "testdb = host=router port=5433 dbname=testdb user=postgres password=password\n"
            "testdb_report = host=router port=5433 dbname=testdb user=report password=report_password pool_size=1 reserve_pool_size=0\n\n"
            "[pgbouncer]\nlisten_addr = 0.0.0.0\nlisten_port = 6432\nauth_type = plain\nauth_file = /etc/pgbouncer/userlist.txt\n"
            "pool_mode = transaction\ndefault_pool_size = 4\nreserve_pool_size = 1\n"
            "max_client_conn = 128\nadmin_users = postgres\nserver_check_query = select 1\n"
            "server_connect_timeout = 1\nserver_login_retry = 1\n",
            encoding="utf-8",
        )
        userlist = self._runtime_dir / "userlist.txt"
        userlist.write_text('"postgres" "password"\n"report" "report_password"\n', encoding="utf-8")
        self._runtime_dir.chmod(0o755)
        for path in (haproxy, pgbouncer, userlist):
            path.chmod(0o644)
        return haproxy, pgbouncer, userlist

    def set_router_backends(self, *, excluded_replicas: tuple[str, ...] = ()) -> bool:
        """Apply an explicit read drain before stopping a replica."""
        excluded = {self.replica_index(replica) for replica in excluded_replicas}
        haproxy, _pgbouncer, _userlist = self._write_router_configs(excluded)
        if not self._container_exists(self.router_container_name):
            return False
        reloaded = self._run(
            ["docker", "kill", "--signal", "HUP", self.router_container_name],
            check=False,
            timeout=30,
        )
        return reloaded.returncode == 0 and self._tcp_ready(self.ports.router, timeout=5.0)

    def _start_router_and_pool(self) -> None:
        if self._container_exists(self.router_container_name):
            self._run(["docker", "start", self.router_container_name], check=False)
            if self._container_exists(self.pgbouncer_container_name):
                self._run(["docker", "start", self.pgbouncer_container_name], check=False)
                return
        haproxy, pgbouncer, userlist = self._write_router_configs()
        router = self._run([
            "docker", "run", "--detach", "--name", self.router_container_name,
            "--network", self.network_name, "--network-alias", "router",
            "--publish", f"{self.ports.router}:5433",
            "--volume", f"{haproxy}:/usr/local/etc/haproxy/haproxy.cfg:ro",
            *self._worker_cpuset_args(),
            self.ROUTER_IMAGE, "haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg",
        ], check=False)
        if router.returncode != 0:
            raise RuntimeError(f"HAProxy router failed to start: {router.stderr.strip()}")
        pgbouncer_image = self.PGBOUNCER_IMAGE
        if not self._image_exists(pgbouncer_image) and self._image_exists(self.PGBOUNCER_LOCAL_FALLBACK):
            pgbouncer_image = self.PGBOUNCER_LOCAL_FALLBACK
        pool = self._run([
            "docker", "run", "--detach", "--name", self.pgbouncer_container_name,
            "--network", self.network_name, "--publish", f"{self.ports.pgbouncer}:6432",
            "--volume", f"{pgbouncer}:/etc/pgbouncer/pgbouncer.ini:ro",
            "--volume", f"{userlist}:/etc/pgbouncer/userlist.txt:ro",
            *self._worker_cpuset_args(),
            pgbouncer_image, "/etc/pgbouncer/pgbouncer.ini",
        ], check=False)
        if pool.returncode != 0:
            raise RuntimeError(f"PgBouncer failed to start: {pool.stderr.strip()}")

    def deploy(self) -> None:
        if self._port_lease is None:
            self._port_lease = claim_host_ports(self.all_ports, owner=self.identity)
        self._assert_ports_available()
        self._ensure_image()
        self._ensure_network()
        self._ensure_volume(self.volume_names["primary"])
        self._start_primary()
        self._wait_primary(timeout=self.PRIMARY_RESTART_READY_TIMEOUT_SECONDS)
        self._configure_primary()
        for name in self.replica_container_names:
            if self._container_exists(name):
                self._container_action(name, "stop")
        for index in range(3):
            self._create_replica(index, start=False)
        for index in range(3):
            if not self._container_exists(self.replica_container_names[index]):
                self._start_replica_container(index)
            else:
                self._run(["docker", "start", self.replica_container_names[index]], check=False)
        self._start_router_and_pool()
        if not self._wait_fleet_ready(timeout=300):
            raise RuntimeError(f"replica fleet did not become ready: identity={self.identity}")

    def is_ready(self) -> bool:
        check_timeout = 10
        replicas = all(
            self._wait_postgres_container(name, timeout=check_timeout)
            for name in self.replica_container_names
        )
        return (
            self._wait_postgres_container(self.container_name, timeout=check_timeout)
            and replicas
            and self._tcp_ready(self.ports.router)
            and self._tcp_ready(self.ports.pgbouncer)
        )

    def wait_for_ready(self, timeout: int = 300) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.is_ready():
                return True
            time.sleep(1)
        return False

    def _container_action(self, name: str, action: str) -> bool:
        if not self._container_exists(name):
            return False
        return self._run(["docker", action, name], check=False, timeout=120).returncode == 0

    def start_pg(self) -> bool:
        return self._container_action(self.container_name, "start")

    def stop_pg(self) -> bool:
        return self._container_action(self.container_name, "stop")

    def restart_pg(self) -> bool:
        return self._container_action(self.container_name, "restart")

    def is_container_running(self) -> bool:
        result = self._run(["docker", "inspect", "--format", "{{.State.Running}}", self.container_name], check=False, timeout=10)
        return result.returncode == 0 and result.stdout.strip() == "true"

    def stop_replica(self, replica: str) -> bool:
        index = self.replica_index(replica)
        return self._container_action(self.replica_container_names[index], "stop")

    def start_replica(self, replica: str) -> bool:
        index = self.replica_index(replica)
        return self._container_action(self.replica_container_names[index], "start")

    def wait_for_replica_ready(self, replica: str, timeout: int = 180) -> bool:
        index = self.replica_index(replica)
        if not self._wait_postgres_container(self.replica_container_names[index], timeout=timeout):
            return False
        deadline = time.time() + timeout
        port = self.ports.replicas[index]
        while time.time() < deadline:
            if self._tcp_ready(port, timeout=1.0):
                try:
                    import psycopg2

                    connection = psycopg2.connect(
                        host="127.0.0.1",
                        port=port,
                        user=self.postgres_user,
                        password=self.postgres_password,
                        dbname=self.postgres_db,
                        connect_timeout=3,
                    )
                    connection.close()
                    return True
                except Exception:
                    pass
            time.sleep(1)
        return False

    def replica_index(self, replica: str) -> int:
        text = str(replica).strip().casefold().replace("-", "_")
        if text.startswith("replica_"):
            index = int(text.removeprefix("replica_"))
        elif text.startswith("read_replica_"):
            index = int(text.removeprefix("read_replica_"))
        else:
            raise ValueError(f"unknown replica target: {replica!r}")
        if index not in range(3):
            raise ValueError(f"replica index outside fleet: {replica!r}")
        return index

    def replica_endpoint(self, replica: str) -> tuple[str, int]:
        index = self.replica_index(replica)
        return "127.0.0.1", self.ports.replicas[index]

    def save_primary_image(self, image_name: str, labels: Mapping[str, str] | None = None) -> None:
        """Commit the primary image and include named-volume data for snapshot/use."""
        self._psql("CHECKPOINT;")
        helper = f"{self.identity}-snapshot-helper"
        self._run(["docker", "rm", "--force", helper], check=False, timeout=60)
        commit = ["docker", "commit"]
        for key, value in (labels or {}).items():
            commit.extend(["--change", f"LABEL {key}={json.dumps(str(value))}"])
        try:
            self._run([
                "docker", "run", "--detach", "--name", helper,
                "--volumes-from", f"{self.container_name}:ro",
                "--env", f"PGDATA={self.PGDATA}",
                *self._worker_cpuset_args(),
                "--entrypoint", "bash", self.image_name, "-lc",
                "set -e; mkdir -p /opt/aiopsbench/replica-cascade; "
                "tar --exclude=postmaster.pid --exclude=postmaster.opts "
                "-cpf /opt/aiopsbench/replica-cascade/primary-data.tar "
                "-C \"$PGDATA\" .",
            ], timeout=120)
            wait = self._run(["docker", "wait", helper], timeout=300)
            if wait.returncode != 0 or wait.stdout.strip() != "0":
                raise RuntimeError(f"snapshot archive helper failed: {wait.stderr.strip()}")
            commit.extend([helper, image_name])
            result = self._run(commit, check=False, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"fault image commit failed: {result.stderr.strip()}")
        finally:
            self._run(["docker", "rm", "--force", helper], check=False, timeout=60)

    def teardown(self) -> None:
        for name in reversed(self._known_containers):
            self._run(["docker", "rm", "--force", name], check=False, timeout=60)
        for volume in self.volume_names.values():
            self._run(["docker", "volume", "rm", "--force", volume], check=False, timeout=60)
        self._run(["docker", "network", "rm", self.network_name], check=False, timeout=60)
        shutil.rmtree(self._runtime_dir, ignore_errors=True)
        if self._port_lease is not None:
            self._port_lease.close()
            self._port_lease = None


class PgReplicaFleetEnv(PGEnv):
    """PGEnv variant exposing primary control and replica/pool observability."""

    # Keep the full normal capture and target capture in the live sampler
    # while the frozen history is being assembled.
    FLEET_HISTORY_MAX_SAMPLES = 4_000
    # The lock-manager wait is short-lived. Keep a dense enough sampling
    # window to observe real LWLock:LockManager waits without changing the
    # evaluator contract or fabricating a history point.
    FLEET_HISTORY_INTERVAL_SECONDS = 0.20
    # A single point per 200ms sampler tick can miss the short real
    # LockManager wait burst even while the probe admission sees it. Keep
    # this bounded sub-window independent of the Agent-facing snapshot.
    # Sixteen endpoint sub-samples remain below the existing jitter budget
    # while making short waiter bursts observable in public history. The
    # admission contract still requires three nonzero history samples across
    # ticks.
    FLEET_HISTORY_WAITER_SAMPLE_COUNT = 16
    FLEET_HISTORY_MAX_JITTER_STEPS = 3
    # Normal endpoint activity can produce a small non-zero duration even
    # without the cascade.  Treat a bounded elevated duration as the public
    # downstream signal that must follow the real waiter lead.
    FLEET_HISTORY_DURATION_SIGNAL_MS = 2_000.0
    # Keep the observation window bounded while giving short real waits more
    # than one chance to appear in pg_stat_activity.
    FLEET_WAITER_SAMPLE_COUNT = 240
    FLEET_WAITER_SAMPLE_INTERVAL_SECONDS = 0.001

    def __init__(self, *, deployment: PgReplicaFleetDeployment, **kwargs: Any):
        super().__init__(deployment=deployment, port=deployment.ports.primary, **kwargs)
        # Keep the ordinary PG sampler as the live provider, but validate and
        # serve the fleet-specific frozen frames through the shared history
        # service after the timeline is bound.
        live_provider = self._metric_service.live
        self._metric_catalog = REPLICA_FLEET_METRIC_CATALOG
        self._metric_service = MetricService(catalog=self._metric_catalog, live=live_provider)
        self.deployment = deployment
        self.port = deployment.ports.primary
        self._direct_connections: dict[str, Any] = {}
        self._last_replay_artifact: dict[str, Any] | None = None
        self._fleet_history: deque[dict[str, Any]] = deque(maxlen=self.FLEET_HISTORY_MAX_SAMPLES)
        self._fleet_history_lock = threading.Lock()
        self._fleet_history_stop = threading.Event()
        self._fleet_history_thread: threading.Thread | None = None
        self._last_replica_calls: dict[str, tuple[int, int]] = {}
        self._last_primary_write_calls: tuple[int, int] | None = None
        self._last_footprint_calls: dict[str, tuple[int, int]] = {}
        self._replay_nonce = uuid.uuid4().hex

    def _enrich_fleet_observation(self, observation: dict[str, Any]) -> dict[str, Any]:
        """Add rate/footprint fields derived from adjacent real snapshots."""
        timestamp_ms = self._snapshot_timestamp_ms(observation)
        replicas = observation.get("replicas", {})
        for target, value in replicas.items():
            calls = int(value.get("query_calls_total", 0) or 0)
            previous = self._last_replica_calls.get(target)
            if previous is None or timestamp_ms <= previous[1]:
                qps = 0.0
            else:
                qps = max(0.0, (calls - previous[0]) / max(0.001, (timestamp_ms - previous[1]) / 1000.0))
            self._last_replica_calls[target] = (calls, timestamp_ms)
            value["queries_per_sec"] = round(qps, 3)
        primary = observation.setdefault("primary", {})
        write_calls = int(primary.get("write_calls_total", 0) or 0)
        if self._last_primary_write_calls is None or timestamp_ms <= self._last_primary_write_calls[1]:
            write_tps = 0.0
        else:
            write_tps = max(
                0.0,
                (write_calls - self._last_primary_write_calls[0])
                / max(0.001, (timestamp_ms - self._last_primary_write_calls[1]) / 1000.0),
            )
        self._last_primary_write_calls = (write_calls, timestamp_ms)
        primary["write_tps"] = round(write_tps, 3)
        lag_values = []
        for row in self._replication_rows(observation.get("replication", {})):
            for key in ("flush_lag", "replay_lag"):
                raw_lag = row.get(key)
                if raw_lag in (None, ""):
                    continue
                try:
                    if hasattr(raw_lag, "total_seconds"):
                        lag_values.append(float(raw_lag.total_seconds()))
                    elif isinstance(raw_lag, str) and raw_lag.count(":") == 2:
                        hours, minutes, seconds = raw_lag.split(":")
                        lag_values.append(int(hours) * 3600 + int(minutes) * 60 + float(seconds))
                    else:
                        lag_values.append(float(raw_lag))
                except (TypeError, ValueError):
                    continue
        # During the first few samples after replica startup, pg_stat_replication
        # can legitimately be empty before streaming connections register. Keep
        # the public history field numeric for that transient baseline; replay
        # validation still reads the live replication contract independently.
        primary["replication_lag_max_sec"] = max(lag_values) if lag_values else 0.0

        footprint_sources = observation.get("footprint_sources", {})
        footprint = {}
        for family, source in footprint_sources.items():
            calls = int(source.get("query_calls_total", 0) or 0)
            previous = self._last_footprint_calls.get(family)
            if previous is None or timestamp_ms <= previous[1]:
                transactions_per_sec = 0.0
            else:
                transactions_per_sec = max(
                    0.0,
                    (calls - previous[0])
                    / max(0.001, (timestamp_ms - previous[1]) / 1000.0),
                )
            self._last_footprint_calls[family] = (calls, timestamp_ms)
            footprint[family] = {
                "transactions_per_sec": round(transactions_per_sec, 3),
                "mean_relation_locks": float(source.get("mean_relation_locks", 0.0) or 0.0),
                "slowpath_fraction": float(source.get("slowpath_fraction", 0.0) or 0.0),
            }
        observation["query_footprint"] = {
            "checkout_read_footprint": footprint.get("checkout_read_footprint", {}),
            "checkout_read_footprint_simple": footprint.get("checkout_read_footprint_simple", {}),
            "report_pool": footprint.get("report_pool", {}),
        }
        return observation

    @staticmethod
    def _replication_rows(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
        """Normalize trusted SQL rows and the internal sampler row shape."""
        if not isinstance(payload, Mapping):
            return ()
        rows = payload.get("result", ())
        columns = payload.get("columns", ())
        if not isinstance(rows, (list, tuple)):
            return ()
        normalized = []
        for row in rows:
            if isinstance(row, Mapping):
                normalized.append(row)
            elif isinstance(row, (list, tuple)) and isinstance(columns, (list, tuple)):
                normalized.append(dict(zip(columns, row)))
        return tuple(normalized)

    def metric_history_catalog(self):
        return REPLICA_FLEET_METRIC_CATALOG

    @staticmethod
    def _snapshot_timestamp_ms(sample: Mapping[str, Any]) -> int:
        value = str(sample.get("observed_at", ""))
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return int(parsed.timestamp() * 1000)

    def _fleet_snapshots_for_range(self, start_ms: int, end_ms: int) -> tuple[dict[str, Any], ...]:
        with self._fleet_history_lock:
            snapshots = tuple(self._fleet_history)
        selected = tuple(
            sample for sample in snapshots
            if start_ms <= self._snapshot_timestamp_ms(sample) <= end_ms
        )
        if not selected:
            raise RuntimeError(
                "replica fleet history has no samples for requested capture: "
                f"window=({start_ms},{end_ms}), available={len(snapshots)}"
            )
        return tuple(sorted(selected, key=self._snapshot_timestamp_ms))

    def history_has_waiter_samples(
        self,
        *,
        min_waiter_samples: int = 3,
        start_ms: int | None = None,
        end_ms: int | None = None,
    ) -> bool:
        """Return whether frozen-admission history contains real waiters."""
        with self._fleet_history_lock:
            snapshots = tuple(self._fleet_history)
        waiter_samples = 0
        for sample in snapshots:
            timestamp_ms = self._snapshot_timestamp_ms(sample)
            if start_ms is not None and timestamp_ms < start_ms:
                continue
            if end_ms is not None and timestamp_ms > end_ms:
                continue
            for value in sample.get("replicas", {}).values():
                if not value.get("healthy"):
                    continue
                observed_samples = int(value.get("lwlock_wait_samples", 0) or 0)
                if observed_samples > 0:
                    waiter_samples += observed_samples
                elif int(value.get("lwlock_waiters", 0) or 0) > 0:
                    # Test doubles and older snapshots only carry the scalar
                    # waiter observation; count that as one real sample.
                    waiter_samples += 1
        return waiter_samples >= min_waiter_samples

    def history_has_waiter_lead(
        self,
        *,
        min_waiter_samples: int = 3,
        start_ms: int | None = None,
        end_ms: int | None = None,
    ) -> bool:
        """Require waiter -> duration -> read-pool queue in public history."""
        with self._fleet_history_lock:
            snapshots = tuple(self._fleet_history)
        waiter_times = []
        duration_times = []
        pool_times = []
        for sample in snapshots:
            timestamp_ms = self._snapshot_timestamp_ms(sample)
            if start_ms is not None and timestamp_ms < start_ms:
                continue
            if end_ms is not None and timestamp_ms > end_ms:
                continue
            waiter_sample_count = 0
            for value in sample.get("replicas", {}).values():
                if not value.get("healthy"):
                    continue
                observed_samples = int(value.get("lwlock_wait_samples", 0) or 0)
                if observed_samples > 0:
                    waiter_sample_count += observed_samples
                elif int(value.get("lwlock_waiters", 0) or 0) > 0:
                    # Test doubles and older snapshots only carry the scalar
                    # waiter observation; count that as one real sample.
                    waiter_sample_count += 1
            waiter_times.extend([timestamp_ms] * waiter_sample_count)
            duration_signal = False
            for value in sample.get("replicas", {}).values():
                if not value.get("healthy"):
                    continue
                duration_signal = duration_signal or max(
                    float(value.get("p95_query_duration_ms", 0.0) or 0.0),
                    float(value.get("p99_query_duration_ms", 0.0) or 0.0),
                ) >= self.FLEET_HISTORY_DURATION_SIGNAL_MS
            if duration_signal:
                duration_times.append(timestamp_ms)
            read_pool_waiting = any(
                str(row.get("database", "")).casefold() == "testdb"
                and int(row.get("cl_waiting", 0) or 0) > 0
                for row in sample.get("pool", {}).get("rows", ())
            )
            if read_pool_waiting or (
                not sample.get("pool", {}).get("rows")
                and int(sample.get("pool", {}).get("waiting_clients", 0) or 0) > 0
            ):
                pool_times.append(timestamp_ms)
        if (
            len(waiter_times) < min_waiter_samples
            or not duration_times
            or not pool_times
        ):
            return False
        first_waiter_ms = min(waiter_times)
        first_pool_ms = min(pool_times)
        duration_after_waiter = [
            timestamp_ms for timestamp_ms in duration_times
            if timestamp_ms > first_waiter_ms
        ]
        if not duration_after_waiter:
            return False
        first_duration_ms = min(duration_after_waiter)
        return (
            first_waiter_ms < first_duration_ms < first_pool_ms
            and sum(timestamp_ms < first_duration_ms for timestamp_ms in waiter_times) >= min_waiter_samples
        )

    @staticmethod
    def _nearest_snapshot(
        snapshots: tuple[dict[str, Any], ...],
        timestamp_ms: int,
        *,
        max_distance_ms: int,
        snapshot_times: tuple[int, ...] | None = None,
    ) -> dict[str, Any]:
        times = snapshot_times or tuple(PgReplicaFleetEnv._snapshot_timestamp_ms(item) for item in snapshots)
        insertion = bisect_left(times, timestamp_ms)
        candidates = {
            max(0, insertion - 1),
            min(len(snapshots) - 1, insertion),
        }
        index = min(candidates, key=lambda item: abs(times[item] - timestamp_ms))
        sample = snapshots[index]
        distance = abs(times[index] - timestamp_ms)
        if distance > max_distance_ms:
            raise RuntimeError(
                "replica fleet history has a sampling gap: "
                f"timestamp_ms={timestamp_ms}, nearest_distance_ms={distance}, max_distance_ms={max_distance_ms}"
            )
        return sample

    @staticmethod
    def _pool_row(rows: Any, name: str) -> Mapping[str, Any]:
        normalized = "testdb_report" if name == "report_pool" else "testdb"
        for row in rows or ():
            if str(row.get("database", "")).casefold() == normalized:
                return row
        return {}

    @staticmethod
    def _required_pool_row(rows: Any, name: str) -> Mapping[str, Any]:
        row = PgReplicaFleetEnv._pool_row(rows, name)
        if not row:
            expected_database = "testdb_report" if name == "report_pool" else "testdb"
            raise RuntimeError(
                "replica fleet pool observation is incomplete: "
                f"pool={name!r}, expected_database={expected_database!r}"
            )
        return row

    @staticmethod
    def _replica_replay_lag(value: Mapping[str, Any], target: str) -> float:
        raw_lag = value.get("replay_lag_sec")
        if raw_lag is None:
            # A healthy standby can answer before pg_last_xact_replay_timestamp
            # has a value during its first streaming samples. Keep the public
            # history frame numeric for that startup interval; replay checks
            # still use the live replication contract after readiness.
            return 0.0
        return max(0.0, float(raw_lag))

    @staticmethod
    def _required_primary_lag(primary: Mapping[str, Any]) -> float:
        raw_lag = primary.get("replication_lag_max_sec")
        if raw_lag is None:
            raise RuntimeError("primary replication-lag observation is unavailable")
        return max(0.0, float(raw_lag))

    @staticmethod
    def _metric_series(sample: Mapping[str, Any], metric: str) -> dict[str, dict[str, float]]:
        replicas = sample.get("replicas", {})
        healthy = [name for name, value in replicas.items() if value.get("healthy")]
        active_count = max(1, len(healthy))
        if metric == "router_distribution":
            return {
                name: {
                    "active_replicas": float(len(healthy)),
                    "traffic_share_percent": 100.0 / active_count if name in healthy else 0.0,
                    "requests_per_sec": float(value.get("queries_per_sec", value.get("active_backends", 0.0)) or 0.0),
                }
                for name, value in replicas.items()
            }
        if metric == "replica_service":
            return {
                name: {
                    "queries_per_sec": float(value.get("queries_per_sec", value.get("active_backends", 0.0)) or 0.0),
                    "p95_ms": float(value.get("p95_query_duration_ms", 0.0) or 0.0),
                    "p99_ms": float(value.get("p99_query_duration_ms", value.get("p95_query_duration_ms", 0.0)) or 0.0),
                    "active_backends": float(value.get("active_backends", 0.0) or 0.0),
                    # An unavailable replica has no meaningful replay lag.
                    # Keep that service series numeric at zero, but fail
                    # explicitly for a healthy replica with no observation.
                    "replay_lag_sec": PgReplicaFleetEnv._replica_replay_lag(value, name),
                }
                for name, value in replicas.items()
            }
        if metric == "replica_lwlock":
            return {
                name: {
                    "lock_manager_waiters": float(value.get("lwlock_waiters", 0.0) or 0.0),
                    "waiter_ms_per_sec": float(value.get("waiter_ms_per_sec", 0.0) or 0.0),
                    "slowpath_backends": float(value.get("slowpath_backends", 0.0) or 0.0),
                }
                for name, value in replicas.items()
            }
        if metric == "query_footprint":
            footprint = sample.get("query_footprint", {})
            return {
                name: {
                    "transactions_per_sec": float(value.get("transactions_per_sec", 0.0) or 0.0),
                    "mean_relation_locks": float(value.get("mean_relation_locks", 0.0) or 0.0),
                    "slowpath_fraction": float(value.get("slowpath_fraction", 0.0) or 0.0),
                }
                for name, value in {
                    "checkout_read_footprint": footprint.get("checkout_read_footprint", {}),
                    "checkout_read_footprint_simple": footprint.get("checkout_read_footprint_simple", footprint.get("checkout_read_footprint", {})),
                    "report_pool": footprint.get("report_pool", {}),
                }.items()
            }
        if metric == "pgbouncer_pool":
            rows = sample.get("pool", {}).get("rows", ())
            pool_rows = {
                name: PgReplicaFleetEnv._required_pool_row(rows, name)
                for name in ("read_pool", "report_pool")
            }
            return {
                name: {
                    "sv_active": float(pool_rows[name].get("sv_active", 0.0) or 0.0),
                    "sv_idle": float(pool_rows[name].get("sv_idle", 0.0) or 0.0),
                    "cl_waiting": float(pool_rows[name].get("cl_waiting", 0.0) or 0.0),
                    "maxwait_sec": PgReplicaFleetEnv._pool_wait_ms(pool_rows[name]) / 1000.0,
                }
                for name in pool_rows
            }
        if metric == "primary_service":
            primary = sample.get("primary", {})
            return {
                "primary": {
                    "write_tps": float(primary.get("write_tps", 0.0) or 0.0),
                    "p99_ms": float(primary.get("p99_query_duration_ms", 0.0) or 0.0),
                    "replication_lag_max_sec": PgReplicaFleetEnv._required_primary_lag(primary),
                }
            }
        raise ValueError(f"unknown replica fleet metric: metric={metric!r}")

    def _fleet_metric_frames(
        self,
        metrics: tuple[str, ...],
        start_ms: int,
        end_ms: int,
        step_seconds: int,
    ) -> tuple[MetricFrame, ...]:
        if step_seconds <= 0:
            raise ValueError(f"fleet metric capture step must be positive: step_seconds={step_seconds}")
        timestamps = tuple(range(start_ms, end_ms + 1, step_seconds * 1000))
        if len(timestamps) < 2:
            raise ValueError("fleet metric capture window must contain at least two samples")
        snapshots = self._fleet_snapshots_for_range(start_ms, end_ms)
        snapshot_times = tuple(self._snapshot_timestamp_ms(sample) for sample in snapshots)
        frames: list[MetricFrame] = []
        for raw_metric in metrics:
            metric = str(raw_metric).casefold()
            definition = self._metric_catalog.definition(metric)
            if metric not in FLEET_METRIC_NAMES:
                continue
            variants = self._metric_catalog.target_variants(metric, self.deployment)
            for query_target in variants:
                series: dict[str, dict[str, list[float]]] = {}
                for timestamp in timestamps:
                    values = self._metric_series(
                        self._nearest_snapshot(
                            snapshots,
                            timestamp,
                            # A bounded two-step tolerance absorbs scheduler
                            # jitter under real contention without hiding a
                            # longer sampler outage.
                            max_distance_ms=max(
                                step_seconds * self.FLEET_HISTORY_MAX_JITTER_STEPS * 1000,
                                int(self.FLEET_HISTORY_INTERVAL_SECONDS * 3 * 1000),
                            ),
                            snapshot_times=snapshot_times,
                        ),
                        metric,
                    )
                    if query_target is None:
                        selected = values
                    else:
                        selected = {query_target: values.get(query_target, {})}
                    for series_target, fields in selected.items():
                        target_fields = series.setdefault(series_target, {field: [] for field in definition.value_fields})
                        for field in definition.value_fields:
                            if field not in fields:
                                raise RuntimeError(
                                    "replica fleet metric observation is incomplete: "
                                    f"metric={metric!r}, target={series_target!r}, field={field!r}"
                                )
                            target_fields[field].append(float(fields[field]))
                frames.append(MetricFrame(
                    metric=metric,
                    query_target=query_target,
                    step_seconds=step_seconds,
                    series=series,
                    timestamps_ms={target: timestamps for target in series},
                ))
        return tuple(frames)

    def capture_metric_history(
        self,
        metrics: tuple[str, ...],
        start_epoch_ms: int,
        end_epoch_ms: int,
        step_seconds: int,
        *,
        metric_targets: Mapping[str, tuple[str | None, ...]] | None = None,
        rate_windows: Mapping[str, int] | None = None,
    ):
        base_metrics = tuple(metric for metric in metrics if str(metric).casefold() not in FLEET_METRIC_NAMES)
        fleet_metrics = tuple(metric for metric in metrics if str(metric).casefold() in FLEET_METRIC_NAMES)
        frames = list(super().capture_metric_history(
            base_metrics,
            start_epoch_ms,
            end_epoch_ms,
            step_seconds,
            metric_targets=metric_targets,
            rate_windows=rate_windows,
        )) if base_metrics else []
        frames.extend(self._fleet_metric_frames(fleet_metrics, start_epoch_ms, end_epoch_ms, step_seconds))
        return tuple(frames)

    def capture_history_records(self, sources, start_epoch_ms: int, end_epoch_ms: int):
        non_events = tuple(source for source in sources if source is not HistoricalRecordSource.OPERATION_EVENT)
        captured = super().capture_history_records(non_events, start_epoch_ms, end_epoch_ms)
        if HistoricalRecordSource.OPERATION_EVENT not in sources:
            return captured
        point_records = list(captured.point_records)
        for sample in self._fleet_snapshots_for_range(start_epoch_ms, end_epoch_ms):
            timestamp_ms = self._snapshot_timestamp_ms(sample)
            replicas = sample.get("replicas", {})
            healthy = [name for name, value in replicas.items() if value.get("healthy")]
            for target, value in replicas.items():
                point_records.append(HistoricalPointRecord(
                    source=HistoricalRecordSource.OPERATION_EVENT,
                    target=target,
                    timestamp_ms=timestamp_ms,
                    payload={
                        "event_type": "replica_lifecycle",
                        "operation": "health_snapshot",
                        "entity": target,
                        "status": "healthy" if value.get("healthy") else "unavailable",
                        "active_replicas": len(healthy),
                        "traffic_share_percent": 100.0 / max(1, len(healthy)) if value.get("healthy") else 0.0,
                    },
                ))
            point_records.append(HistoricalPointRecord(
                source=HistoricalRecordSource.OPERATION_EVENT,
                target="router",
                timestamp_ms=timestamp_ms,
                payload={
                    "event_type": "router_revision",
                    "operation": "route_snapshot",
                    "entity": "router",
                    "status": "ready" if healthy else "degraded",
                    "active_replicas": len(healthy),
                },
            ))
            for target, value in self._metric_series(sample, "query_footprint").items():
                point_records.append(HistoricalPointRecord(
                    source=HistoricalRecordSource.OPERATION_EVENT,
                    target=target,
                    timestamp_ms=timestamp_ms,
                    payload={
                        "event_type": "query_footprint_sample",
                        "operation": "footprint_observation",
                        "entity": target,
                        "status": "observed",
                        **value,
                    },
                ))
            for target in ("read_pool", "report_pool"):
                value = self._metric_series(sample, "pgbouncer_pool")[target]
                point_records.append(HistoricalPointRecord(
                    source=HistoricalRecordSource.OPERATION_EVENT,
                    target=target,
                    timestamp_ms=timestamp_ms,
                    payload={
                        "event_type": "pool_snapshot",
                        "operation": "pool_observation",
                        "entity": target,
                        "status": "observed",
                        **value,
                    },
                ))
        coverage = list(captured.coverage)
        coverage.append(HistoricalCoverage(
            source=HistoricalRecordSource.OPERATION_EVENT,
            target=None,
            start_ms=start_epoch_ms,
            end_ms=end_epoch_ms,
        ))
        return CapturedRecords(
            point_records=tuple(point_records),
            interval_records=captured.interval_records,
            coverage=tuple(coverage),
        )

    def configure_runtime(self, runtime: PgReplicaFleetRuntime) -> None:
        if not isinstance(runtime, PgReplicaFleetRuntime):
            raise TypeError(f"PgReplicaFleetEnv requires PgReplicaFleetRuntime, got {type(runtime).__name__}")
        if not self.deployment._ports_are_explicit:
            self.deployment.ports = runtime.ports
        if runtime.resources is not None:
            self.deployment.resources.update({
                "cpus": runtime.resources.container_cpu_limit,
                "memory_mb": runtime.resources.container_memory_mb,
            })
        # The entrypoint may intentionally allocate an isolated port range.
        # Keep the environment connection aligned with that deployment after
        # the case runtime contract is applied.
        self.port = self.deployment.ports.primary

    def deploy(self) -> None:
        self.deployment.deploy()
        if not self.deployment.wait_for_ready(timeout=180):
            raise RuntimeError(f"replica fleet is not ready: identity={self.deployment.identity}")
        if not self._ensure_connection():
            raise RuntimeError("primary control connection could not be established")
        self._start_sampler()
        self._start_fleet_history_sampler()
        self._snapshot_pgss_baseline()

    def base_snapshot_name(self, case) -> str:
        return case.base_image_name

    def snapshot_name(self, scenario_id: str, case) -> str:
        return case.fault_image_name

    def snapshot_exists(self, snapshot_name: str) -> bool:
        return self.deployment._image_exists(snapshot_name)

    def select_snapshot(self, snapshot_name: str, base_snapshot_name: str) -> None:
        self.deployment.image_name = snapshot_name
        self.baseline_image_name = base_snapshot_name

    def save_snapshot(self, snapshot_name: str, labels: Mapping[str, str]) -> None:
        self.deployment.save_primary_image(snapshot_name, labels)

    def open_workload_connection(self, application_name: str, target: str | None = None, connection_pool: str | None = None):
        import psycopg2

        if target in {"read_pool", "write_pool", "report_pool"} and connection_pool is None:
            connection_pool = target
            target = None
        connection_user = self.user
        connection_password = self.password
        connection_dbname = self.dbname
        if target is not None:
            target_text = target.casefold()
            if target_text == "primary":
                host, port = "127.0.0.1", self.deployment.ports.primary
            elif target_text.startswith("replica") or target_text.startswith("read_replica"):
                host, port = self.deployment.replica_endpoint(target_text)
            elif target_text in {"writer", "writer_primary"}:
                host, port = "127.0.0.1", self.deployment.ports.primary
            else:
                raise ValueError(f"unknown PostgreSQL fleet workload target: {target!r}")
        elif connection_pool == "write_pool":
            host, port = "127.0.0.1", self.deployment.ports.primary
        elif connection_pool == "report_pool":
            host, port = "127.0.0.1", self.deployment.ports.pgbouncer
            connection_user = "report"
            connection_password = "report_password"
            connection_dbname = "testdb_report"
        else:
            host, port = "127.0.0.1", self.deployment.ports.pgbouncer
        conn = psycopg2.connect(
            host=host, port=port, user=connection_user, password=connection_password,
            dbname=connection_dbname, connect_timeout=5, application_name=application_name,
        )
        conn.autocommit = False
        return conn

    @Tool(
        description=lazy_agent_text(
            zh=(
                "管理 replica fleet 的实例生命周期。允许 start/stop/restart 单个 replica；"
                "router 和 pgbouncer 只支持显式的实例生命周期动作；不允许 fleet-wide 操作。"
            ),
            en=(
                "Manage the instance lifecycle of the replica fleet. start/stop/restart of a single replica is allowed; "
                "router and pgbouncer support only explicit instance lifecycle actions; fleet-wide operations are not allowed."
            ),
        ),
        arg_descriptions={
            "action": lazy_agent_text(
                zh="start、stop、restart；replica 不接受通用配置动作",
                en="start, stop, restart; replicas do not accept generic configuration actions",
            ),
            "target": lazy_agent_text(
                zh="primary、replica_0、replica_1、replica_2、router 或 pgbouncer",
                en="primary, replica_0, replica_1, replica_2, router or pgbouncer",
            ),
            "value": lazy_agent_text(zh="配置值", en="Configuration value"),
        },
    )
    def manage_instance(self, action: str, target: str = None, value: str = None) -> str:
        target_text = (target or "primary").casefold().replace("-", "_")
        if target_text in {"primary", "writer", "postgres", "postgres_primary"}:
            return super().manage_instance(action, target="primary", value=value)
        if target_text in {"router", "pgbouncer"} and action in {"start", "stop", "restart"}:
            container = (
                self.deployment.router_container_name
                if target_text == "router" else self.deployment.pgbouncer_container_name
            )
            ok = self.deployment._container_action(container, "restart" if action == "restart" else action)
            return json.dumps({"status": "success" if ok else "error", "action": action, "target": target_text})
        if target_text.startswith("replica_") or target_text.startswith("read_replica_"):
            if action == "start":
                ok = self.deployment.start_replica(target_text)
                if ok:
                    ok = self.deployment.wait_for_replica_ready(target_text, timeout=180)
            elif action == "stop":
                ok = self.deployment.stop_replica(target_text)
            elif action == "restart":
                ok = self.deployment._container_action(
                    self.deployment.replica_container_names[self.deployment.replica_index(target_text)],
                    "restart",
                )
            else:
                return json.dumps({"status": "error", "error": f"unsupported replica action: {action}"})
            return json.dumps({"status": "success" if ok else "error", "action": action, "target": target_text})
        if target_text in {"all", "fleet"}:
            return json.dumps({"status": "error", "error": "fleet-wide lifecycle actions are not permitted"})
        return json.dumps({"status": "error", "error": f"unknown fleet target: {target}"})

    @Tool(
        alias="query_metrics",
        tool_id="query_metrics",
        description=lazy_agent_text(
            zh=(
                "查询 primary、三台 read replica 和 PgBouncer 的真实观测。metric_type 可用 "
                "router_distribution、replica_service、replica_lwlock、query_footprint、"
                "pgbouncer_pool、primary_service，也保留 replica_health、replication、pool、read_apdex "
                "和 PGEnv 基础时序观测。"
                "replica_health、replication、pool 和 read_apdex 只返回当前快照；"
                "任务的 fleet 指标来自冻结历史，用于比较 route、LWLock waiters、"
                "query duration 和 pool waiting/maxwait 的先后。"
                "active_connections 只返回原始连接数时序，disk_usage 只返回容器文件系统容量；"
                "连接状态、锁等待、数据库/表/WAL/temp 细节请通过 execute_sql 查询。"
            ),
            en=(
                "Query real observations of the primary, the three read replicas and PgBouncer. metric_type can be "
                "router_distribution, replica_service, replica_lwlock, query_footprint, "
                "pgbouncer_pool, primary_service; replica_health, replication, pool, read_apdex "
                "and the PGEnv base time-series observations are also kept. "
                "replica_health, replication, pool and read_apdex return only the current snapshot; "
                "the task's fleet metrics come from frozen history and are used to compare the order of route, LWLock waiters, "
                "query duration and pool waiting/maxwait. "
                "active_connections returns only the raw connection count time series, disk_usage returns only the container filesystem capacity; "
                "query connection states, lock waits and database/table/WAL/temp details through execute_sql."
            ),
        ),
        arg_descriptions={
            "metric_type": lazy_agent_text(
                zh="指标类型，如 router_distribution, replica_service, replica_lwlock, query_footprint, pgbouncer_pool, primary_service",
                en="Metric type, such as router_distribution, replica_service, replica_lwlock, query_footprint, pgbouncer_pool, primary_service",
            ),
            "target": lazy_agent_text(
                zh="Fleet 指标可选 replica_0/replica_1/replica_2、read_pool、report_pool 或 query family；cpu 可用 top_processes",
                en="Fleet metrics accept replica_0/replica_1/replica_2, read_pool, report_pool or a query family; cpu accepts top_processes",
            ),
            "limit": lazy_agent_text(
                zh="history 或 workload_activity 返回前 N 条记录，默认 20",
                en="history or workload_activity returns the first N records, default 20",
            ),
            "start_timestamp": lazy_agent_text(
                zh="时序指标开始时间，必须与 end_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
                en="Start time of the time-series metric; must be provided together with end_timestamp, format YYYY-MM-DD HH:mm:ss",
            ),
            "end_timestamp": lazy_agent_text(
                zh="时序指标结束时间，必须与 start_timestamp 同时提供，格式 YYYY-MM-DD HH:mm:ss",
                en="End time of the time-series metric; must be provided together with start_timestamp, format YYYY-MM-DD HH:mm:ss",
            ),
        },
    )
    def _query_metrics_for_agent(
        self,
        metric_type: str,
        target: str = None,
        limit: int = None,
        start_timestamp: str = None,
        end_timestamp: str = None,
        step_seconds: int = None,
    ) -> str:
        if limit is not None:
            try:
                limit = int(limit)
            except (TypeError, ValueError):
                return json.dumps({"status": "error", "error": "limit must be an integer"})
        if str(metric_type or "").casefold() in FLEET_METRIC_NAMES:
            return bound_metric_result(self.query_metrics(
                metric_type=metric_type,
                target=target,
                limit=limit,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                step_seconds=step_seconds,
            ))
        if metric_type.casefold() in {"replica_health", "replication", "pool", "read_apdex"}:
            return bound_metric_result(self.query_metrics(
                metric_type,
                target,
                limit=limit,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            ))
        return super()._query_metrics_for_agent(
            metric_type=metric_type,
            target=target,
            limit=limit,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            step_seconds=step_seconds,
        )

    def query_metrics(
        self,
        metric_type: str,
        target: str = None,
        threshold_ms: int = None,
        tables: str = None,
        limit: int = None,
        start_timestamp: str = None,
        end_timestamp: str = None,
        step_seconds: int = None,
    ) -> str:
        metric = metric_type.casefold()
        if metric in FLEET_METRIC_NAMES:
            try:
                if self._history_timeline is None:
                    raise RuntimeError("replica fleet metric history is not bound")
                start_ms = parse_utc_timestamp(start_timestamp, "start_timestamp") if start_timestamp is not None else None
                end_ms = parse_utc_timestamp(end_timestamp, "end_timestamp") if end_timestamp is not None else None
                frame = self._metric_service.query_public(MetricQuery(
                    metric=metric,
                    target=target,
                    start_epoch_ms=start_ms,
                    end_epoch_ms=end_ms,
                    step_seconds=step_seconds,
                ))
                requested_start = start_ms if start_ms is not None else self._history_timeline.visible_start_ms
                requested_end = end_ms if end_ms is not None else self._history_timeline.visible_end_ms
                requested_step = step_seconds or (
                    self._history_timeline.base_step_seconds if start_ms is not None
                    else frame.step_seconds
                )
                return render_metric_frame(
                    frame,
                    available_start_ms=self._history_timeline.visible_start_ms,
                    available_end_ms=self._history_timeline.visible_end_ms,
                    requested_start_ms=requested_start,
                    requested_end_ms=requested_end,
                    step_seconds=requested_step,
                )
            except (ValueError, RuntimeError, TypeError, KeyError) as exc:
                return json.dumps({"status": "error", "metric": metric, "error": str(exc)}, ensure_ascii=False)
        if metric in {"replica_health", "replication", "pool", "read_apdex"}:
            try:
                snapshot = self.capture_fleet_observation()
                if target:
                    snapshot = {
                        "target": target,
                        "replica": snapshot.get("replicas", {}).get(target, {}),
                        "pool": snapshot.get("pool", {}),
                    }
                return json.dumps(
                    {
                        "status": "success",
                        "metric": metric_type,
                        "kind": "snapshot",
                        "snapshot": snapshot,
                    },
                    default=str,
                )
            except Exception as exc:
                return json.dumps({"status": "error", "metric": metric_type, "error": str(exc)})
        return super().query_metrics(
            metric_type=metric_type,
            target=target,
            threshold_ms=threshold_ms,
            tables=tables,
            limit=limit,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            step_seconds=step_seconds,
        )

    def _endpoint_observation(
        self,
        target: str,
        *,
        waiter_sample_count: int = 1,
    ) -> dict[str, Any]:
        import psycopg2

        host, port = self.deployment.replica_endpoint(target)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
            connect_timeout=3,
            application_name="replica-fleet-observer",
        )
        try:
            sample_count = max(1, int(waiter_sample_count))
            samples = []
            for sample_index in range(sample_count):
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT pg_is_in_recovery(), count(*) FILTER (WHERE state = 'active'), "
                        "count(*) FILTER (WHERE wait_event_type = 'LWLock' AND lower(wait_event) LIKE '%lock%'), "
                        "count(*) FILTER (WHERE wait_event_type = 'Lock'), "
                        "COALESCE(percentile_cont(0.95) WITHIN GROUP (ORDER BY extract(epoch FROM clock_timestamp() - query_start) * 1000) FILTER (WHERE state = 'active'), 0), "
                        "COALESCE(percentile_cont(0.99) WITHIN GROUP (ORDER BY extract(epoch FROM clock_timestamp() - query_start) * 1000) FILTER (WHERE state = 'active'), 0), "
                        "COALESCE(sum(extract(epoch FROM clock_timestamp() - query_start) * 1000) FILTER (WHERE wait_event_type = 'LWLock' AND lower(wait_event) LIKE '%lock%'), 0), "
                        "(SELECT count(DISTINCT pid) FROM pg_locks WHERE NOT fastpath), "
                        "(SELECT COALESCE(sum(calls), 0) FROM pg_stat_statements), "
                        "COALESCE(array_agg(DISTINCT wait_event ORDER BY wait_event) FILTER (WHERE wait_event_type = 'LWLock' AND wait_event IS NOT NULL), ARRAY[]::text[]), "
                        "EXTRACT(EPOCH FROM clock_timestamp() - pg_last_xact_replay_timestamp()) "
                        "FROM pg_stat_activity WHERE backend_type = 'client backend'"
                    )
                    samples.append(cur.fetchone())
                if sample_index + 1 < sample_count:
                    time.sleep(self.FLEET_WAITER_SAMPLE_INTERVAL_SECONDS)
            in_recovery, active, _lwlock_waiters, lock_waiters, _p95, _p99, waiter_ms, slowpath, calls_total, _lwlock_events, replay_lag_sec = samples[-1]
            lwlock_waiters = max(int(sample[2] or 0) for sample in samples)
            # Waiters are accumulated across the bounded sub-window. Use the
            # corresponding duration peak instead of the final instant so a
            # short waiter burst cannot be paired with an unrelated zero
            # duration sample in the public history ordering.
            p95 = max(float(sample[4] or 0.0) for sample in samples)
            p99 = max(float(sample[5] or 0.0) for sample in samples)
            # The event array is the tenth selected column.  Index 5 is the
            # p99 duration scalar and is not iterable when a real endpoint is
            # sampled, so using it here turns every healthy replica into a
            # false readiness failure.
            lwlock_events = sorted({event for sample in samples for event in (sample[9] or ())})
            return {
                "healthy": True,
                "in_recovery": bool(in_recovery),
                "active_backends": int(active or 0),
                "lwlock_waiters": lwlock_waiters,
                "lwlock_wait_samples": sum(1 for sample in samples if int(sample[2] or 0) > 0),
                "lock_waiters": int(lock_waiters or 0),
                "p95_query_duration_ms": float(p95 or 0.0),
                "p99_query_duration_ms": float(p99 or 0.0),
                "waiter_ms_per_sec": float(waiter_ms or 0.0),
                "slowpath_backends": int(slowpath or 0),
                "query_calls_total": int(calls_total or 0),
                "lwlock_wait_events": lwlock_events,
                "replay_lag_sec": None if replay_lag_sec is None else max(0.0, float(replay_lag_sec)),
                # This is deliberately collected on the read endpoint. The
                # primary cannot observe sessions routed through HAProxy.
                "footprint_sources": self._query_footprint_sources(conn),
            }
        finally:
            conn.close()

    def _pool_observation(self) -> dict[str, Any]:
        import psycopg2

        conn = psycopg2.connect(
            host="127.0.0.1", port=self.deployment.ports.pgbouncer,
            user="postgres", password=self.password, dbname="pgbouncer", connect_timeout=3,
        )
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute("SHOW POOLS")
                columns = [description[0] for description in cur.description]
                rows = [dict(zip(columns, row)) for row in cur.fetchall()]
            maxwait = max((self._pool_wait_ms(row) for row in rows), default=0.0)
            return {"rows": rows, "maxwait_ms": maxwait, "waiting_clients": sum(int(row.get("cl_waiting") or 0) for row in rows)}
        finally:
            conn.close()

    def _query_footprint_sources(self, connection) -> dict[str, dict[str, Any]]:
        """Collect read-side footprint inputs from the endpoint being sampled."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(sum(calls) FILTER (WHERE query ILIKE "
                "'SELECT count(*) AS matching_orders%' AND query ILIKE '%rc_footprint_16%' "
                "AND query NOT ILIKE '%o.id = o.id%'), 0), "
                "COALESCE(sum(calls) FILTER (WHERE query ILIKE "
                "'SELECT count(*) AS matching_orders%' AND query ILIKE '%o.id = o.id%'), 0), "
                "COALESCE(sum(calls) FILTER (WHERE query ILIKE "
                "'%FROM rc_orders WHERE status IN%'), 0) "
                "FROM pg_stat_statements"
            )
            checkout_calls, simple_calls, report_calls = cursor.fetchone()
            cursor.execute(
                "SELECT a.application_name, a.pid, "
                "count(l.relation) FILTER (WHERE l.locktype = 'relation' AND l.granted) "
                "FROM pg_stat_activity a LEFT JOIN pg_locks l ON l.pid = a.pid "
                "WHERE a.backend_type = 'client backend' "
                "AND COALESCE(a.application_name, '') NOT IN "
                "('replica-fleet-observer', 'replica-fleet-history-sampler', 'lwlock-cascade-probe') "
                "GROUP BY a.application_name, a.pid"
            )
            lock_rows = cursor.fetchall()

        family_counts: dict[str, list[int]] = {
            "checkout_read_footprint": [],
            "checkout_read_footprint_simple": [],
            "report_pool": [],
        }
        for application_name, _pid, relation_count in lock_rows:
            app = str(application_name or "").casefold()
            count = int(relation_count or 0)
            if app.startswith("checkout-read"):
                family_counts["checkout_read_footprint"].append(count)
            if app.startswith("checkout-read-simple"):
                family_counts["checkout_read_footprint_simple"].append(count)
            if app.startswith("report-pool"):
                family_counts["report_pool"].append(count)

        def footprint(family: str, calls: int) -> dict[str, Any]:
            counts = family_counts[family]
            return {
                "query_calls_total": int(calls or 0),
                "sample_count": len(counts),
                "mean_relation_locks": (
                    sum(counts) / len(counts) if counts else 0.0
                ),
                "slowpath_fraction": (
                    sum(1 for count in counts if count > 16) / len(counts) if counts else 0.0
                ),
            }

        return {
            "checkout_read_footprint": footprint("checkout_read_footprint", checkout_calls),
            "checkout_read_footprint_simple": footprint("checkout_read_footprint_simple", simple_calls),
            "report_pool": footprint("report_pool", report_calls),
        }

    @staticmethod
    def _merge_footprint_sources(replica_observations: Any) -> dict[str, dict[str, Any]]:
        merged: dict[str, dict[str, float]] = {}
        for observation in replica_observations:
            for family, source in (observation or {}).items():
                item = merged.setdefault(family, {"calls": 0.0, "samples": 0.0, "mean_total": 0.0, "slow_total": 0.0})
                sample_count = float(source.get("sample_count", 0) or 0)
                item["calls"] += float(source.get("query_calls_total", 0) or 0)
                item["samples"] += sample_count
                item["mean_total"] += float(source.get("mean_relation_locks", 0.0) or 0.0) * sample_count
                item["slow_total"] += float(source.get("slowpath_fraction", 0.0) or 0.0) * sample_count
        return {
            family: {
                "query_calls_total": int(values["calls"]),
                "mean_relation_locks": values["mean_total"] / values["samples"] if values["samples"] else 0.0,
                "slowpath_fraction": values["slow_total"] / values["samples"] if values["samples"] else 0.0,
            }
            for family, values in merged.items()
        }

    def _primary_service_observation(self, connection) -> dict[str, Any]:
        """Collect primary-only service inputs from live PostgreSQL views."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(percentile_cont(0.99) WITHIN GROUP "
                "(ORDER BY extract(epoch FROM clock_timestamp() - query_start) * 1000) "
                "FILTER (WHERE backend_type = 'client backend' AND state = 'active'), 0) "
                "FROM pg_stat_activity"
            )
            p99_query_duration_ms = float(cursor.fetchone()[0] or 0.0)
            cursor.execute(
                "SELECT COALESCE(n_tup_upd, 0) FROM pg_stat_user_tables "
                "WHERE relname = 'rc_write_probe'"
            )
            write_calls_total = int(cursor.fetchone()[0] or 0)
        return {
            "write_calls_total": write_calls_total,
            "p99_query_duration_ms": p99_query_duration_ms,
        }

    @staticmethod
    def _pool_wait_ms(row: Mapping[str, Any]) -> float:
        """Normalize PgBouncer SHOW POOLS maxwait, whose columns use mixed units."""
        maxwait_us = row.get("maxwait_us")
        if maxwait_us not in (None, ""):
            return max(0.0, float(maxwait_us) / 1000.0)
        return max(0.0, float(row.get("maxwait") or 0.0) * 1000.0)

    @staticmethod
    def _fleet_observed_at() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def _record_fleet_observation(self, observation: dict[str, Any]) -> None:
        sample = dict(observation)
        sample.setdefault("observed_at", self._fleet_observed_at())
        with self._fleet_history_lock:
            self._fleet_history.append(sample)

    def _fleet_history_payload(
        self,
        *,
        limit: int | None = None,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
    ) -> list[dict[str, Any]]:
        try:
            requested_limit = max(1, min(int(limit or 20), self.FLEET_HISTORY_MAX_SAMPLES))
        except (TypeError, ValueError):
            requested_limit = 20
        with self._fleet_history_lock:
            samples = sorted(
                self._fleet_history,
                key=lambda sample: str(sample.get("observed_at", "")),
            )
        if start_timestamp or end_timestamp:
            start = start_timestamp or ""
            end = end_timestamp or "\uffff"
            samples = [
                sample for sample in samples
                if start <= str(sample.get("observed_at", "")) <= end
            ]
        return samples[-requested_limit:]

    def _fleet_history_sampler_loop(self) -> None:
        while not self._fleet_history_stop.is_set():
            try:
                self._capture_fleet_observation_for_history()
            except Exception:
                # The regular sampler and the Agent tool surface report their
                # own errors; a transient replica restart must not kill history.
                pass
            self._fleet_history_stop.wait(self.FLEET_HISTORY_INTERVAL_SECONDS)

    def _capture_fleet_observation_for_history(self) -> None:
        """Capture the history sample with a connection private to the sampler."""
        import psycopg2

        connection = psycopg2.connect(
            host="127.0.0.1",
            port=self.deployment.ports.primary,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
            connect_timeout=3,
            application_name="replica-fleet-history-sampler",
        )
        connection.autocommit = True
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT count(*) FROM pg_stat_activity "
                    "WHERE backend_type = 'client backend'"
                )
                primary = {
                    "status": "success",
                    "metric": "active_connections",
                    "kind": "snapshot",
                    "snapshot": {"connections": int(cursor.fetchone()[0] or 0)},
                }
                primary.update(self._primary_service_observation(connection))
                cursor.execute(
                    "SELECT application_name, state, flush_lag, replay_lag "
                    "FROM pg_stat_replication ORDER BY application_name"
                )
                columns = [description[0] for description in cursor.description]
                replication = {
                    "status": "success",
                    "result": [dict(zip(columns, row)) for row in cursor.fetchall()],
                }
            def capture_replica(target: str) -> tuple[str, dict[str, Any]]:
                try:
                    return target, self._endpoint_observation(
                        target,
                        waiter_sample_count=self.FLEET_HISTORY_WAITER_SAMPLE_COUNT,
                    )
                except Exception as exc:
                    return target, {"healthy": False, "error": str(exc)}

            # Endpoint queries are independent. Running them concurrently keeps
            # one slow or contended replica from stretching a history tick past
            # the bounded jitter contract for the entire fleet.
            with ThreadPoolExecutor(max_workers=3, thread_name_prefix="fleet-history-replica") as executor:
                replicas = dict(executor.map(capture_replica, (f"replica_{index}" for index in range(3))))
            footprint_sources = self._merge_footprint_sources(
                value.get("footprint_sources")
                for value in replicas.values()
                if value.get("healthy")
            )
            observation = self._enrich_fleet_observation({
                "observed_at": self._fleet_observed_at(),
                "primary": primary,
                "replicas": replicas,
                "pool": self._pool_observation(),
                "replication": replication,
                "footprint_sources": footprint_sources,
            })
            self._record_fleet_observation(observation)
        finally:
            connection.close()

    def _start_fleet_history_sampler(self) -> None:
        if self._fleet_history_thread is not None and self._fleet_history_thread.is_alive():
            return
        self._fleet_history_stop.clear()
        self._fleet_history_thread = threading.Thread(
            target=self._fleet_history_sampler_loop,
            name="replica-fleet-history-sampler",
            daemon=True,
        )
        self._fleet_history_thread.start()

    def _stop_fleet_history_sampler(self) -> None:
        self._fleet_history_stop.set()
        if self._fleet_history_thread is not None:
            self._fleet_history_thread.join(timeout=10)
            if self._fleet_history_thread.is_alive():
                raise RuntimeError("replica fleet history sampler did not stop within 10 seconds")
            self._fleet_history_thread = None

    def capture_fleet_observation(
        self,
        *,
        record_history: bool = True,
        waiter_sample_count: int | None = None,
    ) -> dict[str, Any]:
        sample_count = (
            self.FLEET_WAITER_SAMPLE_COUNT
            if waiter_sample_count is None
            else max(1, int(waiter_sample_count))
        )
        replicas = {}
        for index in range(3):
            target = f"replica_{index}"
            try:
                replicas[target] = self._endpoint_observation(
                    target,
                    waiter_sample_count=sample_count,
                )
            except Exception as exc:
                replicas[target] = {"healthy": False, "error": str(exc)}
        pool = self._pool_observation()
        if not self._ensure_connection():
            raise RuntimeError("primary control connection could not be established")
        # This is a live current-state snapshot.  Calling the base metric API
        # here would select the bound frozen timeline after frozen-history setup
        # and can expose a historical variant error as a current observation.
        with self._conn.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE backend_type = 'client backend'"
            )
            primary = {
                "status": "success",
                "metric": "active_connections",
                "kind": "snapshot",
                "snapshot": {"connections": int(cursor.fetchone()[0] or 0)},
            }
        primary.update(self._primary_service_observation(self._conn))
        replication = json.loads(self.execute_sql(
            "SELECT application_name, state, flush_lag, replay_lag "
            "FROM pg_stat_replication ORDER BY application_name"
        ))
        footprint_sources = self._merge_footprint_sources(
            value.get("footprint_sources")
            for value in replicas.values()
            if value.get("healthy")
        )
        observation = self._enrich_fleet_observation({
            "observed_at": self._fleet_observed_at(),
            "primary": primary,
            "replicas": replicas,
            "pool": pool,
            "replication": replication,
            "footprint_sources": footprint_sources,
        })
        if record_history:
            self._record_fleet_observation(observation)
        return observation

    def capture_safety_state(self, case: object) -> dict[str, Any]:
        schema = self.execute_sql(
            "SELECT n.nspname, c.relname, c.relkind FROM pg_class c "
            "JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = 'public' ORDER BY 1, 2, 3"
        )
        return {
            "schema": schema,
            "writer_endpoint": "primary",
            "consistency_policy": "read replicas remain asynchronous and read-only",
        }

    def reset_read_pool(self) -> bool:
        """Discard PgBouncer server sessions after a HAProxy backend change."""
        import psycopg2

        deadline = time.monotonic() + 8.0
        while time.monotonic() < deadline:
            conn = None
            try:
                conn = psycopg2.connect(
                    host="127.0.0.1", port=self.deployment.ports.pgbouncer,
                    user="postgres", password=self.password, dbname="pgbouncer", connect_timeout=3,
                )
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute("RECONNECT testdb")
                    cur.execute("RECONNECT testdb_report")
                return True
            except Exception:
                time.sleep(0.2)
            finally:
                if conn is not None:
                    conn.close()
        return False

    def _warm_read_route(self, query: str, *, attempts: int, timeout: float = 15.0) -> bool:
        """Wait for PgBouncer and HAProxy to establish usable read sessions."""
        deadline = time.monotonic() + timeout
        completed = 0
        while completed < attempts and time.monotonic() < deadline:
            conn = None
            try:
                conn = self.open_workload_connection("read-route-warmup", connection_pool="read_pool")
                with conn.cursor() as cur:
                    cur.execute(query)
                    cur.fetchall()
                conn.rollback()
                completed += 1
            except Exception:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
                time.sleep(0.2)
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
        return completed >= attempts

    def run_n1_replay(self, case: object) -> dict[str, Any]:
        if self._last_replay_artifact is not None:
            return self._last_replay_artifact
        final_observation = self.capture_fleet_observation()
        replicas = final_observation.get("replicas", {})
        active_replicas = sum(
            1 for index in range(len(self.deployment.replica_container_names))
            if replicas.get(f"replica_{index}", {}).get("healthy")
        )
        if active_replicas != len(self.deployment.replica_container_names):
            self._last_replay_artifact = {
                "replicas_restored": False,
                "active_replicas": active_replicas,
                "read_apdex": 0.0,
                "success_rate": 0.0,
                "max_lwlock_waiters": None,
                "pool_maxwait_ms": None,
                "primary_write_ok": False,
                "replication_lag_bytes": None,
                "replay_attempted": False,
                "replay_error": "N-1 replay requires all read replicas to be restored by the agent",
            }
            return self._last_replay_artifact
        candidates = tuple(
            target_name
            for target_name, value in sorted(replicas.items())
            if value.get("healthy") and target_name in {
                f"replica_{index}" for index in range(len(self.deployment.replica_container_names))
            }
        )
        if len(candidates) < 2:
            raise RuntimeError(f"N-1 replay requires at least two healthy replicas: candidates={candidates!r}")
        seed_material = f"{self._replay_nonce}:{case.case_id}:n1".encode("utf-8")
        target = random.Random(int.from_bytes(hashlib.sha256(seed_material).digest()[:8], "big")).choice(candidates)
        latencies: list[float] = []
        successes = 0
        attempts = 0
        result_lock = threading.Lock()
        stop = threading.Event()
        query = case.diagnostic_query
        observations: list[dict[str, Any]] = []

        def read_worker() -> None:
            nonlocal successes, attempts
            conn = None
            try:
                while not stop.is_set():
                    started = time.monotonic()
                    try:
                        if conn is None or getattr(conn, "closed", False):
                            conn = self.open_workload_connection("n1-replay", connection_pool="read_pool")
                        with conn.cursor() as cur:
                            cur.execute(query)
                            cur.fetchall()
                        conn.rollback()
                        with result_lock:
                            successes += 1
                            latencies.append((time.monotonic() - started) * 1000)
                    except Exception:
                        try:
                            conn.close()
                        except Exception:
                            pass
                        conn = None
                    finally:
                        with result_lock:
                            attempts += 1
                    if stop.wait(case.replay_interval_seconds):
                        break
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

        route_drain = getattr(self.deployment, "set_router_backends", None)
        if route_drain is not None and not route_drain(excluded_replicas=(target,)):
            raise RuntimeError(f"failed to drain replay route for {target}")
        if not self.reset_read_pool():
            raise RuntimeError(f"read pool did not reset before replay for {target}")
        if not self._warm_read_route("SELECT 1", attempts=1, timeout=5.0):
            raise RuntimeError(f"read route did not warm before replay for {target}")
        if not self.deployment.stop_replica(target):
            raise RuntimeError(f"failed to stop drained replica for N-1 replay: {target}")
        workers = [threading.Thread(target=read_worker, daemon=True) for _ in range(case.replay_workers)]
        for worker in workers:
            worker.start()
        try:
            deadline = time.time() + case.replay_seconds
            while time.time() < deadline:
                observations.append(self.capture_fleet_observation())
                time.sleep(0.25)
            observation = observations[-1] if observations else self.capture_fleet_observation()
        finally:
            stop.set()
            for worker in workers:
                worker.join(timeout=5)
            restored = self.deployment.start_replica(target) and self.deployment.wait_for_replica_ready(target, timeout=180)
            restore_routes = getattr(self.deployment, "set_router_backends", None)
            if restored and restore_routes is not None:
                restored = restore_routes()
            if restored:
                restored = self.reset_read_pool()
        sorted_latencies = sorted(latencies)
        tolerated = sum(value <= case.apdex_tolerated_ms for value in sorted_latencies)
        satisfied = sum(value <= case.apdex_satisfied_ms for value in sorted_latencies)
        p95_index = min(len(sorted_latencies) - 1, max(0, (len(sorted_latencies) * 95 + 99) // 100 - 1))
        restored_observation = self.capture_fleet_observation() if restored else observation
        write_result = json.loads(self.execute_sql(
            "UPDATE rc_write_probe SET writes = writes + 1, touched_at = clock_timestamp() WHERE id = 1 RETURNING writes"
        ))
        if write_result.get("status") != "success":
            raise RuntimeError(f"primary write verification failed: {write_result!r}")
        write_rows = write_result.get("result") or []
        lag_result = json.loads(self.execute_sql(
            "SELECT max(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) "
            "FROM pg_stat_replication WHERE replay_lsn IS NOT NULL"
        ))
        if lag_result.get("status") != "success":
            raise RuntimeError(f"replication lag verification failed: {lag_result!r}")
        lag_rows = lag_result.get("result")
        if not isinstance(lag_rows, list) or len(lag_rows) != 1 or not lag_rows[0] or lag_rows[0][0] is None:
            raise RuntimeError(f"replication lag verification returned no scalar: {lag_result!r}")
        max_waiters = max(
            (value.get("lwlock_waiters", 0)
             for sample in (*observations, observation)
             for value in sample.get("replicas", {}).values()),
            default=0,
        )
        read_pool_metrics = [
            self._read_pool_metrics(sample)
            for sample in (*observations, observation)
        ]
        max_pool_wait = max((wait_ms for wait_ms, _waiting in read_pool_metrics), default=0.0)
        max_query_duration = max(
            (float(value.get("p95_query_duration_ms", 0))
             for sample in (*observations, observation)
             for value in sample.get("replicas", {}).values()),
            default=0.0,
        )
        max_waiting_clients = max((waiting for _wait_ms, waiting in read_pool_metrics), default=0)
        self._last_replay_artifact = {
            "drained_replica": target,
            "replicas_restored": bool(restored),
            "active_replicas": sum(1 for value in restored_observation["replicas"].values() if value.get("healthy")),
            "read_apdex": (satisfied + 0.5 * max(0, tolerated - satisfied)) / max(1, len(sorted_latencies)),
            "success_rate": successes / max(1, attempts),
            "latency_stats": {
                "count": len(sorted_latencies),
                "p50_ms": sorted_latencies[len(sorted_latencies) // 2] if sorted_latencies else None,
                "p95_ms": sorted_latencies[p95_index] if sorted_latencies else None,
                "max_ms": max(sorted_latencies, default=None),
            },
            "observation_samples": observations,
            "max_lwlock_waiters": max_waiters,
            "pool_maxwait_ms": max_pool_wait,
            "max_query_duration_ms": max_query_duration,
            "max_pool_waiting_clients": max_waiting_clients,
            "primary_write_ok": bool(write_rows and int(write_rows[0][0]) >= case.min_primary_writes),
            "replication_lag_bytes": int(lag_rows[0][0] or 0),
            "observation": observation,
        }
        return self._last_replay_artifact

    @classmethod
    def _read_pool_metrics(cls, sample: Mapping[str, Any]) -> tuple[float, int]:
        row = cls._required_pool_row(sample.get("pool", {}).get("rows", ()), "read_pool")
        return cls._pool_wait_ms(row), int(row.get("cl_waiting") or 0)

    def teardown(self) -> None:
        self._stop_fleet_history_sampler()
        for connection in self._direct_connections.values():
            try:
                connection.close()
            except Exception:
                pass
        self._direct_connections.clear()
        super().teardown()
