# SET NAMES and CHARACTER SET statement reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-set-names.md`
- Source Title: `SET [NAMES|CHARACTER SET] |  TiDB SQL Statement Reference`
- Source Heading Path: `SET [NAMES|CHARACTER SET] | SET [NAMES|CHARACTER SET] > Synopsis | SET [NAMES|CHARACTER SET] > Examples | SET [NAMES|CHARACTER SET] > MySQL compatibility | SET [NAMES|CHARACTER SET] > See also`
- Source Line Ranges: `5-80`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `character-set`, `collation`, `session-variables`, `sql-syntax`, `mysql-compatibility`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0634_3507cbdd37`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-set-names.md#set-names-character-set`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `253202aeb4e429668429de091a552cc97122016be990bc95456053fe1cda52d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-names#set-names-character-set
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-set-names.md

## Retrieval Guidance

- Use When: Use this when looking up the SQL reference for changing the current connection character set or collation with `SET NAMES`, `SET CHARACTER SET`, or `SET CHARSET` and understanding which session variables they modify.
- Retrieval Keywords: SET NAMES, SET CHARACTER SET, SET CHARSET, character_set_client, character_set_results, character_set_connection, CharsetName, CollationName, COLLATE, SHOW VARIABLES LIKE 'character_set%', MySQL compatibility, Character Set and Collation Support
- Follow-up Guidance: See also `SHOW [GLOBAL|SESSION] VARIABLES`, `SET <variable>`, and `Character Set and Collation Support`.
- Classification Note: This is reference content because it defines the statement synopsis, shows example SQL and resulting `character_set%` variables, and states MySQL compatibility for `SET [NAMES|CHARACTER SET]`.

## Official Source Content

# SET [NAMES|CHARACTER SET]

The statements `SET NAMES`, `SET CHARACTER SET` and `SET CHARSET` modify the variables `character_set_client`, `character_set_results` and `character_set_connection` for the current connection.
## Synopsis

```ebnf+diagram
SetNamesStmt ::=
    "SET" ("NAMES" ("DEFAULT" | CharsetName ("COLLATE" ("DEFAULT" | CollationName))?) | ("CHARSET" | ("CHAR" | "CHARACTER") "SET") ("DEFAULT" | CharsetName))
```
## Examples

```sql
mysql> SHOW VARIABLES LIKE 'character_set%';
+--------------------------+--------------------------------------------------------+
| Variable_name            | Value                                                  |
+--------------------------+--------------------------------------------------------+
| character_sets_dir       | /usr/local/mysql-5.6.25-osx10.8-x86_64/share/charsets/ |
| character_set_connection | utf8mb4                                                |
| character_set_system     | utf8                                                   |
| character_set_results    | utf8mb4                                                |
| character_set_client     | utf8mb4                                                |
| character_set_database   | utf8mb4                                                |
| character_set_filesystem | binary                                                 |
| character_set_server     | utf8mb4                                                |
+--------------------------+--------------------------------------------------------+
8 rows in set (0.01 sec)

mysql> SET NAMES utf8;
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW VARIABLES LIKE 'character_set%';
+--------------------------+--------------------------------------------------------+
| Variable_name            | Value                                                  |
+--------------------------+--------------------------------------------------------+
| character_sets_dir       | /usr/local/mysql-5.6.25-osx10.8-x86_64/share/charsets/ |
| character_set_connection | utf8                                                   |
| character_set_system     | utf8                                                   |
| character_set_results    | utf8                                                   |
| character_set_client     | utf8                                                   |
| character_set_server     | utf8mb4                                                |
| character_set_database   | utf8mb4                                                |
| character_set_filesystem | binary                                                 |
+--------------------------+--------------------------------------------------------+
8 rows in set (0.00 sec)

mysql> SET CHARACTER SET utf8mb4;
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW VARIABLES LIKE 'character_set%';
+--------------------------+--------------------------------------------------------+
| Variable_name            | Value                                                  |
+--------------------------+--------------------------------------------------------+
| character_set_connection | utf8mb4                                                |
| character_set_system     | utf8                                                   |
| character_set_results    | utf8mb4                                                |
| character_set_client     | utf8mb4                                                |
| character_sets_dir       | /usr/local/mysql-5.6.25-osx10.8-x86_64/share/charsets/ |
| character_set_database   | utf8mb4                                                |
| character_set_filesystem | binary                                                 |
| character_set_server     | utf8mb4                                                |
+--------------------------+--------------------------------------------------------+
8 rows in set (0.00 sec)
```
## MySQL compatibility

The `SET [NAMES|CHARACTER SET]` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW \[GLOBAL|SESSION\] VARIABLES](/sql-statements/sql-statement-show-variables.md)
* [`SET <variable>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable)
* [Character Set and Collation Support](https://docs.pingcap.com/tidb/stable/character-set-and-collation)
