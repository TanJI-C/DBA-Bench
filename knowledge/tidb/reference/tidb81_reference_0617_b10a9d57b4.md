# Show, instance, and locking SQL statements overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-overview.md`
- Source Title: `SQL Statement Overview`
- Source Heading Path: `SQL Statement Overview > Show statements | SQL Statement Overview > Instance management | SQL Statement Overview > Locking statements`
- Source Line Ranges: `199-269`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`, `pd`
- Topic Tags: `show-statements`, `instance-management`, `locking`, `compatibility`, `monitoring`, `sessions`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0617_b10a9d57b4`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-overview.md#show-statements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3db33788b70ffe8f2e9a884c0c96493722d8fed265a973b5f84f16b6588fa0be`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#show-statements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of SHOW statements, instance management statements, or locking statements in TiDB and want the exact statement names and brief descriptions.
- Retrieval Keywords: SHOW BUILTINS, SHOW CHARACTER SET, SHOW COLLATIONS, SHOW ERRORS, SHOW STATUS, SHOW VARIABLES, SHOW WARNINGS, ALTER INSTANCE, FLUSH STATUS, KILL, SHOW CONFIG, SHOW ENGINES, SHOW PLUGINS, SHOW PROCESSLIST, SHOW PROFILES, SHUTDOWN, LOCK STATS, LOCK TABLES, UNLOCK STATS, UNLOCK TABLES, Prometheus and Grafana, Monitoring, compatibility with MySQL, kills a connection in any TiDB instance in the current TiDB cluster, stops the client-connected TiDB instance
- Follow-up Guidance: The content notes that SHOW STATUS and FLUSH STATUS are included for compatibility with MySQL, while centralized metrics collection uses Prometheus and Grafana or TiDB Cloud Monitoring for most metrics.
- Classification Note: This is a reference overview because it groups SQL statements under Show statements, Instance management, and Locking statements with one-line official descriptions.

## Official Source Content

## Show statements

| SQL Statement | Description |
|---------------|-------------|
| [`SHOW BUILTINS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-builtins) | Lists builtin functions. |
| [`SHOW CHARACTER SET`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-character-set) | Lists character sets. |
| [`SHOW COLLATIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-collation) | Lists collations. |
| [`SHOW ERRORS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-errors) | Shows errors from previously executed statements. |
| [`SHOW STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-status) | Included for [compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility). TiDB uses [Prometheus and Grafana](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework) for centralized metrics collection instead of `SHOW STATUS` for most metrics. |
| [`SHOW VARIABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-variables) | Shows system variables. |
| [`SHOW WARNINGS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-warnings) | Shows warnings and notes from previously executed statements. |

| SQL Statement | Description |
|---------------|-------------|
| [`SHOW BUILTINS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-builtins) | Lists builtin functions. |
| [`SHOW CHARACTER SET`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-character-set) | Lists character sets. |
| [`SHOW COLLATIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-collation) | Lists collations. |
| [`SHOW ERRORS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-errors) | Shows errors from previously executed statements. |
| [`SHOW STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-status) | Included for [compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility). TiDB Cloud provides [Monitoring](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster) for centralized metrics collection instead of `SHOW STATUS` for most metrics. |
| [`SHOW VARIABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-variables) | Shows system variables. |
| [`SHOW WARNINGS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-warnings) | Shows warnings and notes from previously executed statements. |
## Instance management

| SQL Statement | Description |
|---------------|-------------|
| [`ALTER INSTANCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-instance) | Modifies an instance. |
| [`FLUSH STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-status) | Included for [compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility). TiDB uses [Prometheus and Grafana](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework) for centralized metrics collection instead of `SHOW STATUS` for most metrics. |
| [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill) | Kills a connection in any TiDB instance in the current TiDB cluster. |
| [`SHOW CONFIG`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-config) | Shows the configuration of various components of TiDB. |
| [`SHOW ENGINES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-engines) | Shows available storage engines. |
| [`SHOW PLUGINS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-plugins) | Shows installed plugins. |
| [`SHOW PROCESSLIST`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-processlist) | Shows the current sessions connected to the same TiDB server. |
| [`SHOW PROFILES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-profiles) | Included for [compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility). Currently, it only returns an empty result. |
| [`SHUTDOWN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-shutdown) | Stops the client-connected TiDB instance, not the entire TiDB cluster. |

| SQL Statement | Description |
|---------------|-------------|
| [`ALTER INSTANCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-instance) | Modifies an instance. |
| [`FLUSH STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-status) | Included for [compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility). TiDB Cloud provides [Monitoring](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster) for centralized metrics collection instead of `SHOW STATUS` for most metrics. |
| [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill) | Kills a connection in any TiDB instance in the current TiDB cluster. |
| [`SHOW ENGINES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-engines) | Shows available storage engines. |
| [`SHOW PLUGINS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-plugins) | Shows installed plugins. |
| [`SHOW PROCESSLIST`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-processlist) | Shows the current sessions connected to the same TiDB server. |
| [`SHOW PROFILES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-profiles) | Shows query profiles. Included for [compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility). Currently only returns an empty result. |
## Locking statements

| SQL Statement | Description |
|---------------|-------------|
| [`LOCK STATS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats) | Locks statistics of tables or partitions. |
| [`LOCK TABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-tables-and-unlock-tables) | Locks tables for the current session. |
| [`UNLOCK STATS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-unlock-stats) | Unlocks statistics of tables or partitions. |
| [`UNLOCK TABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-tables-and-unlock-tables) | Unlocks tables. |
