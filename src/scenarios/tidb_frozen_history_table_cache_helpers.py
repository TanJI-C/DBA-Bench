from __future__ import annotations

import threading
from collections.abc import Mapping
from dataclasses import dataclass
import re

import pymysql

from src.database.query_results import capture_query_result_truth
from src.database.sql import (
    execute_json_payload,
    execute_result_rows,
    require_one_result_row,
    require_success_payload,
)
from src.database.tidb import execute_integrity_tuple, table_cache_lease_integrity_sql
from src.scenarios.workloads import WorkloadProfile


_SQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_sql_identifier(value: str, name: str) -> str:
    if not _SQL_IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid SQL identifier for {name}: {value!r}")
    return value


def _join_thread(thread: threading.Thread, timeout: float, context: str) -> None:
    thread.join(timeout=timeout)
    if thread.is_alive():
        raise RuntimeError(f"{context} did not stop within {timeout} seconds")


@dataclass(frozen=True, slots=True)
class TableCacheLeaseTables:
    db: str
    catalog: str
    inventory: str
    pricing: str
    orders: str
    healthy_aux: str

    @property
    def causal(self) -> tuple[str, ...]:
        return (self.catalog, self.inventory, self.pricing)

    @property
    def cached(self) -> tuple[str, ...]:
        return (*self.causal, self.healthy_aux)

    @property
    def business(self) -> tuple[str, ...]:
        return (self.catalog, self.orders, self.inventory, self.pricing, self.healthy_aux)


def configure_tables(config: Mapping[str, object]) -> TableCacheLeaseTables:
    return TableCacheLeaseTables(
        db=_validate_sql_identifier(str(config["db"]), "database"),
        catalog=_validate_sql_identifier(str(config["catalog_table"]), "catalog_table"),
        inventory=_validate_sql_identifier(str(config["inventory_table"]), "inventory_table"),
        pricing=_validate_sql_identifier(str(config["pricing_table"]), "pricing_table"),
        orders=_validate_sql_identifier(str(config["orders_table"]), "orders_table"),
        healthy_aux=_validate_sql_identifier(str(config["healthy_aux_table"]), "healthy_aux_table"),
    )


def business_summary_sql(tables: TableCacheLeaseTables) -> str:
    return (
        "SELECT table_name, row_count, id_checksum FROM ("
        f"SELECT 'catalog' AS table_name, COUNT(*) AS row_count, COALESCE(SUM(sku_id), 0) AS id_checksum FROM {tables.db}.{tables.catalog} "
        f"UNION ALL SELECT 'inventory', COUNT(*), COALESCE(SUM(sku_id), 0) FROM {tables.db}.{tables.inventory} "
        f"UNION ALL SELECT 'pricing', COUNT(*), COALESCE(SUM(rule_id), 0) FROM {tables.db}.{tables.pricing} "
        f"UNION ALL SELECT 'orders', COUNT(*), COALESCE(SUM(order_id), 0) FROM {tables.db}.{tables.orders} "
        f"UNION ALL SELECT 'catalog_aux', COUNT(*), COALESCE(SUM(sku_id), 0) FROM {tables.db}.{tables.healthy_aux}"
        ") AS business_summary ORDER BY table_name"
    )


def table_integrity_sql(tables: TableCacheLeaseTables) -> str:
    catalog_integrity = (
        "SELECT COUNT(*), COALESCE(SUM(sku_id), 0), "
        "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', sku_id, tenant_id, category, price, stock))), 0) "
        f"FROM {tables.db}.{tables.catalog}"
    )
    return table_cache_lease_integrity_sql(
        tables.db,
        tables.catalog,
        cache_table=tables.catalog,
        cache_integrity_sql=catalog_integrity,
        orders_table=tables.orders,
        inventory_table=tables.inventory,
        pricing_table=tables.pricing,
        healthy_cache_table_names=(tables.healthy_aux,),
    )


def _execute(env: object, sql: str, context: str, *, target: str | None = None) -> dict:
    result = env.execute_sql(sql) if target is None else env.execute_sql(sql, target=target)
    return require_success_payload(result, f"{context}: sql={sql!r}")


