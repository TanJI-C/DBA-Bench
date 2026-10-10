# Accelerated table creation overview, usage, limits, and implementation

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/accelerated-table-creation.md`
- Source Title: `TiDB Accelerated Table Creation`
- Source Heading Path: `TiDB Accelerated Table Creation | TiDB Accelerated Table Creation > Compatibility with TiDB tools | TiDB Accelerated Table Creation > Limitation | TiDB Accelerated Table Creation > Use `tidb_enable_fast_create_table` to accelerate table creation | TiDB Accelerated Table Creation > Implementation principle`
- Source Line Ranges: `6-57`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `ticdc`
- Topic Tags: `fast-create-table`, `ddl`, `create-table`, `system-variable`, `experimental-feature`, `tool-compatibility`, `limitations`, `implementation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0001_f578c1c87e`
- Source ID: `tidb-docs-8.1:accelerated-table-creation.md#tidb-accelerated-table-creation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `307730b215bb045e0c314b6336026d548a53a8ab0eb01a1c0cf834d928db0e2f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/accelerated-table-creation#tidb-accelerated-table-creation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/accelerated-table-creation.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about accelerated CREATE TABLE behavior in TiDB, including the tidb_enable_fast_create_table system variable, compatibility limits, or how the fast path works internally.
- Retrieval Keywords: tidb_enable_fast_create_table, tidb_ddl_version, fast create table, accelerated table creation, CREATE TABLE, SET GLOBAL tidb_enable_fast_create_table = ON, SET GLOBAL tidb_enable_fast_create_table = OFF, TiCDC does not support replicating the tables, foreign key constraints, mysql.tidb_ddl_job, mysql.tidb_ddl_history, owner node, non-owner node, online asynchronous schema change algorithm, implementation principle
- Follow-up Guidance: The source also states that this experimental feature only applies to CREATE TABLE without foreign key constraints and that TiCDC does not support replicating tables created by tidb_enable_fast_create_table.
- Classification Note: This chunk is classified under performance for the tidb component because it describes a system-variable-based optimization that accelerates table creation DDL execution.

## Official Source Content

# TiDB Accelerated Table Creation

TiDB v7.6.0 introduces the system variable [`tidb_ddl_version`](https://docs.pingcap.com/tidb/v7.6/system-variables#tidb_enable_fast_create_table-new-in-v800) to support accelerating table creation, which improves the efficiency of bulk table creation. Starting from v8.0.0, this system variable is renamed to [`tidb_enable_fast_create_table`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_create_table-new-in-v800).

TiDB uses the online asynchronous schema change algorithm to change the metadata. All DDL jobs are submitted to the `mysql.tidb_ddl_job` table, and the owner node pulls the DDL job to execute. After executing each phase of the online DDL algorithm, the DDL job is marked as completed and moved to the `mysql.tidb_ddl_history` table. Therefore, DDL statements can only be executed on the owner node and cannot be linearly extended.

However, for some DDL statements, it is not necessary to strictly follow the online DDL algorithm. For example, the `CREATE TABLE` statement only has two states for the job: `none` and `public`. Therefore, TiDB can simplify the execution process of DDL, and executes the `CREATE TABLE` statement on a non-owner node to accelerate table creation.

> **Warning:**
>
> This feature is currently an experimental feature and it is not recommended to use in a production environment. This feature might change or be removed without prior notice. If you find a bug, please give feedback by raising an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
## Compatibility with TiDB tools

- [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview) does not support replicating the tables that are created by `tidb_enable_fast_create_table`.
## Limitation

You can now use performance optimization for table creation only in the [`CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table) statement, and this statement must not include any foreign key constraints.
## Use `tidb_enable_fast_create_table` to accelerate table creation

You can enable or disable performance optimization for creating tables by specifying the value of the system variable [`tidb_enable_fast_create_table`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_create_table-new-in-v800).

To enable performance optimization for creating tables, set the value of this variable to `ON`:

```sql
SET GLOBAL tidb_enable_fast_create_table = ON;
```

To disable performance optimization for creating tables, set the value of this variable to `OFF`:

```sql
SET GLOBAL tidb_enable_fast_create_table = OFF;
```
## Implementation principle

The detailed implementation principle of performance optimization for table creation is as follows:

1. Create a `CREATE TABLE` Job.

   The corresponding DDL Job is generated by parsing the `CREATE TABLE` statement.

2. Execute the `CREATE TABLE` job.

   The TiDB node that receives the `CREATE TABLE` statement executes it directly, and then persists the table structure to TiKV. At the same time, the `CREATE TABLE` job is marked as completed and inserted into the `mysql.tidb_ddl_history` table.

3. Synchronize the table information.

   TiDB notifies other nodes to synchronize the newly created table structure.
