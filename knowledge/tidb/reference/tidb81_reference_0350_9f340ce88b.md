# TiDB specific functions overview table

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/tidb-functions.md`
- Source Title: `TiDB Specific Functions`
- Source Heading Path: `TiDB Specific Functions`
- Source Line Ranges: `5-53`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`, `ticdc`
- Topic Tags: `function-overview`, `sql-functions`, `resource-control`, `stale-read`, `tso`, `plan-decoding`, `sql-digests`, `ddl-owner`, `row-checksum`, `shard-index`, `version`, `vitess-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0350_9f340ce88b`
- Source ID: `tidb-docs-8.1:functions-and-operators/tidb-functions.md#tidb-specific-functions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a69838da14ab15d7ac8caf0a0eaa9545b03d73b0b16ae3b8d2f9b9a69e78eb6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb-specific-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/tidb-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of TiDB-specific SQL functions that are extensions not present in MySQL and want to identify the right function name by purpose.
- Retrieval Keywords: TiDB Specific Functions, TiDB extensions not present in MySQL, CURRENT_RESOURCE_GROUP(), TIDB_BOUNDED_STALENESS(), TIDB_CURRENT_TSO(), TIDB_DECODE_BINARY_PLAN(), TIDB_DECODE_KEY(), TIDB_DECODE_PLAN(), TIDB_DECODE_SQL_DIGESTS(), TIDB_ENCODE_SQL_DIGEST(), TIDB_IS_DDL_OWNER(), TIDB_PARSE_TSO(), TIDB_PARSE_TSO_LOGICAL(), TIDB_ROW_CHECKSUM(), TIDB_SHARD(), TIDB_VERSION(), VITESS_HASH(), resource group, stale read, TSO, binary plan, SQL digest, DDL Owner, row checksum, shard index, Vitess HASH compatibility
- Follow-up Guidance: Follow the specific function section for details such as `AS OF TIMESTAMP`, `tidb_current_ts`, FastPlan usage, `STATEMENTS_SUMMARY`, or resource group behavior when those identifiers match your query.
- Classification Note: This is a reference overview because the content is a function table that maps each TiDB-specific function name to a short description and related concept.

## Official Source Content

# TiDB Specific Functions

The following functions are TiDB extensions, and are not present in MySQL:

| Function name | Function description |
| :-------------- | :------------------------------------- |
| [`CURRENT_RESOURCE_GROUP()`](#current_resource_group)  | Returns the name of the resource group that the current session is bound to. See [using resource control to achieve resource isolation](https://docs.pingcap.com/tidb/stable/tidb-resource-control). |
| [`TIDB_BOUNDED_STALENESS()`](#tidb_bounded_staleness) | Instructs TiDB to read the most recent data within a specified time range. See [reading historical data using the `AS OF TIMESTAMP` clause](https://docs.pingcap.com/tidb/stable/as-of-timestamp). |
| [`TIDB_CURRENT_TSO()`](#tidb_current_tso) | Returns the current [TimeStamp Oracle (TSO) in TiDB](https://docs.pingcap.com/tidb/stable/tso). |
| [`TIDB_DECODE_BINARY_PLAN()`](#tidb_decode_binary_plan) | Decodes binary plans. |
| [`TIDB_DECODE_KEY()`](#tidb_decode_key) | Decodes a TiDB-encoded key entry into a JSON structure containing `_tidb_rowid` and `table_id`. These encoded keys can be found in some system tables and logging outputs. |
| [`TIDB_DECODE_PLAN()`](#tidb_decode_plan) | Decodes a TiDB execution plan. |
| [`TIDB_DECODE_SQL_DIGESTS()`](#tidb_decode_sql_digests) | Queries the normalized SQL statements (a form without formats and arguments) corresponding to a set of SQL digests in the cluster. |
| [`TIDB_ENCODE_SQL_DIGEST()`](#tidb_encode_sql_digest) | Gets a digest for a query string. |
| [`TIDB_IS_DDL_OWNER()`](#tidb_is_ddl_owner) | Checks whether or not the TiDB instance you are connected to is the DDL Owner. The DDL Owner is the TiDB instance that is tasked with executing DDL statements on behalf of all other nodes in the cluster. |
| [`TIDB_PARSE_TSO()`](#tidb_parse_tso) | Extracts the physical timestamp from a TiDB TSO timestamp. See also: [`tidb_current_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_current_ts). |
| [`TIDB_PARSE_TSO_LOGICAL()`](#tidb_parse_tso_logical) | Extracts the logical timestamp from a TiDB TSO timestamp. |
| [`TIDB_ROW_CHECKSUM()`](#tidb_row_checksum) | Queries the checksum value of a row. This function can only be used in `SELECT` statements within the FastPlan process. That is, you can query through statements like `SELECT TIDB_ROW_CHECKSUM() FROM t WHERE id = ?` or `SELECT TIDB_ROW_CHECKSUM() FROM t WHERE id IN (?, ?, ...)`. See also: [Data integrity validation for single-row data](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-integrity-check). |
| [`TIDB_SHARD()`](#tidb_shard) | Creates a shard index to scatter the index hotspot. A shard index is an expression index with a `TIDB_SHARD` function as the prefix.|
| [`TIDB_VERSION()`](#tidb_version) | Returns the TiDB version with additional build information. |
| [`VITESS_HASH()`](#vitess_hash) | Returns the hash of a number. This function is compatible with the `HASH` function of Vitess, and is intended to help the data migration from Vitess. |

| Function name | Function description |
| :-------------- | :------------------------------------- |
| [`CURRENT_RESOURCE_GROUP()`](#current_resource_group)  | Returns the resource group name that the current session is bound to. See [using resource control to achieve resource isolation](https://docs.pingcap.com/tidb/stable/tidb-resource-control). |
| [`TIDB_BOUNDED_STALENESS()`](#tidb_bounded_staleness) | Instructs TiDB to read most recent data within a specified time range. See [reading historical data using the `AS OF TIMESTAMP` clause](https://docs.pingcap.com/tidb/stable/as-of-timestamp). |
| [`TIDB_CURRENT_TSO()`](#tidb_current_tso) | Returns the current [TimeStamp Oracle (TSO) in TiDB](https://docs.pingcap.com/tidb/stable/tso). |
| [`TIDB_DECODE_BINARY_PLAN()`](#tidb_decode_binary_plan) | Decodes binary plans. |
| [`TIDB_DECODE_KEY()`](#tidb_decode_key) | Decodes a TiDB-encoded key entry into a JSON structure containing `_tidb_rowid` and `table_id`. These encoded keys can be found in some system tables and logging outputs. |
| [`TIDB_DECODE_PLAN()`](#tidb_decode_plan) | Decodes a TiDB execution plan. |
| [`TIDB_DECODE_SQL_DIGESTS()`](#tidb_decode_sql_digests) | Queries the normalized SQL statements (a form without formats and arguments) corresponding to a set of SQL digests in the cluster. |
| [`TIDB_ENCODE_SQL_DIGEST()`](#tidb_encode_sql_digest) | Gets a digest for a query string. |
| [`TIDB_IS_DDL_OWNER()`](#tidb_is_ddl_owner) | Checks whether or not the TiDB instance you are connected to is the DDL Owner. The DDL Owner is the TiDB instance that is tasked with executing DDL statements on behalf of all other nodes in the cluster. |
| [`TIDB_PARSE_TSO()`](#tidb_parse_tso) | Extracts the physical timestamp from a TiDB TSO timestamp. See also: [`tidb_current_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_current_ts). |
| [`TIDB_PARSE_TSO_LOGICAL()`](#tidb_parse_tso_logical) | Extracts the logical timestamp from a TiDB TSO timestamp. |
| [`TIDB_ROW_CHECKSUM()`](#tidb_row_checksum) | Queries the checksum value of a row. This function can only be used in `SELECT` statements within the FastPlan process. That is, you can query through statements like `SELECT TIDB_ROW_CHECKSUM() FROM t WHERE id = ?` or `SELECT TIDB_ROW_CHECKSUM() FROM t WHERE id IN (?, ?, ...)`. See also: [Data integrity validation for single-row data](https://docs.pingcap.com/tidb/stable/ticdc-integrity-check). |
| [`TIDB_SHARD()`](#tidb_shard) | Creates a shard index to scatter the index hotspot. A shard index is an expression index with a `TIDB_SHARD` function as the prefix.|
| [`TIDB_VERSION()`](#tidb_version) | Returns the TiDB version with additional build information. |
| [`VITESS_HASH()`](#vitess_hash) | Returns the hash of a number. This function is compatible with the `HASH` function of Vitess, and is intended to help the data migration from Vitess. |
