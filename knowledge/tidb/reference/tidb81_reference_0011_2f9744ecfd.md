# SQL feature matrix: advanced SQL, DDL, transactions, and partitioning

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/basic-features.md`
- Source Title: `TiDB Features`
- Source Heading Path: `TiDB Features > Advanced SQL features | TiDB Features > Data definition language (DDL) | TiDB Features > Transactions | TiDB Features > Partitioning`
- Source Line Ranges: `91-169`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`, `pd`
- Topic Tags: `feature-matrix`, `advanced-sql`, `ddl`, `transactions`, `partitioning`, `version-support`, `experimental-features`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0011_2f9744ecfd`
- Source ID: `tidb-docs-8.1:basic-features.md#advanced-sql-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c49dc3027fb3f481444b8c1ca6e5848bedc2c88600304de973e215a413b8da9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/basic-features#advanced-sql-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/basic-features.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB 8.1 feature support matrix for advanced SQL features, DDL, transactions, or partitioning and wants to compare Y, E, or N across versions 8.1 to 5.1.
- Retrieval Keywords: Advanced SQL features, Data definition language (DDL), Transactions, Partitioning, feature matrix, Prepared statement cache, Non-prepared statement cache, SQL binding, Cross-database binding, Create bindings according to historical execution plans, Coprocessor cache, Stale Read, Follower reads, tidb_snapshot, Optimizer hints, MPP execution engine, TiFlash Pipeline Model, TiFlash replica selection strategy, Index Merge, Placement Rules in SQL, Cascades Planner, Runtime Filter, Basic CREATE DROP ALTER RENAME TRUNCATE, Generated columns, Views, Sequences, Auto increment, Auto random, TTL (Time to Live), DDL algorithm assertions, Multi-schema change: add columns, Change column type, Temporary tables, Concurrent DDL statements, Acceleration of ADD INDEX and CREATE INDEX, tidb_ddl_enable_fast_reorg, Metadata lock, FLASHBACK CLUSTER, ADMIN PAUSE DDL, ADMIN RESUME DDL, TiDB Accelerated Table Creation, BDR role, Async commit, 1PC, Large transactions (10GB), Pessimistic transactions, Optimistic transactions, Repeatable-read isolation, Read-committed isolation, tidb_idle_transaction_timeout, tidb_dml_type = "bulk", Range partitioning, Hash partitioning, Key partitioning, List partitioning, List COLUMNS partitioning, Default partition for List and List COLUMNS partitioned tables, EXCHANGE PARTITION, REORGANIZE PARTITION, COALESCE PARTITION, Dynamic pruning, Range COLUMNS partitioning, Range INTERVAL partitioning, Convert a partitioned table to a non-partitioned table, Partition an existing table
- Follow-up Guidance: The tables link each listed item to its dedicated documentation page, such as sql-prepared-plan-cache, sql-statements/sql-statement-alter-table, transaction-isolation-levels, and partitioned-table.
- Classification Note: The classification is reference because the content is a version-by-version support matrix of TiDB features rather than procedural guidance.

## Official Source Content

## Advanced SQL features

