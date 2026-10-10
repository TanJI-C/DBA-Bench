# Character set and collation selection across columns, strings, and client connections

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/character-set-and-collation.md`
- Source Title: `Character Set and Collation`
- Source Heading Path: `Character Set and Collation > Character set and collation in different layers > Column character set and collation | Character Set and Collation > Character set and collation in different layers > String character sets and collation | Character Set and Collation > Character set and collation in different layers > Client connection character set and collation | Character Set and Collation > Selection priorities of character sets and collations | Character Set and Collation > General rules on selecting character sets and collation | Character Set and Collation > Validity check of characters`
- Source Line Ranges: `340-438`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `character-set`, `collation`, `column-definition`, `string-literals`, `client-connection`, `selection-priority`, `utf8-validation`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0038_052edea14a`
- Source ID: `tidb-docs-8.1:character-set-and-collation.md#column-character-set-and-collation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ba8d1a236f9fd60a7b265fc6680e1f85df9ed6a2e1776915fe6fddd41b3311c6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/character-set-and-collation#column-character-set-and-collation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/character-set-and-collation.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented rules for how TiDB chooses character sets and collations for columns, string literals, and client connections, including selection priority and UTF-8 validity checks.
- Retrieval Keywords: CHARACTER SET charset_name, COLLATE collation_name, default_collation_for_utf8mb4, character_set_connection, collation_connection, character_set_client, character_set_results, character_set_server, collation_server, character_set_database, collation_database, SET NAMES, SET CHARACTER SET, String > Column > Table > Database > Server, incorrect utf8 value, tidb_skip_utf8_check, utf8mb4_general_ci
- Follow-up Guidance: The content also gives the equivalent variable assignments for `SET NAMES 'charset_name' [COLLATE 'collation_name']` and `SET CHARACTER SET 'charset_name'`, and notes that invalid `utf8` or `utf8mb4` characters raise `incorrect utf8 value` unless `set @@tidb_skip_utf8_check=1;` is used.
- Classification Note: This is reference content because it defines SQL syntax, system variables, precedence rules, and error behavior for character set and collation handling.

## Official Source Content

### Column character set and collation

You can use the following statement to specify the character set and collation for columns:

```sql
col_name {CHAR | VARCHAR | TEXT} (col_length)
    [CHARACTER SET charset_name]
    [COLLATE collation_name]

col_name {ENUM | SET} (val_list)
    [CHARACTER SET charset_name]
    [COLLATE collation_name]
```

If the column character set and collation are not specified, the table character set and collation are used as their default values. If you only specify the character set as `utf8mb4` without specifying the collation, the collation is determined by the value of the system variable [`default_collation_for_utf8mb4`](https://docs.pingcap.com/tidb/stable/system-variables#default_collation_for_utf8mb4-new-in-v740).
### String character sets and collation

Each string corresponds to a character set and a collation. When you use a string, this option is available:

```sql
[_charset_name]'string' [COLLATE collation_name]
```

Example:

```sql
SELECT 'string';
SELECT _utf8mb4'string';
SELECT _utf8mb4'string' COLLATE utf8mb4_general_ci;
```

Rules:

+ Rule 1: If you specify `CHARACTER SET charset_name` and `COLLATE collation_name`, then the `charset_name` character set and the `collation_name` collation are used directly.
+ Rule 2: If you specify `CHARACTER SET charset_name` but do not specify `COLLATE collation_name`, the `charset_name` character set and the default collation of `charset_name` are used.
+ Rule 3: If you specify neither `CHARACTER SET charset_name` nor `COLLATE collation_name`, the character set and collation given by the system variables `character_set_connection` and `collation_connection` are used.
### Client connection character set and collation

+ The server character set and collation are the values of the `character_set_server` and `collation_server` system variables.

+ The character set and collation of the default database are the values of the `character_set_database` and `collation_database` system variables.

You can use `character_set_connection` and `collation_connection` to specify the character set and collation for each connection. The `character_set_client` variable is to set the client character set.

Before returning the result, the `character_set_results` system variable indicates the character set in which the server returns query results to the client, including the metadata of the result.

You can use the following statement to set the character set and collation that is related to the client:

+ `SET NAMES 'charset_name' [COLLATE 'collation_name']`

    `SET NAMES` indicates what character set the client will use to send SQL statements to the server. `SET NAMES utf8mb4` indicates that all the requests from the client use utf8mb4, as well as the results from the server.

    The `SET NAMES 'charset_name'` statement is equivalent to the following statement combination:

    ```sql
    SET character_set_client = charset_name;
    SET character_set_results = charset_name;
    SET character_set_connection = charset_name;
    ```

    `COLLATE` is optional, if absent, the default collation of the `charset_name` is used to set the `collation_connection`.

+ `SET CHARACTER SET 'charset_name'`

    Similar to `SET NAMES`, the `SET NAMES 'charset_name'` statement is equivalent to the following statement combination:

    ```sql
    SET character_set_client = charset_name;
    SET character_set_results = charset_name;
    SET character_set_connection=@@character_set_database;
    SET collation_connection = @@collation_database;
    ```
## Selection priorities of character sets and collations

String > Column > Table > Database > Server
## General rules on selecting character sets and collation

+ Rule 1: If you specify `CHARACTER SET charset_name` and `COLLATE collation_name`, then the `charset_name` character set and the `collation_name` collation are used directly.
+ Rule 2: If you specify `CHARACTER SET charset_name` and do not specify `COLLATE collation_name`, then the `charset_name` character set and the default collation of `charset_name` are used.
+ Rule 3: If you specify neither `CHARACTER SET charset_name` nor `COLLATE collation_name`, the character set and collation with higher optimization levels are used.
## Validity check of characters

If the specified character set is `utf8` or `utf8mb4`, TiDB only supports the valid `utf8` characters. For invalid characters, TiDB reports the `incorrect utf8 value` error. This validity check of characters in TiDB is compatible with MySQL 8.0 but incompatible with MySQL 5.7 or earlier versions.

To disable this error reporting, use `set @@tidb_skip_utf8_check=1;` to skip the character check.

> **Note:**
>
> If the character check is skipped, TiDB might fail to detect illegal UTF-8 characters written by the application, cause decoding errors when `ANALYZE` is executed, and introduce other unknown encoding issues. If your application cannot guarantee the validity of the written string, it is not recommended to skip the character check.
