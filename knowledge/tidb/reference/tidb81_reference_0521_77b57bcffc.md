# ALTER DATABASE syntax, example, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-database.md`
- Source Title: `ALTER DATABASE | TiDB SQL Statement Reference`
- Source Heading Path: `ALTER DATABASE | ALTER DATABASE > Synopsis | ALTER DATABASE > Examples | ALTER DATABASE > MySQL compatibility | ALTER DATABASE > See also`
- Source Line Ranges: `5-43`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `alter database`, `schema`, `character set`, `collation`, `encryption`, `syntax`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0521_77b57bcffc`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-database.md#alter-database`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a73962c06876512f912e0adf7fe69c2144248b8ef3d2ca0b5790a4ab1bdd7565`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-database#alter-database
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-database.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL reference for ALTER DATABASE or ALTER SCHEMA syntax, default character set or collation changes, ENCRYPTION option syntax, an example altering a database to utf8mb4, or MySQL compatibility wording.
- Retrieval Keywords: ALTER DATABASE, ALTER SCHEMA, AlterDatabaseStmt, DatabaseOption, DEFAULT CHARACTER SET, COLLATE, ENCRYPTION, ALTER DATABASE test DEFAULT CHARACTER SET = utf8mb4;, character set and collation, MySQL compatibility
- Follow-up Guidance: The source also points to Character Set and Collation Support for supported character sets and collations, and to CREATE DATABASE and SHOW DATABASES in See also.
- Classification Note: This is reference content because it defines ALTER DATABASE syntax, shows an example statement and result, and states MySQL compatibility for the statement.

## Official Source Content

# ALTER DATABASE

`ALTER DATABASE` is used to specify or modify the default character set and collation of the current database. `ALTER SCHEMA` has the same effect as `ALTER DATABASE`.
## Synopsis

```ebnf+diagram
AlterDatabaseStmt ::=
    'ALTER' 'DATABASE' DBName? DatabaseOptionList

DatabaseOption ::=
    DefaultKwdOpt ( CharsetKw '='? CharsetName | 'COLLATE' '='? CollationName | 'ENCRYPTION' '='? EncryptionOpt )
```
## Examples

Modify the test database schema to use the utf8mb4 character set:

```sql
ALTER DATABASE test DEFAULT CHARACTER SET = utf8mb4;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

Currently, TiDB only supports some character sets and collations. See [Character Set and Collation Support](https://docs.pingcap.com/tidb/stable/character-set-and-collation) for details.
## MySQL compatibility

The `ALTER DATABASE` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE DATABASE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-database)
* [SHOW DATABASES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-databases)
