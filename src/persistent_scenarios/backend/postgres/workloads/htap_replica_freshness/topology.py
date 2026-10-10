"""Real primary/standby streaming-replication topology for
pg_htap_replica_freshness.

Deploy primitives owned by this instance:
- primary container with pg_wal on an isolated per-run docker volume and a
  PG-native WAL retention quota (max_wal_size + max_slot_wal_keep_size);
- a real physical replication slot consumed by the standby
  (pg_basebackup -R --slot writes primary_slot_name);
- tc tbf bandwidth throttling on the primary's egress toward the standby,
  applied through a NET_ADMIN sidecar sharing the primary's network namespace.

Resource lease: containers/volumes/networks are prefixed `pg5r-htap-`, each run
takes one primary and one standby host port inside 25200-25299, and teardown
removes everything it created.
"""

from __future__ import annotations

import socket
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Any

import psycopg2


@dataclass(frozen=True, slots=True)
class ReplicaTopologyConfig:
    run_id: str
    primary_port: int
    standby_port: int
    cpu_per_node: float = 2.0
    memory_mb_per_node: int = 4096
    max_wal_size_mb: int = 512
    # Retention quota: ~18% of the compressed-run generatable WAL, and
    # >= 1.7x the complete-path transient peak (~4.7MB: replay stalls under
    # recovery conflicts during an alert-cycle repair window with both update
    # surges writing). Quotas under that transient trip wal_status to
    # 'unreserved' in the complete path.
    max_slot_wal_keep_size_mb: int = 8
    # The retention quota is enforced only at a primary checkpoint; a 60s
    # cadence makes quota enforcement deterministic inside a run (the 300s
    # default can miss the whole compressed window entirely).
    checkpoint_timeout_seconds: int = 60
    max_standby_streaming_delay_ms: int = 20000
    # Partial degradation: the shaping rate sits ABOVE the measured business
    # steady-state WAL rate (~240 kbit) so a degraded link still replays the
    # baseline write rate with no visible lag; lag accumulates only while an
    # update surge pushes WAL generation past the shaped rate, preserving the
    # lag/surge cross-window correlation the event is supposed to measure.
    throttle_rate_kbit: int = 448
    cpuset: str | None = None
    postgres_image: str = "postgres:16"
    tc_image: str = "docker.m.daocloud.io/nicolaka/netshoot:latest"

    def __post_init__(self) -> None:
        for name in ("primary_port", "standby_port"):
            port = getattr(self, name)
            if not 25200 <= port <= 25299:
                raise ValueError(f"pg5r HTAP port lease violation: {name}={port}, allowed=[25200, 25299]")
        if self.primary_port == self.standby_port:
            raise ValueError(f"primary and standby ports must differ: port={self.primary_port}")


