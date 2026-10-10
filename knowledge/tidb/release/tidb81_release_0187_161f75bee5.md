# Bug fixes for TiDB and TiKV with PD section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.6.md`
- Source Title: `TiDB 4.0.6 Release Notes`
- Source Heading Path: `TiDB 4.0.6 Release Notes > Bug Fixes`
- Source Line Ranges: `97-159`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `bug-fixes`, `sql-execution`, `ddl`, `statistics`, `privileges`, `region-cache`, `raft`, `gc`, `thread-pool`, `memory-allocation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0187_161f75bee5`
- Source ID: `tidb-docs-8.1:releases/release-4.0.6.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e029c5787ce3818156c16831fa4dbb0d86f56cb7ec33a0a5bcf6dbe489d57f20`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.6 bug fixes affecting TiDB SQL execution, DDL, statistics, privileges, Region cache, or TiKV runtime issues such as GC, Raft membership change, PD client deadlock, unified thread pool hangs, or jemalloc huge page memory allocation.
- Retrieval Keywords: TiDB 4.0.6 Bug Fixes, tikv_cop_wait, SHOW GRANTS, SHOW STATS_META, SHOW STATS_BUCKET, != ALL (subq), enum and set types, builtinGreatestStringSig, builtinLeastStringSig, Apply operator, HashJoin, IndexLookupJoin, processlist, cluster_log, plan digest, Decimal to Int, SELECT ... INTO OUTFILE, builtinRealIsFalseSig, partition expression, anti-semi-join, TopN statistics, batch point get, virtual generated column, TiFlash work index in Region cache, logarithm function warning, no regions error, tiflash_segments, tiflash_tables, Count(col), TRUNCATE runtime error, PREPARE statement FROM @Var, information_schema.statements_summary, INFORMATION_SCHEMA.CLUSTER_HARDWARE, add index generated column case-when, DDL retry too long, foreign key references t2(c1) without use db, dispatch error Info message, TiKV collation estimation error, Green GC miss locks, Raft membership change panic, PD client thread deadlock, jemalloc v5.2.1, unified thread pool hangs
- Follow-up Guidance: The same Bug Fixes section continues with PD, TiFlash, and tool fixes including TiCDC, BR, Dumpling, and TiDB Lightning.
- Classification Note: The official content is a release-note bug-fix list for TiDB and TiKV in TiDB 4.0.6, covering multiple components and operational or SQL correctness issues.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix an issue of collecting the `tikv_cop_wait` time in metric profile [#19881](https://github.com/pingcap/tidb/pull/19881)
    - Fix the wrong result of `SHOW GRANTS` [#19834](https://github.com/pingcap/tidb/pull/19834)
    - Fix the incorrect query result of `!= ALL (subq)` [#19831](https://github.com/pingcap/tidb/pull/19831)
    - Fix a bug of converting the `enum` and `set` types [#19778](https://github.com/pingcap/tidb/pull/19778)
    - Add a privilege check for `SHOW STATS_META` and `SHOW STATS_BUCKET` [#19760](https://github.com/pingcap/tidb/pull/19760)
    - Fix the error of unmatched column lengths caused by `builtinGreatestStringSig` and `builtinLeastStringSig` [#19758](https://github.com/pingcap/tidb/pull/19758)
    - If unnecessary errors or warnings occur, the vectorized control expression fall back to their scalar execution [#19749](https://github.com/pingcap/tidb/pull/19749)
    - Fix the error of the `Apply` operator when the type of the correlation column is `Bit` [#19692](https://github.com/pingcap/tidb/pull/19692)
    - Fix the issue that occurs when the user queries `processlist` and `cluster_log` in MySQL 8.0 client [#19690](https://github.com/pingcap/tidb/pull/19690)
    - Fix the issue that plans of the same type have different plan digests [#19684](https://github.com/pingcap/tidb/pull/19684)
    - Forbid changing the column type from `Decimal` to `Int` [#19682](https://github.com/pingcap/tidb/pull/19682)
    - Fix the issue that `SELECT ... INTO OUTFILE` returns the runtime error [#19672](https://github.com/pingcap/tidb/pull/19672)
    - Fix the incorrect implementation of `builtinRealIsFalseSig` [#19670](https://github.com/pingcap/tidb/pull/19670)
    - Fix the issue that the partition expression check misses the parentheses expression [#19614](https://github.com/pingcap/tidb/pull/19614)
    - Fix a query error when there is an `Apply` operator upon `HashJoin` [#19611](https://github.com/pingcap/tidb/pull/19611)
    - Fix an incorrect result of vectorization that casts `Real` as `Time` [#19594](https://github.com/pingcap/tidb/pull/19594)
    - Fix the bug that the `SHOW GRANTS` statement shows grants for non-existent users [#19588](https://github.com/pingcap/tidb/pull/19588)
    - Fix a query error when there is an `Apply` executor upon `IndexLookupJoin` [#19566](https://github.com/pingcap/tidb/pull/19566)
    - Fix the wrong results when converting `Apply` to `HashJoin` on a partitioned table [#19546](https://github.com/pingcap/tidb/pull/19546)
    - Fix incorrect results when there is an `IndexLookUp` executor on the inner side of an `Apply` [#19508](https://github.com/pingcap/tidb/pull/19508)
    - Fix an unexpected panic when using view [#19491](https://github.com/pingcap/tidb/pull/19491)
    - Fix the incorrect result of the `anti-semi-join` query [#19477](https://github.com/pingcap/tidb/pull/19477)
    - Fix the bug that the `TopN` statistics is not deleted when the statistics is dropped [#19465](https://github.com/pingcap/tidb/pull/19465)
    - Fix a wrong result caused by mistaken usage of batch point get [#19460](https://github.com/pingcap/tidb/pull/19460)
    - Fix the bug that a column cannot be found in `indexLookupJoin` with a virtual generated column [#19439](https://github.com/pingcap/tidb/pull/19439)
    - Fix an error that different plans of the `select` and `update` queries compare datum [#19403](https://github.com/pingcap/tidb/pull/19403)
    - Fix a data race for TiFlash work index in Region cache [#19362](https://github.com/pingcap/tidb/pull/19362)
    - Fix the bug that the `logarithm` function does not show a warning [#19291](https://github.com/pingcap/tidb/pull/19291)
    - Fix an unexpected error that occurs when TiDB persists data to disks [#19272](https://github.com/pingcap/tidb/pull/19272)
    - Support using a single partitioned table on the inner side of index join [#19197](https://github.com/pingcap/tidb/pull/19197)
    - Fix the wrong hash key value generated for decimal [#19188](https://github.com/pingcap/tidb/pull/19188)
    - Fix the issue that TiDB returns a `no regions` error when table endKey and Region endKey are the same [#19895](https://github.com/pingcap/tidb/pull/19895)
    - Fix the unexpected success of alter partition [#19891](https://github.com/pingcap/tidb/pull/19891)
    - Fix the wrong value of the default maximum packet length allowed for pushed down expressions [#19876](https://github.com/pingcap/tidb/pull/19876)
    - Fix a wrong behavior for the `Max`/`Min` functions on the `ENUM`/`SET` columns [#19869](https://github.com/pingcap/tidb/pull/19869)
    - Fix the read failure from the `tiflash_segments` and `tiflash_tables` system tables when some TiFlash nodes are offline [#19748](https://github.com/pingcap/tidb/pull/19748)
    - Fix a wrong result of the `Count(col)` aggregation function [#19628](https://github.com/pingcap/tidb/pull/19628)
    - Fix a runtime error of the `TRUNCATE` operation [#19445](https://github.com/pingcap/tidb/pull/19445)
    - Fix the issue that `PREPARE statement FROM @Var` will fail when `Var` contains uppercase characters [#19378](https://github.com/pingcap/tidb/pull/19378)
    - Fix the bug that schema charset modification in an uppercase schema will cause panic [#19302](https://github.com/pingcap/tidb/pull/19302)
    - Fix the inconsistency of plans between `information_schema.statements_summary` and `explain`, when the information contains `tikv/tiflash` [#19159](https://github.com/pingcap/tidb/pull/19159)
    - Fix the error in tests that the file does not exist for `select into outfile` [#19725](https://github.com/pingcap/tidb/pull/19725)
    - Fix the issue that `INFORMATION_SCHEMA.CLUSTER_HARDWARE` does not have raid device information [#19457](https://github.com/pingcap/tidb/pull/19457)
    - Make the `add index` operation that has a generated column with the `case-when` expression can exit normally when it encounters a parse error [#19395](https://github.com/pingcap/tidb/pull/19395)
    - Fix the bug that the DDL operation takes too long to retry [#19488](https://github.com/pingcap/tidb/pull/19488)
    - Make statements like `alter table db.t1 add constraint fk foreign key (c2) references t2(c1)` execute without first executing `use db` [#19471](https://github.com/pingcap/tidb/pull/19471)
    - Change the dispatch error from the `Error` to the `Info` message in the server log file [#19454](https://github.com/pingcap/tidb/pull/19454)

+ TiKV

    - Fix the estimation error for a non-index column when collation is enabled [#8620](https://github.com/tikv/tikv/pull/8620)
    - Fix the issue that Green GC might miss locks during the process of Region transfer [#8460](https://github.com/tikv/tikv/pull/8460)
    - Fix a panic issue that occurs when TiKV runs very slowly during Raft membership change [#8497](https://github.com/tikv/tikv/pull/8497)
    - Fix the deadlock issue that occurs between the PD client thread and other threads when calling PD sync requests [#8612](https://github.com/tikv/tikv/pull/8612)
    - Upgrade jemalloc to v5.2.1 to address the issue of memory allocation in huge page [#8463](https://github.com/tikv/tikv/pull/8463)
    - Fix the issue that the unified thread pool hangs for long-running queries [#8427](https://github.com/tikv/tikv/pull/8427)

+ PD
