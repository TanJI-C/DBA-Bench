# Relay log internal mechanism, storage layout, and receive position

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/relay-log.md`
- Source Title: `Data Migration Relay Log`
- Source Heading Path: `Data Migration Relay Log > Internal mechanism of relay log | Data Migration Relay Log > Internal mechanism of relay log > Directory structure | Data Migration Relay Log > Internal mechanism of relay log > The position where DM receives the binlog`
- Source Line Ranges: `314-390`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `relay-log`, `directory-structure`, `subdir`, `server-uuid-index`, `relay-meta`, `checkpoint`, `binlog-position`, `gtid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0030_07d1d8b7b8`
- Source ID: `tidb-docs-8.1:dm/relay-log.md#internal-mechanism-of-relay-log`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `72270bf90ad2ca88ca584ce433a96f9cf3c0f158769f16ed041bf0af8e0895b2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/relay-log#internal-mechanism-of-relay-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/relay-log.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the relay log storage layout, the meaning of `subdir`, `server-uuid.index`, and `relay.meta`, or the positions from which DM-worker resumes receiving binlog data.
- Retrieval Keywords: Internal mechanism of relay log, directory structure, subdir, server-uuid.index, relay.meta, binlog-name, binlog-pos, binlog-gtid, DM-worker, dm_meta schema, checkpoint, relay-binlog-name, relay-binlog-gtid, GTID mode, non-GTID mode, The position where DM receives the binlog
- Follow-up Guidance: The source also notes that if the upstream relay log is purged, an error occurs, and in that case `relay-binlog-gtid` is needed to specify the start position of the migration.
- Classification Note: This is classified as an architecture chunk because the official content explains relay log internal structure, metadata files, and the rules DM uses to determine the binlog receive position.

## Official Source Content

## Internal mechanism of relay log

This section introduces the internal mechanism of relay log.
### Directory structure

An example of the directory structure of the local storage for a relay log:

```
<deploy_dir>/<relay_log>/
|-- 7e427cc0-091c-11e9-9e45-72b7c59d52d7.000001
|   |-- mysql-bin.000001
|   |-- mysql-bin.000002
|   |-- mysql-bin.000003
|   |-- mysql-bin.000004
|   `-- relay.meta
|-- 842965eb-091c-11e9-9e45-9a3bff03fa39.000002
|   |-- mysql-bin.000001
|   `-- relay.meta
`-- server-uuid.index
```

- `subdir`:

    - DM-worker stores the binlog migrated from the upstream database in the same directory. Each directory is a `subdir`.

    - `subdir` is named in the format of `<Upstream database UUID>.<Local subdir serial number>`.

    - After a switch between primary and secondary instances in the upstream, DM-worker generates a new `subdir` directory with an incremental serial number.

    - In the above example, for the `7e427cc0-091c-11e9-9e45-72b7c59d52d7.000001` directory, `7e427cc0-091c-11e9-9e45-72b7c59d52d7` is the upstream database UUID and `000001` is the local `subdir` serial number.

- `server-uuid.index`: records a list of the currently available `subdir` directories.

- `relay.meta`: stores the information of the migrated binlog in each `subdir`. For example,

    ```bash
    cat c0149e17-dff1-11e8-b6a8-0242ac110004.000001/relay.meta
    ```

    ```
    binlog-name = "mysql-bin.000010"                            # The name of the currently migrated binlog.
    binlog-pos = 63083620                                       # The position of the currently migrated binlog.
    binlog-gtid = "c0149e17-dff1-11e8-b6a8-0242ac110004:1-3328" # GTID of the currently migrated binlog.
    ```

    There might also be multiple GTIDs:

    ```bash
    cat 92acbd8a-c844-11e7-94a1-1866daf8accc.000001/relay.meta
    ```

    ```
    binlog-name = "mysql-bin.018393"
    binlog-pos = 277987307
    binlog-gtid = "3ccc475b-2343-11e7-be21-6c0b84d59f30:1-14,406a3f61-690d-11e7-87c5-6c92bf46f384:1-94321383,53bfca22-690d-11e7-8a62-18ded7a37b78:1-495,686e1ab6-c47e-11e7-a42c-6c92bf46f384:1-34981190,03fc0263-28c7-11e7-a653-6c0b84d59f30:1-7041423,05474d3c-28c7-11e7-8352-203db246dd3d:1-170,10b039fc-c843-11e7-8f6a-1866daf8d810:1-308290454"
    ```
### The position where DM receives the binlog

- DM obtains the earliest position that each migration task needs from the saved checkpoint (in the downstream `dm_meta` schema by default). If this position is later than any of the following positions, DM starts to migrate from this position.

- If the local relay log is valid, which means that the relay log contains valid `server-uuid.index`, `subdir`, and `relay.meta` files, DM-worker recovers the migration from the position recorded in `relay.meta`.

- If there is no valid local relay log, but the upstream data source configuration file specifies `relay-binlog-name` or `relay-binlog-gtid`:

    - In non-GTID mode, if `relay-binlog-name` is specified, DM-worker starts to migrate from the specified binlog file.
    - In GTID mode, if `relay-binlog-gtid` is specified, DM-worker starts to migrate from the specified GTID.

- If there is no valid local relay log and the `relay-binlog-name` or `relay-binlog-gtid` is not specified in the DM configuration file:

    - In non-GTID mode, DM-worker starts to migrate from the earliest binlog that each subtask is migrating, until the latest binlog is migrated.
    - In GTID mode, DM-worker starts to migrate from the earliest GTID that each subtask is migrating, until the latest GTID is migrated.

    > **Note:**
    >
    > If the upstream relay log is purged, an error occurs. In this case, you need to configure [`relay-binlog-gtid`](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file#global-configuration) to specify the start position of the migration.
