# TiDB 4.0.11 release overview, new features, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.11.md`
- Source Title: `TiDB 4.0.11 Release Notes`
- Source Heading Path: `TiDB 4.0.11 Release Notes | TiDB 4.0.11 Release Notes > New Features | TiDB 4.0.11 Release Notes > Improvements`
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`, `lightning`
- Topic Tags: `release-notes`, `new-features`, `improvements`, `collation`, `grafana`, `slow-query`, `coprocessor`, `import-performance`, `metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0160_060b2ecb12`
- Source ID: `tidb-docs-8.1:releases/release-4.0.11.md#tidb-4-0-11-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4f6e43ac1c6fe60e1f6e0c5879538a8333ad341b278ff31397332dc9a664835`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.11#tidb-4-0-11-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.11.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 4.0.11 release overview, including new features and improvements across TiDB, TiKV, PD, TiFlash, TiCDC, and TiDB Lightning.
- Retrieval Keywords: TiDB 4.0.11 Release Notes, 4.0.11 new features, 4.0.11 improvements, utf8_unicode_ci, utf8mb4_unicode_ci, cast_year_as_time, TiFlash Coprocessor thread pool, cop_pool_size, batch_cop_pool_size, multiple clusters in Grafana dashboards, slow query internal general metrics, RocksDB metrics to TiDB, Load Base Split, TiCDC capture metadata version information, changefeed metadata CLI version, TiDB Lightning create tables in parallel, skip splitting Regions, import progress bar
- Follow-up Guidance: The same release notes also include a Bug Fixes section for TiDB 4.0.11.
- Classification Note: This is a release-notes chunk because it summarizes the TiDB 4.0.11 release date, new features, and improvements for several components.

## Official Source Content

# TiDB 4.0.11 Release Notes

Release date: February 26, 2021

TiDB version: 4.0.11
## New Features

+ TiDB

    - Support the `utf8_unicode_ci` and `utf8mb4_unicode_ci` collations [#22558](https://github.com/pingcap/tidb/pull/22558)

+ TiKV

    - Support the `utf8mb4_unicode_ci` collation [#9577](https://github.com/tikv/tikv/pull/9577)
    - Support the `cast_year_as_time` collation [#9299](https://github.com/tikv/tikv/pull/9299)

+ TiFlash

    - Add a Coprocessor thread pool to queue Coprocessor requests for execution, which avoids out of memory (OOM) in some cases, and add the `cop_pool_size` and `batch_cop_pool_size` configuration items with the default values of `NumOfPhysicalCores * 2`
## Improvements

+ TiDB

    - Reorder inner joins that are simplified from outer joins [#22402](https://github.com/pingcap/tidb/pull/22402)
    - Support multiple clusters in Grafana dashboards [#22534](https://github.com/pingcap/tidb/pull/22534)
    - Add a workaround for the issue of multiple statements [#22468](https://github.com/pingcap/tidb/pull/22468)
    - Divide the metrics of slow query into `internal` and `general` [#22405](https://github.com/pingcap/tidb/pull/22405)
    - Add interface for `utf8_unicode_ci` and `utf8mb4_unicode_ci` collations [#22099](https://github.com/pingcap/tidb/pull/22099)

+ TiKV

    - Add metrics of server information for DBaaS [#9591](https://github.com/tikv/tikv/pull/9591)
    - Support multiple clusters in Grafana dashboards [#9572](https://github.com/tikv/tikv/pull/9572)
    - Report RocksDB metrics to TiDB [#9316](https://github.com/tikv/tikv/pull/9316)
    - Record the suspension time for Coprocessor tasks [#9277](https://github.com/tikv/tikv/pull/9277)
    - Add thresholds of key counts and key size for Load Base Split [#9354](https://github.com/tikv/tikv/pull/9354)
    - Check whether the file exists before data import [#9544](https://github.com/tikv/tikv/pull/9544)
    - Improve Fast Tune panels [#9180](https://github.com/tikv/tikv/pull/9180)

+ PD

    - Support multiple clusters in Grafana dashboards [#3398](https://github.com/pingcap/pd/pull/3398)

+ TiFlash

    - Optimize the performance of the `date_format` function
    - Optimize the memory consumption of handling ingest SST
    - Optimize the retrying logic in Batch Coprocessor to reduce the probability of Region error

+ Tools

    + TiCDC

        - Add the version information in the `capture` metadata and add the CLI version of a `changefeed` in the `changefeed` metadata [#1342](https://github.com/pingcap/tiflow/pull/1342)

    + TiDB Lightning

        - Create tables in parallel to improve import performance [#502](https://github.com/pingcap/tidb-lightning/pull/502)
        - Skip splitting Regions to improve import performance if the engine's total size is smaller than the Region size [#524](https://github.com/pingcap/tidb-lightning/pull/524)
        - Add a import progress bar and optimize the accuracy of restore progress [#506](https://github.com/pingcap/tidb-lightning/pull/506)
