"""PostgreSQL Persistent Scenario environment lifecycle.

Assembly follows the resolved instance binding. Oltp/warehouse instances
deploy one container from the instance's pinned dataset image through the
shared ``PGEnv`` path. The htap instances assemble their own deployment
primitives (instance-three run-scoped single node, instance-four physical
primary/standby streaming topology with the tc sidecar) plus an agent surface
that honors the documented tool contract over those primitives: SQL work with
the standby read-only route, fresh role-scoped connections for GUC scope
verification, bounded container logs, and instance lifecycle.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Callable, Mapping

import psycopg2

from src.execution.deployments.postgres import PGDockerDeployment
from src.execution.environments.postgres import PGEnv
from src.execution.specs import HostPortLayout
from src.persistent_scenarios.model.spec import PersistentScenarioSpec
from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness import (
    FreshnessDatasetScale,
    SMOKE_SCALE as FRESHNESS_SMOKE_SCALE,
    bootstrap as _bootstrap_replica_freshness,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_replica_freshness.topology import (
    HtapReplicaTopology,
    ReplicaTopologyConfig,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation import (
    HtapDatasetScale,
    SMOKE_SCALE as HTAP3_SMOKE_SCALE,
    bootstrap as _bootstrap_shared_isolation,
)
from src.persistent_scenarios.backend.postgres.workloads.htap_shared_isolation.single_node import (
    SingleNodePostgres,
    SingleNodePostgresConfig,
)


_POSTGRES_RUNTIME_OPTIONS = (
    "-c archive_mode=on -c wal_level=replica -c max_wal_senders=2 "
    "-c track_io_timing=on -c log_checkpoints=on "
    "-c shared_preload_libraries=pg_stat_statements -c logging_collector=on "
    "-c log_destination=stderr -c log_directory=/var/log/postgresql "
    "-c log_filename=postgresql-%Y-%m-%d_%H%M%S.log"
)

_SQL_RESULT_ROW_CAP = 200


class HtapScenarioEnvironment:
    """Agent-facing environment over one htap deployment primitive.

    The engine, capability activation contexts, state-fact sampling, trusted
    telemetry and safety floors only require ``open_workload_connection``;
    the agent tool surface below dispatches ``execute_sql`` (with the
    instance-four standby read-only route), ``read_log`` and
    ``manage_instance`` against the primitive's containers.
    """

    def __init__(
        self,
        primitive,
        *,
        bootstrap,
        scale,
        primary_port: Callable[[], int],
        role_credentials: Mapping[str, str],
        log_targets: Mapping[str, str],
        standby_targets: bool,
        time_scale: float = 1.0,
    ):
        self._primitive = primitive
        self._bootstrap = bootstrap
        self._scale = scale
        self._primary_port = primary_port
        self._role_credentials = dict(role_credentials)
        self._log_targets = dict(log_targets)
        self._standby_targets = bool(standby_targets)
        self._agent_sql_timeouts: tuple[str, str] | None = None
        self.time_scale = float(time_scale)

    # -- lifecycle ---------------------------------------------------------

    def deploy(self) -> None:
        self._primitive.deploy()
        self._bootstrap(self._primitive.open_workload_connection, self._scale)

    def teardown(self) -> None:
        self._primitive.teardown()

    # -- engine and capability surfaces -------------------------------------

    def open_workload_connection(self, application_name: str, target: str = "primary"):
        self._require_target(target)
        return self._primitive.open_workload_connection(application_name, target)

    def open_role_connection(self, role_name: str, application_name: str):
        """Fresh login as one of the instance's LOGIN roles (GUC scope checks)."""
        password = self._role_credentials.get(role_name)
        if password is None:
            raise ValueError(
                "No credentials registered for this instance role: "
                f"role={role_name!r}, registered={sorted(self._role_credentials)!r}"
            )
        connection = psycopg2.connect(
            host="localhost",
            port=self._primary_port(),
            user=role_name,
            password=password,
            dbname=self._primitive.workload_dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        connection.autocommit = False
        return connection

    # -- trusted capability surfaces (replica-fleet primitives) --------------

    def primary_sql(self, sql: str) -> list[tuple]:
        return self._primitive.primary_sql(sql)

    def standby_sql(self, sql: str) -> list[tuple]:
        return self._primitive.standby_sql(sql)

    def replication_facts(self) -> dict:
        return self._primitive.replication_facts()

    def throttle_facts(self) -> dict:
        return self._primitive.throttle_facts()

    def apply_bandwidth_limit(self, rate_kbit: int | None = None) -> None:
        self._primitive.apply_bandwidth_limit(rate_kbit)

    def release_bandwidth_limit(self) -> None:
        self._primitive.release_bandwidth_limit()

    def set_agent_sql_timeouts(self, statement_timeout: str, lock_timeout: str) -> None:
        self._agent_sql_timeouts = (statement_timeout, lock_timeout)

    # -- agent tool surface --------------------------------------------------

    def get_tool_schemas(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_sql",
                    "description": "Execute SQL against the primary (or the read-only standby with target='standby').",
                    "parameters": {
                        "type": "object",
                        "required": ["sql_query"],
                        "properties": {
                            "sql_query": {"type": "string"},
                            "target": {"type": "string", "enum": ["primary", "standby"]},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_log",
                    "description": "Read recent container log output for a topology node.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "enum": sorted(self._log_targets)},
                            "tail_lines": {"type": "integer"},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_instance",
                    "description": "Lifecycle action (restart/start/stop) on a topology node.",
                    "parameters": {
                        "type": "object",
                        "required": ["action"],
                        "properties": {
                            "action": {"type": "string", "enum": ["restart", "start", "stop"]},
                            "target": {"type": "string", "enum": sorted(self._log_targets)},
                        },
                    },
                },
            },
        ]

    def execute_action(self, api: str, args: Mapping[str, object]) -> str:
        if api == "execute_sql":
            return self._execute_agent_sql(args)
        if api == "read_log":
            return self._read_log(args)
        if api == "manage_instance":
            return self._manage_instance(args)
        raise ValueError(
            f"Unknown htap environment tool: api={api!r}, known=['execute_sql', 'manage_instance', 'read_log']"
        )

    def _execute_agent_sql(self, args: Mapping[str, object]) -> str:
        sql_query = args.get("sql_query")
        if not isinstance(sql_query, str) or not sql_query.strip():
            raise ValueError(f"execute_sql requires a non-empty sql_query: args={dict(args)!r}")
        target = args.get("target") or "primary"
        self._require_target(target)
        connection = self._primitive.open_workload_connection("pg5r-htap-agent", target)
        try:
            with connection.cursor() as cursor:
                if target == "standby":
                    cursor.execute("SET LOCAL default_transaction_read_only = on;")
                if self._agent_sql_timeouts is not None:
                    statement_timeout, lock_timeout = self._agent_sql_timeouts
                    cursor.execute(f"SET LOCAL statement_timeout = '{statement_timeout}';")
                    cursor.execute(f"SET LOCAL lock_timeout = '{lock_timeout}';")
                cursor.execute(sql_query)
                rows = cursor.fetchall() if cursor.description else []
                columns = [str(column.name) for column in cursor.description] if cursor.description else []
            connection.commit()
        except psycopg2.Error as exc:
            connection.rollback()
            return json.dumps({"status": "error", "error": str(exc).strip()}, ensure_ascii=False)
        finally:
            connection.close()
        truncated = len(rows) > _SQL_RESULT_ROW_CAP
        payload = {
            "status": "success",
            "columns": columns,
            "result": [list(row) for row in rows[:_SQL_RESULT_ROW_CAP]],
            "row_count": len(rows),
        }
        if truncated:
            payload["truncated"] = True
            payload["truncation_hint"] = f"showing first {_SQL_RESULT_ROW_CAP} of {len(rows)} rows"
        return json.dumps(payload, ensure_ascii=False, default=str)

    def _read_log(self, args: Mapping[str, object]) -> str:
        target = args.get("target") or "primary"
        container = self._log_targets.get(str(target))
        if container is None:
            raise ValueError(
                f"Unknown read_log target: target={target!r}, known={sorted(self._log_targets)!r}"
            )
        tail_lines = int(args.get("tail_lines") or 200)
        completed = subprocess.run(
            ["docker", "logs", "--tail", str(tail_lines), container],
            capture_output=True, text=True, check=False,
        )
        return json.dumps({
            "status": "success",
            "target": str(target),
            "log": (completed.stdout + completed.stderr)[-32000:],
        }, ensure_ascii=False)

    def _manage_instance(self, args: Mapping[str, object]) -> str:
        action = args.get("action")
        if action not in {"restart", "start", "stop"}:
            raise ValueError(f"manage_instance action must be restart/start/stop: action={action!r}")
        target = args.get("target") or "primary"
        container = self._log_targets.get(str(target))
        if container is None:
            raise ValueError(
                f"Unknown manage_instance target: target={target!r}, known={sorted(self._log_targets)!r}"
            )
        subprocess.run(["docker", str(action), container], capture_output=True, text=True, check=True)
        return json.dumps({
            "status": "success",
            "action": action,
            "target": str(target),
            "container": container,
        }, ensure_ascii=False)

    def _require_target(self, target: object) -> None:
        allowed = {"primary", "standby"} if self._standby_targets else {"primary"}
        if target not in allowed:
            raise ValueError(
                f"Unknown workload connection target: target={target!r}, allowed={sorted(allowed)!r}"
            )


class RoleAwareEnvironment:
    """``PGEnv`` 外观层：为 ``guc_effective``（scope=role）提供按角色的全新登录。

    required-state 采样器以 duck-typing 探测 ``open_role_connection``；共享层
    ``PGEnv`` 没有角色凭据概念，由绑定把 dataset 镜像的角色表注入本包装层。
    接口与 ``HtapScenarioEnvironment.open_role_connection`` 一致。
    """

    def __init__(self, inner, role_credentials: Mapping[str, str], port: int, dbname: str):
        self._inner = inner
        self._role_credentials = dict(role_credentials)
        self._port = port
        self._dbname = dbname

    def open_role_connection(self, role_name: str, application_name: str):
        if role_name not in self._role_credentials:
            raise ValueError(
                "No credentials registered for this instance role: "
                f"role={role_name!r}, registered={sorted(self._role_credentials)!r}"
            )
        connection = psycopg2.connect(
            host="localhost",
            port=self._port,
            user=role_name,
            password=self._role_credentials[role_name],
            dbname=self._dbname,
            connect_timeout=5,
            application_name=application_name,
        )
        connection.autocommit = False
        return connection

    def __getattr__(self, name: str):
        return getattr(self._inner, name)


class PostgresEnvironmentProvider:
    def __init__(self, runtime_options: str = "", binding=None):
        self._runtime_options = runtime_options
        self._binding = binding

    def _container_name(self, run_id: str) -> str:
        raw = f"pg5r-int-{run_id}"
        if len(raw) <= 120:
            return raw
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
        return f"{raw[:107]}-{digest}"

    def host_ports(self, spec: PersistentScenarioSpec) -> HostPortLayout:
        allowed_range = (25200, 25299) if self._binding is not None and self._binding.style == 'htap' else (1024, 65535)
        return HostPortLayout(offsets=tuple(range(len(spec.environment.nodes))), allowed_range=allowed_range)

    def create(self, spec: PersistentScenarioSpec, run_id: str, port: int, *, time_scale: float = 1.0):
        if self._binding is not None and self._binding.style == "htap":
            return self._create_htap_environment(spec, run_id, port, time_scale=time_scale)
        node = spec.environment.nodes[0]
        if len(spec.environment.nodes) != 1 or node.role != "primary":
            raise ValueError(
                "Multi-node Persistent Scenario topology assembly is htap-only: "
                f"scenario_id={spec.scenario_id!r}, node_ids={[item.node_id for item in spec.environment.nodes]!r}"
            )
        resources = node.resources
        deployment = PGDockerDeployment(
            container_name=self._container_name(run_id),
            postgres_user="postgres",
            postgres_password="password",
            postgres_db="testdb",
            port=port,
            image_name=spec.environment.base_image,
            postgres_runtime_options=_POSTGRES_RUNTIME_OPTIONS
            + (f" {self._runtime_options}" if self._runtime_options else ""),
            initialization_timeout_seconds=1800,
            resources={
                "cpus": resources.container_cpu_limit,
                "memory_mb": resources.container_memory_mb,
                "shm_size": "256m",
                # 不设 disk_quota：校准与 zero 路径（run_path 脚本容器）无可写层配额，
                # 引擎路径必须同条件；8G 配额会让 warehouse 场景的合法批次写入 11 分钟
                # 内 ENOSPC 崩库（calibration/production same-conditions）。
            },
        )
        return RoleAwareEnvironment(
            PGEnv(
                workload=None,
                deployment=deployment,
                host="localhost",
                port=port,
                user="postgres",
                password="password",
                dbname="testdb",
                tool_profile="general_knowledge",
                allow_sampler_reconnect=True,
            ),
            role_credentials=dict(self._binding.role_credentials) if self._binding is not None else {},
            port=port,
            dbname="testdb",
        )

    def _create_htap_environment(self, spec: PersistentScenarioSpec, run_id: str, port: int, *, time_scale: float = 1.0):
        # Compressed-timeline runs bootstrap the instance calibration scale,
        # mirroring the three-path scripts' rule
        # (FULL_SCALE if scoring_seconds >= PRODUCTION_HORIZON_SECONDS else SMOKE_SCALE):
        # the difficulty thresholds are measured on the smoke dataset, so an
        # engine run on the compressed timeline must use the same dataset scale.
        workload = spec.environment.workload
        nodes = spec.environment.nodes
        if workload == "htap_orders":
            scale = HtapDatasetScale() if time_scale <= 1 else HTAP3_SMOKE_SCALE
            if len(nodes) != 1 or nodes[0].role != "primary":
                raise ValueError(
                    "pg_htap_shared_resource_isolation deploys exactly one primary node: "
                    f"scenario_id={spec.scenario_id!r}, "
                    f"nodes={[(item.node_id, item.role) for item in nodes]!r}"
                )
            resources = nodes[0].resources
            primitive = SingleNodePostgres(SingleNodePostgresConfig(
                run_id=run_id,
                port=port,
                workdir=Path("logs") / "pg5r-htap-work" / run_id,
                cpu_limit=resources.container_cpu_limit,
                memory_mb=resources.container_memory_mb,
                image=spec.environment.base_image,
            ))
            return HtapScenarioEnvironment(
                primitive,
                bootstrap=_bootstrap_shared_isolation,
                scale=scale,
                primary_port=lambda: primitive.config.port,
                role_credentials={},
                log_targets={"primary": primitive.container_name},
                standby_targets=False,
                time_scale=time_scale,
            )
        if workload == "frs_orders":
            if [node.role for node in nodes] != ["primary", "standby"]:
                raise ValueError(
                    "pg_htap_replica_freshness deploys one primary plus one standby node: "
                    f"scenario_id={spec.scenario_id!r}, "
                    f"nodes={[(item.node_id, item.role) for item in nodes]!r}"
                )
            resources = nodes[0].resources
            primitive = HtapReplicaTopology(ReplicaTopologyConfig(
                run_id=run_id,
                primary_port=port,
                standby_port=port + 1,
                cpu_per_node=resources.container_cpu_limit,
                memory_mb_per_node=resources.container_memory_mb,
            ))
            return HtapScenarioEnvironment(
                primitive,
                bootstrap=_bootstrap_replica_freshness,
                scale=FreshnessDatasetScale() if time_scale <= 1 else FRESHNESS_SMOKE_SCALE,
                primary_port=lambda: primitive.config.primary_port,
                role_credentials=dict(self._binding.role_credentials),
                log_targets={"primary": primitive.primary_name, "standby": primitive.standby_name},
                standby_targets=True,
                time_scale=time_scale,
            )
        raise ValueError(
            f"No htap environment assembly exists for this workload key: workload={workload!r}"
        )

    def deploy(self, environment) -> None:
        environment.deploy()

    def teardown(self, environment) -> None:
        environment.teardown()
