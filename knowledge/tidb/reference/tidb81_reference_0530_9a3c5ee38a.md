# ALTER TABLE COMPACT syntax, usage, examples, and concurrency

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-table-compact.md`
- Source Title: `ALTER TABLE ... COMPACT`
- Source Heading Path: `ALTER TABLE ... COMPACT | ALTER TABLE ... COMPACT > Synopsis | ALTER TABLE ... COMPACT > Examples | ALTER TABLE ... COMPACT > Examples > Compact TiFlash replicas in a table | ALTER TABLE ... COMPACT > Examples > Compact TiFlash replicas of specified partitions in a table | ALTER TABLE ... COMPACT > Concurrency`
- Source Line Ranges: `5-91`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tiflash`, `tidb`
- Topic Tags: `table-compaction`, `tiflash-replica`, `partition-compaction`, `syntax`, `examples`, `concurrency`, `resource-usage`, `kill`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0530_9a3c5ee38a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-table-compact.md#alter-table-compact`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `413e0e8a9a5da95739e25f00949354e166f464d0b93f8eb9814c0541e1cb7973`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact#alter-table-compact
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-table-compact.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the syntax, examples, supported scope, interruption behavior, or concurrency details of `ALTER TABLE ... COMPACT` for TiFlash replicas.
- Retrieval Keywords: ALTER TABLE ... COMPACT, ALTER TABLE employees COMPACT TIFLASH REPLICA, ALTER TABLE employees COMPACT PARTITION pNorth, pEast TIFLASH REPLICA, TIFLASH REPLICA, TiFlash replicas only, KILL, manual_compact_pool_size, compact all replicas in a table simultaneously, one table at a time by default
- Follow-up Guidance: If the user wants to check compaction progress or whether compaction is needed, see `INFORMATION_SCHEMA.TIFLASH_TABLES` and the `TOTAL_DELTA_ROWS` column.
- Classification Note: This is reference content because it defines the `ALTER TABLE ... COMPACT` syntax, execution characteristics, examples, and TiFlash concurrency behavior.

## Official Source Content

# ALTER TABLE ... COMPACT

To enhance read performance and reduce disk usage, TiDB automatically schedules data compaction on storage nodes in the background. During the compaction, storage nodes rewrite physical data, including cleaning up deleted rows and merging multiple versions of data caused by updates. The `ALTER TABLE ... COMPACT` statement allows you to initiate compaction for a specific table immediately, without waiting until compaction is triggered in the background.

The execution of this statement does not block existing SQL statements or affect any TiDB features, such as transactions, DDL, and GC. Data that can be selected via SQL statements will not be changed either. Executing this statement consumes some IO and CPU resources. Be careful to choose an appropriate timing for execution, such as when resources are available, to avoid negative impact on the business.

The compaction statement will be finished and returned when all replicas of a table are compacted. During the execution process, you can safely interrupt the compaction by executing the [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill) statement. Interrupting a compaction does not break data consistency or lead to data loss, nor does it affect subsequent manual or background compactions.

This data compaction statement is currently supported only for TiFlash replicas, not for TiKV replicas.
## Synopsis

```ebnf+diagram
AlterTableCompactStmt ::=
    'ALTER' 'TABLE' TableName 'COMPACT' ( 'PARTITION' PartitionNameList )? ( 'TIFLASH' 'REPLICA' )?
```

Since v6.2.0, the `TIFLASH REPLICA` part of the syntax can be omitted. When omitted, the semantic of the statement remains unchanged, and takes effect only for TiFlash.
## Examples
### Compact TiFlash replicas in a table

The following takes an `employees` table as an example, which has 4 partitions with 2 TiFlash replicas:

```sql
CREATE TABLE employees (
    id INT NOT NULL,
    hired DATE NOT NULL DEFAULT '1970-01-01',
    store_id INT
)
PARTITION BY LIST (store_id) (
    PARTITION pNorth VALUES IN (1, 2, 3, 4, 5),
    PARTITION pEast VALUES IN (6, 7, 8, 9, 10),
    PARTITION pWest VALUES IN (11, 12, 13, 14, 15),
    PARTITION pCentral VALUES IN (16, 17, 18, 19, 20)
);
ALTER TABLE employees SET TIFLASH REPLICA 2;
```

You can execute the following statement to immediately initiate the compaction for the 2 TiFlash replicas for all partitions in the `employees` table:

```sql
ALTER TABLE employees COMPACT TIFLASH REPLICA;
```
### Compact TiFlash replicas of specified partitions in a table

The following takes an `employees` table as an example, which has 4 partitions with 2 TiFlash replicas:

```sql
CREATE TABLE employees (
    id INT NOT NULL,
    hired DATE NOT NULL DEFAULT '1970-01-01',
    store_id INT
)
PARTITION BY LIST (store_id) (
    PARTITION pNorth VALUES IN (1, 2, 3, 4, 5),
    PARTITION pEast VALUES IN (6, 7, 8, 9, 10),
    PARTITION pWest VALUES IN (11, 12, 13, 14, 15),
    PARTITION pCentral VALUES IN (16, 17, 18, 19, 20)
);

ALTER TABLE employees SET TIFLASH REPLICA 2;
```

You can execute the following statement to immediately initiate the compaction for the 2 TiFlash replicas of the `pNorth` and `pEast` partitions in the `employees` table:

```sql
ALTER TABLE employees COMPACT PARTITION pNorth, pEast TIFLASH REPLICA;
```
## Concurrency

The `ALTER TABLE ... COMPACT` statement compacts all replicas in a table simultaneously.

To avoid a significant impact on online business, each TiFlash instance only compacts data in one table at a time by default (except for the compaction triggered in the background). This means that if you execute the `ALTER TABLE ... COMPACT` statement on multiple tables at the same time, their executions will be queued on the same TiFlash instance, rather than being executed simultaneously.

To obtain greater table-level concurrency with higher resource usage, you can modify the TiFlash configuration [`manual_compact_pool_size`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration). For example, when `manual_compact_pool_size` is set to 2, compaction for 2 tables can be processed simultaneously.