def create_and_seed_schema(env: object, tables: TableCacheLeaseTables, catalog_rows: int) -> None:
    _execute(env, f"CREATE DATABASE IF NOT EXISTS {tables.db}", "create frozen-history table-cache-lease database")
    for table in tables.business:
        _execute(env, f"DROP TABLE IF EXISTS {tables.db}.{table}", f"clear frozen-history table-cache-lease table: table={table}")
    _execute(
        env,
        f"CREATE TABLE {tables.db}.{tables.catalog} ("
        "sku_id BIGINT NOT NULL, tenant_id INT NOT NULL, category VARCHAR(32) NOT NULL, "
        "price DECIMAL(12,2) NOT NULL, stock INT NOT NULL, updated_at DATETIME NOT NULL, "
        "PRIMARY KEY (sku_id)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
        "create frozen-history table-cache-lease catalog table",
    )
    _execute(
        env,
        f"CREATE TABLE {tables.db}.{tables.inventory} ("
        "sku_id BIGINT NOT NULL, warehouse_id INT NOT NULL, available INT NOT NULL, reserved INT NOT NULL, "
        "PRIMARY KEY (sku_id, warehouse_id), KEY idx_inventory_warehouse (warehouse_id, sku_id)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
        "create frozen-history table-cache-lease inventory table",
    )
    _execute(
        env,
        f"CREATE TABLE {tables.db}.{tables.pricing} ("
        "rule_id BIGINT NOT NULL, tenant_id INT NOT NULL, category VARCHAR(32) NOT NULL, "
        "discount_pct DECIMAL(5,2) NOT NULL, priority INT NOT NULL, active TINYINT NOT NULL, "
        "PRIMARY KEY (rule_id), KEY idx_pricing_tenant (tenant_id, active, priority)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
        "create frozen-history table-cache-lease pricing table",
    )
    _execute(
        env,
        f"CREATE TABLE {tables.db}.{tables.orders} ("
        "order_id BIGINT NOT NULL, tenant_id INT NOT NULL, sku_id BIGINT NOT NULL, amount DECIMAL(12,2) NOT NULL, "
        "status VARCHAR(16) NOT NULL, write_attempts INT NOT NULL DEFAULT 0, created_at DATETIME NOT NULL, "
        "PRIMARY KEY (order_id), KEY idx_orders_tenant (tenant_id, created_at), KEY idx_orders_sku (sku_id)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
        "create frozen-history table-cache-lease orders table",
    )
    _execute(
        env,
        f"CREATE TABLE {tables.db}.{tables.healthy_aux} ("
        "sku_id BIGINT NOT NULL, tenant_id INT NOT NULL, category VARCHAR(32) NOT NULL, "
        "price DECIMAL(12,2) NOT NULL, stock INT NOT NULL, updated_at DATETIME NOT NULL, "
        "PRIMARY KEY (sku_id)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin",
        "create frozen-history table-cache-lease auxiliary table",
    )
    _execute(
        env,
        f"INSERT INTO {tables.db}.{tables.catalog} "
        "(sku_id, tenant_id, category, price, stock, updated_at) "
        "SELECT n, MOD(n, 32) + 1, ELT(MOD(n, 4) + 1, 'hardware', 'software', 'service', 'accessory'), "
        "CAST(MOD(n * 7919, 100000) / 100 AS DECIMAL(12,2)), MOD(n * 13, 400), "
        "TIMESTAMPADD(DAY, MOD(n, 365), '2026-01-01 00:00:00') "
        "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
        f"FROM information_schema.columns LIMIT {catalog_rows}) AS source",
        "load frozen-history table-cache-lease catalog",
    )
    _execute(
        env,
        f"INSERT INTO {tables.db}.{tables.inventory} "
        "(sku_id, warehouse_id, available, reserved) "
        "SELECT a.n + 1, b.n + 1, MOD(a.n * 17 + b.n * 11, 400), MOD(a.n + b.n, 40) "
        "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
        "FROM information_schema.columns LIMIT 256) AS a "
        "CROSS JOIN (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
        "FROM information_schema.columns LIMIT 3) AS b",
        "load frozen-history table-cache-lease inventory",
    )
    _execute(
        env,
        f"INSERT INTO {tables.db}.{tables.pricing} "
        "(rule_id, tenant_id, category, discount_pct, priority, active) "
        "SELECT n, MOD(n, 32) + 1, ELT(MOD(n, 4) + 1, 'hardware', 'software', 'service', 'accessory'), "
        "CAST(MOD(n * 17, 2500) / 100 AS DECIMAL(5,2)), MOD(n, 5) + 1, IF(MOD(n, 3) = 0, 0, 1) "
        "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) AS n "
        "FROM information_schema.columns LIMIT 128) AS source",
        "load frozen-history table-cache-lease pricing",
    )
    _execute(
        env,
        f"INSERT INTO {tables.db}.{tables.orders} "
        "(order_id, tenant_id, sku_id, amount, status, created_at) "
        "SELECT a.n * 32 + b.n + 1, MOD(a.n, 32) + 1, MOD(a.n * 7 + b.n, 256), "
        "CAST(MOD((a.n * 32 + b.n) * 313, 100000) / 100 AS DECIMAL(12,2)), "
        "ELT(MOD(a.n + b.n, 4) + 1, 'paid', 'pending', 'shipped', 'cancelled'), "
        "TIMESTAMPADD(MINUTE, a.n * 32 + b.n, '2026-01-01 00:00:00') "
        "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
        "FROM information_schema.columns LIMIT 64) AS a "
        "CROSS JOIN (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
        "FROM information_schema.columns LIMIT 32) AS b",
        "load frozen-history table-cache-lease orders",
    )
    _execute(
        env,
        f"INSERT INTO {tables.db}.{tables.healthy_aux} "
        "(sku_id, tenant_id, category, price, stock, updated_at) "
        "SELECT n + 10000, MOD(n, 32) + 1, ELT(MOD(n, 4) + 1, 'hardware', 'software', 'service', 'accessory'), "
        "CAST(MOD(n * 6151, 100000) / 100 AS DECIMAL(12,2)), MOD(n * 7, 400), "
        "TIMESTAMPADD(DAY, MOD(n, 365), '2026-01-01 00:00:00') "
        "FROM (SELECT ROW_NUMBER() OVER (ORDER BY table_schema, table_name, column_name) - 1 AS n "
        "FROM information_schema.columns LIMIT 64) AS source",
        "load frozen-history table-cache-lease auxiliary table",
    )


