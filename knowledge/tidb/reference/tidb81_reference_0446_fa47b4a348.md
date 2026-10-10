# MySQL compatibility differences for SQL behavior, defaults, and supported features

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/mysql-compatibility.md`
- Source Title: `MySQL Compatibility`
- Source Heading Path: `MySQL Compatibility > Differences from MySQL > Analyzing tables | MySQL Compatibility > Differences from MySQL > Limitations of `SELECT` syntax | MySQL Compatibility > Differences from MySQL > `UPDATE` statement | MySQL Compatibility > Differences from MySQL > Views | MySQL Compatibility > Differences from MySQL > Temporary tables | MySQL Compatibility > Differences from MySQL > Character sets and collations | MySQL Compatibility > Differences from MySQL > Storage engines | MySQL Compatibility > Differences from MySQL > SQL modes | MySQL Compatibility > Differences from MySQL > Default differences | MySQL Compatibility > Differences from MySQL > Date and Time | MySQL Compatibility > Differences from MySQL > Type system differences | MySQL Compatibility > Differences from MySQL > Regular expressions | MySQL Compatibility > Differences from MySQL > Incompatibility due to deprecated features | MySQL Compatibility > Differences from MySQL > `CREATE RESOURCE GROUP`, `DROP RESOURCE GROUP`, and `ALTER RESOURCE GROUP` statements`
- Source Line Ranges: `182-294`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `mysql-compatibility`, `statistics`, `analyze-table`, `select-syntax`, `update`, `views`, `temporary-tables`, `character-sets`, `collations`, `storage-engines`, `sql-modes`, `defaults`, `timezones`, `type-system`, `regular-expressions`, `deprecated-features`, `resource-groups`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0446_fa47b4a348`
- Source ID: `tidb-docs-8.1:mysql-compatibility.md#analyzing-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3350632bba0bcc6bc175cd510e74b1af2084a372dfdafc4831b4c6a7c00d36a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/mysql-compatibility#analyzing-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/mysql-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiDB with MySQL for SQL behavior differences, default settings, unsupported syntax or types, and feature compatibility such as statistics collection, views, temporary tables, collations, SQL modes, timezones, deprecated features, and resource group statements.
- Retrieval Keywords: MySQL compatibility differences, Statistics Collection, ANALYZE TABLE, SELECT ... INTO @variable, GROUP BY expr does not imply ORDER BY expr, UPDATE statement, views are not updatable, UPDATE INSERT DELETE on views, local temporary tables compatibility, Character Set and Collation Overview, GBK compatibility, national character set, storage engines, --store, InnoDB metadata, SQL modes, ONLY_FULL_GROUP_BY, NO_DIR_IN_CREATE, NO_ENGINE_SUBSTITUTION, default character set utf8mb4, default collation utf8mb4_bin, default SQL mode, lower_case_table_names, explicit_defaults_for_timestamp, named timezones, tzdata, timezone table data, SQL_TSI_MONTH, SQL_TSI_WEEK, SQL_TSI_DAY, SQL_TSI_HOUR, SQL_TSI_MINUTE, SQL_TSI_SECOND, regular expression compatibility with MySQL, REGEXP_INSTR(), REGEXP_LIKE(), REGEXP_REPLACE(), REGEXP_SUBSTR(), floating-point precision deprecated, ZEROFILL, CREATE RESOURCE GROUP, DROP RESOURCE GROUP, ALTER RESOURCE GROUP
- Follow-up Guidance: The source points to the statement references for `ANALYZE TABLE`, `SELECT`, `UPDATE`, `CREATE RESOURCE GROUP`, `DROP RESOURCE GROUP`, and `ALTER RESOURCE GROUP`, plus related compatibility pages for temporary tables, collations, GBK, SQL modes, aggregate `GROUP BY` differences, and regular expressions.
- Classification Note: This is a reference chunk because it enumerates documented TiDB versus MySQL compatibility differences, defaults, unsupported features, and related statement-specific references.

## Official Source Content

### Analyzing tables

In TiDB, [Statistics Collection](https://docs.pingcap.com/tidb/stable/statistics#manual-collection) differs from MySQL in that it completely rebuilds the statistics for a table, making it a more resource-intensive operation that takes longer to complete. In contrast, MySQL/InnoDB performs a relatively lightweight and short-lived operation.

For more information, refer to [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table).
### Limitations of `SELECT` syntax

TiDB does not support the following `SELECT` syntax:

- `SELECT ... INTO @variable`
- `SELECT .. GROUP BY expr` does not imply `GROUP BY expr ORDER BY expr` as it does in MySQL 5.7.

For more details, see the [`SELECT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select) statement reference.
### `UPDATE` statement

