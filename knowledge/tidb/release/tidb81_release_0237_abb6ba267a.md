# Bug fixes for PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.5.md`
- Source Title: `TiDB 5.1.5 Release Notes`
- Source Heading Path: `TiDB 5.1.5 Release Notes > Bug fixes`
- Source Line Ranges: `72-124`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `dashboard`, `tiflash`, `br`, `ticdc`
- Topic Tags: `bug-fixes`, `leader-transfer`, `scheduling`, `tso`, `metrics`, `wrong-results`, `panic`, `crash`, `data-inconsistency`, `mpp`, `restore`, `data-loss`, `memory-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0237_abb6ba267a`
- Source ID: `tidb-docs-8.1:releases/release-5.1.5.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `515fded43968f114ad294a9b9039dc804b4b972c35891347b0ae76af16cd7555`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.5#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.5.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.1.5 bug fixes for PD, TiFlash, TiDB Binlog, BR, or TiCDC involving leader transfer, scheduling, TSO, metrics, wrong results, panic, crash, restore, data loss, or memory usage.
- Retrieval Keywords: TiDB 5.1.5 bug fixes, PD leader transfer tombstone store appears again, scheduling cannot start immediately after the PD leader transfer, wrong status code of not leader, PD cannot correctly handle dashboard proxy requests, TSO fallback corner cases, TiFlash learner replica might not be created, label distribution residual labels in the metrics, SchedulerMaxWaitingOperator set to 1, TiFlash incorrect microsecond casting string to datetime, TiFlash panic when TLS is enabled, TiFlash crash due to parallel aggregation, JOIN query might be hung if an error occurs, function OR returns wrong results, invalid storage directory configurations unexpected behaviors, potential data inconsistency after a lot of INSERT and DELETE operations, commit state jump backward, MPP query random gRPC keepalive timeout, MPP tasks might leak threads forever, TiFlash_schema_error, json_length empty string index out of bounds, Drainer compressor zip Pump, BR system tables cannot be restored, TiCDC data loss incremental scanning, TiCDC no sorter metrics, TiCDC excessive memory usage DDL schemas buffered
- Follow-up Guidance: The source groups these fixes under PD, TiFlash, TiDB Binlog, Backup & Restore (BR), and TiCDC in the TiDB 5.1.5 release notes.
- Classification Note: This chunk is classified as a self-managed release-note bug-fix summary because the official content lists resolved issues across PD, TiFlash, and tools for TiDB 5.1.5.

## Official Source Content

- Fix the issue that a removed tombstone store appears again after the PD leader transfer ​​[#4941](https://github.com/tikv/pd/issues/4941)
    - Fix the issue that scheduling cannot start immediately after the PD leader transfer [#4769](https://github.com/tikv/pd/issues/4769)
    - Fix the wrong status code of `not leader` [#4797](https://github.com/tikv/pd/issues/4797)
    - Fix the issue that PD cannot correctly handle dashboard proxy requests [#5321](https://github.com/tikv/pd/issues/5321)
    - Fix a bug of TSO fallback in some corner cases [#4884](https://github.com/tikv/pd/issues/4884)
    - Fix the issue that the TiFlash learner replica might not be created in specific scenarios [#5401](https://github.com/tikv/pd/issues/5401)
    - Fix the issue that the label distribution has residual labels in the metrics [#4825](https://github.com/tikv/pd/issues/4825)
    - Fix the issue that when there exists a Store with large capacity (2T for example), fully allocated small Stores cannot be detected, which results in no balance operator being generated [#4805](https://github.com/tikv/pd/issues/4805)
    - Fix the issue that schedulers do not work when `SchedulerMaxWaitingOperator` is set to `1` [#4946](https://github.com/tikv/pd/issues/4946)

+ TiFlash

    - Fix incorrect `microsecond` when casting string to datetime [#3556](https://github.com/pingcap/tiflash/issues/3556)
    - Fix the panic issue that occurs when TLS is enabled [#4196](https://github.com/pingcap/tiflash/issues/4196)
    - Fix a bug that TiFlash might crash due to an error in parallel aggregation [#5356](https://github.com/pingcap/tiflash/issues/5356)
    - Fix the issue that a query containing `JOIN` might be hung if an error occurs [#4195](https://github.com/pingcap/tiflash/issues/4195)
    - Fix the issue that the function `OR` returns wrong results [#5849](https://github.com/pingcap/tiflash/issues/5849)
    - Fix the bug that invalid storage directory configurations lead to unexpected behaviors [#4093](https://github.com/pingcap/tiflash/issues/4093)
    - Fix potential data inconsistency after a lot of INSERT and DELETE operations [#4956](https://github.com/pingcap/tiflash/issues/4956)
    - Fix a bug that data not matching any region range remains on a TiFlash node [#4414](https://github.com/pingcap/tiflash/issues/4414)
    - Fix the potential query error after adding columns under heavy read workload [#3967](https://github.com/pingcap/tiflash/issues/3967)
    - Fix repeated crashes caused by the `commit state jump backward` errors [#2576](https://github.com/pingcap/tiflash/issues/2576)
    - Fix potential errors when querying on a table with many delete operations [#4747](https://github.com/pingcap/tiflash/issues/4747)
    - Fix the issue that the date format identifies `''` as an invalid separator [#4036](https://github.com/pingcap/tiflash/issues/4036)
    - Fix the wrong result that occurs when casting `DATETIME` to `DECIMAL` [#4151](https://github.com/pingcap/tiflash/issues/4151)
    - Fix the bug that some exceptions are not handled properly [#4101](https://github.com/pingcap/tiflash/issues/4101)
    - Fix the issue that `Prepare Merge` might damage the metadata of the raft store and cause TiFlash to restart [#3435](https://github.com/pingcap/tiflash/issues/3435)
    - Fix a bug that an MPP query might fail due to random gRPC keepalive timeout [#4662](https://github.com/pingcap/tiflash/issues/4662)
    - Fix the issue that the result of `IN` is incorrect in multi-value expressions [#4016](https://github.com/pingcap/tiflash/issues/4016)
    - Fix a bug that MPP tasks might leak threads forever [#4238](https://github.com/pingcap/tiflash/issues/4238)
    - Fix the issue that expired data is recycled slowly [#4146](https://github.com/pingcap/tiflash/issues/4146)
    - Fix the overflow that occurs when casting `FLOAT` to `DECIMAL` [#3998](https://github.com/pingcap/tiflash/issues/3998)
    - Fix the issue that logical operators return wrong results when the argument type is UInt8 [#6127](https://github.com/pingcap/tiflash/issues/6127)
    - Fix the potential `index out of bounds` error if calling `json_length` with empty string [#2705](https://github.com/pingcap/tiflash/issues/2705)
    - Fix wrong decimal comparison results in corner cases [#4512](https://github.com/pingcap/tiflash/issues/4512)
    - Fix `TiFlash_schema_error` reported when `NOT NULL` columns are added [#4596](https://github.com/pingcap/tiflash/issues/4596)
    - Fix the issue that TiFlash bootstrap fails when `0.0` is used as the default value for integers, for example, `` `i` int(11) NOT NULL DEFAULT '0.0'`` [#3157](https://github.com/pingcap/tiflash/issues/3157)

+ Tools

    + TiDB Binlog

        - Fix the issue that Drainer cannot send requests to Pump correctly when `compressor` is set to `zip` [#1152](https://github.com/pingcap/tidb-binlog/issues/1152)

    + Backup & Restore (BR)

        - Fix the issue that system tables cannot be restored because concurrently backing up system tables makes the table name fail to update [#29710](https://github.com/pingcap/tidb/issues/29710)

    + TiCDC

        - Fix data loss that occurs in special incremental scanning scenarios [#5468](https://github.com/pingcap/tiflow/issues/5468)
        - Fix the issue that there are no sorter metrics [#5690](https://github.com/pingcap/tiflow/issues/5690)
        - Fix excessive memory usage by optimizing the way DDL schemas are buffered [#1386](https://github.com/pingcap/tiflow/issues/1386)
