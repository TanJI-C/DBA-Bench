# Improvements across TiDB TiFlash TiCDC and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.2.md`
- Source Title: `TiDB 6.5.2 Release Notes`
- Source Heading Path: `TiDB 6.5.2 Release Notes > Improvements`
- Source Line Ranges: `22-49`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `ticdc`, `lightning`, `br`
- Topic Tags: `release-notes`, `improvements`, `plan-cache`, `index-join`, `logging`, `query-latency`, `cpu-usage`, `data-import`, `openapi`, `memory-limit`, `replication-performance`, `redo-log`, `disaster-recovery`, `csv`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0391_48ef6bab7e`
- Source ID: `tidb-docs-8.1:releases/release-6.5.2.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `677a1e348a3a2ed2374150fdb938f3c7a44c6fc7edd4a0946faa014b3a0641c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.2#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.2.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants a summary of improvements introduced in TiDB 6.5.2 across TiDB, TiFlash, TiCDC, and TiDB Lightning.
- Retrieval Keywords: TiDB 6.5.2 improvements, BatchPointGet, Prepared Plan Cache, Index Join, Index Merge readers, debug, distsql_concurrency, Range partitioned tables, Limit, TiFlash reads, CPU consumption, BR, TiDB Lightning, TiCDC Open API v2.0, gomemlimit, OOM, batch execution of UPDATE statements, redo applier, throughput, RTO, disaster recovery, DDL events in redo logs, CSV data files with BOM headers
- Follow-up Guidance: The content lists improvements by component, including Prepared Plan Cache support for BatchPointGet, TiCDC Open API v2.0, gomemlimit for OOM prevention, and CSV import with BOM headers in TiDB Lightning.
- Classification Note: This is an improvements chunk because it enumerates new optimizations, support additions, and performance enhancements delivered in the TiDB 6.5.2 release.

## Official Source Content

## Improvements

+ TiDB

    - Support caching the execution plan for `BatchPointGet` in Prepared Plan Cache [#42125](https://github.com/pingcap/tidb/issues/42125) @[qw4990](https://github.com/qw4990)
    - Support more SQL formats for Index Join [#40505](https://github.com/pingcap/tidb/issues/40505) @[Yisaer](https://github.com/Yisaer)
    - Change the log level of some Index Merge readers from `"info"` to `"debug"` [#41949](https://github.com/pingcap/tidb/issues/41949) @[yibin87](https://github.com/yibin87)
    - Optimize the `distsql_concurrency` setting for Range partitioned tables with Limit to reduce query latency [#41480](https://github.com/pingcap/tidb/issues/41480) @[you06](https://github.com/you06)

+ TiFlash

    - Reduce CPU consumption of task scheduling during TiFlash reads [#6495](https://github.com/pingcap/tiflash/issues/6495) @[JinheLin](https://github.com/JinheLin)
    - Improve performance of data import from BR and TiDB Lightning to TiFlash with default configurations [#7272](https://github.com/pingcap/tiflash/issues/7272) @[breezewish](https://github.com/breezewish)

+ Tools

    + TiCDC

        - Release TiCDC Open API v2.0 [#8743](https://github.com/pingcap/tiflow/issues/8743) @[sdojjy](https://github.com/sdojjy)
        - Introduce `gomemlimit` to prevent TiCDC from OOM issues [#8675](https://github.com/pingcap/tiflow/issues/8675) @[amyangfei](https://github.com/amyangfei)
        - Use the multi-statement approach to optimize the replication performance in scenarios involving batch execution of `UPDATE` statements [#8057](https://github.com/pingcap/tiflow/issues/8057) @[amyangfei](https://github.com/amyangfei)
        - Support splitting transactions in the redo applier to improve its throughput and reduce RTO in disaster recovery scenarios [#8318](https://github.com/pingcap/tiflow/issues/8318) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Support applying DDL events in redo logs [#8361](https://github.com/pingcap/tiflow/issues/8361) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Lightning

        - Support importing CSV data files with BOM headers [#40744](https://github.com/pingcap/tidb/issues/40744) @[dsdashun](https://github.com/dsdashun)