def enable_cache_and_verify(env: object, tables: TableCacheLeaseTables) -> None:
    for table in tables.business:
        _execute(env, f"ANALYZE TABLE {tables.db}.{table}", f"analyze frozen-history table-cache-lease table: table={table}")
    for table in tables.cached:
        _execute(env, f"ALTER TABLE {tables.db}.{table} CACHE", f"enable frozen-history table-cache-lease cache: table={table}")
    lease_rows = execute_result_rows(
        env.execute_sql,
        "SHOW GLOBAL VARIABLES LIKE 'tidb_table_cache_lease'",
        "verify frozen-history table-cache-lease cache lease",
    )
    lease_row = require_one_result_row(lease_rows, "verify frozen-history table-cache-lease cache lease")
    if int(lease_row[1]) != 3:
        raise RuntimeError(f"table-cache-lease requires initial tidb_table_cache_lease=3: rows={lease_rows!r}")
    for table in tables.cached:
        definition = execute_result_rows(
            env.execute_sql,
            f"SHOW CREATE TABLE {tables.db}.{table}",
            f"verify frozen-history table-cache-lease cache marker: table={table}",
        )
        row = require_one_result_row(definition, f"verify frozen-history table-cache-lease cache marker: table={table}")
        if "cached on" not in str(row[1]).casefold():
            raise RuntimeError(f"table-cache-lease cache marker is absent: table={tables.db}.{table}, row={row!r}")


