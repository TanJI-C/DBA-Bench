# RC read analysis and small table cache tuning scenario

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-practices.md`
- Source Title: `Performance Tuning Practices for OLTP Scenarios`
- Source Heading Path: `Performance Tuning Practices for OLTP Scenarios > Scenario 6: Enable the `tidb_rc_read_check_ts` variable to reduce TSO requests > Performance analysis > Performance Overview dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 6: Enable the `tidb_rc_read_check_ts` variable to reduce TSO requests > Analysis conclusion | Performance Tuning Practices for OLTP Scenarios > Scenario 7: Use the small table cache | Performance Tuning Practices for OLTP Scenarios > Scenario 7: Use the small table cache > Application configuration | Performance Tuning Practices for OLTP Scenarios > Scenario 7: Use the small table cache > Performance analysis | Performance Tuning Practices for OLTP Scenarios > Scenario 7: Use the small table cache > Performance analysis > TiDB Dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 7: Use the small table cache > Performance analysis > Performance Overview dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 7: Use the small table cache > Analysis conclusion`
- Source Line Ranges: `327-409`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `dashboard`, `sql`
- Topic Tags: `oltp`, `rc-read`, `tso`, `plan-cache`, `small-table-cache`, `qps`, `latency`, `cpu`, `execute-phase`, `kv-reads`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0143_93028296cc`
- Source ID: `tidb-docs-8.1:performance-tuning-practices.md#performance-overview-dashboard`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ccb55ada8251005dbc54b964ad4e6327ba8c638da95bf1f1f0e9481bddd8318`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-practices#performance-overview-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-practices.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing OLTP performance changes after enabling `tidb_rc_read_check_ts` or using `alter table t1 cache;`, especially for shifts in `tso cmd`, `tso wait`, `execute`-phase time, KV read requests, QPS, and CPU or latency metrics shown in Performance Overview.
- Retrieval Keywords: tidb_rc_read_check_ts, set global tidb_rc_read_check_ts=on;, RC Read, small table cache, alter table t1 cache;, tso cmd, tso wait, avg pd tso wait duration, execute phase, Get, Cop, Prewrite, Commit, Queries Using Plan Cache OPS, StmtExecute, Performance Overview dashboard, TiDB Dashboard, avg QPS, avg query duration, avg execution duration
- Follow-up Guidance: The content also notes limits of small table caching: read-only table data might be too large to cache fully, and write operations require a default wait of 3 seconds so cache on all TiDB nodes is invalidated first.
- Classification Note: This is classified as performance content because it compares QPS, query latency, CPU utilization, `tso wait`, and SQL or KV execution breakdowns for RC Read and small table cache tuning in TiDB.

## Official Source Content

#### Performance Overview dashboard

After using RC read, QPS increases from 30.9k to 34.9k, and the `tso wait` time consumed per second decreases from 5.46 s to 456 ms.

![performance-overview-1-for-rc-read](/media/performance/j-6.png)

- Database Time by SQL Type: the `Select` statement type takes most of the time.
- Database Time by SQL Phase: the `execute` phase takes most of the time.
- SQL Execute Time Overview: `Get`, `Cop`, and `Prewrite` take most of the time.
- Execution plan cache is hit. The value of Queries Using Plan Cache OPS roughly equals `StmtExecute` per second.
- CPS By Type: only the `StmtExecute` command is used.
- avg QPS = 34.9k (from 30.9k to 34.9k)

The `tso cmd` per second drops from 28.3k to 2.7k.

![performance-overview-2-for-rc-read](/media/performance/j-6-cmd.png)

The average TiDB CPU increases to 603% (from 577% to 603%).

![performance-overview-3-for-rc-read](/media/performance/j-6-cpu.png)

The key latency metrics are as follows:

![performance-overview-4-for-rc-read](/media/performance/j-6-duration.png)

- avg query duration = 533μs (from 690μs to 533μs)
- avg parse duration = 13.4μs (from 13.5μs to 13.4μs )
- avg compile duration = 50.3μs (from 49.7μs to 50.3μs)
- avg execution duration = 466μs (from 623μs to 466μs)
- avg pd tso wait duration = 171μs (from 196μs to 171μs)
### Analysis conclusion

After enabling RC Read by `set global tidb_rc_read_check_ts=on;`, RC Read significantly reduces the times of `tso cmd`, thus reducing `tso wait` and average query duration, and improving QPS.

The bottlenecks of both current database time and latency are in the `execute` phase, in which the `Get` and `Cop` read requests take the highest percentage. Most of the tables in this workload are read-only or rarely modified, so you can use the small table caching feature supported since TiDB v6.0.0 to cache the data of these small tables and reduce the waiting time and resource consumption of KV read requests.
## Scenario 7: Use the small table cache
### Application configuration

Compared with Scenario 6, the application configuration remains the same. The only difference is that Scenario 7 uses SQL statements such as `alter table t1 cache;` to cache those read-only tables for the business.
### Performance analysis
#### TiDB Dashboard

The flame chart of the TiDB CPU does not have any significant changes.

![flame-graph-for-table-cache](/media/performance/7.2.png)
#### Performance Overview dashboard

The QPS increases from 34.9k to 40.9k, and the KV request types take the most time in the `execute` phase change to `Prewrite` and `Commit`. The database time consumed by `Get` per second decreases from 5.33 seconds to 1.75 seconds, and the database time consumed by `Cop` per second decreases from 3.87 seconds to 1.09 seconds.

![performance-overview-1-for-table-cache](/media/performance/j-7.png)

- Database Time by SQL Type: the `Select` statement type takes most of the time.
- Database Time by SQL Phase: the `execute` and `compile` phases take most of the time.
- SQL Execute Time Overview: `Prewrite`, `Commit`, and `Get` take most of the time.
- Execution plan cache is hit. The value of Queries Using Plan Cache OPS roughly equals `StmtExecute` per second.
- CPS By Type: only the `StmtExecute` command is used.
- avg QPS = 40.9k (from 34.9k to 40.9k)

The average TiDB CPU utilization drops from 603% to 478% and the average TiKV CPU utilization drops from 346% to 256%.

![performance-overview-2-for-table-cache](/media/performance/j-7-cpu.png)

The average query latency drops from 533 us to 313 us. The average `execute` latency drops from 466 us to 250 us.

![performance-overview-3-for-table-cache](/media/performance/j-7-duration.png)

- avg query duration = 313μs (from 533μs to 313μs)
- avg parse duration = 11.9μs (from 13.4μs to 11.9μs)
- avg compile duration = 47.7μs (from 50.3μs to 47.7μs)
- avg execution duration = 251μs (from 466μs to 251μs)
### Analysis conclusion

After caching all read-only tables, the `Execute Duration` drops significantly because all read-only tables are cached in TiDB and there is no need to query data in TiKV for those tables, so the query duration drops and the QPS increases.

This is an optimistic result because data of read-only tables in actual business might be too large for TiDB to cache them all. Another limitation is that although the small table caching feature supports write operations, the write operation requires a default wait of 3 seconds to ensure that the cache of all TiDB nodes is invalidated first, which might not be feasible to applications with strict latency requirements.
