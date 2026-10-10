# Create and verify TiFlash database replicas

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/create-tiflash-replicas.md`
- Source Title: `Create TiFlash Replicas`
- Source Heading Path: `Create TiFlash Replicas > Create TiFlash replicas for databases | Create TiFlash Replicas > Create TiFlash replicas for databases > Check replication progress`
- Source Line Ranges: `74-126`
- Source Scope: `all`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `replica-creation`, `database-replication`, `ddl`, `replication-progress`, `batch-operations`, `availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0475_656bc54dcf`
- Source ID: `tidb-docs-8.1:tiflash/create-tiflash-replicas.md#create-tiflash-replicas-for-databases`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1262660154c0f865dd8008c36a8847473b375be9b9f1aaa795a63548f35f9804`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas#create-tiflash-replicas-for-databases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/create-tiflash-replicas.md

## Retrieval Guidance

- Use When: Use this when you need the exact SQL and caveats for creating or deleting TiFlash replicas for all tables in a database and checking database-wide replication progress.
- Retrieval Keywords: ALTER DATABASE db_name SET TIFLASH REPLICA count, ALTER DATABASE `tpch50` SET TIFLASH REPLICA 2, ALTER DATABASE `tpch50` SET TIFLASH REPLICA 0, SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>', SELECT TABLE_NAME FROM information_schema.tables where TABLE_SCHEMA = "<db_name>" and TABLE_NAME not in (SELECT TABLE_NAME FROM information_schema.tiflash_replica where TABLE_SCHEMA = "<db_name>"), tidb_batch_pending_tiflash_count, system tables, views, temporary tables, character sets not supported by TiFlash
- Follow-up Guidance: The source notes that ALTER DATABASE ... SET TIFLASH REPLICA performs a series of resource-intensive DDL operations, can be interrupted without rollback, and should not be combined with replica-count changes or other DDL on that database until all tables are replicated.
- Classification Note: This is classified as an operation chunk because it describes database-level DDL for TiFlash replica creation and deletion, plus SQL to inspect replication coverage and progress.

## Official Source Content

## Create TiFlash replicas for databases

Similar to creating TiFlash replicas for tables, you can send a DDL statement to TiDB through a MySQL client to create a TiFlash replica for all tables in a specific database:

```sql
ALTER DATABASE db_name SET TIFLASH REPLICA count;
```

In this statement, `count` indicates the number of replicas. When you set it to `0`, replicas are deleted.

Examples:

- Create two replicas for all tables in the database `tpch50`:

    ```sql
    ALTER DATABASE `tpch50` SET TIFLASH REPLICA 2;
    ```

- Delete TiFlash replicas created for the database `tpch50`:

    ```sql
    ALTER DATABASE `tpch50` SET TIFLASH REPLICA 0;
    ```

> **Note:**
>
> - This statement actually performs a series of DDL operations, which are resource-intensive. If the statement is interrupted during the execution, executed operations are not rolled back and unexecuted operations do not continue.
>
> - After executing the statement, do not set the number of TiFlash replicas or perform DDL operations on this database until **all tables in this database are replicated**. Otherwise, unexpected results might occur, which include:
>     - If you set the number of TiFlash replicas to 2 and then change the number to 1 before all tables in the database are replicated, the final number of TiFlash replicas of all the tables is not necessarily 1 or 2.
>     - After executing the statement, if you create tables in this database before the completion of the statement execution, TiFlash replicas **might or might not** be created for these new tables.
>     - After executing the statement, if you add indexes for tables in the database before the completion of the statement execution, the statement might hang and resume only after the indexes are added.
>
> - If you create tables in this database **after** the completion of the statement execution, TiFlash replicas are not created automatically for these new tables.
>
> - This statement skips system tables, views, temporary tables, and tables with character sets not supported by TiFlash.

> - You can control the number of tables allowed to remain unavailable during execution by setting the [`tidb_batch_pending_tiflash_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_batch_pending_tiflash_count-new-in-v60) system variable. Lowering this value helps reduce the pressure on the cluster during replication. Note that this limit is not real-time, so it is still possible for the number of unavailable tables to exceed the limit after the setting is applied.
### Check replication progress

Similar to creating TiFlash replicas for tables, successful execution of the DDL statement does not mean the completion of replication. You can execute the following SQL statement to check the progress of replication on target tables:

```sql
SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>';
```

To check tables without TiFlash replicas in the database, you can execute the following SQL statement:

```sql
SELECT TABLE_NAME FROM information_schema.tables where TABLE_SCHEMA = "<db_name>" and TABLE_NAME not in (SELECT TABLE_NAME FROM information_schema.tiflash_replica where TABLE_SCHEMA = "<db_name>");
```
