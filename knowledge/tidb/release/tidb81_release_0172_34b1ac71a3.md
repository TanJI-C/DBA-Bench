# 4.0.14 bug fixes across TiDB, TiKV, PD, Dashboard, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.14.md`
- Source Title: `TiDB 4.0.14 Release Notes`
- Source Heading Path: `TiDB 4.0.14 Release Notes > Bug fixes`
- Source Line Ranges: `80-167`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `br`, `lightning`, `dumpling`, `ticdc`
- Topic Tags: `bug fixes`, `sql execution`, `statistics`, `panic`, `memory usage`, `region split`, `scheduler`, `ui`, `backup restore`, `import export`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0172_34b1ac71a3`
- Source ID: `tidb-docs-8.1:releases/release-4.0.14.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc70e8c16126a17eaf4a1ccb95bdd88b1505a5a5773bb3e73ebac4d2aa33c1b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.14#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.14.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 4.0.14 release-note information about bug fixes across TiDB, TiKV, PD, TiDB Dashboard, TiFlash, BR, TiDB Lightning, Dumpling, or TiCDC for issues such as wrong query results, panic, memory leak, Region split, scheduler behavior, UI errors, restore/import failures, or changefeed problems.
- Retrieval Keywords: TiDB 4.0.14 Bug fixes, release-4.0.14, TiDB bug fixes, TiKV bug fixes, PD bug fixes, TiDB Dashboard bug fixes, TiFlash bug fixes, BR bug fixes, TiDB Lightning bug fixes, Dumpling S3 ListBucket permission, TiCDC bug fixes, SELECT ... FOR UPDATE panic join partitioned table, cached prepared plan point get, LOAD DATA non-utf8 data, TIKV_REGION_PEERS DOWN status, select into outfile YEAR no result, NULL in UNION subquery wrong result, projection operator panic, Region split might panic and corrupt the metadata, Region heartbeats prevent splitting large Regions, apply wait duration metric, Missing Blob delete_files_in_range Titan, scheduler might reappear after executing the delete operation, PD Leader re-election is slow when there are many stores, Profiling UI cannot profile all TiDB instances, Statements UI Plan Count, Slow Query unknown field error after cluster upgrade, data restore from the mysql schema might fail, Lightning EOF error large CSV files, DECIMAL type data in Parquet files, changefeed cannot be created when start TS is less than current TS minus GC TTL
- Follow-up Guidance: The chunk groups the fixes by component and names the exact statements, tables, functions, metrics, errors, and operational conditions addressed in TiDB 4.0.14.
- Classification Note: This is classified as a release chunk because the official content is the Bug fixes section of the TiDB 4.0.14 Release Notes covering multiple components.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that the `SELECT` result is incompatible with MySQL when joining a subquery with a `WHERE` clause evaluated to `false` [#24865](https://github.com/pingcap/tidb/issues/24865)
    - Fix the calculation error of the `ifnull` function that occurs when the argument is the `ENUM` or `SET` type [#24944](https://github.com/pingcap/tidb/issues/24944)
    - Fix the wrong aggregate pruning in some cases [#25202](https://github.com/pingcap/tidb/issues/25202)
    - Fix the incorrect result of the merge join operation that might occur when the column is the `SET` type [#25669](https://github.com/pingcap/tidb/issues/25669)
    - Fix the issue that TiDB returns wrong results for cartesian join [#25591](https://github.com/pingcap/tidb/issues/25591)
    - Fix the panic issue that occurs when `SELECT ... FOR UPDATE` works on a join operation and the join uses a partitioned table [#20028](https://github.com/pingcap/tidb/issues/20028)
    - Fix the issue that the cached `prepared` plan is incorrectly used for `point get` [#24741](https://github.com/pingcap/tidb/issues/24741)
    - Fix the issue that the `LOAD DATA` statement can abnormally import non-utf8 data [#25979](https://github.com/pingcap/tidb/issues/25979)
    - Fix a potential memory leak issue that occurs when accessing the statistics via an HTTP API [#24650](https://github.com/pingcap/tidb/pull/24650)
    - Fix a security issue that occurs when executing the `ALTER USER` statement [#25225](https://github.com/pingcap/tidb/issues/25225)
    - Fix a bug that the `TIKV_REGION_PEERS` table cannot correctly handle the `DOWN` status [#24879](https://github.com/pingcap/tidb/issues/24879)
    - Fix the issue that invalid strings are not truncated when parsing `DateTime` [#22231](https://github.com/pingcap/tidb/issues/22231)
    - Fix the issue that the `select into outfile` statement might have no result when the column type is `YEAR` [#22159](https://github.com/pingcap/tidb/issues/22159)
    - Fix the issue that the query result might be wrong when `NULL` is in the `UNION` subquery [#26532](https://github.com/pingcap/tidb/issues/26532)
    - Fix the issue that the projection operator in execution might cause panic in some cases [#26534](https://github.com/pingcap/tidb/pull/26534)

+ TiKV

    - Fix the issue that the duration calculation might panic on certain platforms [#related-issue](https://github.com/rust-lang/rust/issues/86470#issuecomment-877557654)
    - Fix the wrong function that casts `DOUBLE` to `DOUBLE` [#25200](https://github.com/pingcap/tidb/issues/25200)
    - Fix the issue that the panic log might be lost when using the async logger [#8998](https://github.com/tikv/tikv/issues/8998)
    - Fix the panic issue that occurs when building a snapshot twice if encryption is enabled [#9786](https://github.com/tikv/tikv/issues/9786) [#10407](https://github.com/tikv/tikv/issues/10407)
    - Fix the wrong arguments type of the `json_unquote()` function in the coprocessor [#10176](https://github.com/tikv/tikv/issues/10176)
    - Fix the issues of suspicious warnings during shutdown and the non-deterministic response from Raftstore [#10353](https://github.com/tikv/tikv/issues/10353) [#10307](https://github.com/tikv/tikv/issues/10307)
    - Fix the issue of backup threads leak [#10287](https://github.com/tikv/tikv/issues/10287)
    - Fix the issue that Region split might panic and corrupt the metadata if the split process is too slow and Region merge is on-going [#8456](https://github.com/tikv/tikv/issues/8456) [#8783](https://github.com/tikv/tikv/issues/8783)
    - Fix the issue that the Region heartbeats prevent TiKV from splitting large Regions in some situations [#10111](https://github.com/tikv/tikv/issues/10111)
    - Fix the wrong statistics caused by the format inconsistency of CM Sketch between TiKV and TiDB [#25638](https://github.com/pingcap/tidb/issues/25638)
    - Fix the wrong statistics of the `apply wait duration` metric [#9893](https://github.com/tikv/tikv/issues/9893)
    - Fix the "Missing Blob" error after using `delete_files_in_range` in Titan [#10232](https://github.com/tikv/tikv/pull/10232)

+ PD

    - Fix a bug that the scheduler might reappear after executing the delete operation [#2572](https://github.com/tikv/pd/issues/2572)
    - Fix the data race issue that might occur when the scheduler is started before the temporary configuration is loaded [#3771](https://github.com/tikv/pd/issues/3771)
    - Fix a PD panic issue that might occur during the Region scattering operation [#3761](https://github.com/pingcap/pd/pull/3761)
    - Fix the issue that the priority of some operators is not set correctly [#3703](https://github.com/pingcap/pd/pull/3703)
    - Fix a PD panic issue that might occur when deleting the `evict-leader` scheduler from a non-existent store [#3660](https://github.com/tikv/pd/issues/3660)
    - Fix the issue that the PD Leader re-election is slow when there are many stores [#3697](https://github.com/tikv/pd/issues/3697)

+ TiDB Dashboard

    - Fix the issue that the **Profiling** UI cannot profile all TiDB instances [#944](https://github.com/pingcap/tidb-dashboard/pull/944)
    - Fix the issue that the **Statements** UI does not display "Plan Count" [#939](https://github.com/pingcap/tidb-dashboard/pull/939)
    - Fix the issue that the **Slow Query** UI might display the "unknown field" error after cluster upgrade [#902](https://github.com/pingcap/tidb-dashboard/issues/902)

+ TiFlash

    - Fix the potential panic issue that occurs when compiling DAG requests
    - Fix the panic issue that occurs when the read load is heavy
    - Fix the issue that TiFlash keeps restarting because of the split failure in column storage
    - Fix a potential bug that TiFlash cannot delete the delta data
    - Fix the incorrect results that occur when cloning the shared delta index concurrently
    - Fix a bug that TiFlash fails to restart in the case of incomplete data
    - Fix the issue that the old dm files cannot be removed automatically
    - Fix the panic issue that occurs when executing the `SUBSTRING` function with specific arguments
    - Fix the issue of incorrect results when casting the `INTEGER` type to the `TIME` type

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the data restore from the `mysql` schema might fail [#1142](https://github.com/pingcap/br/pull/1142)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning fails to parse the `DECIMAL` type data in Parquet files [#1276](https://github.com/pingcap/br/pull/1276)
        - Fix the EOF error reported when TiDB Lightning splits the imported large CSV files [#1133](https://github.com/pingcap/br/issues/1133)
        - Fix a bug that an excessively large base value is generated when TiDB Lightning imports tables with the `auto_increment` column of the `FLOAT` or `DOUBLE` type [#1185](https://github.com/pingcap/br/pull/1185)
        - Fix the issue of TiDB Lightning panic that occurs when generating KV data larger than 4 GB [#1128](https://github.com/pingcap/br/pull/1128)

    + Dumpling

        - When using Dumpling to export data to the S3 storage, the `s3:ListBucket` permission is no longer required on the entire bucket. The permission is required only on the data source prefix. [#898](https://github.com/pingcap/br/issues/898)

    + TiCDC
        - Fix the issue of extra partition dispatching after adding new table partitions [#2205](https://github.com/pingcap/tiflow/pull/2205)
        - Fix the panic issue that occurs when TiCDC fails to read `/proc/meminfo` [#2023](https://github.com/pingcap/tiflow/pull/2023)
        - Reduce TiCDC's runtime memory consumption [#2011](https://github.com/pingcap/tiflow/pull/2011) [#1957](https://github.com/pingcap/tiflow/pull/1957)
        - Fix a bug that some MySQL connection might leak after MySQL sink meets the error and pauses [#1945](https://github.com/pingcap/tiflow/pull/1945)
        - Fix the issue that TiCDC changefeed cannot be created when start TS is less than current TS minus GC TTL [#1839](https://github.com/pingcap/tiflow/issues/1839)
        - Reduce memory `malloc` in sort heap to avoid too much CPU overhead [#1853](https://github.com/pingcap/tiflow/issues/1853)
        - Fix a bug that the replication task might stop when moving a table [#1827](https://github.com/pingcap/tiflow/pull/1827)
