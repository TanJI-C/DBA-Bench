# Column default values and supported default expressions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-default-values.md`
- Source Title: `TiDB Data Type`
- Source Heading Path: `Default Values | Default Values > Specify expressions as default values`
- Source Line Ranges: `5-53`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `default-values`, `column-definition`, `sql-mode`, `strict-mode`, `implicit-defaults`, `expressions`, `blob`, `text`, `json`, `timestamp`, `sequence`, `uuid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0075_cac5461f57`
- Source ID: `tidb-docs-8.1:data-type-default-values.md#default-values`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db4389d0dacace9e7ca5da6a2caf542d7d034051569169f2729a449a80443bd5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-default-values#default-values
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-default-values.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiDB column DEFAULT behavior, including supported default expressions, implicit defaults for NOT NULL columns without an explicit DEFAULT, or defaults for BLOB, TEXT, and JSON.
- Retrieval Keywords: DEFAULT value clause, default values, Specify expressions as default values, strict SQL mode, implicit default value, NOT NULL column, INSERT, REPLACE, TIMESTAMP, DATETIME, NOW, CURRENT_TIMESTAMP, LOCALTIME, LOCALTIMESTAMP, NEXT VALUE FOR, RAND(), UUID(), UUID_TO_BIN(), BLOB, TEXT, JSON, UPPER(SUBSTRING_INDEX(USER(), '@', 1)), REPLACE(UPPER(UUID()), '-', ''), DATE_FORMAT(NOW(), '%Y-%m'), DATE_FORMAT(NOW(), '%Y-%m-%d'), DATE_FORMAT(NOW(), '%Y-%m-%d %H.%i.%s'), DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), STR_TO_DATE('1980-01-01', '%Y-%m-%d'), CREATE TABLE t2 (b BLOB DEFAULT (RAND()));, AUTO_INCREMENT, DEFAULT NULL
- Follow-up Guidance: The source also lists the exact implicit defaults by type category and the supported expression forms for the DEFAULT clause.
- Classification Note: This is a SQL reference chunk because it defines official DEFAULT clause semantics, supported default expressions, and implicit default handling for data types and SQL mode.

## Official Source Content

# Default Values

The `DEFAULT` value clause in a data type specification indicates a default value for a column.

You can set default values for all data types. Typically, default values must be constants and cannot be functions or expressions, but there are some exceptions:

- For time types, you can use `NOW`, `CURRENT_TIMESTAMP`, `LOCALTIME`, and `LOCALTIMESTAMP` functions as default values for `TIMESTAMP` and `DATETIME` columns.
- For integer types, you can use the `NEXT VALUE FOR` function to set the next value of a sequence as the default value for a column, and use the [`RAND()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/numeric-functions-and-operators) function to generate a random floating-point value as the default value for a column.
- For string types, you can use the [`UUID()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/miscellaneous-functions) function to generate a [universally unique identifier (UUID)](https://docs.pingcap.com/tidb/stable/best-practices/uuid) as the default value for a column.
- For binary types, you can use the [`UUID_TO_BIN()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/miscellaneous-functions) function to convert a UUID to the binary format and set the converted value as the default value for a column.
- Starting from v8.0.0, TiDB additionally supports [specifying the default values](#specify-expressions-as-default-values) for [`BLOB`](https://docs.pingcap.com/tidb/stable/data-type-string#blob-type), [`TEXT`](https://docs.pingcap.com/tidb/stable/data-type-string#text-type), and [`JSON`](https://docs.pingcap.com/tidb/stable/data-type-json#json-data-type) data types, but you can only use expressions to set the [default values](#default-values) for them.

If a column definition includes no explicit `DEFAULT` value, TiDB determines the default value as follows:

- If the column can take `NULL` as a value, the column is defined with an explicit `DEFAULT NULL` clause.
- If the column cannot take `NULL` as the value, TiDB defines the column with no explicit `DEFAULT` clause.

For data entry into a `NOT NULL` column that has no explicit `DEFAULT` clause, if an `INSERT` or `REPLACE` statement includes no value for the column, TiDB handles the column according to the SQL mode in effect at the time:

- If strict SQL mode is enabled, an error occurs for transactional tables, and the statement is rolled back. For nontransactional tables, an error occurs.
- If strict mode is not enabled, TiDB sets the column to the implicit default value for the column data type.

Implicit defaults are defined as follows:

- For numeric types, the default is 0. If declared with the `AUTO_INCREMENT` attribute, the default is the next value in the sequence.
- For date and time types other than `TIMESTAMP`, the default is the appropriate "zero" value for the type. For `TIMESTAMP`, the default value is the current date and time.
- For string types other than `ENUM`, the default value is the empty string. For `ENUM`, the default is the first enumeration value.
## Specify expressions as default values

Starting from 8.0.13, MySQL supports specifying expressions as default values in the `DEFAULT` clause. For more information, see [Explicit default handling as of MySQL 8.0.13](https://dev.mysql.com/doc/refman/8.0/en/data-type-defaults.html#data-type-defaults-explicit).

Starting from v8.0.0, TiDB additionally supports specifying the following expressions as default values in the `DEFAULT` clause.

* `UPPER(SUBSTRING_INDEX(USER(), '@', 1))`
* `REPLACE(UPPER(UUID()), '-', '')`
* `DATE_FORMAT` expressions in the following formats:
    * `DATE_FORMAT(NOW(), '%Y-%m')`
    * `DATE_FORMAT(NOW(), '%Y-%m-%d')`
    * `DATE_FORMAT(NOW(), '%Y-%m-%d %H.%i.%s')`
    * `DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s')`
* `STR_TO_DATE('1980-01-01', '%Y-%m-%d')`

Starting from v8.0.0, TiDB additionally supports assigning default values to `BLOB`, `TEXT`, and `JSON` data types. However, you can only use expressions to set the default values for these data types. The following is an example of `BLOB`:

```sql
CREATE TABLE t2 (b BLOB DEFAULT (RAND()));
```
