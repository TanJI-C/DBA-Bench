# Compatibility and behavior changes in 7.4.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Compatibility changes | TiDB 7.4.0 Release Notes > Compatibility changes > Behavior changes`
- Source Line Ranges: `281-298`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `sql`, `ticdc`, `tiflash`, `tidb`
- Topic Tags: `upgrade`, `compatibility`, `mysql-8-0`, `behavior-changes`, `downgrade`, `tso`, `information-schema`, `update-events`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0511_f939aa2c8d`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cdf36e5a2651e95242151cf5e0af41f4171dd0db9de11cefce88380a1bf9f005`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about TiDB 7.4.0 compatibility or behavior changes after upgrading from v7.3.0, including MySQL 8.0 compatibility, TiFlash downgrade behavior, TSO parsing, information_schema additions, or TiCDC update event behavior.
- Retrieval Keywords: TiDB 7.4.0 compatibility changes, Behavior changes, upgrade from v7.3.0, MySQL 8.0 compatibility, version() returns 8.0.11, TiFlash in-place downgrade not supported, PageStorage V3 compaction, TIDB_PARSE_TSO_LOGICAL(), logical part of TSO timestamp, information_schema.CHECK_CONSTRAINTS, TiCDC splits update into delete and insert, delete events preceding insert events, transactions containing multiple changes
- Follow-up Guidance: The source notes that upgrades from v7.2.0 or earlier might also require checking compatibility changes introduced in intermediate versions.
- Classification Note: This chunk is classified as compatibility and behavior changes because it lists upgrade-impacting changes introduced in TiDB 7.4.0.

## Official Source Content

## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v7.3.0 to the current version (v7.4.0). If you are upgrading from v7.2.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.
### Behavior changes

- Starting with v7.4.0, TiDB is compatible with essential features of MySQL 8.0, and `version()` returns the version prefixed with `8.0.11`.

- After TiFlash is upgraded to v7.4.0 from an earlier version, in-place downgrading to the original version is not supported. This is because, starting from v7.4, TiFlash optimizes the data compaction logic of PageStorage V3 to reduce the read and write amplification generated during data compaction, which leads to changes to some of the underlying storage file names.

- A [`TIDB_PARSE_TSO_LOGICAL()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb-specific-functions) function is added to allow the extraction of the logical part of the TSO timestamp.

- The [`information_schema.CHECK_CONSTRAINTS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-check-constraints) table is added for improved compatibility with MySQL 8.0.

- For transactions containing multiple changes, if the primary key or non-null unique index value is modified in the update event, TiCDC splits an event into delete and insert events and ensures that all events follow the sequence of delete events preceding insert events. For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#transactions-containing-multiple-update-changes).
