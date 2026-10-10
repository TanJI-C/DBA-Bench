# 7.2.0 improvements across TiDB, TiKV, PD, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.2.0.md`
- Source Title: `TiDB 7.2.0 Release Notes`
- Source Heading Path: `TiDB 7.2.0 Release Notes > Improvements`
- Source Line Ranges: `209-256`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `br`, `ticdc`, `dm`, `lightning`
- Topic Tags: `improvements`, `stale-read`, `index-scan`, `monitoring-metrics`, `long-running-transactions`, `mysql-protocol-compression`, `utf8-compatibility`, `sql-assignment`, `pd-connections`, `resource-control`, `gzip-compression`, `leader-election`, `bucket-splitting`, `azure-blob-storage`, `kafka-replication`, `oauthbearer`, `compressed-binlog`, `import-retry`, `checksum-verification`, `oom-optimization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0492_480bca0a20`
- Source ID: `tidb-docs-8.1:releases/release-7.2.0.md#improvements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f7b5383af82d794843c7435a54b3fbe93ce9eaa2fa6b1abecfe1d192db73f569`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.2.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.2.0 improvement items across TiDB, TiKV, PD, BR, TiCDC, DM, and TiDB Lightning, including new metrics, protocol support, configuration names, and replication or import related enhancements.
- Retrieval Keywords: TiDB 7.2.0 Improvements, constructing index scan range, complex conditions into index scan range, Stale Read OPS, Stale Read Traffic, stale read retry leader encounters a lock, estimated time to calculate stale read ts, logs and system variables for long-running transactions, compressed MySQL protocol, zlib, zstd, utf8, utf8bm3, legacy three-byte UTF-8, := for assignment in UPDATE statements, pd.retry-interval, resource control scheduling algorithm, global resource usage, check_leader requests, gzip compression, related metrics for check_leader requests, detailed time information during TiKV handling write commands, separate gRPC connection for PD leader election, bucket splitting by default, hotspot issues in multi-Region scenarios, Azure Blob Storage, shared access signature, SAS, TiCDC object storage service DDL directory structure, OAUTHBEARER, replication to Kafka, outputting only the handle keys for the DELETE operation, DM compressed binlogs in MySQL 8.0, incremental replication, TiDB Lightning retry mechanism during import, leader switching, Verify checksum through SQL after the import, OOM issues when importing wide tables
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note improvement summary because it enumerates enhancement items introduced in TiDB 7.2.0 across multiple components and tools.

## Official Source Content

## Improvements

+ TiDB

    - Optimize the logic of constructing index scan range so that it supports converting complex conditions into index scan range [#41572](https://github.com/pingcap/tidb/issues/41572) [#44389](https://github.com/pingcap/tidb/issues/44389) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Add new monitoring metrics `Stale Read OPS` and `Stale Read Traffic` [#43325](https://github.com/pingcap/tidb/issues/43325) @[you06](https://github.com/you06)
    - When the retry leader of stale read encounters a lock, TiDB forcibly retries with the leader after resolving the lock, which avoids unnecessary overhead [#43659](https://github.com/pingcap/tidb/issues/43659) @[you06](https://github.com/you06)
    - Use estimated time to calculate stale read ts and reduce the overhead of stale read [#44215](https://github.com/pingcap/tidb/issues/44215) @[you06](https://github.com/you06)
    - Add logs and system variables for long-running transactions [#41471](https://github.com/pingcap/tidb/issues/41471) @[crazycs520](https://github.com/crazycs520)
    - Support connecting to TiDB through the compressed MySQL protocol, which improves the performance of data-intensive queries under low bandwidth networks and saves bandwidth costs. This supports both `zlib` and `zstd` based compression. [#22605](https://github.com/pingcap/tidb/issues/22605) @[dveeden](https://github.com/dveeden)
    - Recognize both `utf8` and `utf8bm3` as the legacy three-byte UTF-8 character set encodings, which facilitates the migration of tables with legacy UTF-8 encodings from MySQL 8.0 to TiDB [#26226](https://github.com/pingcap/tidb/issues/26226) @[dveeden](https://github.com/dveeden)
    - Support using `:=` for assignment in `UPDATE` statements [#44751](https://github.com/pingcap/tidb/issues/44751) @[CbcWestwolf](https://github.com/CbcWestwolf)

+ TiKV

    - Support configuring the retry interval of PD connections in scenarios such as connection request failures using `pd.retry-interval` [#14964](https://github.com/tikv/tikv/issues/14964) @[rleungx](https://github.com/rleungx)
    - Optimize the resource control scheduling algorithm by incorporating the global resource usage [#14604](https://github.com/tikv/tikv/issues/14604) @[Connor1996](https://github.com/Connor1996)
    - Use gzip compression for `check_leader` requests to reduce traffic [#14553](https://github.com/tikv/tikv/issues/14553) @[you06](https://github.com/you06)
    - Add related metrics for `check_leader` requests [#14658](https://github.com/tikv/tikv/issues/14658) @[you06](https://github.com/you06)
    - Provide detailed time information during TiKV handling write commands [#12362](https://github.com/tikv/tikv/issues/12362) @[cfzjywxk](https://github.com/cfzjywxk)

+ PD

    - Use a separate gRPC connection for PD leader election to prevent the impact of other requests [#6403](https://github.com/tikv/pd/issues/6403) @[rleungx](https://github.com/rleungx)
    - Enable the bucket splitting by default to mitigate hotspot issues in multi-Region scenarios [#6433](https://github.com/tikv/pd/issues/6433) @[bufferflies](https://github.com/bufferflies)

+ Tools

    + Backup & Restore (BR)

        - Support access to Azure Blob Storage by shared access signature (SAS) [#44199](https://github.com/pingcap/tidb/issues/44199) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Optimize the structure of the directory where data files are stored when a DDL operation occurs in the scenario of replication to an object storage service [#8891](https://github.com/pingcap/tiflow/issues/8891) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Support the OAUTHBEARER authentication in the scenario of replication to Kafka [#8865](https://github.com/pingcap/tiflow/issues/8865) @[hi-rustin](https://github.com/Rustin170506)
        - Add the option of outputting only the handle keys for the `DELETE` operation in the scenario of replication to Kafka [#9143](https://github.com/pingcap/tiflow/issues/9143) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiDB Data Migration (DM)

        - Support reading compressed binlogs in MySQL 8.0 as a data source for incremental replication [#6381](https://github.com/pingcap/tiflow/issues/6381) @[dveeden](https://github.com/dveeden)

    + TiDB Lightning

        - Optimize the retry mechanism during import to avoid errors caused by leader switching [#44263](https://github.com/pingcap/tidb/issues/44263) @[lance6716](https://github.com/lance6716)
        - Verify checksum through SQL after the import to improve stability of verification [#41941](https://github.com/pingcap/tidb/issues/41941) @[GMHDBJD](https://github.com/GMHDBJD)
        - Optimize TiDB Lightning OOM issues when importing wide tables [#43853](https://github.com/pingcap/tidb/issues/43853) @[D3Hunter](https://github.com/D3Hunter)