See the [`UPDATE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update) statement reference.
### Views

Views in TiDB are not updatable and do not support write operations such as `UPDATE`, `INSERT`, and `DELETE`.
### Temporary tables

For more information, see [Compatibility between TiDB local temporary tables and MySQL temporary tables](https://docs.pingcap.com/tidb/stable/temporary-tables#compatibility-with-mysql-temporary-tables).
### Character sets and collations

* To learn about the character sets and collations supported by TiDB, see [Character Set and Collation Overview](https://docs.pingcap.com/tidb/stable/character-set-and-collation).

* For information on the MySQL compatibility of the GBK character set, refer to [GBK compatibility](https://docs.pingcap.com/tidb/stable/character-set-gbk#mysql-compatibility) .

* TiDB inherits the character set used in the table as the national character set.
### Storage engines

TiDB allows for tables to be created with alternative storage engines. Despite this, the metadata as described by TiDB is for the InnoDB storage engine as a way to ensure compatibility.

To specify a storage engine using the [`--store`](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tidb-configuration#--store) option, it is necessary to start the TiDB server. This storage engine abstraction feature is similar to MySQL.
### SQL modes

TiDB supports most [SQL modes](https://docs.pingcap.com/tidb/stable/sql-mode):

- The compatibility modes, such as `Oracle` and `PostgreSQL` are parsed but ignored. Compatibility modes are deprecated in MySQL 5.7 and removed in MySQL 8.0.
- The `ONLY_FULL_GROUP_BY` mode has minor [semantic differences](https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions#differences-from-mysql) from MySQL 5.7.
- The `NO_DIR_IN_CREATE` and `NO_ENGINE_SUBSTITUTION` SQL modes in MySQL are accepted for compatibility, but are not applicable to TiDB.
### Default differences

TiDB has default differences when compared with MySQL 5.7 and MySQL 8.0:

- Default character set:
    - TiDB's default value is `utf8mb4`.
    - MySQL 5.7's default value is `latin1`.
    - MySQL 8.0's default value is `utf8mb4`.
- Default collation:
    - TiDB's default collation is `utf8mb4_bin`.
    - MySQL 5.7's default collation is `utf8mb4_general_ci`.
    - MySQL 8.0's default collation is `utf8mb4_0900_ai_ci`.
- Default SQL mode:
    - TiDB's default SQL mode includes these modes: `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION`.
    - MySQL's default SQL mode:
        - The default SQL mode in MySQL 5.7 is the same as TiDB.
        - The default SQL mode in MySQL 8.0 includes these modes: `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION`.
- Default value of `lower_case_table_names`:
    - The default value in TiDB is `2`, and only `2` is currently supported.
    - MySQL defaults to the following values:
        - On Linux: `0`. It means that table and database names are stored on disk according to the letter case specified in the `CREATE TABLE` or `CREATE DATABASE` statement. Name comparisons are case-sensitive.
        - On Windows: `1`. It means table names are stored in lowercase on disk, and name comparisons are not case-sensitive. MySQL converts all table names to lowercase on storage and lookup. This behavior also applies to database names and table aliases.
        - On macOS: `2`. It means table and database names are stored on disk according to the letter case specified in the `CREATE TABLE` or `CREATE DATABASE` statement, but MySQL converts them to lowercase on lookup. Name comparisons are not case-sensitive.
- Default value of `explicit_defaults_for_timestamp`:
    - The default value in TiDB is `ON`, and only `ON` is currently supported.
    - MySQL defaults to the following values:
        - For MySQL 5.7: `OFF`.
        - For MySQL 8.0: `ON`.
### Date and Time

TiDB supports named timezones with the following considerations:

+ TiDB uses all the timezone rules presently installed in the system for calculation, typically the `tzdata` package. This makes it possible to use all timezone names without needing to import timezone table data. Importing timezone table data will not change the calculation rules.
+ Currently, MySQL uses the local timezone by default, then relies on the current timezone rules built into the system (for example, when daylight savings time begins) for calculation. Without [importing timezone table data](https://dev.mysql.com/doc/refman/8.0/en/time-zone-support.html#time-zone-installation), MySQL cannot specify the timezone by name.
### Type system differences

The following column types are supported by MySQL but **not** by TiDB:

- `SQL_TSI_*` (includes SQL_TSI_MONTH, SQL_TSI_WEEK, SQL_TSI_DAY, SQL_TSI_HOUR, SQL_TSI_MINUTE, and SQL_TSI_SECOND, but excludes SQL_TSI_YEAR)
### Regular expressions

For information about TiDB regular expression compatibility with MySQL, including `REGEXP_INSTR()`, `REGEXP_LIKE()`, `REGEXP_REPLACE()`, and `REGEXP_SUBSTR()`, see [Regular expression compatibility with MySQL](https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#regular-expression-compatibility-with-mysql).
### Incompatibility due to deprecated features

TiDB does not implement specific features deprecated in MySQL, including:

- Specifying precision for floating-point types. MySQL 8.0 [deprecates](https://dev.mysql.com/doc/refman/8.0/en/floating-point-types.html) this feature, and it is recommended to use the `DECIMAL` type instead.
- The `ZEROFILL` attribute. MySQL 8.0 [deprecates](https://dev.mysql.com/doc/refman/8.0/en/numeric-type-attributes.html) this feature, and it is recommended to pad numeric values in your application instead.
### `CREATE RESOURCE GROUP`, `DROP RESOURCE GROUP`, and `ALTER RESOURCE GROUP` statements

The following statements for creating, modifying, and dropping resource groups have different supported parameters than MySQL. For details, see the following documents:

- [`CREATE RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group)
- [`DROP RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group)
- [`ALTER RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group)
