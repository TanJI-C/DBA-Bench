# Ease of use: TiKV API V2 GA and TiFlash replication progress

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > New features > Ease of use`
- Source Line Ranges: `144-167`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `tiflash`, `tidb`
- Topic Tags: `api-v2`, `rawkv`, `mvcc`, `cdc`, `multi-tenancy`, `configuration`, `replication-progress`, `information-schema`, `tiflash-replica`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0352_59b878bb75`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#ease-of-use`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `772095c4d7455997b8986a0efa6c46eab95e4e36c4a73486a21aacf589f261c8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#ease-of-use
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.4.0 release details about TiKV API V2 GA or about how TiFlash replication progress is shown in INFORMATION_SCHEMA.TIFLASH_REPLICA.
- Retrieval Keywords: TiKV API V2, api-version = 2, [storage], RawKV, MVCC, Change Data Capture, CDC, Transactional KV, Key Space, multi-tenancy, INFORMATION_SCHEMA.TIFLASH_REPLICA, PROGRESS, TiFlash replica, replication progress, TiKV to TiFlash
- Follow-up Guidance: The content points to the TiKV configuration file document for `api-version` and to the `INFORMATION_SCHEMA.TIFLASH_REPLICA` document for replication progress details.
- Classification Note: This is classified as a release note for shared components because it announces new 6.4.0 ease-of-use features spanning TiKV, TiDB, and TiFlash.

## Official Source Content

### Ease of use

* TiKV API V2 becomes generally available (GA) [#11745](https://github.com/tikv/tikv/issues/11745) @[pingyu](https://github.com/pingyu)

    Before v6.1.0, TiKV only provides basic Key Value read and write capability because it only stores the raw data passed in by the client. In addition, due to different coding methods and unscoped data ranges, TiDB, Transactional KV, and RawKV cannot be used at the same time in the same TiKV cluster; instead, multiple clusters are needed in this case, thus increasing machine and deployment costs.

    TiKV API V2 provides a new RawKV storage format and access interface, which delivers the following benefits:

    - Store data in MVCC with the change timestamp of the data recorded, based on which Change Data Capture (CDC) is implemented. This feature is experimental and is detailed in [TiKV-CDC](https://github.com/tikv/migration/blob/main/cdc/README.md).
    - Data is scoped according to different usage and API V2 supports co-existence of TiDB, Transactional KV, and RawKV applications in a single cluster.
    - Reserve the Key Space field to support features such as multi-tenancy.

  To enable TiKV API V2, set `api-version = 2` in the `[storage]` section of the TiKV configuration file.

  For more information, see [User document](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#api-version-new-in-v610).

* Improve the accuracy of TiFlash data replication progress [#4902](https://github.com/pingcap/tiflash/issues/4902) @[hehechen](https://github.com/hehechen)

    In TiDB, the `PROGRESS` field of the `INFORMATION_SCHEMA.TIFLASH_REPLICA` table is used to indicate the progress of data replication from the corresponding tables in TiKV to the TiFlash replicas. In earlier TiDB versions, the `PROCESS` field only provides the progress of data replication during the creation of the TiFlash replicas. After a TiFlash replica is created, if new data is imported to a corresponding table in TiKV, this field will not be updated to show the replication progress from TiKV to TiFlash for the new data.

    In v6.4.0, TiDB improves the update mechanism of data replication progress for TiFlash replicas. After a TiFlash replica is created, if new data is imported to a corresponding table in TiKV, the `PROGRESS` value in the [`INFORMATION_SCHEMA.TIFLASH_REPLICA`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tiflash-replica) table will be updated to show the actual replication progress from TiKV to TiFlash for the new data. With this improvement, you can easily view the actual progress of TiFlash data replication.

    For more information, see [User document](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tiflash-replica).
