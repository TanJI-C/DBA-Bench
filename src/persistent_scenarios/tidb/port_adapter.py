"""Real-environment adapter: ``TiDBDockerDeployment`` -> TiDBPersistentEnvironmentPort.

This adapter lives in the instance package and is consumed by the mechanism
verification and three-path scripts. The backend assembly provides its own
persistent environment through the same port.
"""

from __future__ import annotations


import json
import re
import subprocess
import time
from typing import Any, Mapping

import pymysql

from .port import DBConnection

IO_LIMIT_KEY = "storage.io-rate-limit.max-bytes-per-sec"

_BYTE_RATE_UNITS = {"B": 1, "KiB": 1024, "MiB": 1024 ** 2, "GiB": 1024 ** 3, "TiB": 1024 ** 4}


def parse_bytes_per_sec(value: Any) -> int:
    """TiKV reports storage.io-rate-limit.max-bytes-per-sec in human-readable
    form (e.g. "0KiB", "1MiB"); callers need bytes per second as an int."""
    if isinstance(value, bool):
        raise ValueError(f"unparseable TiKV byte-rate value: {value!r}")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([KMGT]?i?B)", str(value).strip())
    if match is None:
        raise ValueError(f"unparseable TiKV byte-rate value: {value!r}")
    number, unit = match.groups()
    if unit not in _BYTE_RATE_UNITS:
        raise ValueError(f"unsupported TiKV byte-rate unit: {value!r}, known={sorted(_BYTE_RATE_UNITS)}")
    return int(float(number) * _BYTE_RATE_UNITS[unit])