def table_id(env: object, tables: TableCacheLeaseTables, table: str) -> int:
    rows = execute_result_rows(
        env.execute_sql,
        "SELECT TIDB_TABLE_ID FROM information_schema.tables "
        f"WHERE TABLE_SCHEMA = '{tables.db}' AND TABLE_NAME = '{table}'",
        f"read frozen-history table-cache-lease table ID: table={table}",
    )
    row = require_one_result_row(rows, f"read frozen-history table-cache-lease table ID: table={table}")
    if len(row) != 1:
        raise ValueError(f"table-cache-lease table ID result shape is invalid: table={table!r}, row={row!r}")
    return int(row[0])


def _capture_table_state(env: object, tables: TableCacheLeaseTables, table: str) -> dict[str, object]:
    definition_rows = execute_result_rows(
        env.execute_sql,
        f"SHOW CREATE TABLE {tables.db}.{table}",
        f"capture frozen-history table-cache-lease table definition: table={table}",
    )
    definition = require_one_result_row(definition_rows, f"capture frozen-history table-cache-lease table definition: table={table}")
    current_id = table_id(env, tables, table)
    meta = execute_json_payload(
        env.execute_sql,
        "SELECT tid, lock_type, lease, oldReadLease FROM mysql.table_cache_meta "
        f"WHERE tid = {current_id}",
        f"capture frozen-history table-cache-lease cache metadata: table={table}",
    )
    return {
        "table_id": current_id,
        "show_create": definition,
        "cached_on": "cached on" in str(definition[1]).casefold(),
        "cache_meta": meta,
        "integrity": integrity(env, tables, table),
    }


def cache_state(env: object, tables: TableCacheLeaseTables) -> dict[str, object]:
    return {table: _capture_table_state(env, tables, table) for table in tables.cached}


def business_state(env: object, tables: TableCacheLeaseTables) -> dict[str, object]:
    return {table: _capture_table_state(env, tables, table) for table in tables.business}


def integrity(env: object, tables: TableCacheLeaseTables, table: str) -> tuple[int, int, int]:
    return execute_integrity_tuple(
        env.execute_sql,
        table_cache_lease_integrity_sql(
            tables.db,
            table,
            cache_table=tables.catalog,
            cache_integrity_sql=table_integrity_sql(tables),
            orders_table=tables.orders,
            inventory_table=tables.inventory,
            pricing_table=tables.pricing,
            healthy_cache_table_names=(tables.healthy_aux,),
        ),
        f"capture frozen-history table-cache-lease integrity: table={table}",
    )


def capture_business_truth(env: object, tables: TableCacheLeaseTables) -> object:
    payload = execute_json_payload(
        env.execute_sql,
        business_summary_sql(tables),
        "capture frozen-history table-cache-lease business truth",
    )
    return capture_query_result_truth(payload, ordered=True)


