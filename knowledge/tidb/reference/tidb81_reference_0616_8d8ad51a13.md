# Placement resource group and utility statements overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-overview.md`
- Source Title: `SQL Statement Overview`
- Source Heading Path: `SQL Statement Overview > Placement policy | SQL Statement Overview > Resource groups | SQL Statement Overview > Utility statements`
- Source Line Ranges: `146-198`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `pd`, `tidb`
- Topic Tags: `placement-policy`, `placement-rules`, `labels`, `resource-groups`, `request-unit`, `runaway-queries`, `query-watch`, `schema-inspection`, `execution-plan`, `trace`, `database-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0616_8d8ad51a13`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-overview.md#placement-policy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `decfd710cc98427198cb8251097e9f0259e739e0522b0d6e2cea6221508e96fa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#placement-policy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview of SQL statements for placement policy, resource groups, runaway query watch management, execution plan inspection, tracing, or selecting the current database.
- Retrieval Keywords: Placement policy, ALTER PLACEMENT POLICY, ALTER RANGE, CREATE PLACEMENT POLICY, DROP PLACEMENT POLICY, SHOW CREATE PLACEMENT POLICY, SHOW PLACEMENT FOR, SHOW PLACEMENT LABELS, SHOW PLACEMENT, Resource groups, ALTER RESOURCE GROUP, CALIBRATE RESOURCE, Request Unit, RU, CREATE RESOURCE GROUP, DROP RESOURCE GROUP, QUERY WATCH, runaway query watch list, SET RESOURCE GROUP, SHOW CREATE RESOURCE GROUP, Utility statements, DESC, DESCRIBE, DO, EXPLAIN, TRACE, USE
- Follow-up Guidance: The overview groups statement-specific pages under placement policy, resource groups, and utility statements, including `CALIBRATE RESOURCE`, `QUERY WATCH`, `EXPLAIN`, and `TRACE`.
- Classification Note: This chunk is a reference overview because it lists SQL statements by category and summarizes what each one does.

## Official Source Content

## Placement policy

| SQL Statement | Description |
|---------------|-------------|
| [`ALTER PLACEMENT POLICY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-placement-policy) | Modifies a placement policy. |
| [`ALTER RANGE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-range) | Modifies the range of a placement policy. |
| [`CREATE PLACEMENT POLICY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy) | Creates a new placement policy. |
| [`DROP PLACEMENT POLICY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-placement-policy) | Drops an existing placement policy. |
| [`SHOW CREATE PLACEMENT POLICY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-placement-policy) | Shows the `CREATE` statement for a placement policy. |
| [`SHOW PLACEMENT FOR`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement-for) | Shows placement rules for a specific table. |
| [`SHOW PLACEMENT LABELS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement-labels) | Shows available placement labels. |
| [`SHOW PLACEMENT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement) | Shows placement rules. |
## Resource groups

| SQL Statement | Description |
|---------------|-------------|
| [`ALTER RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group) | Modifies a resource group. |
| [`CALIBRATE RESOURCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource) | Estimates and outputs the [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru) capacity of the current cluster. |
| [`CREATE RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group) | Creates a new resource group. |
| [`DROP RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group) | Drops a resource group. |
| [`QUERY WATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-query-watch) | Manages the runaway query watch list. |
| [`SET RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-resource-group) | Sets a resource group. |
| [`SHOW CREATE RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-resource-group) | Shows the `CREATE` statement for a resource group. |

| SQL Statement | Description |
|---------------|-------------|
| [`ALTER RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group) | Modifies a resource group. |
| [`CREATE RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group) | Creates a new resource group. |
| [`DROP RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group) | Drops a resource group. |
| [`QUERY WATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-query-watch) | Manages the runaway query watch list. |
| [`SET RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-resource-group) | Sets a resource group. |
| [`SHOW CREATE RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-resource-group) | Shows the `CREATE` statement for a resource group. |
## Utility statements

| SQL Statement | Description |
|---------------|-------------|
| [`DESC`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-desc) | An alias to `DESCRIBE`, which shows the structure of a table. |
| [`DESCRIBE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-describe) | Shows the structure of a table. |
| [`DO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-do) | Executes an expression but does not return any results. |
| [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) | Shows the execution plan of a query. |
| [`TRACE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-trace) | Provides detailed information about query execution. |
| [`USE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-use) | Sets the current database. |
