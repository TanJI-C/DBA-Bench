# CREATE DATABASE statement syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-database.md`
- Source Title: `CREATE DATABASE | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE DATABASE | CREATE DATABASE > Synopsis | CREATE DATABASE > Syntax | CREATE DATABASE > Examples | CREATE DATABASE > MySQL compatibility | CREATE DATABASE > See also`
- Source Line Ranges: `5-83`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `create-database`, `schema`, `syntax`, `charset`, `collation`, `placement-policy`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0551_59b4f350a1`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-database.md#create-database`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f8997d8f70cfadbbf1a9833547846d9b1a488b96571ca25dc6c70fe75812e174`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-database#create-database
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-database.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the SQL syntax, options, examples, or MySQL compatibility of creating a database or schema in TiDB.
- Retrieval Keywords: CREATE DATABASE, CREATE SCHEMA, IF NOT EXISTS, CHARACTER SET, COLLATE, ENCRYPTION, PLACEMENT POLICY, PLACEMENT POLICY DEFAULT, CreateDatabaseStmt, DatabaseOption, PolicyName, CREATE DATABASE mynewdatabase, SHOW TABLES, database changed, MySQL compatibility
- Follow-up Guidance: The source also points to related statements `USE`, `ALTER DATABASE`, `DROP DATABASE`, and `SHOW DATABASES`.
- Classification Note: This is reference content because it provides the formal synopsis, syntax, options, examples, and compatibility note for the `CREATE DATABASE` SQL statement.

## Official Source Content

# CREATE DATABASE

This statement creates a new database in TiDB. The MySQL terminology for 'database' most closely maps to a schema in the SQL standard.
## Synopsis

```ebnf+diagram
CreateDatabaseStmt ::=
    'CREATE' 'DATABASE' IfNotExists DBName DatabaseOptionListOpt

IfNotExists ::=
    ( 'IF' 'NOT' 'EXISTS' )?

DBName ::=
    Identifier

DatabaseOptionListOpt ::=
    DatabaseOptionList?

DatabaseOptionList ::=
    DatabaseOption ( ','? DatabaseOption )*

DatabaseOption ::=
    DefaultKwdOpt ( CharsetKw '='? CharsetName | 'COLLATE' '='? CollationName | 'ENCRYPTION' '='? EncryptionOpt )
|   DefaultKwdOpt PlacementPolicyOption

PlacementPolicyOption ::=
    "PLACEMENT" "POLICY" EqOpt PolicyName
|   "PLACEMENT" "POLICY" (EqOpt | "SET") "DEFAULT"
```
## Syntax

The `CREATE DATABASE` statement is used to create a database, and to specify the default properties of the database, such as the default character set and collation. `CREATE SCHEMA` is a synonym for `CREATE DATABASE`.

```sql
CREATE {DATABASE | SCHEMA} [IF NOT EXISTS] db_name
    [create_specification] ...

create_specification:
    [DEFAULT] CHARACTER SET [=] charset_name
  | [DEFAULT] COLLATE [=] collation_name
```

If you create an existing database and does not specify `IF NOT EXISTS`, an error is displayed.

The `create_specification` option is used to specify the specific `CHARACTER SET` and `COLLATE` in the database. Currently, TiDB only supports some of the character sets and collations. For details, see [Character Set and Collation Support](https://docs.pingcap.com/tidb/stable/character-set-and-collation).
## Examples

```sql
mysql> CREATE DATABASE mynewdatabase;
Query OK, 0 rows affected (0.09 sec)

mysql> USE mynewdatabase;
Database changed
mysql> CREATE TABLE t1 (a int);
Query OK, 0 rows affected (0.11 sec)

mysql> SHOW TABLES;
+-------------------------+
| Tables_in_mynewdatabase |
+-------------------------+
| t1                      |
+-------------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

The `CREATE DATABASE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [USE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-use)
* [ALTER DATABASE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-database)
* [DROP DATABASE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-database)
* [SHOW DATABASES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-databases)
