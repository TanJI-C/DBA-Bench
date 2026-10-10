# Prepared statements, plan cache, and client-side prepared object caching

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-practices.md`
- Source Title: `Performance Tuning Practices for OLTP Scenarios`
- Source Heading Path: `Performance Tuning Practices for OLTP Scenarios > Scenario 3. Use the Prepared Statement interface with execution plan caching not enabled > Analysis conclusion | Performance Tuning Practices for OLTP Scenarios > Scenario 4. Use the Prepared Statement interface and enable execution plan caching | Performance Tuning Practices for OLTP Scenarios > Scenario 4. Use the Prepared Statement interface and enable execution plan caching > Application configuration | Performance Tuning Practices for OLTP Scenarios > Scenario 4. Use the Prepared Statement interface and enable execution plan caching > Performance analysis | Performance Tuning Practices for OLTP Scenarios > Scenario 4. Use the Prepared Statement interface and enable execution plan caching > Performance analysis > TiDB Dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 4. Use the Prepared Statement interface and enable execution plan caching > Performance analysis > Performance Overview dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 4. Use the Prepared Statement interface and enable execution plan caching > Analysis conclusion | Performance Tuning Practices for OLTP Scenarios > Scenario 5. Cache prepared objects on the client side | Performance Tuning Practices for OLTP Scenarios > Scenario 5. Cache prepared objects on the client side > Application configuration | Performance Tuning Practices for OLTP Scenarios > Scenario 5. Cache prepared objects on the client side > Performance analysis | Performance Tuning Practices for OLTP Scenarios > Scenario 5. Cache prepared objects on the client side > Performance analysis > TiDB Dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 5. Cache prepared objects on the client side > Performance analysis > Performance Overview dashboard | Performance Tuning Practices for OLTP Scenarios > Scenario 5. Cache prepared objects on the client side > Analysis conclusion`
- Source Line Ranges: `187-310`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `dashboard`, `pd`, `tikv`
- Topic Tags: `prepared-statements`, `plan-cache`, `jdbc`, `qps`, `latency`, `cpu`, `tso`, `dashboard`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0141_9224350d78`
- Source ID: `tidb-docs-8.1:performance-tuning-practices.md#analysis-conclusion`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8378e020264690577ae9f85a6eaa896af2850b7523a808c006128ce5fd5e4531`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-practices#analysis-conclusion
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-practices.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB OLTP performance tuning details about prepared statements, execution plan cache, JDBC prepared statement caching, CPS By Type changes, compile time reduction, and TSO wait behavior across Scenarios 3 to 5.
- Retrieval Keywords: tidb_ignore_prepared_cache_close_stmt, prepared-plan-cache: {enabled: true}, set global tidb_ignore_prepared_cache_close_stmt=on;, Prepared Statement interface, StmtPrepare, StmtExecute, StmtClose, Queries Using Plan Cache OPS, CompileExecutePreparedStmt, Optimize, Prepare command, cachePrepStmts=true, prepStmtCacheSize=1000, prepStmtCacheSqlLimit=20480, useServerPrepStmts=true, useConfigs=maxPerformance, CPS By Type, general SQL type, Database Time by SQL Type, Database Time by SQL Phase, SQL Execute Time Overview, tso wait, tidb_rc_read_check_ts, set global tidb_rc_read_check_ts=on;, rc read, read committed isolation level
- Follow-up Guidance: The chunk also points to reducing TSO requests in read committed mode with `set global tidb_rc_read_check_ts=on;` and explains the `rc read` behavior introduced in TiDB v6.0.
- Classification Note: This is classified as performance for TiDB because the content analyzes QPS, CPU utilization, query and compile duration, plan cache hits, JDBC prepared object caching, and PD TSO wait effects in self-managed OLTP scenarios.

## Official Source Content

### Analysis conclusion

Unlike Scenario 2, the application in Scenario 3 enables the Prepared Statement interface but still fails to hit the cache. In addition, Scenario 2 has only one CPS By Type command type (`Query`), while Scenario 3 has three more command types (`StmtPrepare`, `StmtExecute`, `StmtClose`). Compared with Scenario 2, Scenario 3 has two more network round-trip delays.

- Analysis for the decrease in QPS: From the **CPS By Type** pane, you can see that Scenario 2 has only one CPS By Type command type (`Query`), while Scenario 3 has three more command types (`StmtPrepare`, `StmtExecute`, `StmtClose`). `StmtPrepare` and `StmtClose` are non-conventional commands that are not counted by QPS, so QPS is reduced. The non-conventional commands `StmtPrepare` and `StmtClose` are counted in the `general` SQL type, so `general` time is displayed in the database overview of Scenario 3, and it accounts for more than a quarter of the database time.
- Analysis for the significant decrease in average query duration: for the `StmtPrepare` and `StmtClose` command types newly added in Scenario 3, their query duration is calculated separately in the TiDB internal processing. TiDB executes these two types of commands very quickly, so the average query duration is significantly reduced.

Although Scenario 3 uses the Prepared Statement interface, the execution plan cache is still not hit, because many application frameworks call the `StmtClose` method after `StmtExecute` to prevent memory leaks. Starting from v6.0.0, you can set the global variable `tidb_ignore_prepared_cache_close_stmt=on;`. After that, TiDB will not clear the cached execution plans even if the application calls the `StmtClose` method, so the next SQL execution can reuse the existing execution plan and avoid compiling the execution plan repeatedly.
## Scenario 4. Use the Prepared Statement interface and enable execution plan caching
### Application configuration

The application configuration remains the same as that of Scenario 3. To resolve the issue of not hitting the cache even if the application triggers `StmtClose`, the following parameters are configured.

- Set the TiDB global variable `set global tidb_ignore_prepared_cache_close_stmt=on;` (introduced since TiDB v6.0.0, `off` by default).
- Set the TiDB configuration item `prepared-plan-cache: {enabled: true}` to enable the plan cache feature.
### Performance analysis
#### TiDB Dashboard

From the flame chart of the TiDB CPU usage, you can see that `CompileExecutePreparedStmt` and `Optimize` have no significant CPU consumption. 25% of the CPU is consumed by the `Prepare` command, which contains parsing-related functions of Prepare such as `PlanBuilder` and `parseSQL`.

PreparseStmt cpu = 25% cpu time = 12.75s

![flame-graph-for-3-commands](/media/performance/4.2.png)
#### Performance Overview dashboard

In the Performance Overview dashboard, the most significant change is the average time of the `compile` phase, which is reduced from 8.95 seconds per second in Scenario 3 to 1.18 seconds per second. The number of queries using the execution plan cache is roughly equal to the value of `StmtExecute`. With the increase in QPS, the database time consumed by `Select` statements per second decreases, and the database time consumed by `general` statements per second type increases.

![performance-overview-1-for-3-commands](/media/performance/j-4.png)

- Database Time by SQL Type: the `Select` statement type takes the most time.
- Database Time by SQL Phase: the `execute` phase takes most of the time.
- SQL Execute Time Overview: `tso wait`, `Get`, and `Cop` take most of the time.
- Execution plan cache is hit. The value of Queries Using Plan Cache OPS roughly equals `StmtExecute` per second.
- CPS By Type: 3 types of commands (same as Scenario 3)
- Compared with scenario 3, the time consumed by `general` statements is longer because the QPS is increased.
- avg QPS = 22.1k (from 19.7k to 22.1k)

The average TiDB CPU utilization drops from 936% to 827%.

![performance-overview-2-for-3-commands](/media/performance/4.4.png)

The average `compile` time drops significantly, from 374 us to 53.3 us. Because the QPS increases, the average `execute` time increases too.

![performance-overview-3-for-3-commands](/media/performance/4.5.png)

- avg query duration = 426μs (from 528μs to 426μs)
- avg parse duration = 12.3μs (from 14.8μs to 12.3μs)
- avg compile duration = 53.3μs (from 374μs to 53.3μs)
- avg execution duration = 699μs (from 649μs to 699us)
### Analysis conclusion

Compared with Scenario 3, Scenario 4 also uses 3 command types. The difference is that Scenario 4 hits the execution plan cache, which reduces compile duration greatly, reduces the query duration, and improves QPS.

Because the `StmtPrepare` and `StmtClose` commands consume significant database time and increase the number of interactions between the application and TiDB each time the application executes a SQL statement. The next scenario will further tune the performance by eliminating the calls of these two commands through JDBC configurations.
## Scenario 5. Cache prepared objects on the client side
### Application configuration

Compared with Scenario 4, 3 new JDBC parameters `cachePrepStmts=true&prepStmtCacheSize=1000&prepStmtCacheSqlLimit=20480` are configured, as explained below.

- `cachePrepStmts = true`: caches Prepared Statement objects on the client side, which eliminates the calls of StmtPrepare and StmtClose.
- `prepStmtCacheSize`: the value must be greater than 0.
- `prepStmtCacheSqlLimit`: the value must be greater than the length of the SQL text.

In Scenario 5, the complete JDBC configurations are as follows.

```
useServerPrepStmts=true&cachePrepStmts=true&prepStmtCacheSize=1000&prepStmtCacheSqlLimit=20480&useConfigs=maxPerformance
```
### Performance analysis
#### TiDB Dashboard

From the following flame chart of TiDB, you can see that the high CPU consumption of the `Prepare` command is no longer present.

- ExecutePreparedStmt cpu = 22% cpu time = 8.4s

![flame-graph-for-1-command](/media/performance/5.1.1.png)
#### Performance Overview dashboard

In the Performance Overview dashboard, the most notable changes are that the three Stmt command types in the **CPS By Type** pane drop to one type, the `general` statement type in the **Database Time by SQL Type** pane is disappeared, and the QPS in the **QPS** pane increases to 30.9k.

![performance-overview-for-1-command](/media/performance/j-5.png)

- Database Time by SQL Type: the `Select` statement type takes most of the time and the `general` statement type disappears.
- Database Time by SQL Phase: the `execute` phase takes most of the time.
- SQL Execute Time Overview: `tso wait`, `Get`, and `Cop` take most of the time.
- Execution plan cache is hit. The value of Queries Using Plan Cache OPS roughly equals `StmtExecute` per second.
- CPS By Type: only the `StmtExecute` command is used.
- avg QPS = 30.9k (from 22.1k to 30.9k)

The average TiDB CPU utilization drops from 827% to 577%. As the QPS increases, the average TiKV CPU utilization increases to 313%.

![performance-overview-for-2-command](/media/performance/j-5-cpu.png)

The key latency metrics are as follows:

![performance-overview-for-3-command](/media/performance/j-5-duration.png)

- avg query duration = 690μs (from 426μs to 690μs)
- avg parse duration = 13.5μs (from 12.3μs to 13.5μs )
- avg compile duration = 49.7μs (from 53.3μs to 49.7μs)
- avg execution duration = 623μs (from 699us to 623μs)
- avg pd tso wait duration = 196μs (from 224μs to 196μs)
- connection idle duration avg-in-txn = 608μs (from 250μs to 608μs)
### Analysis conclusion

- Compared with Scenario 4, the **CPS By Type** pane in Scenario 5 has the `StmtExecute` command only, which avoids two network round trips and increases the overall system QPS.
- In the case of QPS increase, the latency decreases in terms of parse duration, compile duration, and execution duration, but the query duration increases instead. This is because TiDB processes `StmtPrepare` and `StmtClose` very quickly, and eliminating these two command types increases the average query duration.
- In Database Time by SQL Phase, `execute` takes the most time and is close to the database time. While in SQL Execute Time Overview, `tso wait` takes most of the time, and more than a quarter of `execute` time is taken to wait for TSO.
- The total `tso wait` time per second is 5.46s. The average `tso wait` time is 196 us, and the number of `tso cmd` times per second is 28k, which is very close to the QPS of 30.9k. This is because according to the implementation of the `read committed` isolation level in TiDB, every SQL statement in a transaction needs to request TSO from PD.

TiDB v6.0 provides `rc read`, which optimizes the `read committed` isolation level by reducing `tso cmd`. This feature is controlled by the global variable `set global tidb_rc_read_check_ts=on;`. When this variable is enabled, the default behavior of TiDB acts the same as the `repeatable-read` isolation level, at which only `start-ts` and `commit-ts` need to be obtained from the PD. The statements in a transaction use the `start-ts` to read data from TiKV first. If the data read from TiKV is earlier than `start-ts`, the data is returned directly. If the data read from TiKV is later than `start-ts`, the data is discarded. TiDB requests TSO from PD, and then retries the read. The `for update ts` of subsequent statements uses the latest PD TSO.