def build_workload_profiles(tables: TableCacheLeaseTables) -> tuple[WorkloadProfile, ...]:
    catalog_queries = (
        (
            "catalog_tenant_rollup",
            f"SELECT tenant_id, category, COUNT(*), AVG(price) FROM {tables.db}.{tables.catalog} "
            "WHERE tenant_id IN (3, 7, 11) GROUP BY tenant_id, category ORDER BY tenant_id, category",
            "catalog-api",
        ),
        (
            "catalog_sku_lookup",
            f"SELECT sku_id, category, price, stock FROM {tables.db}.{tables.catalog} "
            "WHERE sku_id BETWEEN 17 AND 96 ORDER BY sku_id",
            "catalog-api",
        ),
        (
            "catalog_category_probe",
            f"SELECT sku_id, price FROM {tables.db}.{tables.catalog} "
            "WHERE category IN ('hardware', 'software') ORDER BY price DESC, sku_id LIMIT 40",
            "pricing-api",
        ),
        (
            "catalog_stock_report",
            f"SELECT SUM(stock), MIN(price), MAX(price) FROM {tables.db}.{tables.catalog} "
            "WHERE stock > 0",
            "inventory-api",
        ),
        (
            "catalog_price_preview",
            f"SELECT category, COUNT(*), MIN(price), MAX(price) FROM {tables.db}.{tables.catalog} "
            "GROUP BY category ORDER BY category",
            "merchandising-preview",
        ),
        (
            "catalog_recent_probe",
            f"SELECT sku_id, updated_at FROM {tables.db}.{tables.catalog} "
            "WHERE updated_at >= '2026-01-01 00:00:00' ORDER BY updated_at DESC, sku_id LIMIT 64",
            "catalog-cache-warmup",
        ),
    )
    inventory_queries = (
        (
            "inventory_health_rollup",
            f"SELECT warehouse_id, COUNT(*), SUM(available) FROM {tables.db}.{tables.inventory} "
            "GROUP BY warehouse_id ORDER BY warehouse_id",
            "inventory-monitor",
        ),
        (
            "inventory_low_stock_probe",
            f"SELECT sku_id, warehouse_id, available FROM {tables.db}.{tables.inventory} "
            "WHERE available < 20 ORDER BY available, sku_id LIMIT 80",
            "replenishment-worker",
        ),
        (
            "warehouse_availability_read",
            f"SELECT sku_id, warehouse_id, reserved FROM {tables.db}.{tables.inventory} "
            "WHERE sku_id BETWEEN 15 AND 80 ORDER BY sku_id, warehouse_id LIMIT 60",
            "warehouse-api",
        ),
        (
            "inventory_capacity_probe",
            f"SELECT warehouse_id, SUM(available + reserved) FROM {tables.db}.{tables.inventory} "
            "GROUP BY warehouse_id",
            "capacity-planner",
        ),
    )
    pricing_queries = (
        (
            "pricing_rule_tenant_lookup",
            f"SELECT rule_id, tenant_id, category, discount_pct FROM {tables.db}.{tables.pricing} "
            "WHERE tenant_id IN (3, 7, 11) AND active = 1 ORDER BY tenant_id, priority, rule_id",
            "pricing-api",
        ),
        (
            "pricing_rule_rollup",
            f"SELECT category, COUNT(*), AVG(discount_pct) FROM {tables.db}.{tables.pricing} "
            "WHERE active = 1 GROUP BY category ORDER BY category",
            "pricing-analytics",
        ),
    )
    causal = []
    for name, sql, application in (*catalog_queries, *inventory_queries, *pricing_queries):
        causal.append(WorkloadProfile(
            name=name,
            sql=sql,
            qps=0.65,
            tier="OLTP_CORE",
            application_name=application,
            target="tidb/tidb-0",
        ))
    return (
        *causal,
        WorkloadProfile(
            name="aux_catalog_lookup",
            sql=(
                f"SELECT sku_id, category, price, stock FROM {tables.db}.{tables.healthy_aux} "
                "WHERE sku_id BETWEEN 10017 AND 10096 ORDER BY sku_id"
            ),
            qps=1.25,
            tier="OLTP_CORE",
            application_name="catalog-aux-reader",
            target="tidb/tidb-0",
        ),
        WorkloadProfile(
            name="aux_catalog_rollup",
            sql=(
                f"SELECT category, COUNT(*), AVG(price) FROM {tables.db}.{tables.healthy_aux} "
                "GROUP BY category ORDER BY category"
            ),
            qps=0.70,
            tier="OLAP_BURST",
            application_name="catalog-aux-report",
            target="tidb/tidb-0",
        ),
        WorkloadProfile(
            name="aux_catalog_point_probe",
            sql=(
                f"SELECT sku_id, category, stock FROM {tables.db}.{tables.healthy_aux} "
                "WHERE sku_id IN (10017, 10032, 10064, 10096) ORDER BY sku_id"
            ),
            qps=0.65,
            tier="OLTP_CORE",
            application_name="catalog-aux-point-reader",
            target="tidb/tidb-0",
        ),
        WorkloadProfile(
            name="orders_dashboard_rollup",
            sql=(
                f"SELECT tenant_id, status, COUNT(*), COALESCE(SUM(amount), 0) FROM {tables.db}.{tables.orders} "
                "GROUP BY tenant_id, status ORDER BY tenant_id, status"
            ),
            qps=0.35,
            tier="OLAP_BURST",
            application_name="orders-dashboard",
        ),
        WorkloadProfile(
            name="orders_recent_lookup",
            sql=(
                f"SELECT order_id, sku_id, amount, status FROM {tables.db}.{tables.orders} "
                "WHERE tenant_id = 7 ORDER BY created_at DESC, order_id DESC LIMIT 30"
            ),
            qps=0.55,
            tier="OLTP_CORE",
            application_name="orders-api",
        ),
        WorkloadProfile(
            name="schema_status_probe",
            sql=f"SHOW TABLE STATUS FROM {tables.db} LIKE '{tables.catalog}'",
            qps=0.22,
            tier="OPS_MAINTENANCE",
            application_name="schema-observer",
            transactional=False,
        ),
        WorkloadProfile(
            name="cluster_tso_probe",
            sql="SELECT @@tidb_current_ts",
            qps=0.35,
            tier="OPS_MAINTENANCE",
            application_name="transaction-monitor",
            transactional=False,
        ),
    )


