# SQL mode settings and supported mode values

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-mode.md`
- Source Title: `SQL Mode`
- Source Heading Path: `SQL Mode | SQL Mode > Important `sql_mode` values | SQL Mode > SQL mode table`
- Source Line Ranges: `5-58`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `sql_mode`, `session_scope`, `global_scope`, `privileges`, `strict_mode`, `ansi`, `traditional`, `data_validation`, `syntax_support`, `group_by`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0499_9cf7cc53d9`
- Source ID: `tidb-docs-8.1:sql-mode.md#sql-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `71f72c5edb4d2587a1574fcb86dfceca4620222c19e60e2044e3a3cc2b325c97`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-mode#sql-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-mode.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB SQL mode statement, default sql_mode value, or the meanings of modes such as ANSI, STRICT_TRANS_TABLES, and TRADITIONAL.
- Retrieval Keywords: SET [ SESSION | GLOBAL ] sql_mode='modes', SELECT @@sql_mode, SUPER privilege, SESSION level, GLOBAL level, ONLY_FULL_GROUP_BY, STRICT_TRANS_TABLES, NO_ZERO_IN_DATE, NO_ZERO_DATE, ERROR_FOR_DIVISION_BY_ZERO, NO_AUTO_CREATE_USER, NO_ENGINE_SUBSTITUTION, ANSI, STRICT_TRANS_TABLES, TRADITIONAL, PIPES_AS_CONCAT, ANSI_QUOTES, IGNORE_SPACE, NO_UNSIGNED_SUBTRACTION, NO_BACKSLASH_ESCAPES, ALLOW_INVALID_DATES, ERROR_FOR_DIVISION_BY_ZERO, NO_AUTO_CREATE_USER, ONLY_FULL_GROUP_BY, sql_mode table
- Follow-up Guidance: If you need a specific mode detail, consult the SQL mode table entries for the exact behavior and equivalent mode समूह.
- Classification Note: This is a reference chunk describing TiDB SQL mode configuration, supported mode values, and the SQL mode table.

## Official Source Content

# SQL Mode

TiDB servers operate in different SQL modes and apply these modes differently for different clients. SQL mode defines the SQL syntaxes that TiDB supports and the type of data validation check to perform, as described below:

After TiDB is started, you can use the `SET [ SESSION | GLOBAL ] sql_mode='modes'` statement to set SQL mode.

- Ensure that you have `SUPER` privilege when setting SQL mode at `GLOBAL` level, and your setting at this level only affects the connections established afterwards. 

- Changes to SQL mode at `SESSION` level only affect the current client.

In this statement, `modes` is a set of modes separated by commas (','). You can use the `SELECT @@sql_mode` statement to check the current SQL mode. The default value of SQL mode: `ONLY_FULL_GROUP_BY, STRICT_TRANS_TABLES, NO_ZERO_IN_DATE, NO_ZERO_DATE, ERROR_FOR_DIVISION_BY_ZERO, NO_AUTO_CREATE_USER, NO_ENGINE_SUBSTITUTION`.
## Important `sql_mode` values

* `ANSI`: This mode complies with standard SQL. In this mode, data is checked. If data does not comply with the defined type or length, the data type is adjusted or trimmed and a `warning` is returned.
* `STRICT_TRANS_TABLES`: Strict mode, where data is strictly checked. If any data is incorrect, it cannot be inserted into a table and an error is returned.
* `TRADITIONAL`: In this mode, TiDB behaves like a "traditional" SQL database system. An error instead of a warning is returned when any incorrect value is inserted into a column. Then, the `INSERT` or `UPDATE` statement is immediately stopped.
## SQL mode table

| Name | Description |
| :--- | :--- |
| `PIPES_AS_CONCAT` | Treats "\|\|" as a string concatenation operator (`+`) (the same as `CONCAT()`), not as an `OR` (full support) |
| `ANSI_QUOTES` | Treats `"` as an identifier. If `ANSI_QUOTES` is enabled, only single quotes are treated as string literals, and double quotes are treated as identifiers. Therefore, double quotes cannot be used to quote strings. (full support)|
| `IGNORE_SPACE` | If this mode is enabled, the system ignores space. For example: "user" and "user " are the same. (full support)|
| `ONLY_FULL_GROUP_BY` | A SQL statement is invalid if it refers to a column in `SELECT`, `HAVING`, or `ORDER BY` that is neither aggregated nor included in the `GROUP BY` clause. This is because displaying such a column in query results is abnormal. This setting is affected by the [`tidb_enable_new_only_full_group_by_check`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_new_only_full_group_by_check-new-in-v610) system variable. (full support)|
| `NO_UNSIGNED_SUBTRACTION` | Does not mark the result as `UNSIGNED` if an operand has no symbol in subtraction. (full support)|
| `NO_DIR_IN_CREATE` | Ignores all `INDEX DIRECTORY` and `DATA DIRECTORY` directives when a table is created. This option is only useful for secondary replication servers (syntax support only) |
| `NO_KEY_OPTIONS` | When you use the `SHOW CREATE TABLE` statement, MySQL-specific syntaxes such as `ENGINE` are not exported. Consider this option when migrating across DB types using mysqldump. (syntax support only)|
| `NO_FIELD_OPTIONS` | When you use the `SHOW CREATE TABLE` statement, MySQL-specific syntaxes such as `ENGINE` are not exported. Consider this option when migrating across DB types using mysqldump. (syntax support only) |
| `NO_TABLE_OPTIONS` | When you use the `SHOW CREATE TABLE` statement, MySQL-specific syntaxes such as `ENGINE` are not exported. Consider this option when migrating across DB types using mysqldump. (syntax support only)|
| `NO_AUTO_VALUE_ON_ZERO` | If this mode is enabled, when the value passed in the [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment) column is `0` or a specific value, the system directly writes this value to this column. When `NULL` is passed, the system automatically generates the next serial number. (full support)|
| `NO_BACKSLASH_ESCAPES` | If this mode is enabled, the `\` backslash symbol only stands for itself. (full support)|
| `STRICT_TRANS_TABLES` | Enables the strict mode for the transaction storage engine and rolls back the entire statement after an illegal value is inserted. (full support) |
| `STRICT_ALL_TABLES` | For transactional tables, rolls back the entire transaction statement after an illegal value is inserted. (full support) |
| `NO_ZERO_IN_DATE` | Strict mode, where dates with a month or day part of `0` are not accepted. If you use the `IGNORE` option, TiDB inserts '0000-00-00' for a similar date. In non-strict mode, this date is accepted but a warning is returned. (full support)
| `NO_ZERO_DATE` | Does not use '0000-00-00' as a legal date in strict mode. You can still insert a zero date with the `IGNORE` option. In non-strict mode, this date is accepted but a warning is returned. (full support)|
| `ALLOW_INVALID_DATES` | In this mode, the system does not check the validity of all dates. It only checks the month value ranging from `1` to `12` and the date value ranging from `1` to `31`. The mode only applies to `DATE` and `DATATIME` columns. All `TIMESTAMP` columns need a full validity check. (full support) |
| `ERROR_FOR_DIVISION_BY_ZERO` | If this mode is enabled, the system returns an error when handling division by `0` in data-change operations (`INSERT` or `UPDATE`). <br/> If this mode is not enabled, the system returns a warning and `NULL` is used instead. (full support) |
| `NO_AUTO_CREATE_USER` | Prevents `GRANT` from automatically creating new users, except for the specified password (full support)|
| `HIGH_NOT_PRECEDENCE` | The precedence of the NOT operator is such that expressions such as `NOT a BETWEEN b AND c` are parsed as `NOT (a BETWEEN b AND c)`. In some older versions of MySQL, this expression is parsed as `(NOT a) BETWEEN b AND c`. (full support) |
| `NO_ENGINE_SUBSTITUTION` | Prevents the automatic replacement of storage engines if the required storage engine is disabled or not compiled. (syntax support only)|
| `PAD_CHAR_TO_FULL_LENGTH` | If this mode is enabled, the system does not trim the trailing spaces for `CHAR` types. (syntax support only. This mode has been [deprecated in MySQL 8.0](https://dev.mysql.com/doc/refman/8.0/en/sql-mode.html#sqlmode_pad_char_to_full_length).) |
| `REAL_AS_FLOAT` | Treats `REAL` as the synonym of `FLOAT`, not the synonym of `DOUBLE` (full support)|
| `POSTGRESQL` | Equivalent to `PIPES_AS_CONCAT`, `ANSI_QUOTES`, `IGNORE_SPACE`, `NO_KEY_OPTIONS`, `NO_TABLE_OPTIONS`, `NO_FIELD_OPTIONS` (syntax support only)|
| `MSSQL` | Equivalent to `PIPES_AS_CONCAT`, `ANSI_QUOTES`, `IGNORE_SPACE`, `NO_KEY_OPTIONS`, `NO_TABLE_OPTIONS`, `NO_FIELD_OPTIONS` (syntax support only)|
| `DB2` | Equivalent to `PIPES_AS_CONCAT`, `ANSI_QUOTES`, `IGNORE_SPACE`, `NO_KEY_OPTIONS`, `NO_TABLE_OPTIONS`, `NO_FIELD_OPTIONS` (syntax support only)|
| `MAXDB` | Equivalent to `PIPES_AS_CONCAT`, `ANSI_QUOTES`, `IGNORE_SPACE`, `NO_KEY_OPTIONS`, `NO_TABLE_OPTIONS`, `NO_FIELD_OPTIONS`, `NO_AUTO_CREATE_USER` (full support)|
| `MySQL323` | Equivalent to `NO_FIELD_OPTIONS`, `HIGH_NOT_PRECEDENCE` (syntax support only)|
| `MYSQL40` | Equivalent to `NO_FIELD_OPTIONS`, `HIGH_NOT_PRECEDENCE` (syntax support only)|
| `ANSI` | Equivalent to `REAL_AS_FLOAT`, `PIPES_AS_CONCAT`, `ANSI_QUOTES`, `IGNORE_SPACE`, `ONLY_FULL_GROUP_BY` (syntax support only)|
| `TRADITIONAL` | Equivalent to `STRICT_TRANS_TABLES`, `STRICT_ALL_TABLES`, `NO_ZERO_IN_DATE`, `NO_ZERO_DATE`, `ERROR_FOR_DIVISION_BY_ZERO`, `NO_AUTO_CREATE_USER` (syntax support only) |
| `ORACLE` | Equivalent to `PIPES_AS_CONCAT`, `ANSI_QUOTES`, `IGNORE_SPACE`, `NO_KEY_OPTIONS`, `NO_TABLE_OPTIONS`, `NO_FIELD_OPTIONS`, `NO_AUTO_CREATE_USER` (syntax support only)|
