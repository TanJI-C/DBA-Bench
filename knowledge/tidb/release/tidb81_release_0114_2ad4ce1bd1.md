# TiDB 3.0.2 fixes for server, DDL, and monitor

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.2.md`
- Source Title: `TiDB 3.0.2 Release Notes`
- Source Heading Path: `TiDB 3.0.2 Release Notes > TiDB`
- Source Line Ranges: `54-96`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `sql`, `shared`
- Topic Tags: `release-notes`, `server`, `ddl`, `monitoring`, `http-api`, `region-cache`, `pessimistic-locking`, `load-data`, `show-create-user`, `trace`, `admin-check-table`, `split-table`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0114_2ad4ce1bd1`
- Source ID: `tidb-docs-8.1:releases/release-3.0.2.md#tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6351d9676b1f3ffe248fadd43d686c201db35eb29a2550ff320344d5ba9666ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.2#tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.2 release-note fixes and additions for server, DDL, or monitor behavior involving SQL compatibility, HTTP APIs, Region cache, pessimistic locking, tracing, split table output, or monitoring metrics.
- Retrieval Keywords: TiDB 3.0.2, LOAD DATA TIMESTAMP missing field current timestamp, SHOW CREATE USER CURRENT_USER privilege check, INFORMATION_SCHEMA.TIDB_HOT_REGIONS REGION_ID, http://{TiDBIP}:10080/regions/hot, mvcc/key API Region ID, pessimistic locking TTL 40 seconds 120 seconds, SendRequest connect to another peer, Region cache invalid store same address, Scatter Table API Range key, ALTER TABLE MODIFY COLUMN character set collation, TRACE subquery details, ADMIN CHECK TABLE execution time, SPLIT TABLE REGIONS INDEX TOTAL_SPLIT_REGION SCATTER_FINISH_RATIO, TiKVTxnCmdCounter, BindUsageCounter, BindTotalGauge, BindMemoryUsage
- Follow-up Guidance: The chunk also lists specific SQL statements, HTTP APIs, information schema objects, and monitoring metric names changed in TiDB 3.0.2.
- Classification Note: This is classified as a TiDB release-notes chunk because the official content is the TiDB section of the 3.0.2 release notes covering Server, DDL, and Monitor fixes and additions.

## Official Source Content

- Fix the issue that the result is incompatible with MySQL when an SQL statement involves computing the current time and the value is fetched multiple times; use the same value when fetching the current time for the same SQL statement [#11394](https://github.com/pingcap/tidb/pull/11394)
    - Fix the issue that `Close` is not called for `ChildExecutor` when the `Close` of `baseExecutor` reports an error. This issue might lead to Goroutine leaks when the `KILL` statements do not take effect and `ChildExecutor` is not closed [#11576](https://github.com/pingcap/tidb/pull/11576)
+ Server
    - Fix the issue that the auto-added value is 0 instead of the current timestamp when `LOAD DATA` processes the missing `TIMESTAMP` field in the CSV file [#11250](https://github.com/pingcap/tidb/pull/11250)
    - Fix issues that the `SHOW CREATE USER` statement does not correctly check related privileges, and `USER` and `HOST` returned by `SHOW CREATE USER CURRENT_USER()` might be wrong [#11229](https://github.com/pingcap/tidb/pull/11229)
    - Fix the issue that the returned result might be wrong when `executeBatch` is used in JDBC [#11290](https://github.com/pingcap/tidb/pull/11290)
    - Reduce printing the log information of the streaming client when changing the TiKV server's port [#11370](https://github.com/pingcap/tidb/pull/11370)
    - Optimize the logic of reconnecting the streaming client to the TiKV server so that the streaming client will not be blocked for a long time [#11372](https://github.com/pingcap/tidb/pull/11372)
    - Add `REGION_ID` in `INFORMATION_SCHEMA.TIDB_HOT_REGIONS` [#11350](https://github.com/pingcap/tidb/pull/11350)
    - Cancel the timeout duration of obtaining Region information from the PD API to ensure that obtaining Region information will not end in a failure when TiDB API `http://{TiDBIP}:10080/regions/hot` is called due to PD timeout when the number of Regions is large [#11383](https://github.com/pingcap/tidb/pull/11383)
    - Fix the issue that Region related requests do not return partitioned table-related Regions in the HTTP API [#11466](https://github.com/pingcap/tidb/pull/11466)
    - Make the following changes to reduce the probability of locking timeout caused by slow operations when the user manually validates pessimistic locking [#11521](https://github.com/pingcap/tidb/pull/11521):
        - Increase the default TTL of pessimistic locking from 30 seconds to 40 seconds
        - Increase the maximum TTL from 60 seconds to 120 seconds
        - Calculate the pessimistic locking duration from the first `LockKeys` request
    - Change the `SendRequest` function logic in the TiKV client: try to immediately connect to another peer instead of keeping waiting when the connect cannot be built [#11531](https://github.com/pingcap/tidb/pull/11531)
    - Optimize the Region cache: label the removed store as invalid when a store is moved while another store goes online with a same address, to update the store information in the cache as soon as possible [#11567](https://github.com/pingcap/tidb/pull/11567)
    - Add the Region ID to the result returned by the `http://{TiDB_ADDRESS:TIDB_IP}/mvcc/key/{db}/{table}/{handle}` API [#11557](https://github.com/pingcap/tidb/pull/11557)
    - Fix the issue that Scatter Table does not work caused by the Scatter Table API not escaping the Range key [#11298](https://github.com/pingcap/tidb/pull/11298)
    - Optimize the Region cache: label the store where the Region exists as invalid when the correspondent store is inaccessible, to avoid reduced query performance caused by accessing this store [#11498](https://github.com/pingcap/tidb/pull/11498)
    - Fix the error that the table schema can still be obtained through the HTTP API after dropping the database with the same name multiple times [#11585](https://github.com/pingcap/tidb/pull/11585)
+ DDL
    - Fix the issue that an error occurs when a non-string column with a zero length is being indexed [#11214](https://github.com/pingcap/tidb/pull/11214)
    - Disallow modifying the columns with foreign key constraints and full-text indexes (Note: TiDB still supports foreign key constraints and full-text indexes in syntax) [#11274](https://github.com/pingcap/tidb/pull/11274)
    - Fix the issue that the index offset of the column might be wrong because the position changed by the `ALTER TABLE` statement and the default value of the column are used concurrently [#11346](https://github.com/pingcap/tidb/pull/11346)
    - Fix two issues that occur when parsing JSON files:
        - `int64` is used as the intermediate parsing result of `uint64` in `ConvertJSONToFloat`, which leads to the precision overflow error [#11433](https://github.com/pingcap/tidb/pull/11433)
        - `int64` is used as the intermediate parsing result of `uint64` in `ConvertJSONToInt`, which leads to the precision overflow error [#11551](https://github.com/pingcap/tidb/pull/11551)
    - Disallow dropping indexes on the auto-increment column to avoid that the auto-increment column might get an incorrect result [#11399](https://github.com/pingcap/tidb/pull/11399)
    - Fix the following issues [#11492](https://github.com/pingcap/tidb/pull/11492):
        - The character set and the collation of the column are not consistent when explicitly specifying the collation but not the character set
        - The error is not correctly reported when there is a conflict between the character set and the collation that are specified by `ALTER TABLE … MODIFY COLUMN`
        - Incompatibility with MySQL when using `ALTER TABLE … MODIFY COLUMN` to specify character sets and collations multiple times
    - Add the trace details of the subquery to the result of the `TRACE` query [#11458](https://github.com/pingcap/tidb/pull/11458)
    - Optimize the performance of executing `ADMIN CHECK TABLE` and greatly reduce its execution time [#11547](https://github.com/pingcap/tidb/pull/11547)
    - Add the result returned by `SPLIT TABLE … REGIONS/INDEX` and make `TOTAL_SPLIT_REGION` and `SCATTER_FINISH_RATIO` display the number of Regions that have been split successfully before timeout in the result [#11484](https://github.com/pingcap/tidb/pull/11484)
    - Fix the issue that the precision displayed by statements like `SHOW CREATE TABLE` is incomplete when `ON UPDATE CURRENT_TIMESTAMP` is the column attribute and the float precision is specified [#11591](https://github.com/pingcap/tidb/pull/11591)
    - Fix the issue that the index result of the column cannot be correctly calculated when the expression of a virtual generated column contains another virtual generated column [#11475](https://github.com/pingcap/tidb/pull/11475)
    - Fix the issue that the minus sign cannot be added after `VALUE LESS THAN` in the `ALTER TABLE … ADD PARTITION …` statement [#11581](https://github.com/pingcap/tidb/pull/11581)
+ Monitor
    - Fix the issue that data is not collected and reported because the `TiKVTxnCmdCounter` monitoring metric is not registered [#11316](https://github.com/pingcap/tidb/pull/11316)
    - Add the `BindUsageCounter`, `BindTotalGauge` and `BindMemoryUsage` monitoring metrics for the Bind Info [#11467](https://github.com/pingcap/tidb/pull/11467)
