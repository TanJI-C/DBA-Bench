# 6.2.0 improvements across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > Improvements`
- Source Line Ranges: `326-380`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `lightning`, `pd`, `ticdc`, `tidb`, `tiflash`, `tikv`, `tiup`
- Topic Tags: `improvements`, `sql`, `system-variables`, `observability`, `metrics`, `performance`, `ddl`, `memory-tracking`, `coprocessor`, `transactions`, `gzip`, `grafana`, `compaction`, `cpu-usage`, `mpp`, `backup`, `s3`, `redo-log`, `retryable-errors`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0330_287c5c7dd3`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `25cd731645a828fdc1dc975855cdec2d6d3310330c28415cd28ca573e21c5c3b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.2.0 improvement items across TiDB, TiKV, PD, TiFlash, BR, TiCDC, TiDB Lightning, and TiUP, including new SQL support, system variables, observability, performance, and deployment-related changes.
- Retrieval Keywords: TiDB 6.2.0 Improvements, SHOW COUNT(*) WARNINGS, SHOW COUNT(*) ERRORS, KILL command supports DDL operations, SHOW TABLES LIKE, SHOW DATABASES LIKE, tidb_enable_paging, INFORMATION_SCHEMA.DATA_LOCK_WAIT, optimistic transactions, transaction monitoring metrics, gzip metrics response, rocksdb.max-sub-compactions, CPU usage of a Region, Load Base Split, TiFlash MPP engine, UTF8_BIN, UTF8MB4_BIN, BR S3 rate limiting, TiCDC redo log, TiDB Lightning retryable errors, EOF, Read index not ready, Coprocessor timeout, TiUP node-exporter 1.3.1, blackbox-exporter 0.21.1
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release improvement summary because the official content lists new capabilities, optimizations, and tooling changes introduced in TiDB 6.2.0 across multiple components.

## Official Source Content

## Improvements

