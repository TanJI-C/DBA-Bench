# v6.0.0 improvements across TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > Improvements`
- Source Line Ranges: `561-621`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `dashboard`, `tiflash`, `ticdc`
- Topic Tags: `improvements`, `sql`, `mpp`, `partition-pruning`, `function-pushdown`, `observability`, `performance`, `dynamic-configuration`, `rawkv`, `raftstore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0291_55e4cd9acb`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#improvements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7707f9f6f2669c736fe5f6de2944aecd322205a653c127627f7c65b2d5eb7d5f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for a summary of TiDB 6.0.0 improvements or for specific new SQL, TiFlash pushdown, observability, MPP, partition pruning, TiKV dynamic configuration, RawKV V2, or Raftstore-related enhancements.
- Retrieval Keywords: TiDB 6.0.0 improvements, FLASHBACK, RECOVER, performance overview dashboard, LOAD DATA LOCAL INFILE REPLACE, partition pruning IN expression Range partition tables, MPP aggregation queries Exchange, ADMIN SHOW DDL JOBS CREATE_TIME, CHARSET(), baseline capturing blocklist usernames, baseline capturing blocklist wildcards, SHOW TABLE STATUS time_zone, DAYNAME() MONTHNAME() pushdown to TiFlash, REGEXP pushdown to TiFlash, DAYOFMONTH() LAST_DAY() pushdown to TiFlash, DAYOFWEEK() DAYOFYEAR() pushdown to TiFlash, IS_TRUE IS_FALSE IS_TRUE_WITH_NULL pushdown to TiFlash, GREATEST LEAST pushdown to TiFlash, UnionScan operator, PointGet _tidb_rowid, EXPLAIN original partition name, RANGE COLUMNS dynamic pruning, system variable set to NULL, Broadcast Join non-MPP mode, MPP plans on partitioned tables, common table expressions CTE predicate pushdown, Statement Summary, Capture Plan Baselines, raftstore.raft-max-inflight-msgs, EXTRA_PHYSICAL_TABLE_ID_COL_ID, RawKV API V2, raw_get raw_scan, storage.scheduler-worker-pool-size, readpool.unified.max-thread-count, rocksdb.enable-multibatch-write
- Follow-up Guidance: The chunk groups improvements by component and includes TiDB items such as `LOAD DATA LOCAL INFILE` with `REPLACE`, `ADMIN SHOW DDL JOBS` `CREATE_TIME`, multiple TiFlash function pushdowns, and TiKV items such as dynamic modification of `raftstore.raft-max-inflight-msgs`, `raftstore.raft-max-size-per-msg`, `storage.scheduler-worker-pool-size`, and `readpool.unified.max-thread-count`.
- Classification Note: This is a release improvements chunk because it enumerates new capabilities, optimizations, and dynamic configuration support added in TiDB 6.0.0 across TiDB and TiKV.

## Official Source Content

## Improvements