class DeploymentPort:
    """Serves the port surface from a configured, deployed TiDB compose project."""

    def __init__(self, deployment: Any, *, sql_port: int, database: str = "shop") -> None:
        self.deployment = deployment
        self.sql_port = sql_port
        self.database = database
        self._driver: Any = None

    # -- wiring ---------------------------------------------------------------

    def attach_driver(self, driver: Any) -> None:
        self._driver = driver

    def connect_sql(self, database: str | None = None, *, read_timeout_ms: int = 3000,
                    target: str | None = None) -> DBConnection:
        if target is not None:
            host, port = self.deployment.tidb_endpoints[target]
        else:
            host, port = self.deployment.tidb_endpoints["tidb/tidb-0"]
        return pymysql.connect(
            host=host,
            port=port,
            user="root",
            password="",
            database=database,
            charset="utf8mb4",
            autocommit=False,
            connect_timeout=5,
            read_timeout=read_timeout_ms / 1000.0,
        )

    # -- TiDBPersistentEnvironmentPort ---------------------------------------

    def control_connection(self) -> DBConnection:
        return self.connect_sql(self.database, read_timeout_ms=10000)

    def workload(self) -> Any:
        if self._driver is None:
            raise RuntimeError("DeploymentPort has no workload driver attached")
        return self._driver

    def pd_stores(self) -> tuple[Mapping[str, Any], ...]:
        payload = self.deployment.pd_request("GET", "/pd/api/v1/stores")
        return tuple(payload.get("stores", ()))

    def set_tikv_io_rate_limit(self, target: str, max_bytes_per_sec: int) -> Mapping[str, Any]:
        body = json.dumps({IO_LIMIT_KEY: str(max_bytes_per_sec)}, separators=(",", ":"))
        output = self.deployment.exec(
            target,
            ["wget", "-qO-", "--timeout=5", "--content-on-error",
             "--method=POST", "--header=Content-Type: application/json",
             f"--body-data={body}", "http://127.0.0.1:20180/config"],
        )
        if output.strip() and output.strip() != "{}":
            payload = json.loads(output)
            if payload.get("error"):
                raise RuntimeError(
                    f"TiKV config update failed: target={target!r}, value={max_bytes_per_sec!r}, "
                    f"response={payload!r}"
                )
        return self.tikv_io_rate_limit(target)

    def tikv_io_rate_limit(self, target: str) -> Mapping[str, Any]:
        output = self.deployment.exec(
            target, ["wget", "-qO-", "--timeout=5", "http://127.0.0.1:20180/config"],
        )
        payload = json.loads(output)
        limits = dict(payload["storage"]["io-rate-limit"])
        limits["max-bytes-per-sec"] = parse_bytes_per_sec(limits["max-bytes-per-sec"])
        return limits

    # -- container-level slow-node injection (host docker CLI, same privilege
    #    the deployment itself uses) ------------------------------------------

    def _compose_container_id(self, target: str) -> str:
        service = target.rsplit("/", 1)[-1]
        result = subprocess.run(
            [
                "docker", "ps",
                "--filter", f"label=com.docker.compose.project={self.deployment.project_name}",
                "--filter", f"label=com.docker.compose.service={service}",
                "--format", "{{.ID}}",
            ],
            check=True, capture_output=True, text=True, timeout=15,
        )
        ids = result.stdout.split()
        if len(ids) != 1:
            raise RuntimeError(
                f"expected exactly one compose container for the target: target={target!r}, "
                f"project={self.deployment.project_name!r}, service={service!r}, ids={ids!r}"
            )
        return ids[0]

    def tikv_container_cpu_limit(self, target: str) -> Mapping[str, Any]:
        container = self._compose_container_id(target)
        result = subprocess.run(
            ["docker", "inspect", container,
             "--format", "{{.HostConfig.NanoCpus}} {{.HostConfig.CpuQuota}} {{.HostConfig.CpuPeriod}}"],
            check=True, capture_output=True, text=True, timeout=15,
        )
        nano_cpus, cpu_quota, cpu_period = (int(value) for value in result.stdout.split())
        return {
            "target": target,
            "container_id": container,
            "nano_cpus": nano_cpus,
            "cpus": nano_cpus / 1_000_000_000,
            "cpu_quota": cpu_quota,
            "cpu_period": cpu_period,
        }

    def set_tikv_container_cpu_limit(self, target: str, cpus: float) -> Mapping[str, Any]:
        if cpus <= 0:
            raise ValueError(f"container CPU limit must be positive: target={target!r}, cpus={cpus!r}")
        container = self._compose_container_id(target)
        subprocess.run(
            ["docker", "update", "--cpus", str(cpus), container],
            check=True, capture_output=True, text=True, timeout=15,
        )
        observed = self.tikv_container_cpu_limit(target)
        if abs(observed["cpus"] - cpus) > 1e-9:
            raise RuntimeError(
                f"container CPU limit did not take effect: target={target!r}, "
                f"requested_cpus={cpus!r}, observed={observed!r}"
            )
        return observed

    def start_tikv(self, target: str) -> Mapping[str, Any]:
        return self.deployment.stores.scale_out_tikv(target)

    def pd_regions_check(self, kind: str) -> tuple[Mapping[str, Any], ...]:
        allowed = ("miss-peer", "down-peer", "pending-peer")
        if kind not in allowed:
            raise ValueError(f"unsupported PD region check kind: kind={kind!r}, allowed={allowed!r}")
        payload = self.deployment.pd_request("GET", f"/pd/api/v1/regions/check/{kind}")
        if isinstance(payload, dict):
            return tuple(payload.get("regions", ()))
        return tuple(payload)

    def table_region_ids(self, table: str) -> tuple[int, ...]:
        db_name, _, table_name = table.rpartition(".")
        table_name = table_name or table
        sql = ("SELECT REGION_ID FROM INFORMATION_SCHEMA.TIKV_REGION_STATUS "
               "WHERE TABLE_NAME = %s AND IS_INDEX = 0")
        params: tuple = (table_name,)
        if db_name:
            sql += " AND DB_NAME = %s"
            params = (table_name, db_name)
        deadline = time.monotonic() + 30.0
        rows: tuple[tuple, ...] = ()
        while True:
            connection = self.connect_sql(None, read_timeout_ms=10000)
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                connection.commit()
            finally:
                connection.close()
            if rows or time.monotonic() >= deadline:
                break
            time.sleep(2)
        if not rows:
            raise RuntimeError(
                f"no regions visible for the business table in INFORMATION_SCHEMA.TIKV_REGION_STATUS: "
                f"table={table!r} (region key decoding follows PD heartbeats)"
            )
        return tuple(int(row[0]) for row in rows)

    def table_leader_distribution(self, table: str) -> Mapping[str, int]:
        """Leader count per store target for one business table: region list
        comes from INFORMATION_SCHEMA, leaders from the PD API per region."""
        store_address = {}
        for store in self.pd_stores():
            record = store["store"]
            store_address[int(record["id"])] = self._target_for_address(str(record["address"]))
        deadline = time.monotonic() + 30.0
        while True:
            distribution: dict[str, int] = {}
            for region_id in self.table_region_ids(table):
                region = self.deployment.pd_request("GET", f"/pd/api/v1/region/id/{region_id}")
                leader = region.get("leader") or {}
                if not leader.get("store_id"):
                    break  # leader transfer in flight; retry the snapshot
                store_id = int(leader["store_id"])
                target = store_address.get(store_id)
                if target is None:
                    raise RuntimeError(
                        f"leader store is not a known PD store: store_id={store_id!r}, table={table!r}"
                    )
                distribution[target] = distribution.get(target, 0) + 1
            if distribution or time.monotonic() >= deadline:
                break
            time.sleep(2)
        if not distribution:
            raise RuntimeError(
                f"no leader distribution observable for the business table: table={table!r}, "
                f"regions={len(self.table_region_ids(table))}"
            )
        return distribution

    def backend_connection_counts(self) -> Mapping[str, int]:
        counts: dict[str, int] = {}
        for target, (host, port) in self.deployment.tidb_endpoints.items():
            connection = pymysql.connect(host=host, port=port, user="root", password="",
                                         charset="utf8mb4", connect_timeout=5)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT CONNECTION_ID()")
                    own_id = int(cursor.fetchone()[0])
                    cursor.execute("SHOW PROCESSLIST")
                    rows = cursor.fetchall()
            finally:
                connection.close()
            # The probing session itself is excluded by id: row[4] is the
            # Command column ("Query" while running SHOW PROCESSLIST), so the
            # probe can never be identified by a name match and would
            # otherwise keep every count at >= 1 forever. Root infra rows
            # (health pings) stay filtered by command name.
            counts[target] = sum(
                1 for row in rows
                if int(row[0]) != own_id
                and (row[1] != "root" or str(row[4]) not in ("SHOW PROCESSLIST", "Ping Handler", "ok"))
            )
        return counts

    def drain_backend(self, target: str) -> Mapping[str, Any]:
        return {"drained": target, "note": "driver-side pool flag; router drain belongs to the backend env"}

    @staticmethod
    def _target_for_address(address: str) -> str:
        service = address.split(":", 1)[0]
        return f"tikv/{service}"