+ TiDB

    - Support the `SHOW COUNT(*) WARNINGS` and `SHOW COUNT(*) ERRORS` statements [#25068](https://github.com/pingcap/tidb/issues/25068) @[likzn](https://github.com/likzn)
    - Add validation check for some system variables [#35048](https://github.com/pingcap/tidb/issues/35048) @[morgo](https://github.com/morgo)
    - Optimize the error messages for some type conversions [#32744](https://github.com/pingcap/tidb/issues/32744) @[fanrenhoo](https://github.com/fanrenhoo)
    - The `KILL` command now supports DDL operations [#24144](https://github.com/pingcap/tidb/issues/24144) @[morgo](https://github.com/morgo)
    - Make the output of `SHOW TABLES/DATABASES LIKE …` more MySQL-compatible. The column names in the output contain the `LIKE` value [#35116](https://github.com/pingcap/tidb/issues/35116) @[likzn](https://github.com/likzn)
    - Improve the performance of JSON-related functions [#35859](https://github.com/pingcap/tidb/issues/35859) @[wjhuang2016](https://github.com/wjhuang2016)
    - Improve the verification speed of password login using SHA-2 [#35998](https://github.com/pingcap/tidb/issues/35998) @[virusdefender](https://github.com/virusdefender)
    - Simplify some log outputs [#36011](https://github.com/pingcap/tidb/issues/36011) @[dveeden](https://github.com/dveeden)
    - Optimize the Coprocessor communication protocol. This can greatly reduce the memory consumption of the TiDB processes when reading data, and further alleviate the OOM issue in the scenario of scanning tables and exporting data by Dumpling. The system variable `tidb_enable_paging` is introduced to control whether to enable this communication protocol (with the scope of SESSION or GLOBAL). This protocol is disabled by default. To enable it, set the variable value to `true` [#35633](https://github.com/pingcap/tidb/issues/35633) @[tiancaiama](https://github.com/tiancaiamao) @[wshwsh12](https://github.com/wshwsh12)
    - Optimize the accuracy of memory tracking for some operators (HashJoin, HashAgg, Update, Delete) ([#35634](https://github.com/pingcap/tidb/issues/35634), [#35631](https://github.com/pingcap/tidb/issues/35631), [#35635](https://github.com/pingcap/tidb/issues/35635) @[wshwsh12](https://github.com/wshwsh12)) ([#34096](https://github.com/pingcap/tidb/issues/34096) @[ekexium](https://github.com/ekexium))

    - The system table `INFORMATION_SCHEMA.DATA_LOCK_WAIT` supports recording the locking information of optimistic transactions [#34609](https://github.com/pingcap/tidb/issues/34609) @[longfangson](https://github.com/longfangsong)
    - Add some monitoring metrics for transactions [#34456](https://github.com/pingcap/tidb/issues/34456) @[longfangsong](https://github.com/longfangsong)

+ TiKV

    - Support compressing the metrics response using gzip to reduce the HTTP body size [#12355](https://github.com/tikv/tikv/issues/12355) @[glorv](https://github.com/glorv)
    - Improve the readability of the TiKV panel in Grafana Dashboard [#12007](https://github.com/tikv/tikv/issues/12007) @[kevin-xianliu](https://github.com/kevin-xianliu)
    - Optimize the commit pipeline performance of the Apply operator [#12898](https://github.com/tikv/tikv/issues/12898) @[ethercflow](https://github.com/ethercflow)
    - Support dynamically modifying the number of sub-compaction operations performed concurrently in RocksDB (`rocksdb.max-sub-compactions`) [#13145](https://github.com/tikv/tikv/issues/13145) @[ethercflow](https://github.com/ethercflow)

+ PD

    - Support the statistical dimension of CPU usage of a Region and enhance the usage scenarios of Load Base Split [#12063](https://github.com/tikv/tikv/issues/12063) @[Jmpotato](https://github.com/JmPotato)

+ TiFlash

    - Refine error handling of the TiFlash MPP engine, thereby enhancing stability [#5095](https://github.com/pingcap/tiflash/issues/5095) @[windtalker](https://github.com/windtalker) @[yibin87](https://github.com/yibin87)

    - Optimize the comparison and sorting of UTF8_BIN and UTF8MB4_BIN collations [#5294](https://github.com/pingcap/tiflash/issues/5294) @[solotzg](https://github.com/solotzg)

+ Tools

    - Backup & Restore (BR)

        - Adjust the backup data directory structure to fix backup failure caused by S3 rate limiting in large cluster backup [#30087](https://github.com/pingcap/tidb/issues/30087) @[MoCuishle28](https://github.com/MoCuishle28)

    - TiCDC

        - Reduce performance overhead caused by runtime context switching in multi-Region scenarios [#5610](https://github.com/pingcap/tiflow/issues/5610) @[hicqu](https://github.com/hicqu)

        - Optimize redo log performance, and fix meta and data inconsistency problems ([#6011](https://github.com/pingcap/tiflow/issues/6011) @[CharlesCheung96](https://github.com/CharlesCheung96)) ([#5924](https://github.com/pingcap/tiflow/issues/5924) @[zhaoxinyu](https://github.com/zhaoxinyu)) ([#6277](https://github.com/pingcap/tiflow/issues/6277) @[hicqu](https://github.com/hicqu))

    - TiDB Lightning

        - Add more retryable errors, including EOF, Read index not ready, and Coprocessor timeout [#36674](https://github.com/pingcap/tidb/issues/36674), [#36566](https://github.com/pingcap/tidb/issues/36566) @[D3Hunter](https://github.com/D3Hunter)

    - TiUP

        - When a new cluster is deployed using TiUP, node-exporter will use the [1.3.1](https://github.com/prometheus/node_exporter/releases/tag/v1.3.1) version, and blackbox-exporter will use the [0.21.1](https://github.com/prometheus/blackbox_exporter/releases/tag/v0.21.1) version, which ensures successful deployment in different systems and environments
