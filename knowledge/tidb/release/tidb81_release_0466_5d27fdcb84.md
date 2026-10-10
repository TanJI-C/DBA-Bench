# 7.1.3 bug fixes for TiDB query execution, memory, DDL, import, and runtime behavior

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.3.md`
- Source Title: `TiDB 7.1.3 Release Notes`
- Source Heading Path: `TiDB 7.1.3 Release Notes > Bug fixes`
- Source Line Ranges: `54-93`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `shared`, `sql`
- Topic Tags: `bug-fixes`, `cte`, `memory-limit`, `cpu-usage`, `oom`, `query-correctness`, `optimizer`, `pointget`, `statistics`, `plan-digest`, `import-into`, `ddl`, `partitioning`, `auto-id-cache`, `graceful-shutdown`, `cgroup`, `systemd`, `mpp`, `hash-join`, `tablesample`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0466_5d27fdcb84`
- Source ID: `tidb-docs-8.1:releases/release-7.1.3.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4c22b24420a99004e63d35315e157621639bf1f54570435fe2954da535950f67`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.3#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.3.md

## Retrieval Guidance

- Use When: Use when looking for TiDB 7.1.3 release note bug fixes about query execution, memory pressure, DDL, import, runtime behavior, or related SQL/operator issues.
- Retrieval Keywords: TiDB 7.1.3 bug fixes, common table expressions, CTE, memory limit exceeded, tidb_server_memory_limit, tidb_max_chunk_size, runtime error: index out of range [32] with length 32, ENUM join key, recursive CTE, UPDATE statements, PointGet, stats_history, PLAN_DIGEST, GenJSONTableFromStats, AUTO_ID_CACHE=1, Duplicate entry, graceful shutdown, ErrLoadDataInvalidURI, ALTER TABLE ... LAST PARTITION, IMPORT INTO, cgroup v2, UNION ALL, DUAL table, TABLESAMPLE, tidb_enable_ordered_result_mode, IndexFullScan, INDEX_LOOKUP_HASH_JOIN, COUNT(INT), HashJoin
- Follow-up Guidance: See the TiDB bug-fix list in the 7.1.3 release notes for the specific issue references.
- Classification Note: The chunk is a TiDB 7.1.3 bug-fix release note listing fixes for query execution, memory usage, DDL, import, and runtime issues.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue that queries containing common table expressions (CTEs) unexpectedly get stuck when the memory limit is exceeded [#49096](https://github.com/pingcap/tidb/issues/49096) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that high CPU usage of TiDB occurs due to long-term memory pressure caused by `tidb_server_memory_limit` [#48741](https://github.com/pingcap/tidb/issues/48741) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that queries containing CTEs report `runtime error: index out of range [32] with length 32` when `tidb_max_chunk_size` is set to a small value [#48808](https://github.com/pingcap/tidb/issues/48808) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the query result is incorrect when an `ENUM` type column is used as the join key [#48991](https://github.com/pingcap/tidb/issues/48991) @[winoros](https://github.com/winoros)
    - Fix the parsing error caused by aggregate or window functions in recursive CTEs [#47711](https://github.com/pingcap/tidb/issues/47711) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that `UPDATE` statements might be incorrectly converted to PointGet [#47445](https://github.com/pingcap/tidb/issues/47445) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the OOM issue that might occur when TiDB performs garbage collection on the `stats_history` table [#48431](https://github.com/pingcap/tidb/issues/48431) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the same query plan has different `PLAN_DIGEST` values in some cases [#47634](https://github.com/pingcap/tidb/issues/47634) @[King-Dylan](https://github.com/King-Dylan)
    - Fix the issue that `GenJSONTableFromStats` cannot be killed when it consumes a large amount of memory [#47779](https://github.com/pingcap/tidb/issues/47779) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the result might be incorrect when predicates are pushed down to common table expressions [#47881](https://github.com/pingcap/tidb/issues/47881) @[winoros](https://github.com/winoros)
    - Fix the issue that `Duplicate entry` might occur when `AUTO_ID_CACHE=1` is set [#46444](https://github.com/pingcap/tidb/issues/46444) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB server might consume a significant amount of resources when the enterprise plugin for audit logging is used [#49273](https://github.com/pingcap/tidb/issues/49273) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that TiDB server might panic during graceful shutdown [#36793](https://github.com/pingcap/tidb/issues/36793) @[bb7133](https://github.com/bb7133)
    - Fix the issue that tables with `AUTO_ID_CACHE=1` might lead to gRPC client leaks when there are a large number of tables [#48869](https://github.com/pingcap/tidb/issues/48869) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the incorrect error message for `ErrLoadDataInvalidURI` (invalid S3 URI error) [#48164](https://github.com/pingcap/tidb/issues/48164) @[lance6716](https://github.com/lance6716)
    - Fix the issue that executing `ALTER TABLE ... LAST PARTITION` fails when the partition column type is `DATETIME` [#48814](https://github.com/pingcap/tidb/issues/48814) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that the actual error message during `IMPORT INTO` execution might be overridden by other error messages [#47992](https://github.com/pingcap/tidb/issues/47992) [#47781](https://github.com/pingcap/tidb/issues/47781) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that TiDB deployed in the cgroup v2 container cannot be detected [#48342](https://github.com/pingcap/tidb/issues/48342) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that executing `UNION ALL` with the DUAL table as the first subnode might cause an error [#48755](https://github.com/pingcap/tidb/issues/48755) @[winoros](https://github.com/winoros)
    - Fix the TiDB node panic issue that occurs when DDL `jobID` is restored to 0 [#46296](https://github.com/pingcap/tidb/issues/46296) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue of unsorted row data returned by `TABLESAMPLE` [#48253](https://github.com/pingcap/tidb/issues/48253) @[tangenta](https://github.com/tangenta)
    - Fix the issue that panic might occur when `tidb_enable_ordered_result_mode` is enabled [#45044](https://github.com/pingcap/tidb/issues/45044) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the optimizer mistakenly selects IndexFullScan to reduce sort introduced by window functions [#46177](https://github.com/pingcap/tidb/issues/46177) @[qw4990](https://github.com/qw4990)
    - Fix the issue of not handling locks in the MVCC interface when reading schema diff commit versions from the TiDB schema cache [#48281](https://github.com/pingcap/tidb/issues/48281) @[cfzjywxk](https://github.com/cfzjywxk)
    - Fix the issue of incorrect memory usage estimation in `INDEX_LOOKUP_HASH_JOIN` [#47788](https://github.com/pingcap/tidb/issues/47788) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue of `IMPORT INTO` task failure caused by PD leader malfunction for 1 minute [#48307](https://github.com/pingcap/tidb/issues/48307) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the panic issue of `batch-client` in `client-go` [#47691](https://github.com/pingcap/tidb/issues/47691) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that column pruning can cause panic in specific situations [#47331](https://github.com/pingcap/tidb/issues/47331) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that TiDB does not read `cgroup` resource limits when it is started with `systemd` [#47442](https://github.com/pingcap/tidb/issues/47442) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue of possible syntax error when a common table expression (CTE) containing aggregate or window functions is referenced by other recursive CTEs [#47603](https://github.com/pingcap/tidb/issues/47603) [#47711](https://github.com/pingcap/tidb/issues/47711)  @[elsa0520](https://github.com/elsa0520)
    - Fix the panic issue that might occur when constructing TopN structure for statistics [#35948](https://github.com/pingcap/tidb/issues/35948) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that the result of `COUNT(INT)` calculated by MPP might be incorrect [#48643](https://github.com/pingcap/tidb/issues/48643) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the chunk cannot be reused when the HashJoin operator performs probe [#48082](https://github.com/pingcap/tidb/issues/48082) @[wshwsh12](https://github.com/wshwsh12)

+ TiKV
