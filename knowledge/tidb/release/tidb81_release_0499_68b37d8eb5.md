# 7.3.0 improvements across TiDB, TiKV, PD, TiFlash, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.3.0.md`
- Source Title: `TiDB 7.3.0 Release Notes`
- Source Heading Path: `TiDB 7.3.0 Release Notes > Improvements`
- Source Line Ranges: `229-264`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`
- Topic Tags: `improvements`, `system-variables`, `optimizer`, `session-management`, `locking-functions`, `disk-spill`, `metrics`, `safe-ts`, `resolved-ts`, `swagger-api`, `etcd`, `memory-optimization`, `storage-format`, `backup`, `azure-blob-storage`, `encryption`, `open-protocol`, `storage-sink`, `kafka-sink`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0499_68b37d8eb5`
- Source ID: `tidb-docs-8.1:releases/release-7.3.0.md#improvements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `865816420a1eb4be94b21151f839d096c11fe0b1eef67d8775be16b1fe73607c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.3.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.3.0 improvement items across TiDB, TiKV, PD, TiFlash, BR, and TiCDC, including new variables, metrics, commands, API behavior, storage format, and sink or backup enhancements.
- Retrieval Keywords: TiDB 7.3.0 Improvements, tidb_opt_enable_non_eval_scalar_subquery, EXPLAIN executes subqueries in advance during optimization phase, Global Kill, Control+C terminate current session, IS_FREE_LOCK(), IS_USED_LOCK(), reading dumped chunks from disk, Optimizer Fix Controls, Index Join inner table overestimation, Max gap of safe-ts, Min safe ts region, tikv-ctl get-region-read-progress, resolved-ts, safe-ts, Swagger API blocked by default, Swagger server is not enabled, Improve the high availability of etcd, GetRegions requests memory consumption, storage.format_version = 5, DTFile format version 5, reduce the number of physical files, BR Azure Blob Storage encryption scope, BR Azure Blob Storage encryption key, server-side encryption, TiCDC Open Protocol updated column values, Storage Sink hexadecimal encoding, AWS DMS format specifications, Kafka Sink sending only handle key data, message exceeds the Kafka topic limit
- Follow-up Guidance: The chunk points to related documentation links for the system variable, Global Kill, TiFlash configuration, and TiCDC Kafka sink handle-key behavior.
- Classification Note: This is classified as a release improvement summary because the official content lists enhancements introduced in TiDB 7.3.0 across multiple components.

## Official Source Content

## Improvements

+ TiDB

    - Introduce a new system variable [`tidb_opt_enable_non_eval_scalar_subquery`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_non_eval_scalar_subquery-new-in-v730) to control whether the `EXPLAIN` statement executes subqueries in advance during the optimization phase [#22076](https://github.com/pingcap/tidb/issues/22076) @[winoros](https://github.com/winoros)
    - When [Global Kill](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610) is enabled, you can terminate the current session by pressing <kbd>Control+C</kbd> [#8854](https://github.com/pingcap/tidb/issues/8854) @[pingyu](https://github.com/pingyu)
    - Support the `IS_FREE_LOCK()` and `IS_USED_LOCK()` locking functions [#44493](https://github.com/pingcap/tidb/issues/44493) @[dveeden](https://github.com/dveeden)
    - Optimize the performance of reading the dumped chunks from disk [#45125](https://github.com/pingcap/tidb/issues/45125) @[YangKeao](https://github.com/YangKeao)
    - Optimize the overestimation issue of the inner table of Index Join by using Optimizer Fix Controls [#44855](https://github.com/pingcap/tidb/issues/44855) @[time-and-fate](https://github.com/time-and-fate)

+ TiKV

    - Add the `Max gap of safe-ts` and `Min safe ts region` metrics and introduce the `tikv-ctl get-region-read-progress` command to better observe and diagnose the status of resolved-ts and safe-ts [#15082](https://github.com/tikv/tikv/issues/15082) @[ekexium](https://github.com/ekexium)

+ PD

    - Support blocking the Swagger API by default when the Swagger server is not enabled [#6786](https://github.com/tikv/pd/issues/6786) @[bufferflies](https://github.com/bufferflies)
    - Improve the high availability of etcd [#6554](https://github.com/tikv/pd/issues/6554) [#6442](https://github.com/tikv/pd/issues/6442) @[lhy1024](https://github.com/lhy1024)
    - Reduce the memory consumption of `GetRegions` requests [#6835](https://github.com/tikv/pd/issues/6835) @[lhy1024](https://github.com/lhy1024)

+ TiFlash

    - Support a new DTFile format version [`storage.format_version = 5`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration) to reduce the number of physical files (experimental) [#7595](https://github.com/pingcap/tiflash/issues/7595) @[hongyunyan](https://github.com/hongyunyan)

+ Tools

    + Backup & Restore (BR)

        - When backing up data to Azure Blob Storage using BR, you can specify either an encryption scope or an encryption key for server-side encryption [#45025](https://github.com/pingcap/tidb/issues/45025) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Optimize the message size of the Open Protocol output to make it include only the updated column values when sending `UPDATE` events [#9336](https://github.com/pingcap/tiflow/issues/9336) @[3AceShowHand](https://github.com/3AceShowHand)
        - Storage Sink now supports hexadecimal encoding for HEX formatted data, making it compatible with AWS DMS format specifications [#9373](https://github.com/pingcap/tiflow/issues/9373) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Kafka Sink supports [sending only handle key data](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#handle-messages-that-exceed-the-kafka-topic-limit) when the message is too large, reducing the size of the message [#9382](https://github.com/pingcap/tiflow/issues/9382) @[3AceShowHand](https://github.com/3AceShowHand)
