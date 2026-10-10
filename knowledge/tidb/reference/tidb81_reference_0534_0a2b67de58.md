# ALTER TABLE compatibility restrictions and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-table.md`
- Source Title: `ALTER TABLE | TiDB SQL Statement Reference`
- Source Heading Path: `ALTER TABLE > MySQL compatibility | ALTER TABLE > See also`
- Source Line Ranges: `166-201`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `alter-table`, `mysql-compatibility`, `restrictions`, `partitioned-tables`, `generated-columns`, `data-types`, `cached-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0534_0a2b67de58`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-table.md#mysql-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fb261193e7438db64416379950bd06653f96022ecfb37110a0867c090ca9ace3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-table.md

## Retrieval Guidance

- Use When: Use this chunk when you need MySQL compatibility restrictions for ALTER TABLE in TiDB or pointers to related ALTER, CREATE, DROP, and SHOW statements.
- Retrieval Keywords: ALTER TABLE MySQL compatibility, multiple schema objects in a single ALTER TABLE statement, validated according to the table schema before execution, left to right, Reorg-Data types on primary key columns, partitioned tables, generated columns, CAST function behavior, Spatial data types are not supported, ALTER TABLE t CACHE | NOCACHE, Cached Tables, See also
- Follow-up Guidance: The source directs readers to MySQL Compatibility for further DDL restrictions and lists related statements such as ADD COLUMN, DROP COLUMN, ADD INDEX, DROP INDEX, RENAME INDEX, ALTER INDEX, CREATE TABLE, DROP TABLE, and SHOW CREATE TABLE.
- Classification Note: This is reference content because it lists explicit compatibility restrictions and related statement links for ALTER TABLE.

## Official Source Content

## MySQL compatibility

The following major restrictions apply to `ALTER TABLE` in TiDB:

- When altering multiple schema objects in a single `ALTER TABLE` statement:

    - Modifying the same object in multiple changes is not supported.
    - TiDB validates statements according to the table schema **before execution**. For example, an error returns when `ALTER TABLE t ADD COLUMN c1 INT, ADD COLUMN c2 INT AFTER c1;` is executed because column `c1` does not exist in the table.
    - For an `ALTER TABLE` statement, the order of execution in TiDB is one change after another from left to right, which is incompatible with MySQL in some cases.

- Changes of the [Reorg-Data](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-modify-column#reorg-data-change) types on primary key columns are not supported.

- Changes of column types on partitioned tables are not supported.

- Changes of column types on generated columns are not supported.

- Changes of some data types (for example, some TIME, Bit, Set, Enum, and JSON types) are not supported due to the compatibility issues of the `CAST` function's behavior between TiDB and MySQL.

- Spatial data types are not supported.

- `ALTER TABLE t CACHE | NOCACHE` is a TiDB extension to MySQL syntax. For details, see [Cached Tables](https://docs.pingcap.com/tidb/stable/cached-tables).

For further restrictions, see [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility#ddl-operations).
## See also

- [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility#ddl-operations)
- [ADD COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column)
- [DROP COLUMN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-column)
- [ADD INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index)
- [DROP INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index)
- [RENAME INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-index)
- [ALTER INDEX](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index)
- [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
- [DROP TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table)
- [SHOW CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table)