| Advanced SQL features | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [Prepared statement cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) | Y | Y | Y | Y | Y | Y | Y | E | E |
| [Non-prepared statement cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache) | Y | Y | E | N | N | N | N | N | N |
| [SQL binding](https://docs.pingcap.com/tidb/stable/sql-plan-management#sql-binding) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Cross-database binding](https://docs.pingcap.com/tidb/stable/sql-plan-management#cross-database-binding) | Y | N | N | N | N | N | N | N | N |
| [Create bindings according to historical execution plans](https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding-according-to-a-historical-execution-plan) | Y | Y | Y | E | N | N | N | N | N |
| [Coprocessor cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Stale Read](https://docs.pingcap.com/tidb/stable/stale-read) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Follower reads](https://docs.pingcap.com/tidb/stable/follower-read) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Read historical data (tidb_snapshot)](https://docs.pingcap.com/tidb/stable/read-historical-data) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Optimizer hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [MPP execution engine](https://docs.pingcap.com/tidb/stable/explain-mpp) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [MPP execution engine - compression exchange](https://docs.pingcap.com/tidb/stable/explain-mpp#mpp-version-and-exchange-data-compression) | Y | Y | Y | N | N | N | N | N | N |
| [TiFlash Pipeline Model](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-pipeline-model) | Y | Y | N | N | N | N | N | N | N |
| [TiFlash replica selection strategy](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_replica_read-new-in-v730) | Y | Y | N | N | N | N | N | N | N |
| [Index Merge](https://docs.pingcap.com/tidb/stable/explain-index-merge) | Y | Y | Y | Y | Y | Y | E | E | E |
| [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql) | Y | Y | Y | Y | Y | E | E | N | N |
| [Cascades Planner](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_cascades_planner) | E | E | E | E | E | E | E | E | E |
| [Runtime Filter](https://docs.pingcap.com/tidb/stable/runtime-filter) | Y | Y | N | N | N | N | N | N | N |
## Data definition language (DDL)

| Data definition language (DDL) | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Basic `CREATE`, `DROP`, `ALTER`, `RENAME`, `TRUNCATE` | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Generated columns](https://docs.pingcap.com/tidb/stable/generated-columns) | Y | Y | Y | E | E | E | E | E | E |
| [Views](https://docs.pingcap.com/tidb/stable/views) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Sequences](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Auto increment](https://docs.pingcap.com/tidb/stable/auto-increment) | Y | Y | Y | Y[^4] | Y | Y | Y | Y | Y |
| [Auto random](https://docs.pingcap.com/tidb/stable/auto-random) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [TTL (Time to Live)](https://docs.pingcap.com/tidb/stable/time-to-live) | Y | Y | Y | E | N | N | N | N | N |
| [DDL algorithm assertions](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| Multi-schema change: add columns | Y | Y | Y | Y | E | E | E | E | E |
| [Change column type](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-modify-column) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Temporary tables](https://docs.pingcap.com/tidb/stable/temporary-tables) | Y | Y | Y | Y | Y | Y | Y | N | N |
| Concurrent DDL statements | Y | Y | Y | Y | N | N | N | N | N |
| [Acceleration of `ADD INDEX` and `CREATE INDEX`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) | Y | Y | Y | Y | N | N | N | N | N |
| [Metadata lock](https://docs.pingcap.com/tidb/stable/metadata-lock) | Y | Y | Y | Y | N | N | N | N | N |
| [`FLASHBACK CLUSTER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster) | Y | Y | Y | Y | N | N | N | N | N |
| [Pause](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl)/[Resume](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl) DDL | Y | Y | N | N | N | N | N | N | N |
| [TiDB Accelerated Table Creation](https://docs.pingcap.com/tidb/stable/accelerated-table-creation) | E | N | N | N | N | N | N | N | N |
| [Configure BDR role to replicate DDL statements in BDR mode](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-bdr-role#admin-setshowunset-bdr-role) | E | N | N | N | N | N | N | N | N |
## Transactions

| Transactions | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [Async commit](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_async_commit-new-in-v50) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [1PC](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_1pc-new-in-v50) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Large transactions (10GB)](https://docs.pingcap.com/tidb/stable/transaction-overview#transaction-size-limit) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Pessimistic transactions](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Optimistic transactions](https://docs.pingcap.com/tidb/stable/optimistic-transaction) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Repeatable-read isolation (snapshot isolation)](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Read-committed isolation](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Automatically terminating long-running idle transactions](https://docs.pingcap.com/tidb/stable/system-variables#tidb_idle_transaction_timeout-new-in-v760) | Y | N | N | N | N | N | N | N | N |
| [Bulk DML execution mode (`tidb_dml_type = "bulk"`)](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800) | E | N | N | N | N | N | N | N | N |
## Partitioning

| Partitioning | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [Range partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table#range-partitioning) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Hash partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table#hash-partitioning) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Key partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table#key-partitioning) | Y | Y | Y | N | N | N | N | N | N |
| [List partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table#list-partitioning) | Y | Y | Y | Y | Y | E | E | E | E |
| [List COLUMNS partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table) | Y | Y | Y | Y | Y | E | E | E | E |
| [Default partition for List and List COLUMNS partitioned tables](https://docs.pingcap.com/tidb/stable/partitioned-table#default-list-partition) | Y | Y | N | N | N | N | N | N | N |
| [`EXCHANGE PARTITION`](https://docs.pingcap.com/tidb/stable/partitioned-table) | Y | Y | Y | Y | E | E | E | E | E |
| [`REORGANIZE PARTITION`](https://docs.pingcap.com/tidb/stable/partitioned-table#reorganize-partitions) | Y | Y | Y | N | N | N | N | N | N |
| [`COALESCE PARTITION`](https://docs.pingcap.com/tidb/stable/partitioned-table#decrease-the-number-of-partitions) | Y | Y | Y | N | N | N | N | N | N |
| [Dynamic pruning](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode) | Y | Y | Y | Y | Y | E | E | E | E |
| [Range COLUMNS partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table#range-columns-partitioning) | Y | Y | Y | Y | N | N | N | N | N |
| [Range INTERVAL partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table#range-interval-partitioning) | Y | Y | Y | E | N | N | N | N | N |
| [Convert a partitioned table to a non-partitioned table](https://docs.pingcap.com/tidb/stable/partitioned-table#convert-a-partitioned-table-to-a-non-partitioned-table) | Y | Y | N | N | N | N | N | N | N |
| [Partition an existing table](https://docs.pingcap.com/tidb/stable/partitioned-table#partition-an-existing-table) | Y | Y | N | N | N | N | N | N | N |
