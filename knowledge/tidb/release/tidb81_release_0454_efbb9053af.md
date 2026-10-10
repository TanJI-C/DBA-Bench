# TiDB 7.1.1 release overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.1.md`
- Source Title: `TiDB 7.1.1 Release Notes`
- Source Heading Path: `TiDB 7.1.1 Release Notes | TiDB 7.1.1 Release Notes > Compatibility changes | TiDB 7.1.1 Release Notes > Compatibility changes > Behavior changes | TiDB 7.1.1 Release Notes > Improvements`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `ticdc`, `lightning`, `dumpling`
- Topic Tags: `release-notes`, `compatibility`, `behavior-changes`, `system-variables`, `plan-cache`, `stale-read`, `swagger-api`, `oauthbearer`, `kafka`, `checksum`, `export`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0454_efbb9053af`
- Source ID: `tidb-docs-8.1:releases/release-7.1.1.md#tidb-7-1-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3dbd43d3e9754a4f3bfa32ac29d249c135b1c72d5e78a3bc73256c23ac9a0f8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.1#tidb-7-1-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.1 release-note coverage of compatibility changes, behavior changes, or improvements across TiDB, PD, TiCDC, TiDB Lightning, Dumpling, and TiDB Binlog.
- Retrieval Keywords: TiDB 7.1.1 Release Notes, Compatibility changes, Behavior changes, Improvements, tidb_lock_unchanged_keys, lock unchanged keys, TiCDC splits an event into delete and insert events, primary key or non-null unique index value is modified, Plan Cache supports queries with more than 200 parameters, stale read retry leader encounters a lock, PD blocks Swagger API by default, Swagger server is disabled, OAUTHBEARER authentication, replication to Kafka, ClientTSOStreamClosed, checksum phase, Verify checksum through SQL after the import, Dumpling --sql parameter, Drainer initialization time and memory usage
- Follow-up Guidance: For the TiCDC update-event behavior change, the source points to documentation about transactions containing a single update change.
- Classification Note: This is a release-notes summary chunk covering 7.1.1 compatibility changes, behavior changes, and cross-component improvements rather than a task procedure.

## Official Source Content

# TiDB 7.1.1 Release Notes

Release date: July 24, 2023

TiDB version: 7.1.1

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.1/production-deployment-using-tiup)
## Compatibility changes

- TiDB introduces a new system variable `tidb_lock_unchanged_keys` to control whether to lock unchanged keys [#44714](https://github.com/pingcap/tidb/issues/44714) @[ekexium](https://github.com/ekexium)
### Behavior changes

- When processing update event, TiCDC splits an event into delete and insert events if the primary key or non-null unique index value is modified in the event. For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#transactions-containing-a-single-update-change).
## Improvements

+ TiDB

    - Plan Cache supports queries with more than 200 parameters [#44823](https://github.com/pingcap/tidb/issues/44823) @[qw4990](https://github.com/qw4990)
    - Optimize the performance of reading the dumped chunks from disk [#45125](https://github.com/pingcap/tidb/issues/45125) @[YangKeao](https://github.com/YangKeao)
    - Optimize the logic of constructing index scan range so that it supports converting complex conditions into index scan range [#41572](https://github.com/pingcap/tidb/issues/41572) [#44389](https://github.com/pingcap/tidb/issues/44389) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - When the retry leader of stale read encounters a lock, TiDB forcibly retries with the leader after resolving the lock, which avoids unnecessary overhead [#43659](https://github.com/pingcap/tidb/issues/43659) @[you06](https://github.com/you06)

+ PD

    - PD blocks Swagger API by default when the Swagger server is disabled [#6786](https://github.com/tikv/pd/issues/6786) @[bufferflies](https://github.com/bufferflies)

+ Tools

    + TiCDC

        - Optimize the encoding format of binary fields when TiCDC replicates data to object storage services [#9373](https://github.com/pingcap/tiflow/issues/9373) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Support the OAUTHBEARER authentication in the scenario of replication to Kafka [#8865](https://github.com/pingcap/tiflow/issues/8865) @[hi-rustin](https://github.com/Rustin170506)

    + TiDB Lightning

        - Improve the retry logic of TiDB Lightning for the PD `ClientTSOStreamClosed` error during the checksum phase [#45301](https://github.com/pingcap/tidb/issues/45301) @[lance6716](https://github.com/lance6716)
        - Verify checksum through SQL after the import to improve stability of verification [#41941](https://github.com/pingcap/tidb/issues/41941) @[GMHDBJD](https://github.com/GMHDBJD)

    + Dumpling

        - Dumpling avoids executing table queries when the `--sql` parameter is used, thereby reducing the export overhead [#45239](https://github.com/pingcap/tidb/issues/45239) @[lance6716](https://github.com/lance6716)

    + TiDB Binlog

        - Optimize the method of retrieving table information to reduce the initialization time and memory usage of Drainer [#1137](https://github.com/pingcap/tidb-binlog/issues/1137) @[lichunzhu](https://github.com/lichunzhu)
