# Compatibility changes overview in v6.6.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Compatibility changes | TiDB 6.6.0 Release Notes > Compatibility changes > MySQL compatibility | TiDB 6.6.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `332-349`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `sql`, `tidb`
- Topic Tags: `upgrade`, `compatibility`, `mysql-compatibility`, `foreign-keys`, `multi-valued-indexes`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0419_f59bb10639`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b83b6bf7f79e0670cc2073e90e3a54e53176f45f37b96c8b7e5b6f76e08f3c85`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB v6.6.0 compatibility changes for upgrades from v6.5.0, especially MySQL-compatible foreign key constraints and multi-valued indexes.
- Retrieval Keywords: TiDB 6.6.0 Compatibility changes, upgrade from v6.5.0 to v6.6.0, MySQL compatibility, foreign key constraints experimental, MySQL-compatible foreign key constraints, multi-valued indexes experimental, MySQL-compatible multi-valued indexes, sql-statement-create-index#multi-valued-indexes, System variables
- Follow-up Guidance: The source says that upgrades from v6.4.0 or earlier might also need compatibility changes from intermediate versions and points to the SQL section and related documentation for foreign keys and multi-valued indexes.
- Classification Note: This is classified as release content because it provides an upgrade-oriented compatibility overview, including MySQL compatibility items and a system variables heading for v6.6.0.

## Official Source Content

## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v6.5.0 to the current version (v6.6.0). If you are upgrading from v6.4.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.
### MySQL compatibility

* Support MySQL-compatible foreign key constraints (experimental) [#18209](https://github.com/pingcap/tidb/issues/18209) @[crazycs520](https://github.com/crazycs520)

    For more information, see the [SQL](#sql) section in this document and [documentation](https://docs.pingcap.com/tidb/stable/foreign-key).

* Support the MySQL-compatible multi-valued indexes (experimental) [#39592](https://github.com/pingcap/tidb/issues/39592) @[xiongjiwei](https://github.com/xiongjiwei) @[qw4990](https://github.com/qw4990)

    For more information, see the [SQL](#sql) section in this document and [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#multi-valued-indexes).
### System variables
