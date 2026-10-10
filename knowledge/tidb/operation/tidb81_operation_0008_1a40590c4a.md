# DDL best practices for execution speed and load impact

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/ddl-introduction.md`
- Source Title: `Execution Principles and Best Practices of DDL Statements`
- Source Heading Path: `Execution Principles and Best Practices of DDL Statements > Best practices | Execution Principles and Best Practices of DDL Statements > Best practices > Balance the physical DDL execution speed and the impact on application load through system variables | Execution Principles and Best Practices of DDL Statements > Best practices > Quickly create many tables by concurrently sending DDL requests | Execution Principles and Best Practices of DDL Statements > Best practices > Make multiple changes in a single `ALTER` statement | Execution Principles and Best Practices of DDL Statements > Best practices > Check the read and write performance`
- Source Line Ranges: `134-168`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `shared`
- Topic Tags: `ddl`, `best-practices`, `reorg-workers`, `batch-size`, `add-index`, `alter-table`, `concurrency`, `performance-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0008_1a40590c4a`
- Source ID: `tidb-docs-8.1:best-practices/ddl-introduction.md#best-practices`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63e992657ad7bc6658f5eca3e2a6b04b2dc09a7a26e76776a907a008ff933d8f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction#best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/ddl-introduction.md

## Retrieval Guidance

- Use When: Use this chunk when discussing DDL execution best practices for balancing `ADD INDEX` or column type change speed against cluster load, creating many tables faster, combining schema changes in one `ALTER`, or checking performance during backfill.
- Retrieval Keywords: tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_batch_size, re-organize phase, backfilling, physical DDL, ADD INDEX, column type changes, concurrently sending DDL requests, single ALTER statement, multiple schema objects, atomicity, write reorg, Grafana dashboard, read and write performance metrics, application response time
- Follow-up Guidance: It notes that these two system variables can be dynamically adjusted during a DDL task and take effect in the next transaction batch.
- Classification Note: Classified as operation because the content gives operational tuning and usage practices for DDL execution speed, concurrency, and monitoring impact on application load.

## Official Source Content

## Best practices
### Balance the physical DDL execution speed and the impact on application load through system variables

When executing physical DDL statements (including adding indexes or column type changes), you can adjust the values of the following system variables to balance the speed of DDL execution and the impact on application load:

- [`tidb_ddl_reorg_worker_cnt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_worker_cnt): This variable sets the number of reorg workers for a DDL operation, which controls the concurrency of backfilling.

- [`tidb_ddl_reorg_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_batch_size): This variable sets the batch size for a DDL operation in the `re-organize` phase, which controls the amount of data to be backfilled.

    Recommended values:

    - If there is no other load, you can increase the values of `tidb_ddl_reorg_worker_cnt` and `tidb_ddl_reorg_batch_size` to speed up the `ADD INDEX` operation. For example, you can set the values of the two variables to `20` and `2048`, respectively.
    - If there is other load, you can decrease the values of `tidb_ddl_reorg_worker_cnt` and `tidb_ddl_reorg_batch_size` to minimize the impact on other application. For example, you can set the values of the these variables to `4` and `256`, respectively.

> **Tip:**
>
> - The preceding two variables can be dynamically adjusted during the execution of a DDL task, and take effect in the next transaction batch.
> - Choose the appropriate time to execute the DDL operation based on the type of the operation and the application load pressure. For example, it is recommended to run the `ADD INDEX` operation when the application load is low.
> - Because the duration of adding an index is relatively long, TiDB will execute the task in the background after the command is sent. If the TiDB server is down, the execution will not be affected.
### Quickly create many tables by concurrently sending DDL requests

A table creation operation takes about 50 milliseconds. The actual time taken to create a table might be longer because of the framework limitations.

To create tables faster, it is recommended to send multiple DDL requests concurrently to achieve the fastest table creation speed. If you send DDL requests serially and do not send them to the Owner node, the table creation speed will be very slow.
### Make multiple changes in a single `ALTER` statement

Starting from v6.2.0, TiDB supports modifying multiple schema objects (such as columns and indexes) of a table in a single `ALTER` statement while ensuring the atomicity of the entire statement. Therefore, it is recommended to make multiple changes in a single `ALTER` statement.
### Check the read and write performance

When TiDB is adding an index, the phase of backfilling data will cause read and write pressure on the cluster. After the `ADD INDEX` command is sent and the `write reorg` phase starts, it is recommended to check the read and write performance metrics of TiDB and TiKV on the Grafana dashboard and the application response time, to determine whether the `ADD INDEX` operation affects the cluster.
