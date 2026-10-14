"""Run-scoped single-node PostgreSQL deployment used by pg5 HTAP instance 3
mechanism verification and three-path scripts.

This is the instance-owned deployment primitive for this single-node instance;
the production persistent backend wiring stays with the integration owner and
reuses the shared environment provider. Containers, volumes and networks use
the batch resource lease prefix `pg5r-htap-` and ports from 25200-25299.
"""

from __future__ import annotations

import os
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from src.execution.host_ports import claim_host_ports

import psycopg2


@dataclass(frozen=True, slots=True)
class SingleNodePostgresConfig:
    run_id: str
    port: int
    workdir: Path
    cpu_limit: float = 4.0
    memory_mb: int = 6144
    image: str = "postgres:16"

    def __post_init__(self) -> None:
        if not 25200 <= self.port <= 25299:
            raise ValueError(f"pg5r HTAP port lease violation: port={self.port}, allowed=[25200, 25299]")


class SingleNodePostgres:
    PREFIX = "pg5r-htap"
    workload_dbname = "testdb"

    def __init__(self, config: SingleNodePostgresConfig):
        self.config = config
        self.container_name = f"pg5r-htap-i3-{config.run_id}"
        self.volume_name = f"pg5r-htap-i3-{config.run_id}-data"
        self.network_name = f"pg5r-htap-i3-{config.run_id}-net"
        self._port_lease = None

    def deploy(self) -> None:
        if self._port_lease is None:
            self._port_lease = claim_host_ports((self.config.port,), owner=self.container_name)
        self._assert_port_free()
        self._run(["docker", "network", "create", self.network_name])
        self._run(["docker", "volume", "create", self.volume_name])
        self._run(
            [
                "docker", "run", "--detach", "--name", self.container_name,
                "--network", self.network_name,
                "--publish", f"{self.config.port}:5432",
                "--env", "POSTGRES_USER=postgres",
                "--env", "POSTGRES_PASSWORD=password",
                "--env", "POSTGRES_DB=testdb",
                "--env", "PGDATA=/var/lib/postgresql/data/pgdata",
                "--volume", f"{self.volume_name}:/var/lib/postgresql/data",
                *self._cpuset_args(),
                "--cpus", str(self.config.cpu_limit),
                "--memory", f"{self.config.memory_mb}m",
                "--shm-size", "256m",
                self.config.image,
                "postgres", "-c", "fsync=on", "-c", "full_page_writes=on",
                "-c", "wal_level=replica", "-c", "max_wal_senders=4", "-c", "max_replication_slots=4",
                "-c", "track_io_timing=on", "-c", "logging_collector=off",
            ]
        )
        self._wait_ready(timeout=240)

    @staticmethod
    def _cpuset_args() -> list[str]:
        cpuset_cpus = os.environ.get("AIOPS_CPUSET_CPUS")
        cpuset_mems = os.environ.get("AIOPS_CPUSET_MEMS")
        if bool(cpuset_cpus) != bool(cpuset_mems):
            raise RuntimeError(
                "pg5r HTAP single-node worker isolation requires both cpuset values: "
                f"AIOPS_CPUSET_CPUS={cpuset_cpus!r}, AIOPS_CPUSET_MEMS={cpuset_mems!r}"
            )
        if not cpuset_cpus:
            return []
        return ["--cpuset-cpus", cpuset_cpus, "--cpuset-mems", cpuset_mems]

    def open_workload_connection(self, application_name: str, _target: str = "primary"):
        connection = psycopg2.connect(
            host="localhost",
            port=self.config.port,
            user="postgres",
            password="password",
            dbname="testdb",
            connect_timeout=5,
            application_name=application_name,
        )
        connection.autocommit = False
        return connection

    def psql(self, sql: str) -> list[tuple]:
        connection = self.open_workload_connection("pg5r-htap3-psql")
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall() if cursor.description else []
            connection.rollback()
        finally:
            connection.close()
        return rows

    def teardown(self) -> None:
        self._run(["docker", "rm", "-f", self.container_name], check=False)
        self._run(["docker", "volume", "rm", "-f", self.volume_name], check=False)
        self._run(["docker", "network", "rm", self.network_name], check=False)
        if self._port_lease is not None:
            self._port_lease.close()
            self._port_lease = None

    def _assert_port_free(self) -> None:
        with socket.socket() as sock:
            bound = sock.connect_ex(("127.0.0.1", self.config.port)) == 0
        if bound:
            raise RuntimeError(
                f"pg5r HTAP port lease is occupied: port={self.config.port}, container={self.container_name!r}"
            )

    def _wait_ready(self, timeout: int) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = self._run(
                ["docker", "inspect", "--format", "{{.State.Status}}", self.container_name],
                check=False,
            )
            if state.returncode == 0 and state.stdout.strip() != "running":
                logs = self._run(["docker", "logs", "--tail", "40", self.container_name], check=False)
                raise RuntimeError(
                    f"pg5r HTAP single-node container exited during startup: container={self.container_name!r}, "
                    f"state={state.stdout.strip()!r}, logs={(logs.stdout + logs.stderr)!r}"
                )
            try:
                rows = self.psql("SELECT 1;")
                if rows == [(1,)]:
                    return
            except psycopg2.Error:
                pass
            time.sleep(1.0)
        raise RuntimeError(
            f"pg5r HTAP single-node container not ready in time: container={self.container_name!r}, timeout={timeout}"
        )

    def _run(self, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run(args, capture_output=True, text=True, timeout=300)
        if check and result.returncode != 0:
            raise RuntimeError(
                f"docker command failed: args={args!r}, stderr={result.stderr.strip()!r}"
            )
        return result