def dual_cache_read_replay(
    env: object,
    tables: TableCacheLeaseTables,
    targets: tuple[str, ...],
    *,
    rounds: int,
) -> dict[str, int]:
    if len(targets) != 2:
        raise RuntimeError(f"table-cache-lease dual cache replay requires exactly two TiDB targets: targets={targets!r}")
    conflicts = {table: 0 for table in tables.causal}
    for round_no in range(1, rounds + 1):
        for table in tables.causal:
            barrier = threading.Barrier(2, timeout=30)
            failures: list[BaseException] = []
            round_conflicts = 0
            lock = threading.Lock()

            def worker(target: str) -> None:
                nonlocal round_conflicts
                connection = env.open_workload_connection(
                    f"cache-replay-{table}-{target.rsplit('/', 1)[1]}",
                    target=target,
                )
                try:
                    with connection.cursor() as cursor:
                        barrier.wait()
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {tables.db}.{table}")
                            cursor.fetchall()
                            connection.rollback()
                        except pymysql.MySQLError as exc:
                            connection.rollback()
                            code = exc.args[0] if exc.args else None
                            if code != 9007:
                                raise RuntimeError(
                                    "table-cache-lease cached-table replay returned an unexpected SQL error: "
                                    f"table={table!r}, target={target!r}, round={round_no}, code={code!r}, error={exc}"
                                ) from exc
                            with lock:
                                round_conflicts += 1
                except BaseException as exc:
                    failures.append(exc)
                    barrier.abort()
                finally:
                    connection.close()

            threads = tuple(
                threading.Thread(
                    target=worker,
                    args=(target,),
                    name=f"cache-replay-{round_no}-{target}",
                    daemon=True,
                )
                for target in targets
            )
            for thread in threads:
                thread.start()
            for thread in threads:
                _join_thread(thread, 45, f"table-cache-lease cached-table replay {thread.name}")
            if failures:
                raise RuntimeError(
                    "table-cache-lease cached-table replay failed: "
                    f"table={table!r}, round={round_no}, failures={failures!r}"
                ) from failures[0]
            conflicts[table] += round_conflicts
    return conflicts


def drop_schema(env: object, tables: TableCacheLeaseTables) -> None:
    for table in tables.cached:
        _execute(env, f"ALTER TABLE {tables.db}.{table} NOCACHE", f"disable frozen-history table-cache-lease cache: table={table}")
    _execute(env, "SET GLOBAL tidb_table_cache_lease = 3", "restore frozen-history table-cache-lease lease")
    _execute(env, f"DROP DATABASE IF EXISTS {tables.db}", "drop frozen-history table-cache-lease database")


__all__ = (
    "TableCacheLeaseTables",
    "business_summary_sql",
    "business_state",
    "build_workload_profiles",
    "cache_state",
    "capture_business_truth",
    "configure_tables",
    "create_and_seed_schema",
    "drop_schema",
    "dual_cache_read_replay",
    "enable_cache_and_verify",
    "integrity",
    "table_id",
    "table_integrity_sql",
)