+ TiDB

    - Clear the placement rule settings of a table automatically after restoring the table using the `FLASHBACK` or `RECOVER` statement  [#31668](https://github.com/pingcap/tidb/issues/31668)
    - Add a performance overview dashboard to show core performance metrics on typical critical paths, making metrics analysis on TiDB easier [#31676](https://github.com/pingcap/tidb/issues/31676)
    - Support using the `REPLACE` keyword in the `LOAD DATA LOCAL INFILE` statement [#24515](https://github.com/pingcap/tidb/issues/24515)
    - Support partition pruning for the built-in `IN` expression in Range partition tables [#26739](https://github.com/pingcap/tidb/issues/26739)
    - Improve query efficiency by eliminating potentially redundant Exchange operations in MPP aggregation queries [#31762](https://github.com/pingcap/tidb/issues/31762)
    - Improve compatibility with MySQL by allowing duplicate partition names in the `TRUNCATE PARTITION` and `DROP PARTITION` statements [#31681](https://github.com/pingcap/tidb/issues/31681)
    - Support showing the `CREATE_TIME` information in the results of the `ADMIN SHOW DDL JOBS` statement [#23494](https://github.com/pingcap/tidb/issues/23494)
    - Support a new built-in function `CHARSET()` [#3931](https://github.com/pingcap/tidb/issues/3931)
    - Support filtering a baseline capturing blocklist by usernames [#32558](https://github.com/pingcap/tidb/issues/32558)
    - Support using wildcards in a baseline capturing blocklist [#32714](https://github.com/pingcap/tidb/issues/32714)
    - Optimize the results of the `ADMIN SHOW DDL JOBS` and `SHOW TABLE STATUS` statements by displaying the time according to the current `time_zone` [#26642](https://github.com/pingcap/tidb/issues/26642)
    - Support pushing down the `DAYNAME()` and `MONTHNAME()` functions to TiFlash [#32594](https://github.com/pingcap/tidb/issues/32594)
    - Support pushing down the `REGEXP` function to TiFlash [#32637](https://github.com/pingcap/tidb/issues/32637)
    - Support pushing down the `DAYOFMONTH()` and `LAST_DAY()` functions to TiFlash [#33012](https://github.com/pingcap/tidb/issues/33012)
    - Support pushing down the `DAYOFWEEK()` and `DAYOFYEAR()` functions to TiFlash [#33130](https://github.com/pingcap/tidb/issues/33130)
    - Support pushing down the `IS_TRUE`, `IS_FALSE`, and `IS_TRUE_WITH_NULL` functions to TiFlash [#33047](https://github.com/pingcap/tidb/issues/33047)
    - Support pushing down the `GREATEST` and `LEAST` functions to TiFlash [#32787](https://github.com/pingcap/tidb/issues/32787)
    - Support tracking the execution of the `UnionScan` operator [#32631](https://github.com/pingcap/tidb/issues/32631)
    - Support using the PointGet plan for queries that read the `_tidb_rowid` column [#31543](https://github.com/pingcap/tidb/issues/31543)
    - Support showing the original partition name in the output of the `EXPLAIN` statement without converting the name to lowercase [#32719](https://github.com/pingcap/tidb/issues/32719)
    - Enable partition pruning for RANGE COLUMNS partitionings on IN conditions and string type columns [#32626](https://github.com/pingcap/tidb/issues/32626)
    - Return an error message when a system variable is set to NULL [#32850](https://github.com/pingcap/tidb/issues/32850)
    - Remove Broadcast Join from the non-MPP mode [#31465](https://github.com/pingcap/tidb/issues/31465)
    - Support executing MPP plans on partitioned tables in dynamic pruning mode [#32347](https://github.com/pingcap/tidb/issues/32347)
    - Support pushing down predicates for common table expressions (CTEs) [#28163](https://github.com/pingcap/tidb/issues/28163)
    - Simplify the configurations of `Statement Summary` and `Capture Plan Baselines` to be available on a global basis only [#30557](https://github.com/pingcap/tidb/issues/30557)
    - Update gopsutil to v3.21.12 to address alarms reported when building binary on macOS 12 [#31607](https://github.com/pingcap/tidb/issues/31607)

+ TiKV

    - Improve the sampling accuracy of the Raftstore for batches with many key ranges [#12327](https://github.com/tikv/tikv/issues/12327)
    - Add the correct "Content-Type" for `debug/pprof/profile` to make the Profile more easily identified [#11521](https://github.com/tikv/tikv/issues/11521)
    - Renew the lease time of the leader infinitely when the Raftstore has heartbeats or handles read requests, which helps reduce latency jitter [#11579](https://github.com/tikv/tikv/issues/11579)
    - Choose the store with the least cost when switching the leader, which helps improve performance stability [#10602](https://github.com/tikv/tikv/issues/10602)
    - Fetch Raft logs asynchronously to reduce the performance jitter caused by blocking the Raftstore [#11320](https://github.com/tikv/tikv/issues/11320)
    - Support the `QUARTER` function in vector calculation [#5751](https://github.com/tikv/tikv/issues/5751)
    - Support pushing down the `BIT` data type to TiKV [#30738](https://github.com/pingcap/tidb/issues/30738)
    - Support pushing down the `MOD` function and the `SYSDATE` function to TiKV [#11916](https://github.com/tikv/tikv/issues/11916)
    - Reduce the TiCDC recovery time by reducing the number of the Regions that require the Resolve Locks step [#11993](https://github.com/tikv/tikv/issues/11993)
    - Support dynamically modifying `raftstore.raft-max-inflight-msgs` [#11865](https://github.com/tikv/tikv/issues/11865)
    - Support `EXTRA_PHYSICAL_TABLE_ID_COL_ID` to enable dynamic pruning mode [#11888](https://github.com/tikv/tikv/issues/11888)
    - Support calculation in buckets [#11759](https://github.com/tikv/tikv/issues/11759)
    - Encode the keys of RawKV API V2 as `user-key` + `memcomparable-padding` + `timestamp` [#11965](https://github.com/tikv/tikv/issues/11965)
    - Encode the values of RawKV API V2 as `user-value` + `ttl` + `ValueMeta` and encode `delete` in `ValueMeta` [#11965](https://github.com/tikv/tikv/issues/11965)
    - Support dynamically modifying `raftstore.raft-max-size-per-msg` [#12017](https://github.com/tikv/tikv/issues/12017)
    - Support monitoring multi-k8s in Grafana [#12014](https://github.com/tikv/tikv/issues/12014)
    - Transfer the leadership to CDC observer to reduce latency jitter [#12111](https://github.com/tikv/tikv/issues/12111)
    - Support dynamically modifying `raftstore.apply_max_batch_size` and `raftstore.store_max_batch_size` [#11982](https://github.com/tikv/tikv/issues/11982)
    - RawKV V2 returns the latest version upon receiving the `raw_get` or `raw_scan` request [#11965](https://github.com/tikv/tikv/issues/11965)
    - Support the RCCheckTS consistency reads [#12097](https://github.com/tikv/tikv/issues/12097)
    - Support dynamically modifying `storage.scheduler-worker-pool-size`(the thread count of the Scheduler pool) [#12067](https://github.com/tikv/tikv/issues/12067)
    - Control the use of CPU and bandwidth by using the global foreground flow controller to improve the performance stability of TiKV [#11855](https://github.com/tikv/tikv/issues/11855)
    - Support dynamically modifying `readpool.unified.max-thread-count` (the thread count of the UnifyReadPool) [#11781](https://github.com/tikv/tikv/issues/11781)
    - Use the TiKV internal pipeline to replace the RocksDB pipeline and deprecate the `rocksdb.enable-multibatch-write` parameter [#12059](https://github.com/tikv/tikv/issues/12059)

+ PD
