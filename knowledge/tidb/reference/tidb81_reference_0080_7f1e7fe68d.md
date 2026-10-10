# String type reference and syntax

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-string.md`
- Source Title: `String types`
- Source Heading Path: `String Types | String Types > Supported types | String Types > Supported types > `CHAR` type | String Types > Supported types > `VARCHAR` type | String Types > Supported types > `TEXT` type | String Types > Supported types > `TINYTEXT` type | String Types > Supported types > `MEDIUMTEXT` type | String Types > Supported types > `LONGTEXT` type | String Types > Supported types > `BINARY` type | String Types > Supported types > `VARBINARY` type | String Types > Supported types > `BLOB` type | String Types > Supported types > `TINYBLOB` type | String Types > Supported types > `MEDIUMBLOB` type | String Types > Supported types > `LONGBLOB` type | String Types > Supported types > `ENUM` type | String Types > Supported types > `SET` type`
- Source Line Ranges: `5-208`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `string-types`, `char`, `varchar`, `text`, `blob`, `binary`, `varbinary`, `enum`, `set`, `character-set`, `collation`, `column-length`, `row-size-limit`, `syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0080_7f1e7fe68d`
- Source ID: `tidb-docs-8.1:data-type-string.md#string-types`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `025caa8bdf1fa0161fd254e72f0b4558687df687e16da1a63cc6eb91df5ef755`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-string#string-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-string.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the TiDB string type reference, including syntax, length limits, character set and collation clauses, or the behavior of CHAR, VARCHAR, TEXT, BLOB, ENUM, and SET types.
- Retrieval Keywords: String Types, CHAR, VARCHAR, TEXT, TINYTEXT, MEDIUMTEXT, LONGTEXT, BINARY, VARBINARY, BLOB, TINYBLOB, MEDIUMBLOB, LONGBLOB, ENUM, SET, [NATIONAL] CHAR[(M)], [NATIONAL] VARCHAR(M), TEXT[(M)], BINARY(M), VARBINARY(M), BLOB[(M)], CHARACTER SET charset_name, COLLATE collation_name, maximum row length, column-length in characters, 65,535 bytes, utf8mb4, txn-entry-size-limit, ENUM('value1','value2',...), SET('value1','value2',...)
- Follow-up Guidance: The chunk also points to the txn-entry-size-limit limitation for MEDIUMTEXT, LONGTEXT, MEDIUMBLOB, and LONGBLOB row storage size, and to MySQL references for String Types, ENUM, and SET.
- Classification Note: This is classified as reference content because it lists supported string data types, their SQL syntax, storage and length rules, and identifier-specific details such as character sets, collations, and internal ENUM and SET value mappings.

## Official Source Content

# String Types

