# Temporary table restrictions and migration tool support

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/temporary-tables.md`
- Source Title: `Temporary Tables`
- Source Heading Path: `Temporary Tables > Compatibility restrictions with other TiDB features | Temporary Tables > TiDB migration tool support | Temporary Tables > See also`
- Source Line Ranges: `293-332`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `ticdc`, `sql`
- Topic Tags: `temporary-tables`, `compatibility-restrictions`, `migration-tools`, `backup`, `replication`, `restore`, `limitations`, `version-requirements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0756_470e10c975`
- Source ID: `tidb-docs-8.1:temporary-tables.md#compatibility-restrictions-with-other-tidb-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad466b58cf219e8cb3fd8c5e84b7691983172a0237a0328f2293a2de6a860a76`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/temporary-tables#compatibility-restrictions-with-other-tidb-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/temporary-tables.md

## Retrieval Guidance

- Use When: Use this chunk when asking about temporary table compatibility restrictions in TiDB or how local and global temporary tables behave with BR, TiCDC, export, backup, restore, and replication.
- Retrieval Keywords: temporary tables compatibility restrictions, local temporary tables, global temporary tables, AUTO_RANDOM, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, Partitioned tables, SPLIT REGION, ADMIN CHECK TABLE, ADMIN CHECKSUM TABLE, FLASHBACK TABLE, RECOVER TABLE, CREATE TABLE LIKE temporary table, Stale Read, Foreign keys, SQL bindings, TiFlash replicas, Placement Rules, prepare plan cache, tidb_snapshot, TiDB migration tool support, BR v5.3.0 or later, TiCDC v5.3.0 or later, table definition is wrong, data on the tables are not exported
- Follow-up Guidance: The source also points to CREATE TABLE, CREATE TABLE LIKE, and DROP TABLE as related references.
- Classification Note: This is a reference chunk because it lists unsupported features and version-related migration tool behavior for local and global temporary tables in TiDB.

## Official Source Content

## Compatibility restrictions with other TiDB features

Local temporary tables and global temporary tables in TiDB are **NOT** compatible with the following TiDB features:

- `AUTO_RANDOM` columns
- `SHARD_ROW_ID_BITS` and `PRE_SPLIT_REGIONS` table options
- Partitioned tables
- `SPLIT REGION` statements
- `ADMIN CHECK TABLE` and `ADMIN CHECKSUM TABLE` statements
- `FLASHBACK TABLE` and `RECOVER TABLE` statements
- Executing `CREATE TABLE LIKE` statements based on a temporary table
- Stale Read
- Foreign keys
- SQL bindings
- TiFlash replicas
- Creating views on a temporary table
- Placement Rules
- Execution plans involving a temporary table are not cached by `prepare plan cache`.

Local temporary tables in TiDB do **NOT** support the following feature:

- Reading historical data using the `tidb_snapshot` system variable.
## TiDB migration tool support

Local temporary tables are not exported, backed up or replicated by TiDB migration tools, because these tables are visible only to the current session.

Global temporary tables are exported, backed up, and replicated by TiDB migration tools, because the table definition is globally visible. Note that the data on the tables are not exported.

> **Note:**
>
> - Replicating temporary tables using TiCDC requires TiCDC v5.3.0 or later. Otherwise, the table definition of the downstream table is wrong.
> - Backing up temporary tables using BR requires BR v5.3.0 or later. Otherwise, the table definitions of the backed temporary tables are wrong.
> - The cluster to export, the cluster after data restore, and the downstream cluster of a replication should support global temporary tables. Otherwise, an error is reported.
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [CREATE TABLE LIKE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table-like)
* [DROP TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table)
