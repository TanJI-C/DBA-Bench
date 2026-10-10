# Bug fixes for TiKV, TiFlash, TiCDC, and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.13.md`
- Source Title: `TiDB 4.0.13 Release Notes`
- Source Heading Path: `TiDB 4.0.13 Release Notes > Bug Fixes`
- Source Line Ranges: `104-143`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `tiflash`, `ticdc`, `lightning`
- Topic Tags: `bug-fixes`, `startup`, `memory-usage`, `oom`, `scan-speed`, `back-pressure`, `s3-timeout`, `prometheus`, `grafana`, `panic`, `segment-split`, `restore`, `data-loss`, `gc`, `collation`, `type-casting`, `replication`, `safe-point`, `deadlock`, `autocommit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0168_2c56f8256d`
- Source ID: `tidb-docs-8.1:releases/release-4.0.13.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0fc713d2f04cefd3bab36edbf0b0eadc3cacb181f974d4af8a33fb8207cab822`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.13#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.13.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.13 bug fixes related to TiKV startup, TiCDC scan speed or OOM behavior, TiFlash panic or incorrect-result issues, S3 timeout handling, Grafana or Prometheus reporting, TiKV GC safe point blocking, or TiDB Lightning autocommit behavior.
- Retrieval Keywords: TiDB 4.0.13 bug fixes, TiKV cannot start file_dict disk full, file_dict not fully written, TiCDC scan speed 128MB/s by default, TiCDC initial scan memory usage, back pressure for TiCDC scan speed, TiCDC old values OOM, S3 storages timeout mechanism client hanging without responses, TiFlash delta-merge-tasks Prometheus, TiFlash Segment Split panic, Region write Duration (write blocks) Grafana, TiFlash fails to remove data, casting TIME to INTEGER incorrect results, bitwise operator different from TiDB, casting STRING to INTEGER incorrect results, consecutive and fast writes TiFlash out of memory, null pointer during table GC, writing data to dropped tables panic, BR restore panic, general CI collation wrong weights, data lost in tombstoned tables, string contains zero bytes incorrect results, logical function null constants wrong results, logical function only accepts the numeric type, 1970-01-01 negative timezone offset incorrect results, Decimal256 hash value not stable, deadlock issue caused by the flow control sorter's input channel blocked, TiKV GC safe point blocked changefeed checkpoint stagnation, explicit_defaults_for_timestamp SUPER privilege replicating data to MySQL, TiDB Lightning TiDB-backend cannot load any data autocommit is disabled
- Follow-up Guidance: 
- Classification Note: This is a self-managed release-notes bug-fix summary covering shared components, specifically TiKV, TiFlash, TiCDC, and TiDB Lightning issues fixed in TiDB 4.0.13.

## Official Source Content

- Fix a bug that TiKV cannot start if the `file_dict` file is not fully written into the disk that has been full [#9963](https://github.com/tikv/tikv/pull/9963)
    - Limit TiCDC's scan speed at 128MB/s by default [#9983](https://github.com/tikv/tikv/pull/9983)
    - Reduce the memory usage of TiCDC's initial scan [#10133](https://github.com/tikv/tikv/pull/10133)
    - Support the back pressure for TiCDC's scan speed [#10142](https://github.com/tikv/tikv/pull/10142)
    - Fix a potential OOM issue by avoiding unnecessary reads to get TiCDC old values [#10031](https://github.com/tikv/tikv/pull/10031)
    - Fix a TiCDC OOM issue caused by reading old values [#10197](https://github.com/tikv/tikv/pull/10197)
    - Add a timeout mechanism for S3 storages to avoid the client hanging without responses [#10132](https://github.com/tikv/tikv/pull/10132)

+ TiFlash

    - Fix the issue that number of `delta-merge-tasks` is not reported to Prometheus
    - Fix the TiFlash panic issue that occurs during `Segment Split`
    - Fix the issue that the `Region write Duration (write blocks)` panel in Grafana is shown in a wrong place
    - Fix the potential issue that the storage engine fails to remove data
    - Fix the issue of incorrect results when casting the `TIME` type to the `INTEGER` type
    - Fix a bug that the behavior of the `bitwise` operator is different from that of TiDB
    - Fix the issue of incorrect results when casting the `STRING` type to the `INTEGER` type
    - Fix the issue that consecutive and fast writes might make TiFlash out of memory
    - Fix the potential issue that the exception of null pointer might be raised during the table GC
    - Fix the TiFlash panic issue that occurs when writing data to dropped tables
    - Fix the TiFlash panic issue that occurs during BR restore
    - Fix a bug that the weights of some characters are wrong when using the general CI collation
    - Fix the potential issue that data will be lost in tombstoned tables
    - Fix the issue of incorrect results when comparing the string which contains zero bytes
    - Fix the issue that the logical function returns wrong results if the input column contains null constants
    - Fix the issue that the logical function only accepts the numeric type
    - Fix the issue of incorrect results that occurs when the timestamp value is `1970-01-01` and the timezone offset is negative
    - Fix the issue that hash value of `Decimal256` is not stable

+ Tools

    + TiCDC

        - Fix the deadlock issue caused by the flow control when the sorter's input channel has been blocked [#1779](https://github.com/pingcap/tiflow/pull/1779)
        - Fix the issue that the TiKV GC safe point is blocked due to the stagnation of TiCDC changefeed checkpoint [#1756](https://github.com/pingcap/tiflow/pull/1756)
        - Revert the update in `explicit_defaults_for_timestamp` which requires the `SUPER` privilege when replicating data to MySQL [#1749](https://github.com/pingcap/tiflow/pull/1749)

    + TiDB Lightning

        - Fix a bug that TiDB Lightning's TiDB-backend cannot load any data when autocommit is disabled
