"""Rolling-upgrade business canaries, backup evidence and Agent controls."""
import hashlib
import json
from typing import Any, Dict

from src.execution.environments.tidb import TiDBEnv
from src.execution.tidb_cluster_control import TiDBClusterControl


class RollingUpgradeControl(TiDBClusterControl):
    def _release(self, operation, target, parameters):
        env = self.env
        if operation == "get":
            return super()._release(operation, target, parameters)
        elif operation not in {"prepare", "snapshot", "verify", "upgrade", "rollback"}:
            raise ValueError(f"Unsupported release operation: operation={operation!r}")
        elif env.deployment.upgrade_release is None:
            raise ValueError(
                "release "
                + operation
                + " is unavailable on this case: no upgrade release configured"
                + f" (current_release={env.deployment.release.version!r})"
            )
        elif operation == "prepare":
            details = env._run_upgrade_precheck()
            result = env._agent_upgrade_precheck_result(details)
        elif operation == "snapshot":
            result = env._agent_upgrade_backup_result(env._create_upgrade_backup())
        elif operation == "verify":
            phase = str(parameters.get("phase", ""))
            if phase not in {"before", "after"}:
                raise ValueError(
                    "release verify requires parameters.phase=before or after"
                )
            details = env._run_upgrade_canary(phase)
            result = env._agent_canary_result(phase, details)
        elif operation in {"upgrade", "rollback"}:
            return super()._release(operation, target, parameters)
        return result


class RollingUpgradeEnv(TiDBEnv):
    cluster_control_type = RollingUpgradeControl

    def _require_business_change_case(self):
        if self._case is None:
            raise RuntimeError("TiDB business-change action requires a configured scenario case")
        required = ("database", "table", "row_count")
        missing = [name for name in required if not hasattr(self._case, name)]
        if missing:
            raise RuntimeError(
                f"TiDB business-change action received a case without required fields: "
                f"case={self._case.case_id!r}, missing={missing!r}"
            )
        return self._case


    def _business_checksum(self, case) -> list[dict[str, Any]]:
        return self._query_rows(
            f"SELECT COUNT(*) AS row_count, "
            f"CAST(SUM(amount * 100) AS SIGNED) AS amount_cents, "
            f"CAST(SUM(tenant_id) AS SIGNED) AS tenant_sum "
            f"FROM {case.database}.{case.table}"
        )


    def _canary_queries(self, case) -> tuple[str, ...]:
        table = f"{case.database}.{case.table}"
        return (
            f"SELECT COUNT(*) AS row_count, CAST(SUM(amount * 100) AS SIGNED) AS amount_cents, "
            f"CAST(SUM(tenant_id) AS SIGNED) AS tenant_sum FROM {table}",
            f"SELECT event_type, COUNT(*) AS event_count, "
            f"CAST(SUM(amount * 100) AS SIGNED) AS amount_cents FROM {table} "
            "GROUP BY event_type ORDER BY event_type",
            f"SELECT tenant_id, COUNT(*) AS event_count FROM {table} "
            "GROUP BY tenant_id ORDER BY tenant_id LIMIT 32",
            f"SELECT event_id, event_type, amount FROM {table} "
            "WHERE tenant_id = 17 ORDER BY event_time DESC LIMIT 32",
        )


    def _run_canary_on_endpoint(self, target: str, case) -> dict[str, Any]:
        import pymysql

        host, port = self.deployment.tidb_endpoints[target]
        results = []
        with pymysql.connect(
            host=host,
            port=port,
            user=self.user,
            password=self.password,
            database=case.database,
            charset="utf8mb4",
            autocommit=True,
            connect_timeout=5,
            read_timeout=self.sql_timeout_seconds,
            write_timeout=self.sql_timeout_seconds,
        ) as connection:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                for sql in self._canary_queries(case):
                    cursor.execute(sql)
                    results.append(list(cursor.fetchall()))
        encoded = json.dumps(results, ensure_ascii=False, sort_keys=True, default=str).encode()
        return {
            "target": target,
            "endpoint": f"{host}:{port}",
            "result_digest": hashlib.sha256(encoded).hexdigest(),
            "query_count": len(results),
            "rows": results,
        }


    def _run_upgrade_canary(self, phase: str) -> dict[str, Any]:
        case = self._require_business_change_case()
        if phase not in {"before", "after"}:
            raise ValueError(f"BC01 canary phase must be before or after: phase={phase!r}")
        endpoints = {
            target: self._run_canary_on_endpoint(target, case)
            for target in self.deployment.tidb_endpoints
        }
        digest = hashlib.sha256(
            json.dumps(
                {target: item["result_digest"] for target, item in endpoints.items()},
                sort_keys=True,
            ).encode()
        ).hexdigest()
        event = self.deployment.rollout.record_upgrade_event(
            f"canary_{phase}",
            endpoint_count=len(endpoints),
            result_digest=digest,
            endpoints=endpoints,
        )
        return event


    def _create_upgrade_backup(self) -> dict[str, Any]:
        case = self._require_business_change_case()
        checksum = self._business_checksum(case)
        schema = self._query_rows(f"SHOW CREATE TABLE {case.database}.{case.table}")
        payload = {"checksum": checksum, "schema": schema, "rpo": "0"}
        digest = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode()
        ).hexdigest()
        event = self.deployment.rollout.record_upgrade_event(
            "backup_created",
            backup_id=f"bc01-{self.run_id}-logical-manifest",
            manifest_digest=digest,
            checksum=checksum,
            schema=schema,
            schema_digest=hashlib.sha256(
                json.dumps(schema, ensure_ascii=False, sort_keys=True, default=str).encode()
            ).hexdigest(),
            rpo="0",
        )
        return event


    def _run_upgrade_precheck(self) -> dict[str, Any]:
        case = self._require_business_change_case()
        deployment = self.deployment
        readiness = deployment.rollout.wait_for_upgrade_precheck()
        cluster_info = self._query_rows(
            "SELECT TYPE, INSTANCE, VERSION FROM information_schema.cluster_info "
            "ORDER BY TYPE, INSTANCE"
        )
        variables = self._query_rows(
            "SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb "
            "WHERE VARIABLE_NAME IN ('new_collation_enabled', 'tidb_server_version') "
            "ORDER BY VARIABLE_NAME"
        )
        event = deployment.rollout.record_upgrade_event(
            "upgrade_precheck",
            readiness=readiness,
            current_version=deployment.release.version,
            target_version=deployment.upgrade_release.version if deployment.upgrade_release else None,
            cluster_info=cluster_info,
            compatibility_variables=variables,
            business_table=f"{case.database}.{case.table}",
        )
        return event


    @staticmethod
    def _agent_upgrade_precheck_result(details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "current_version": details["current_version"],
            "target_version": details["target_version"],
            "cluster_info": details["cluster_info"],
            "compatibility_variables": details["compatibility_variables"],
        }


    @staticmethod
    def _agent_upgrade_backup_result(details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "checksum": details["checksum"],
            "schema": details["schema"],
        }


    @staticmethod
    def _agent_canary_result(phase: str, details: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "phase": phase,
            "endpoints": {
                target: {
                    "endpoint": endpoint["endpoint"],
                    "query_count": endpoint["query_count"],
                    "rows": endpoint["rows"],
                }
                for target, endpoint in details["endpoints"].items()
            },
        }
