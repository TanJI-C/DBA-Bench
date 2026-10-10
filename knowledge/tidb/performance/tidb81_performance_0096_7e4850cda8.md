# DDL and index tuning best practices

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-optimize-sql-best-practices.md`
- Source Title: `Performance Tuning Best Practices`
- Source Heading Path: `Performance Tuning Best Practices > DDL best practices | Performance Tuning Best Practices > DDL best practices > Primary key best practices | Performance Tuning Best Practices > Index best practices | Performance Tuning Best Practices > Index best practices > Add index best practices`
- Source Line Ranges: `119-151`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `ddl`, `primary-key`, `indexes`, `add-index`, `online-ddl`, `reorg`, `concurrency`, `batch-size`, `write-conflicts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0096_7e4850cda8`
- Source ID: `tidb-docs-8.1:develop/dev-guide-optimize-sql-best-practices.md#ddl-best-practices`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `187f796478124d3a46da88f6ca8af60680fea1105d5d7c67f4faaff9223662c1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-best-practices#ddl-best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-optimize-sql-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB DDL and index tuning guidance, especially online add index behavior and the re-organize phase system variables.
- Retrieval Keywords: DDL best practices, Primary key best practices, rules to follow when selecting the primary key, Index best practices, Add index best practices, online index add operation, ADD INDEX, CREATE INDEX, re-organize phase, tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_batch_size, SET @@global.tidb_ddl_reorg_worker_cnt = 16, SET @@global.tidb_ddl_reorg_batch_size = 4096, SET @@global.tidb_ddl_reorg_worker_cnt = 4, SET @@global.tidb_ddl_reorg_batch_size = 128, write conflicts, does not block data reads and writes
- Follow-up Guidance: The source explains that increasing tidb_ddl_reorg_worker_cnt and tidb_ddl_reorg_batch_size can speed up add index, while frequently updated target columns can cause more write conflicts and longer completion due to retries.
- Classification Note: This is classified as performance for TiDB because it focuses on DDL and index creation behavior, including tuning add index concurrency and batch size with TiDB system variables.

## Official Source Content

## DDL best practices

This section describes the best practices involved when using TiDB's DDL.
### Primary key best practices

See the [rules to follow when selecting the primary key](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#guidelines-to-follow-when-selecting-primary-key).
## Index best practices

See [Index Best Practices](https://docs.pingcap.com/tidb/stable/develop/dev-guide-index-best-practice).
### Add index best practices

TiDB supports the online index add operation. You can use [ADD INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) or [CREATE INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index) statement to add an index. It does not block data reads and writes in the table. You can adjust the concurrency and the batch size during the `re-organize` phase of the index add operation by modifying the following system variables:

* [`tidb_ddl_reorg_worker_cnt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_worker_cnt)
* [`tidb_ddl_reorg_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_batch_size)

To reduce the impact on the online application, the default speed of add index operation is slow. When the target column of add index operation only involves read load or is not directly related to online workload, you can appropriately increase the value of the above variables to speed up the add index operation:

```sql
SET @@global.tidb_ddl_reorg_worker_cnt = 16;
SET @@global.tidb_ddl_reorg_batch_size = 4096;
```

When the target column of the add index operation is updated frequently (including `UPDATE`, `INSERT` and `DELETE`), increasing the above variables causes more write conflicts, which impacts the online workload. Accordingly, the add index operation might take a long time to complete due to constant retries. In this case, it is recommended to decrease the value of the above variables to avoid write conflicts with the online application:

```sql
SET @@global.tidb_ddl_reorg_worker_cnt = 4;
SET @@global.tidb_ddl_reorg_batch_size = 128;
```
