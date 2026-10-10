# SQL optimization references and DDL job inspection

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/sql-faq.md`
- Source Title: `SQL FAQs`
- Source Heading Path: `SQL FAQs > SQL optimization | SQL FAQs > SQL optimization > TiDB execution plan description | SQL FAQs > SQL optimization > Statistics collection | SQL FAQs > SQL optimization > How to optimize `select count(1)`? | SQL FAQs > SQL optimization > How to view the progress of the current DDL job? | SQL FAQs > SQL optimization > How to view the DDL job?`
- Source Line Ranges: `407-452`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `execution-plan`, `statistics`, `count`, `concurrency`, `coprocessor-cache`, `ddl-jobs`, `admin-show-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0118_0ff91e5592`
- Source ID: `tidb-docs-8.1:faq/sql-faq.md#sql-optimization`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fdfbd8c6d82edd6a5897ffce990b228ffabe5edb5c6943c1833a1604c8d57c43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/sql-faq#sql-optimization
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/sql-faq.md

## Retrieval Guidance

- Use When: Use this chunk when looking up SQL optimization references for execution plans or statistics, tuning `select count(1)`, or inspecting running and historical DDL jobs with `ADMIN SHOW DDL` commands.
- Retrieval Keywords: Understand the Query Execution Plan, Introduction to Statistics, select count(1), tidb_distsql_scan_concurrency, default value is 10, improve it to 50, TiDB accesses TiKV in every query, Coprocessor Cache, Tune TiKV Thread Performance, Tune TiKV Memory Performance, ADMIN SHOW DDL, ADMIN SHOW DDL JOBS, ADMIN SHOW DDL JOBS QUERIES, RUNNING_JOBS, RowCount, ADD INDEX
- Follow-up Guidance: The content says `ADMIN SHOW DDL` shows the current DDL job progress including fields such as `RUNNING_JOBS` and `RowCount`, while `ADMIN SHOW DDL JOBS` and `ADMIN SHOW DDL JOBS QUERIES 'job_id'` show queued, recent completed, and original SQL information.
- Classification Note: This is classified as performance because it includes SQL optimization guidance for `count(1)` and references for execution plans and statistics, while also covering DDL job inspection commands.

## Official Source Content

## SQL optimization
### TiDB execution plan description

See [Understand the Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview).
### Statistics collection

See [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics).
### How to optimize `select count(1)`?

The `count(1)` statement counts the total number of rows in a table. Improving the degree of concurrency can significantly improve the speed. To modify the concurrency, refer to the [`tidb_distsql_scan_concurrency` document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_distsql_scan_concurrency). But it also depends on the CPU and I/O resources. TiDB accesses TiKV in every query. When the amount of data is small, all MySQL is in memory, and TiDB needs to conduct a network access.

Recommendations:

- Improve the hardware configuration. See [Software and Hardware Requirements](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements).
- Improve the concurrency. The default value is 10. You can improve it to 50 and have a try. But usually the improvement is 2-4 times of the default value.
- Test the `count` in the case of large amount of data.
- Optimize the TiKV configuration. See [Tune TiKV Thread Performance](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance) and [Tune TiKV Memory Performance](https://docs.pingcap.com/tidb/stable/tune-tikv-memory-performance).
- Enable the [Coprocessor Cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache).
### How to view the progress of the current DDL job?

You can use `ADMIN SHOW DDL` to view the progress of the current DDL job. The operation is as follows:

```sql
ADMIN SHOW DDL;
```

```
*************************** 1. row ***************************
  SCHEMA_VER: 140
       OWNER: 1a1c4174-0fcd-4ba0-add9-12d08c4077dc
RUNNING_JOBS: ID:121, Type:add index, State:running, SchemaState:write reorganization, SchemaID:1, TableID:118, RowCount:77312, ArgLen:0, start time: 2018-12-05 16:26:10.652 +0800 CST, Err:<nil>, ErrCount:0, SnapshotVersion:404749908941733890
     SELF_ID: 1a1c4174-0fcd-4ba0-add9-12d08c4077dc
```

From the above results, you can get that the `ADD INDEX` operation is currently being processed. You can also get from the `RowCount` field of the `RUNNING_JOBS` column that now the `ADD INDEX` operation has added 77312 rows of indexes.
### How to view the DDL job?

- `ADMIN SHOW DDL`: to view the running DDL job
- `ADMIN SHOW DDL JOBS`: to view all the results in the current DDL job queue (including tasks that are running and waiting to run) and the last ten results in the completed DDL job queue
- `ADMIN SHOW DDL JOBS QUERIES 'job_id' [, 'job_id'] ...`: to view the original SQL statement of the DDL task corresponding to the `job_id`; the `job_id` only searches the running DDL job and the last ten results in the DDL history job queue.
