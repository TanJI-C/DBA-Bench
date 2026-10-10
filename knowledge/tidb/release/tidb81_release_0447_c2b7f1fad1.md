# Compatibility behavior changes and system variables section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes > Compatibility changes > Behavior changes | TiDB 7.1.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `294-305`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `tidb`, `lightning`, `pd`, `br`
- Topic Tags: `compatibility`, `behavior-changes`, `security`, `deprecation`, `upgrade`, `tiflash`, `grpc`, `lightning`, `scheduler`, `flashback`, `restore`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0447_c2b7f1fad1`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#behavior-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a2b6340743a7f40e9eac27055d0cfb445a205539702c43adee5c6f0c93766bdb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#behavior-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.0 compatibility behavior changes involving TiFlash HTTP port deprecation, TiDB Lightning pause-pd-scheduler-scope scheduling behavior, or FLASHBACK CLUSTER TO TIMESTAMP issues, and when locating the start of the System variables section.
- Retrieval Keywords: TiDB 7.1.0 Behavior changes, System variables section start, TiFlash deprecates HTTP service port 8123, gRPC port replacement, INFORMATION_SCHEMA.TIFLASH_TABLES, INFORMATION_SCHEMA.TIFLASH_SEGMENTS, TiDB cannot read TiFlash system tables, TiDB Lightning pause-pd-scheduler-scope, pause global scheduling, Region that stores the target table data, target cluster version earlier than v6.1.0, change the value of the parameter to "global", FLASHBACK CLUSTER TO TIMESTAMP, Regions remain in the FLASHBACK process, TiDB snapshot backup and restore, #44292
- Follow-up Guidance: The content notes that if TiFlash is upgraded to v7.1.0, TiDB cannot read INFORMATION_SCHEMA.TIFLASH_TABLES and INFORMATION_SCHEMA.TIFLASH_SEGMENTS during the TiDB upgrade to v7.1.0, and it also states that if FLASHBACK CLUSTER TO TIMESTAMP hits the described issue, TiDB snapshot backup and restore can be used to restore data.
- Classification Note: This chunk is classified as a release note for shared self-managed compatibility changes because it describes behavior changes across TiFlash, TiDB Lightning, TiDB, PD, and BR in TiDB 7.1.0 and marks the transition into the System variables section.

## Official Source Content

### Behavior changes

* To improve security, TiFlash deprecates the HTTP service port (default `8123`) and uses the gRPC port as a replacement

    If you have upgraded TiFlash to v7.1.0, then during the TiDB upgrade to v7.1.0, TiDB cannot read the TiFlash system tables ([`INFORMATION_SCHEMA.TIFLASH_TABLES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tiflash-tables) and [`INFORMATION_SCHEMA.TIFLASH_SEGMENTS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tiflash-segments)).

* TiDB Lightning in TiDB versions from v6.2.0 to v7.0.0 decides whether to pause global scheduling based on the TiDB cluster version. When TiDB cluster version >= v6.1.0, scheduling is only paused for the Region that stores the target table data and is resumed after the target table import is complete. While for other versions, TiDB Lightning pauses global scheduling. Starting from TiDB v7.1.0, you can control whether to pause global scheduling by configuring [`pause-pd-scheduler-scope`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration). By default, TiDB Lightning pauses scheduling for the Region that stores the target table data. If the target cluster version is earlier than v6.1.0, an error occurs. In this case, you can change the value of the parameter to `"global"` and try again.

* When you use [`FLASHBACK CLUSTER TO TIMESTAMP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster) in TiDB v7.1.0, some Regions might remain in the FLASHBACK process even after the completion of the FLASHBACK operation. It is recommended to avoid using this feature in v7.1.0. For more information, see issue [#44292](https://github.com/pingcap/tidb/issues/44292). If you have encountered this issue, you can use the [TiDB snapshot backup and restore](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide) feature to restore data.
### System variables
