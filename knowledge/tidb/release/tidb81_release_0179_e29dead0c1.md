# Improvements across TiDB, TiKV, TiFlash, and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.2.md`
- Source Title: `TiDB 4.0.2 Release Notes`
- Source Heading Path: `TiDB 4.0.2 Release Notes > Improvements`
- Source Line Ranges: `74-99`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`
- Topic Tags: `release-notes`, `improvements`, `query-latency`, `failure-recovery`, `coprocessor-pushdown`, `row-count-estimation`, `monitoring-metrics`, `upgrade-compatibility`, `memory-consumption`, `restore-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0179_e29dead0c1`
- Source ID: `tidb-docs-8.1:releases/release-4.0.2.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c9b076ca962612731a1cec76a7f31f1fe5fec6ba8b3c2e02c8eb96caf48b5df8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.2#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.2 improvement notes about performance, recovery, coprocessor behavior, estimation accuracy, monitoring metrics, upgrade compatibility, memory usage, or BR restore performance.
- Retrieval Keywords: TiDB 4.0.2 Improvements, CM-Sketch, query latency, Golang memory allocation, QPS recovery duration, TiKV server failure recovery process, aggregate functions to TiKV/TiFlash Coprocessor on partition tables, row count estimation, index equal conditions, PD client panic log, process_cpu_seconds_total, process_start_time_seconds, TiFlash backward compatibility, delta index, memory consumption of delta index, update algorithm for delta index, Backup & Restore, BR, pipelining the restore process
- Follow-up Guidance: 
- Classification Note: This is classified as a release chunk because the official content enumerates improvement items delivered in TiDB 4.0.2 for TiDB, TiKV, TiFlash, and BR.

## Official Source Content

## Improvements

+ TiDB

    - Reduce the query latency caused by the Golang memory allocation when CM-Sketch consumes too much memory [#17545](https://github.com/pingcap/tidb/pull/17545)
    - Reduce the QPS recovery duration of a cluster when a TiKV server is in the failure recovery process [#17681](https://github.com/pingcap/tidb/pull/17681)
    - Support pushing aggregate functions to TiKV/TiFlash Coprocessor on partition tables [#17655](https://github.com/pingcap/tidb/pull/17655)
    - Improve the accuracy of row count estimation for index equal conditions [#17611](https://github.com/pingcap/tidb/pull/17611)

+ TiKV

    - Improve the PD client panic log [#8093](https://github.com/tikv/tikv/pull/8093)
    - Add back the `process_cpu_seconds_total` and `process_start_time_seconds` monitoring metrics [#8029](https://github.com/tikv/tikv/pull/8029)

+ TiFlash

    - Improve backward compatibility when upgrading from an older version [#786](https://github.com/pingcap/tics/pull/786)
    - Reduce memory consumption of delta index [#787](https://github.com/pingcap/tics/pull/787)
    - Use the more efficient update algorithm for delta index [#794](https://github.com/pingcap/tics/pull/794)

+ Tools

    - Backup & Restore (BR)

        - Improve the performance by pipelining the restore process [#266](https://github.com/pingcap/br/pull/266)
