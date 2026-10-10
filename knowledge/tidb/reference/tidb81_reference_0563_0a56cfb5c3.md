# CREATE TABLE MySQL compatibility and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-table.md`
- Source Title: `CREATE TABLE | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE TABLE > MySQL compatibility | CREATE TABLE > See also`
- Source Line Ranges: `270-298`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `mysql-compatibility`, `index-types`, `fulltext`, `index-length`, `column-limits`, `partitioning`, `related-links`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0563_0a56cfb5c3`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-table.md#mysql-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f549439dca72a17cf15a0fc6b002ba5ddb0e3bd705855130d6098ac1a424edc8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about CREATE TABLE MySQL compatibility, ignored index syntax, FULLTEXT support status, index length limits, column count limits, supported partitioning types, or related statements.
- Retrieval Keywords: MySQL compatibility, spatial types, HASH, BTREE, RTREE, FULLTEXT, index_col_name, max-index-length, 3072 bytes, ASC DESC parsed but ignored, WITH PARSER, 1017 columns, 4096 columns, HASH partitioning, RANGE partitioning, LIST partitioning, KEY partitioning, Warning: Unsupported partition type %s, treat as normal table, DROP TABLE, CREATE TABLE LIKE, SHOW CREATE TABLE
- Follow-up Guidance: The source also links related statements and references including Data Types, DROP TABLE, CREATE TABLE LIKE, and SHOW CREATE TABLE.
- Classification Note: This is reference content because it summarizes compatibility rules, limits, warnings, and related SQL statements for CREATE TABLE.

## Official Source Content

## MySQL compatibility

* All of the data types except spatial types are supported.
* TiDB accepts index types such as `HASH`, `BTREE` and `RTREE` in syntax for compatibility with MySQL, but ignores them.
* TiDB supports parsing the `FULLTEXT` syntax but does not support using the `FULLTEXT` indexes.

* For compatibility, the `index_col_name` attribute supports the length option with a maximum length limit of 3072 bytes by default. The length limit can be changed through the `max-index-length` configuration option. For details, see [TiDB configuration file](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max-index-length).

* For compatibility, the `index_col_name` attribute supports the length option with a maximum length limit of 3072 bytes.

* The `[ASC | DESC]` in `index_col_name` is currently parsed but ignored (MySQL 5.7 compatible behavior).
* The `COMMENT` attribute does not support the `WITH PARSER` option.
* TiDB supports 1017 columns in a single table by default and 4096 columns at most. The corresponding number limit in InnoDB is 1017 columns, and the hard limit in MySQL is 4096 columns. For details, see [TiDB Limitations](https://docs.pingcap.com/tidb/stable/tidb-limitations).
* TiDB supports `HASH`, `RANGE`, `LIST`, and `KEY` [partitioning types](https://docs.pingcap.com/tidb/stable/partitioned-table#partitioning-types). For an unsupported partition type, TiDB returns `Warning: Unsupported partition type %s, treat as normal table`, where `%s` is the specific unsupported partition type.
## See also

* [Data Types](https://docs.pingcap.com/tidb/stable/data-type-overview)
* [DROP TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table)
* [CREATE TABLE LIKE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table-like)
* [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
