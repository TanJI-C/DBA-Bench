# TiDB 5.2.2 release overview and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.2.md`
- Source Title: `TiDB 5.2.2 Release Notes`
- Source Heading Path: `TiDB 5.2.2 Release Notes | TiDB 5.2.2 Release Notes > Improvements`
- Source Line Ranges: `5-42`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `ticdc`
- Topic Tags: `release-date`, `version`, `improvements`, `debug-logging`, `backup-restore`, `flow-control`, `scheduler`, `dashboard-update`, `kafka`, `memory-usage`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0243_2a88df259c`
- Source ID: `tidb-docs-8.1:releases/release-5.2.2.md#tidb-5-2-2-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e8bf45854ffe5d81028fd143404debc564a40f92c653f0257e8c030ef7b8dd4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.2#tidb-5-2-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.2.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an overview of TiDB 5.2.2 release date, version, and the listed improvements across TiDB, TiKV, PD, Dashboard, and TiCDC.
- Retrieval Keywords: TiDB 5.2.2 Release Notes, Release Date October 29 2021, TiDB version 5.2.2, Improvements, affected SQL statements in the debug log, coprocessor encounters a lock, size of the backup and restore data, SQL logical layer, L0 flow control, raft client module, logging threads performance bottleneck, write queries statistics types, QPS dimensions in the hotspot scheduler, balance region scheduler retry limit, TiDB Dashboard v2021.10.08.1, evict leader scheduler, unhealthy peers, Kafka sink MaxMessageBytes, 64 MB to 1 MB, large messages are rejected by the Kafka Broker, memory usage in the relpication pipeline, monitoring items and alert rules, observability of synchronous links, historical error messages are displayed
- Follow-up Guidance: The same release notes also contain a Bug Fixes section for TiDB, TiKV, PD, TiFlash, TiCDC, and TiDB Binlog.
- Classification Note: This is a release overview chunk because the official content gives the TiDB 5.2.2 release date, version, and improvement items grouped by component.

## Official Source Content

# TiDB 5.2.2 Release Notes

Release Date: October 29, 2021

TiDB version: 5.2.2
## Improvements

+ TiDB

    - Show the affected SQL statements in the debug log when the coprocessor encounters a lock, which is helpful in diagnosing problems [#27718](https://github.com/pingcap/tidb/issues/27718)
    - Support showing the size of the backup and restore data when backing up and restoring data in the SQL logical layer [#27247](https://github.com/pingcap/tidb/issues/27247)

+ TiKV

    - Simplify the algorithm of L0 flow control [#10879](https://github.com/tikv/tikv/issues/10879)
    - Improve the error log report in the raft client module [#10983](https://github.com/tikv/tikv/pull/10983)
    - Improve logging threads to avoid them becoming a performance bottleneck [#10841](https://github.com/tikv/tikv/issues/10841)
    - Add more statistics types of write queries [#10507](https://github.com/tikv/tikv/issues/10507)

+ PD

    - Add more types of write queries to QPS dimensions in the hotspot scheduler [#3869](https://github.com/tikv/pd/issues/3869)
    - Support dynamically adjusting the retry limit of the balance region scheduler to improve the performance of the scheduler [#3744](https://github.com/tikv/pd/issues/3744)
    - Update TiDB Dashboard to v2021.10.08.1 [#4070](https://github.com/tikv/pd/pull/4070)
    - Support that the evict leader scheduler can schedule regions with unhealthy peers [#4093](https://github.com/tikv/pd/issues/4093)
    - Speed up the exit process of schedulers [#4146](https://github.com/tikv/pd/issues/4146)

+ Tools

    + TiCDC

        - Reduce the default value of the Kafka sink configuration item `MaxMessageBytes` from 64 MB to 1 MB to fix the issue that large messages are rejected by the Kafka Broker [#3104](https://github.com/pingcap/tiflow/pull/3104)
        - Reduce memory usage in the relpication pipeline [#2553](https://github.com/pingcap/tiflow/issues/2553) [#3037](https://github.com/pingcap/tiflow/pull/3037) [#2726](https://github.com/pingcap/tiflow/pull/2726)
        - Optimize monitoring items and alert rules to improve observability of synchronous links, memory GC, and stock data scanning processes [#2735](https://github.com/pingcap/tiflow/pull/2735) [#1606](https://github.com/pingcap/tiflow/issues/1606) [#3000](https://github.com/pingcap/tiflow/pull/3000) [#2985](https://github.com/pingcap/tiflow/issues/2985) [#2156](https://github.com/pingcap/tiflow/issues/2156)
        - When the sync task status is normal, no more historical error messages are displayed to avoid misleading users [#2242](https://github.com/pingcap/tiflow/issues/2242)
