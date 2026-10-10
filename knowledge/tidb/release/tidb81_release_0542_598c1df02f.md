# TiDB 7.5.4 bug fixes across TiDB, TiKV, and PD

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.4.md`
- Source Title: `TiDB 7.5.4 Release Notes`
- Source Heading Path: `TiDB 7.5.4 Release Notes > Bug fixes`
- Source Line Ranges: `48-94`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dm`, `tiflash`
- Topic Tags: `release-notes`, `bug-fixes`, `flashback-database`, `partitioning`, `union`, `join`, `stale-read`, `spill-to-disk`, `query-kill`, `table-replication`, `information-schema`, `generated-columns`, `statistics`, `data-race`, `memory-quota`, `runtime-error`, `order-by`, `panic`, `cancel-query`, `integer-width`, `unique-index`, `import-into`, `index-consistency`, `raft-snapshot`, `flow-control`, `bloom-filter`, `kms`, `metrics`, `deadlock-detection`, `region-api`, `scheduler`, `leader-switch`, `resource-group`, `runaway-watches`, `strictly-match-label`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0542_598c1df02f`
- Source ID: `tidb-docs-8.1:releases/release-7.5.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `23561949636587c919c5ba54e778fdb5b0ea8f9aaea5bbedc4f5457e9557e79f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.4.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.5.4 bug fixes for specific SQL errors, performance problems, panics, replication issues, monitoring inaccuracies, or PD scheduling and API issues.
- Retrieval Keywords: TiDB 7.5.4 Release Notes, Bug fixes, FLASHBACK DATABASE, RANGE partitioned tables, UNION incorrect results, INDEX_HASH_JOIN, PipelinedWindow, Apply, stale reads, information schema cache misses, Sort spills, query killed incorrect results, DM, max-index-length, INFORMATION_SCHEMA.STATISTICS, SUB_PART, nested generated columns, mysql.stats_histograms, tot_col_size, IndexNestedLoopHashJoin, tidb_mem_quota_query, runtime error: index out of range, ORDER BY performance, StreamAggExec, TiDB queries cannot be canceled during cop task construction, out of range, duplicate entry, IMPORT INTO, temporary tables, data index inconsistency, adding unique indexes, Raft snapshots, flow control, bloom filters, master key rotation, Key Management Service, KMS, Storage async write duration, deadlock detection, PD Region API, evict-leader-scheduler, microservice mode, INFORMATION_SCHEMA.RUNAWAY_WATCHES, replication.strictly-match-label
- Follow-up Guidance: The chunk groups the fixes by TiDB, TiKV, and PD, and ends with a TiFlash heading without listing TiFlash fixes in the provided content.
- Classification Note: This is classified as a release chunk because the official content is the Bug fixes section of the TiDB 7.5.4 release notes.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that `FLASHBACK DATABASE` fails when many tables exist in the database [#54415](https://github.com/pingcap/tidb/issues/54415) @[lance6716](https://github.com/lance6716)
    - Fix the issue that RANGE partitioned tables that are not strictly self-incrementing can be created [#54829](https://github.com/pingcap/tidb/issues/54829) @[Defined2014](https://github.com/Defined2014)
     - Fix the issue that a query statement that contains `UNION` might return incorrect results [#52985](https://github.com/pingcap/tidb/issues/52985) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that `INDEX_HASH_JOIN` cannot exit properly when SQL is abnormally interrupted [#54688](https://github.com/pingcap/tidb/issues/54688) @[wshwsh12](https://github.com/wshwsh12)
    - Reset the parameters in the `Open` method of `PipelinedWindow` to fix the unexpected error that occurs when the `PipelinedWindow` is used as a child node of `Apply` due to the reuse of previous parameter values caused by repeated opening and closing operations [#53600](https://github.com/pingcap/tidb/issues/53600) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that the query latency of stale reads increases, caused by information schema cache misses [#53428](https://github.com/pingcap/tidb/issues/53428) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that disk files might not be deleted after the `Sort` operator spills and a query error occurs [#55061](https://github.com/pingcap/tidb/issues/55061) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the query might return incorrect results instead of an error after being killed [#50089](https://github.com/pingcap/tidb/issues/50089) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that table replication fails when the index length of the table replicated from DM exceeds the maximum length specified by `max-index-length` [#55138](https://github.com/pingcap/tidb/issues/55138) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the `SUB_PART` value in the `INFORMATION_SCHEMA.STATISTICS` table is `NULL` [#55812](https://github.com/pingcap/tidb/issues/55812) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that an error occurs when a DML statement contains nested generated columns [#53967](https://github.com/pingcap/tidb/issues/53967) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the `tot_col_size` column in the `mysql.stats_histograms` table might be a negative number [#55126](https://github.com/pingcap/tidb/issues/55126) @[qw4990](https://github.com/qw4990)
    - Fix the data race issue in `IndexNestedLoopHashJoin` [#49692](https://github.com/pingcap/tidb/issues/49692) @[solotzg](https://github.com/solotzg)
    - Fix the issue that the query might get stuck when terminated because the memory usage exceeds the limit set by `tidb_mem_quota_query` [#55042](https://github.com/pingcap/tidb/issues/55042) @[yibin87](https://github.com/yibin87)
    - Fix the issue that `columnEvaluator` cannot identify the column references in the input chunk, which leads to `runtime error: index out of range` when executing SQL statements [#53713](https://github.com/pingcap/tidb/issues/53713) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the performance of the `SELECT ... WHERE ... ORDER BY ...` statement execution is poor in some cases [#54969](https://github.com/pingcap/tidb/issues/54969) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that empty `groupOffset` in `StreamAggExec` might cause TiDB to panic [#53867](https://github.com/pingcap/tidb/issues/53867) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that TiDB queries cannot be canceled during cop task construction [#55957](https://github.com/pingcap/tidb/issues/55957) @[yibin87](https://github.com/yibin87)
    - Fix the issue that an `out of range` error might occur when a small display width is specified for a column of the integer type [#55837](https://github.com/pingcap/tidb/issues/55837) @[windtalker](https://github.com/windtalker)
    - Fix the issue that `duplicate entry` might occur when adding unique indexes [#56161](https://github.com/pingcap/tidb/issues/56161) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TiDB panics when importing temporary tables using the `IMPORT INTO` statement [#55970](https://github.com/pingcap/tidb/issues/55970) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue of data index inconsistency caused by retries during index addition [#55808](https://github.com/pingcap/tidb/issues/55808) @[lance6716](https://github.com/lance6716)

+ TiKV

    - Fix the issue that TiKV might panic when a stale replica processes Raft snapshots, triggered by a slow split operation and immediate removal of the new replica [#17469](https://github.com/tikv/tikv/issues/17469) @[hbisheng](https://github.com/hbisheng)
    - Fix the flow control issue that might occur after deleting large tables or partitions [#17304](https://github.com/tikv/tikv/issues/17304) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that bloom filters are incompatible between earlier versions (earlier than v7.1) and later versions [#17272](https://github.com/tikv/tikv/issues/17272) @[v01dstar](https://github.com/v01dstar)
    - Fix the issue that prevents master key rotation when the master key is stored in a Key Management Service (KMS) [#17410](https://github.com/tikv/tikv/issues/17410) @[hhwyt](https://github.com/hhwyt)
    - Fix the issue that the **Storage async write duration** monitoring metric on the TiKV panel in Grafana is inaccurate [#17579](https://github.com/tikv/tikv/issues/17579) @[overvenus](https://github.com/overvenus)
    - Fix the issue that when a large number of transactions are queuing for lock release on the same key and the key is frequently updated, excessive pressure on deadlock detection might cause TiKV OOM issues [#17394](https://github.com/tikv/tikv/issues/17394) @[MyonKeminta](https://github.com/MyonKeminta)

+ PD

    - Fix the issue that PD's Region API cannot be requested when a large number of Regions exist [#55872](https://github.com/pingcap/tidb/issues/55872) @[rleungx](https://github.com/rleungx)
    - Fix the issue that when using a wrong parameter in `evict-leader-scheduler`, PD does not report errors correctly and some schedulers are unavailable [#8619](https://github.com/tikv/pd/issues/8619) @[rleungx](https://github.com/rleungx)
    - Fix the issue that data race might occur in the scheduling server when a PD leader is switched in the microservice mode [#8538](https://github.com/tikv/pd/issues/8538) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that slots are not fully deleted in a resource group client, which causes the number of the allocated tokens to be less than the specified value [#7346](https://github.com/tikv/pd/issues/7346) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the time data type in the `INFORMATION_SCHEMA.RUNAWAY_WATCHES` table is incorrect [#54770](https://github.com/pingcap/tidb/issues/54770) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that setting `replication.strictly-match-label` to `true` causes TiFlash to fail to start [#8480](https://github.com/tikv/pd/issues/8480) @[rleungx](https://github.com/rleungx)

+ TiFlash