TiDB supports all the MySQL string types, including `CHAR`, `VARCHAR`, `BINARY`, `VARBINARY`, `BLOB`, `TEXT`, `ENUM`, and `SET`. For more information, see [String Types in MySQL](https://dev.mysql.com/doc/refman/8.0/en/string-types.html).
## Supported types
### `CHAR` type

`CHAR` is a fixed length string. M represents the column-length in characters (not bytes). The range of M is 0 to 255. Different from the `VARCHAR` type, when data is inserted into a `CHAR` column, the trailing spaces are truncated.

```sql
[NATIONAL] CHAR[(M)] [CHARACTER SET charset_name] [COLLATE collation_name]
```
### `VARCHAR` type

`VARCHAR` is a string of variable-length. M represents the maximum column length in characters (not bytes). The maximum size of `VARCHAR` cannot exceed 65,535 bytes. The maximum row length and the character set being used determine the `VARCHAR` length.

The space occupied by a single character might differ for different character sets. The following table shows the bytes consumed by a single character, and the range of the `VARCHAR` column length in each character set:

| Character Set | Byte(s) per Character | Range of the Maximum `VARCHAR` Column Length |
| ----- | ---- | ---- |
| ascii | 1 | (0, 65535] |
| latin1 | 1 | (0, 65535] |
| binary | 1 | (0, 65535] |
| utf8 | 3 | (0, 21845] |
| utf8mb4 | 4 | (0, 16383] |

```sql
[NATIONAL] VARCHAR(M) [CHARACTER SET charset_name] [COLLATE collation_name]
```
### `TEXT` type

`TEXT` is a string of variable-length. The maximum column length is 65,535 bytes. The optional M argument is in characters and is used to automatically select the fittest type of a `TEXT` column. For example `TEXT(60)` will yield a `TINYTEXT` data type that can hold up to 255 bytes, which fits a 60-character UTF-8 string that has up to 4 bytes per character (4×60=240). Using the M argument is not recommended.

```sql
TEXT[(M)] [CHARACTER SET charset_name] [COLLATE collation_name]
```
### `TINYTEXT` type

The `TINYTEXT` type is similar to the [`TEXT` type](#text-type). The difference is that the maximum column length of `TINYTEXT` is 255.

```sql
TINYTEXT [CHARACTER SET charset_name] [COLLATE collation_name]
```
### `MEDIUMTEXT` type

The `MEDIUMTEXT` type is similar to the [`TEXT` type](#text-type). The difference is that the maximum column length of `MEDIUMTEXT` is 16,777,215. But due to the limitation of [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500), the maximum storage size of a single row in TiDB is 6 MiB by default and can be increased to 120 MiB by changing the configuration.

The `MEDIUMTEXT` type is similar to the [`TEXT` type](#text-type). The difference is that the maximum column length of `MEDIUMTEXT` is 16,777,215. But due to the limitation of [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500), the maximum storage size of a single row in TiDB is 6 MiB by default and can be increased to 120 MiB by changing the configuration.

```sql
MEDIUMTEXT [CHARACTER SET charset_name] [COLLATE collation_name]
```
### `LONGTEXT` type

The `LONGTEXT` type is similar to the [`TEXT` type](#text-type). The difference is that the maximum column length of `LONGTEXT` is 4,294,967,295. But due to the limitation of [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500), the maximum storage size of a single row in TiDB is 6 MiB by default and can be increased to 120 MiB by changing the configuration.

The `LONGTEXT` type is similar to the [`TEXT` type](#text-type). The difference is that the maximum column length of `LONGTEXT` is 4,294,967,295. But due to the limitation of [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500), the maximum storage size of a single row in TiDB is 6 MiB by default and can be increased to 120 MiB by changing the configuration.

```sql
LONGTEXT [CHARACTER SET charset_name] [COLLATE collation_name]
```
### `BINARY` type

The `BINARY` type is similar to the [`CHAR` type](#char-type). The difference is that `BINARY` stores binary byte strings.

```sql
BINARY(M)
```
### `VARBINARY` type

The `VARBINARY` type is similar to the [`VARCHAR` type](#varchar-type). The difference is that the `VARBINARY` stores binary byte strings.

```sql
VARBINARY(M)
```
### `BLOB` type

`BLOB` is a large binary file. M represents the maximum column length in bytes, ranging from 0 to 65,535.

```sql
BLOB[(M)]
```
### `TINYBLOB` type

The `TINYBLOB` type is similar to the [`BLOB` type](#blob-type). The difference is that the maximum column length of `TINYBLOB` is 255.

```sql
TINYBLOB
```
### `MEDIUMBLOB` type

The `MEDIUMBLOB` type is similar to the [`BLOB` type](#blob-type). The difference is that the maximum column length of `MEDIUMBLOB` is 16,777,215. But due to the limitation of [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500), the maximum storage size of a single row in TiDB is 6 MiB by default and can be increased to 120 MiB by changing the configuration.

The `MEDIUMBLOB` type is similar to the [`BLOB` type](#blob-type). The difference is that the maximum column length of `MEDIUMBLOB` is 16,777,215. But due to the limitation of [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500), the maximum storage size of a single row in TiDB is 6 MiB by default and can be increased to 120 MiB by changing the configuration.

```sql
MEDIUMBLOB
```
### `LONGBLOB` type

The `LONGBLOB` type is similar to the [`BLOB` type](#blob-type). The difference is that the maximum column length of `LONGBLOB` is 4,294,967,295. But due to the limitation of [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500), the maximum storage size of a single row in TiDB is 6 MiB by default and can be increased to 120 MiB by changing the configuration.

The `LONGBLOB` type is similar to the [`BLOB` type](#blob-type). The difference is that the maximum column length of `LONGBLOB` is 4,294,967,295. But due to the limitation of [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500), the maximum storage size of a single row in TiDB is 6 MiB by default and can be increased to 120 MiB by changing the configuration.

```sql
LONGBLOB
```
### `ENUM` type

An `ENUM` is a string object with a value chosen from a list of permitted values that are enumerated explicitly in the column specification when the table is created. The syntax is:

```sql
ENUM('value1','value2',...) [CHARACTER SET charset_name] [COLLATE collation_name]

# For example:
ENUM('apple', 'orange', 'pear')
```

The value of the `ENUM` data type is stored as numbers. Each value is converted to a number according the definition order. In the previous example, each string is mapped to a number:

| Value | Number |
| ---- | ---- |
| NULL | NULL |
| '' | 0 |
| 'apple' | 1 |
| 'orange' | 2 |
| 'pear' | 3 |

For more information, see [the ENUM type in MySQL](https://dev.mysql.com/doc/refman/8.0/en/enum.html).
### `SET` type

A `SET` is a string object that can have zero or more values, each of which must be chosen from a list of permitted values specified when the table is created. The syntax is:

```sql
SET('value1','value2',...) [CHARACTER SET charset_name] [COLLATE collation_name]

# For example:
SET('1', '2') NOT NULL
```

In the example, any of the following values can be valid:

```
''
'1'
'2'
'1,2'
```

In TiDB, the values of the `SET` type is internally converted to `Int64`. The existence of each element is represented using a binary: 0 or 1. For a column specified as `SET('a','b','c','d')`, the members have the following decimal and binary values.

| Member | Decimal Value | Binary Value |
| ---- | ---- | ------ |
| 'a' | 1 | 0001 |
| 'b' | 2 | 0010 |
| 'c' | 4 | 0100 |
| 'd' | 8 | 1000 |

In this case, for an element of `('a', 'c')`, it is `0101` in binary.

For more information, see [the SET type in MySQL](https://dev.mysql.com/doc/refman/8.0/en/set.html).
