# Improvements across TiDB, PD, TiFlash, TiCDC, and Dumpling

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.0.md`
- Source Title: `TiDB 5.2 Release Notes`
- Source Heading Path: `TiDB 5.2 Release Notes > Improvements`
- Source Line Ranges: `196-248`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tiflash`, `ticdc`, `dumpling`, `sql`, `tikv`
- Topic Tags: `improvements`, `query-optimization`, `mpp`, `bindings`, `hot-region-scheduling`, `functions`, `incremental-scan`, `workerpool`, `table-splitting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0240_4d92f6754a`
- Source ID: `tidb-docs-8.1:releases/release-5.2.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f75e027a4568a8c5377500591a2d2b47978c7854fa8b3fe940e38a23b78df7c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when locating TiDB 5.2 improvement notes across TiDB, PD, TiFlash, TiCDC, and Dumpling for query optimization, MPP, bindings, hot Region scheduling, incremental scan, workerpool, or table splitting changes.
- Retrieval Keywords: TiDB 5.2 Improvements, json_unquote() pushdown to TiKV, remove the union branch from the dual table, aggregate operator's cost factor, MPP outer join build table based on the table row count, balancing the MPP query workload among different TiFlash nodes based on Regions, invalidating stale Regions in the cache after the MPP query is executed, str_to_date %b %M %r %T, SHOW BINDINGS, EXPLAIN VERBOSE, last_plan_binding_update_time, admin evolve bindings, hot Region scheduling, write hotspot of TiFlash, Shuffled Hash Join, Shuffled Hash Aggregation, incremental scan of kv client, resolve lock, workerpool, tidb_rowid, information_schema
- Follow-up Guidance: The chunk also lists exact built-in functions, status variables, SQL statements, and component-specific improvements introduced in these release notes.
- Classification Note: This is a release-note improvement summary because the official content enumerates enhancements and fixes for multiple components under the Improvements section of TiDB 5.2 Release Notes.

## Official Source Content

## Improvements

+ TiDB

    - Support pushing down the built-in function `json_unquote()` to TiKV [#24415](https://github.com/pingcap/tidb/issues/24415)
    - Support removing the `union` branch from the dual table [#25614](https://github.com/pingcap/tidb/pull/25614)
    - Optimize the aggregate operator's cost factor [#25241](https://github.com/pingcap/tidb/pull/25241)
    - Allow the MPP outer join to choose the build table based on the table row count [#25142](https://github.com/pingcap/tidb/pull/25142)
    - Support balancing the MPP query workload among different TiFlash nodes based on Regions [#24724](https://github.com/pingcap/tidb/pull/24724)
    - Support invalidating stale Regions in the cache after the MPP query is executed [#24432](https://github.com/pingcap/tidb/pull/24432)
    - Improve the MySQL compatibility of the built-in function`str_to_date` for the format specifiers `%b/%M/%r/%T` [#25767](https://github.com/pingcap/tidb/pull/25767)
    - Fix the issue that inconsistent binding caches might be created in multiple TiDB after recreating different bindings for the same query [#26015](https://github.com/pingcap/tidb/pull/26015)
    - Fix the issue that the existing bindings cannot be loaded into cache after upgrade [#23295](https://github.com/pingcap/tidb/pull/23295)
    - Support ordering the result of `SHOW BINDINGS` by (`original_sql`, `update_time`) [#26139](https://github.com/pingcap/tidb/pull/26139)
    - Improve the logic of query optimization when bindings exist, and reduce optimization times of a query [#26141](https://github.com/pingcap/tidb/pull/26141)
    - Support completing the garbage collection automatically for the bindings in the "deleted" status [#26206](https://github.com/pingcap/tidb/pull/26206)
    - Support showing whether a binding is used for query optimization in the result of `EXPLAIN VERBOSE` [#26930](https://github.com/pingcap/tidb/pull/26930)
    - Add a new status variation `last_plan_binding_update_time` to view the timestamp corresponding to the binding cache in the current TiDB instance [#26340](https://github.com/pingcap/tidb/pull/26340)
    - Support reporting an error when starting binding evolution or running `admin evolve bindings` to ban the baseline evolution (currently disabled in the TiDB Self-Managed version because it is an experimental feature) affecting other features [#26333](https://github.com/pingcap/tidb/pull/26333)

+ PD

    - Add more QPS dimensions for hot Region scheduling, and support adjusting the priority of the scheduling [#3869](https://github.com/tikv/pd/issues/3869)
    - Support hot Region balance scheduling for the write hotspot of TiFlash [#3900](https://github.com/tikv/pd/pull/3900)

+ TiFlash

    - Add operators: `MOD / %`, `LIKE`
    - Add string functions: `ASCII()`, `COALESCE()`, `LENGTH()`, `POSITION()`, `TRIM()`
    - Add mathematical functions: `CONV()`, `CRC32()`, `DEGREES()`, `EXP()`, `LN()`, `LOG()`, `LOG10()`, `LOG2()`, `POW()`, `RADIANS()`, `ROUND(decimal)`, `SIN()`, `MOD()`
    - Add date functions: `ADDDATE(string, real)`, `DATE_ADD(string, real)`, `DATE()`
    - Add other functions: `INET_NTOA()`, `INET_ATON()`, `INET6_ATON`, `INET6_NTOA()`
    - Support Shuffled Hash Join calculation and Shuffled Hash Aggregation calculation in the MPP mode when a new collation is enabled
    - Optimize basic code to improve MPP performance
    - Support casting the `STRING` type to the `DOUBLE` type
    - Optimize the non-joined data in right outer join using multiple threads
    - Support automatically invalidating stale Regions in MPP queries

+ Tools

    + TiCDC

        - Add the concurrency limit to the incremental scan of kv client [#1899](https://github.com/pingcap/tiflow/pull/1899)
        - TiCDC can always pull the old value internally [#2271](https://github.com/pingcap/tiflow/pull/2271)
        - TiCDC can fail and exit fast when unrecoverable DML errors occur [#1928](https://github.com/pingcap/tiflow/pull/1928)
        - `resolve lock` cannot be run immediately after a Region is initialized [#2235](https://github.com/pingcap/tiflow/pull/2235)
        - Optimize workerpool to reduce the number of goroutines under high concurrency [#2201](https://github.com/pingcap/tiflow/pull/2201)

    + Dumpling

        - Support always splitting TiDB v3.x tables through `tidb_rowid` to save TiDB memory [#301](https://github.com/pingcap/dumpling/pull/301)
        - Reduce access of Dumpling to the `information_schema` to improve stability [#305](https://github.com/pingcap/dumpling/pull/305)