class HtapReplicaTopology:
    PREFIX = "pg5r-htap"
    SLOT_NAME = "frs_replication_slot"
    REPLICATION_USER = "frs_replicator"
    REPLICATION_PASSWORD = "frs_replica_password"
    PGDATA = "/var/lib/postgresql/data/pgdata"
    WAL_VOLUME_MOUNT = "/var/lib/postgresql/walvolume"
    # Database the fleet bootstraps business data into; role-logins
    # (guc-effective scope checks) must target the same database.
    workload_dbname = "postgres"

    def __init__(self, config: ReplicaTopologyConfig):
        self.config = config
        self.network_name = f"pg5r-htap-i4-{config.run_id}-net"
        self.primary_name = f"pg5r-htap-i4-{config.run_id}-primary"
        self.standby_name = f"pg5r-htap-i4-{config.run_id}-standby"
        self.tc_name = f"pg5r-htap-i4-{config.run_id}-tc"
        self.primary_data_volume = f"pg5r-htap-i4-{config.run_id}-primary-data"
        self.primary_wal_volume = f"pg5r-htap-i4-{config.run_id}-primary-wal"
        self.standby_data_volume = f"pg5r-htap-i4-{config.run_id}-standby-data"
        self.standby_wal_volume = f"pg5r-htap-i4-{config.run_id}-standby-wal"
        self.throttle_applied = False
        self.throttle_rate_kbit_applied: int | None = None
        # The governor thread and capability evidence paths both mutate/read the
        # qdisc; tc operations are serialized so sidecar creation and qdisc
        # state changes cannot interleave.
        self._tc_lock = threading.RLock()

    # -- deploy / teardown -------------------------------------------------

    def deploy(self, *, seed_sql: str | None = None, bootstrap_timeout: int = 600) -> None:
        self._assert_ports_free()
        self._run(["docker", "network", "create", self.network_name])
        for volume in (
            self.primary_data_volume,
            self.primary_wal_volume,
            self.standby_data_volume,
            self.standby_wal_volume,
        ):
            self._run(["docker", "volume", "create", volume])
        self._start_postgres(
            self.primary_name,
            self.primary_data_volume,
            self.primary_wal_volume,
            self.config.primary_port,
            primary_options=(
                "-c wal_level=replica -c max_wal_senders=8 -c max_replication_slots=8 "
                f"-c max_wal_size={self.config.max_wal_size_mb}MB "
                f"-c max_slot_wal_keep_size={self.config.max_slot_wal_keep_size_mb}MB "
                f"-c checkpoint_timeout={self.config.checkpoint_timeout_seconds}s "
                "-c wal_keep_size=0 -c archive_mode=off "
                "-c track_io_timing=on -c fsync=on -c full_page_writes=on"
            ),
        )
        self._wait_ready(self.primary_name, timeout=bootstrap_timeout)
        self._configure_primary()
        if seed_sql:
            self.primary_sql(seed_sql)
        self._create_standby(bootstrap_timeout)
        self._wait_streaming(timeout=bootstrap_timeout)

    def teardown(self) -> None:
        if self.throttle_applied:
            self.release_bandwidth_limit()
        for name in (self.tc_name, self.standby_name, self.primary_name):
            self._run(["docker", "rm", "-f", name], check=False)
        for volume in (
            self.primary_data_volume,
            self.primary_wal_volume,
            self.standby_data_volume,
            self.standby_wal_volume,
        ):
            self._run(["docker", "volume", "rm", "-f", volume], check=False)
        self._run(["docker", "network", "rm", self.network_name], check=False)

    # -- connections / sql -------------------------------------------------

    def open_workload_connection(self, application_name: str, target: str = "primary"):
        if target not in {"primary", "standby"}:
            raise ValueError(f"pg5r HTAP replica topology supports targets primary/standby: target={target!r}")
        port = self.config.primary_port if target == "primary" else self.config.standby_port
        connection = psycopg2.connect(
            host="localhost",
            port=port,
            user="postgres",
            password="password",
            dbname="postgres",
            connect_timeout=5,
            application_name=application_name,
        )
        connection.autocommit = False
        return connection

    def primary_sql(self, sql: str) -> list[tuple]:
        return self._sql_on(self.primary_name, sql)

    def standby_sql(self, sql: str) -> list[tuple]:
        return self._sql_on(self.standby_name, sql)

    def replication_facts(self) -> dict[str, Any]:
        primary = self.primary_sql(
            "SELECT slot_name, active, wal_status, "
            "COALESCE(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn), 0) "
            f"FROM pg_replication_slots WHERE slot_name = '{self.SLOT_NAME}';"
        )
        standby_state = self.standby_sql(
            "SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn(), pg_is_in_recovery();"
        )
        conflicts = self.standby_sql(
            "SELECT confl_snapshot + confl_lock + confl_bufferpin + confl_deadlock + confl_tablespace "
            "FROM pg_stat_database_conflicts WHERE datname = 'postgres';"
        )
        primary_lsn = self.primary_sql("SELECT pg_current_wal_lsn();")
        slot = primary[0] if primary else None
        return {
            "slot_present": slot is not None,
            "slot_active": self._pg_bool(slot[1]) if slot else False,
            "slot_wal_status": str(slot[2]) if slot else None,
            "slot_retained_bytes": int(slot[3]) if slot else 0,
            "primary_lsn": str(primary_lsn[0][0]),
            "standby_receive_lsn": str(standby_state[0][0]),
            "standby_replay_lsn": str(standby_state[0][1]),
            "standby_in_recovery": self._pg_bool(standby_state[0][2]),
            "standby_recovery_conflicts": int(conflicts[0][0]),
            "replay_lag_bytes": self._lsn_distance(str(primary_lsn[0][0]), str(standby_state[0][1])),
        }

    def drop_replication_slot(self) -> None:
        """Terminate the slot's walsender and drop the physical slot.

        A slot consumed by a live walreceiver cannot be dropped, so the
        walsender is terminated and the slot dropped inside one psql session:
        the standby only reconnects after its wal_retrieve_retry_interval
        (5s), which the retry loop covers as well.
        """
        drop_command = (
            "SELECT pg_terminate_backend(active_pid) FROM pg_replication_slots "
            f"WHERE slot_name = '{self.SLOT_NAME}' AND active_pid IS NOT NULL; "
            f"SELECT pg_drop_replication_slot('{self.SLOT_NAME}');"
        )
        deadline = time.monotonic() + 60
        last_error = None
        while time.monotonic() < deadline:
            try:
                self.primary_sql(drop_command)
                return
            except RuntimeError as exc:
                last_error = str(exc)
            time.sleep(2.0)
        raise RuntimeError(
            "pg5r HTAP failed to drop replication slot after walsender termination: "
            f"slot={self.SLOT_NAME!r}, last_error={last_error!r}"
        )

    # -- bandwidth throttling ---------------------------------------------

    def apply_bandwidth_limit(self, rate_kbit: int | None = None) -> None:
        """Shape the primary's egress toward the standby with tc tbf.

        The shaping is replication-scoped by construction: the only traffic
        that ever leaves the primary container toward the standby's IP is the
        WAL sender stream (the workload driver reaches the standby through the
        host-published port, hot_standby_feedback is off), so the standby-dst
        u32 filter throttles the replication link and nothing else — business
        sessions, agent sessions and the standby's own CPU/IO profile stay
        unshaped. The standby-dst filter MUST carry the lowest u32 preference
        number: the catch-all ip filter (prio 3) would otherwise shadow it
        (prio is matched smallest-first), silently disabling the whole
        throttle. Commands run one by one; a failing command
        raises instead of being masked by the exit code of the last command in
        the chain.

        Multi-stage link events change the rate while the previous stage's tbf
        is still applied; ``tc qdisc add`` refuses to touch an existing qdisc
        ("Exclusivity flag on, cannot modify"), so an applied-state re-apply
        updates the tbf in place instead of rebuilding the topology (same
        containers, same standby_ip, same filters).
        """
        rate = self.config.throttle_rate_kbit if rate_kbit is None else rate_kbit
        with self._tc_lock:
            self._ensure_tc_sidecar()
            if self.throttle_applied:
                self._tc_exec(
                    [
                        "tc qdisc change dev eth0 parent 1:3 handle 30: tbf "
                        f"rate {rate}kbit burst 32kbit latency 400ms",
                    ]
                )
            else:
                standby_ip = self._container_ip(self.standby_name)
                self._tc_exec(
                    [
                        "tc qdisc replace dev eth0 root handle 1: prio",
                        "tc qdisc add dev eth0 parent 1:3 handle 30: tbf "
                        f"rate {rate}kbit burst 32kbit latency 400ms",
                        f"tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dst {standby_ip} flowid 1:3",
                        "tc filter add dev eth0 protocol arp parent 1:0 prio 2 u32 match u32 0 0 flowid 1:1",
                        "tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match u32 0 0 flowid 1:2",
                    ]
                )
            self.throttle_applied = True
            self.throttle_rate_kbit_applied = int(rate)

    def release_bandwidth_limit(self) -> None:
        """Remove the shaping qdisc; a no-op while no throttle is applied.

        Release can legitimately run twice for one qdisc (agent repair through
        the control plane, then injector cleanup), so the applied-state check is
        the release's state machine, not defensive padding.
        """
        with self._tc_lock:
            if not self.throttle_applied:
                return
            self._tc_exec(["tc qdisc del dev eth0 root"])
            self.throttle_applied = False
            self.throttle_rate_kbit_applied = None

    def throttle_facts(self) -> dict[str, Any]:
        """Applied-state evidence: the qdisc and the dst-scoped filter set.

        ``filter_show`` is the replication-only scoping proof: exactly one ip
        filter matches the standby's address into the tbf band, so the evidence
        can always show the shaping never touched non-replication traffic.
        """
        return {
            "qdisc_show": self._tc_exec(["tc qdisc show dev eth0"]),
            "filter_show": self._tc_exec(["tc filter show dev eth0"]),
        }

    # -- internals ---------------------------------------------------------

    @staticmethod
    def _pg_bool(value: str) -> bool:
        text = str(value).strip()
        if text not in {"t", "f"}:
            raise ValueError(f"Expected PostgreSQL boolean text: value={value!r}")
        return text == "t"

    def _assert_ports_free(self) -> None:
        for name, port in (("primary", self.config.primary_port), ("standby", self.config.standby_port)):
            with socket.socket() as sock:
                occupied = sock.connect_ex(("127.0.0.1", port)) == 0
            if occupied:
                raise RuntimeError(f"pg5r HTAP port lease is occupied: node={name}, port={port}")

    def _start_postgres(self, name: str, data_volume: str, wal_volume: str, port: int, *, primary_options: str) -> None:
        entrypoint = (
            f'if [ ! -s "{self.PGDATA}/PG_VERSION" ]; then '
            'echo password > /tmp/pgpw; chown postgres:postgres /tmp/pgpw; '
            f'chown -R postgres:postgres "{self.PGDATA}" "{self.WAL_VOLUME_MOUNT}"; '
            f'gosu postgres initdb -D "{self.PGDATA}" --no-sync -U postgres '
            '--pwfile=/tmp/pgpw --auth-local=trust --auth-host=scram-sha-256; '
            f'mkdir -p "{self.WAL_VOLUME_MOUNT}/pg_wal"; '
            f'mv "{self.PGDATA}/pg_wal"/* "{self.WAL_VOLUME_MOUNT}/pg_wal"/; '
            f'chown -R postgres:postgres "{self.WAL_VOLUME_MOUNT}/pg_wal"; '
            f'rmdir "{self.PGDATA}/pg_wal"; '
            f'ln -s "{self.WAL_VOLUME_MOUNT}/pg_wal" "{self.PGDATA}/pg_wal"; '
            "fi; "
            f'exec gosu postgres postgres -D "{self.PGDATA}" {primary_options}'
        )
        self._run(
            [
                "docker", "run", "--detach", "--name", name,
                "--network", self.network_name,
                "--network-alias", name.rsplit("-", 1)[-1],
                "--publish", f"{port}:5432",
                "--env", f"PGDATA={self.PGDATA}",
                "--volume", f"{data_volume}:{self.PGDATA}",
                "--volume", f"{wal_volume}:{self.WAL_VOLUME_MOUNT}",
                "--cpus", str(self.config.cpu_per_node),
                *(("--cpuset-cpus", self.config.cpuset) if self.config.cpuset else ()),
                "--memory", f"{self.config.memory_mb_per_node}m",
                "--shm-size", "256m",
                "--entrypoint", "bash",
                self.config.postgres_image,
                "-c", entrypoint,
            ]
        )

    def _configure_primary(self) -> None:
        self.primary_sql(
            f"CREATE ROLE {self.REPLICATION_USER} WITH REPLICATION LOGIN "
            f"PASSWORD '{self.REPLICATION_PASSWORD}';"
        )
        self.primary_sql(f"SELECT pg_create_physical_replication_slot('{self.SLOT_NAME}');")
        self.primary_sql("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;")
        self._exec_in(
            self.primary_name,
            "printf '%s\\n' 'host replication frs_replicator 0.0.0.0/0 scram-sha-256' "
            "'host all all 0.0.0.0/0 scram-sha-256' >> \"$PGDATA/pg_hba.conf\"",
        )
        self.primary_sql("SELECT pg_reload_conf();")

    def _create_standby(self, bootstrap_timeout: int) -> None:
        backup_command = (
            f"rm -rf {self.PGDATA}/* {self.PGDATA}/.[!.]* 2>/dev/null || true; "
            f"mkdir -p {self.WAL_VOLUME_MOUNT}/pg_wal; "
            f"mkdir -p {self.PGDATA}; chmod 700 {self.PGDATA}; "
            f"chown -R postgres:postgres {self.PGDATA} {self.WAL_VOLUME_MOUNT}; "
            f"PGPASSWORD={self.REPLICATION_PASSWORD} gosu postgres pg_basebackup "
            f"-h {self._container_ip(self.primary_name)} -D {self.PGDATA} "
            f"-U {self.REPLICATION_USER} -Fp -Xs -P -R -c fast --slot={self.SLOT_NAME}"
        )
        result = self._run(
            [
                "docker", "run", "--rm", "--user", "root", "--entrypoint", "bash",
                "--network", self.network_name,
                "--volume", f"{self.standby_data_volume}:{self.PGDATA}",
                "--volume", f"{self.standby_wal_volume}:{self.WAL_VOLUME_MOUNT}",
                self.config.postgres_image,
                "-c", backup_command,
            ],
            timeout=900,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"pg5r HTAP standby basebackup failed: run_id={self.config.run_id!r}, "
                f"stderr={result.stderr.strip()!r}"
            )
        self._relocate_standby_wal()
        self._start_postgres(
            self.standby_name,
            self.standby_data_volume,
            self.standby_wal_volume,
            self.config.standby_port,
            primary_options=(
                "-c hot_standby=on "
                f"-c max_standby_streaming_delay={self.config.max_standby_streaming_delay_ms}ms "
                "-c hot_standby_feedback=off"
            ),
        )
        self._wait_ready(self.standby_name, timeout=bootstrap_timeout)

    def _relocate_standby_wal(self) -> None:
        """Point the standby's pg_wal at its own isolated volume.

        pg_basebackup may materialize pg_wal as a real directory even when the
        source holds a symlink; normalize it exactly like the primary.
        """
        relocate = (
            f"if [ ! -L {self.PGDATA}/pg_wal ]; then "
            f"mkdir -p {self.WAL_VOLUME_MOUNT}/pg_wal; "
            f"mv {self.PGDATA}/pg_wal/* {self.WAL_VOLUME_MOUNT}/pg_wal/; "
            f"chown -R postgres:postgres {self.WAL_VOLUME_MOUNT}/pg_wal; "
            f"rmdir {self.PGDATA}/pg_wal; "
            f"ln -s {self.WAL_VOLUME_MOUNT}/pg_wal {self.PGDATA}/pg_wal; "
            "fi"
        )
        result = self._run(
            [
                "docker", "run", "--rm", "--user", "root", "--entrypoint", "bash",
                "--volume", f"{self.standby_data_volume}:{self.PGDATA}",
                "--volume", f"{self.standby_wal_volume}:{self.WAL_VOLUME_MOUNT}",
                self.config.postgres_image,
                "-c", relocate,
            ],
            timeout=600,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"pg5r HTAP standby pg_wal relocation failed: run_id={self.config.run_id!r}, "
                f"stderr={result.stderr.strip()!r}"
            )

    def _wait_ready(self, name: str, timeout: int) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = self._run(["docker", "inspect", "--format", "{{.State.Status}}", name], check=False)
            if state.returncode == 0 and state.stdout.strip() != "running":
                logs = self._run(["docker", "logs", "--tail", "50", name], check=False)
                raise RuntimeError(
                    f"pg5r HTAP postgres container exited during startup: container={name!r}, "
                    f"logs={(logs.stdout + logs.stderr).strip()!r}"
                )
            probe = self._exec_in(name, "pg_isready -U postgres -d postgres -t 2", check=False)
            if probe.returncode == 0:
                return
            time.sleep(1.0)
        raise RuntimeError(f"pg5r HTAP postgres container not ready in time: container={name!r}, timeout={timeout}")

    def _wait_streaming(self, timeout: int) -> None:
        deadline = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < deadline:
            try:
                rows = self.primary_sql("SELECT state FROM pg_stat_replication LIMIT 1;")
                if rows and rows[0][0] == "streaming":
                    for container in (self.primary_name, self.standby_name):
                        wal_target = self._exec_in(container, f"readlink {self.PGDATA}/pg_wal").stdout.strip()
                        if wal_target != f"{self.WAL_VOLUME_MOUNT}/pg_wal":
                            raise RuntimeError(
                                "pg5r HTAP pg_wal is not on the isolated volume: "
                                f"container={container!r}, readlink={wal_target!r}"
                            )
                    return
                last_error = f"replication state={rows!r}"
            except (psycopg2.Error, RuntimeError) as exc:
                last_error = repr(exc)
            time.sleep(1.0)
        raise RuntimeError(
            f"pg5r HTAP standby did not reach streaming replication in time: "
            f"run_id={self.config.run_id!r}, timeout={timeout}, last_error={last_error!r}"
        )

    def _sql_on(self, container: str, sql: str) -> list[tuple]:
        result = self._exec_in(
            container,
            "psql -X -v ON_ERROR_STOP=1 -U postgres -d postgres -At -F '|' -c " + self._shell_quote(sql),
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"pg5r HTAP psql failed: container={container!r}, sql={sql!r}, stderr={result.stderr.strip()!r}"
            )
        return [tuple(line.split("|")) for line in result.stdout.strip().splitlines()]

    def _ensure_tc_sidecar(self) -> None:
        with self._tc_lock:
            state = self._run(["docker", "inspect", "--format", "{{.State.Running}}", self.tc_name], check=False)
            if state.returncode == 0 and state.stdout.strip() == "true":
                return
            self._run(["docker", "rm", "-f", self.tc_name], check=False)
            self._run(
                [
                    "docker", "run", "--detach", "--name", self.tc_name,
                    "--network", f"container:{self.primary_name}",
                    "--cap-add", "NET_ADMIN",
                    "--entrypoint", "sleep",
                    self.config.tc_image,
                    "100000000",
                ]
            )
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                probe = self._exec_in(self.tc_name, "tc -V", check=False)
                if probe.returncode == 0:
                    return
                time.sleep(1.0)
            raise RuntimeError(f"pg5r HTAP tc sidecar not ready: container={self.tc_name!r}")

    def _container_ip(self, container: str) -> str:
        result = self._run(
            ["docker", "inspect", "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container]
        )
        ip = result.stdout.strip()
        if not ip:
            raise RuntimeError(f"pg5r HTAP container has no network IP: container={container!r}")
        return ip

    def _tc_exec(self, commands: list[str]) -> str:
        self._ensure_tc_sidecar()
        outputs: list[str] = []
        for command in commands:
            result = self._exec_in(self.tc_name, command, check=False)
            if result.returncode != 0:
                raise RuntimeError(
                    f"pg5r HTAP tc command failed: command={command!r}, stderr={result.stderr.strip()!r}"
                )
            outputs.append(result.stdout.strip())
        return "\n".join(outputs)

    def _exec_in(self, container: str, command: str, *, check: bool = True) -> subprocess.CompletedProcess:
        return self._run(["docker", "exec", container, "bash", "-c", command], check=check)

    @staticmethod
    def _shell_quote(value: str) -> str:
        return "'" + value.replace("'", "'\\''") + "'"

    @staticmethod
    def _lsn_distance(left: str, right: str) -> int:
        def to_int(lsn: str) -> int:
            high, low = lsn.split("/")
            return int(high, 16) * (1 << 32) + int(low, 16)

        return to_int(left) - to_int(right)

    def _run(self, args: list[str], *, check: bool = True, timeout: int = 300) -> subprocess.CompletedProcess:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        if check and result.returncode != 0:
            raise RuntimeError(f"docker command failed: args={args!r}, stderr={result.stderr.strip()!r}")
        return result
