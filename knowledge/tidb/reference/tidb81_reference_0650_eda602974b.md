# SHOW CREATE DATABASE syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-create-database.md`
- Source Title: `SHOW CREATE DATABASE`
- Source Heading Path: `SHOW CREATE DATABASE | SHOW CREATE DATABASE > Synopsis | SHOW CREATE DATABASE > Examples | SHOW CREATE DATABASE > MySQL compatibility | SHOW CREATE DATABASE > See also`
- Source Line Ranges: `5-64`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show-create-database`, `show-create-schema`, `syntax`, `examples`, `mysql-compatibility`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0650_eda602974b`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-create-database.md#show-create-database`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `909ce598203df3d0aa8acff0efa4b7584d9f18443138c6842def915631a7956b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-database#show-create-database
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-create-database.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the syntax, synonym, example output, or MySQL compatibility note for retrieving the exact SQL statement that re-creates an existing database.
- Retrieval Keywords: SHOW CREATE DATABASE, SHOW CREATE SCHEMA, ShowCreateDatabaseStmt, SHOW CREATE DATABASE syntax, SHOW CREATE SCHEMA IF NOT EXISTS, IF NOT EXISTS, DBName, CREATE DATABASE `test` /*!40100 DEFAULT CHARACTER SET utf8mb4 */, CREATE DATABASE /*!32312 IF NOT EXISTS*/ `test` /*!40100 DEFAULT CHARACTER SET utf8mb4 */, MySQL compatibility
- Follow-up Guidance: See also related SQL statements: CREATE TABLE, DROP TABLE, SHOW TABLES, and SHOW COLUMNS FROM.
- Classification Note: This is reference content because it defines the SHOW CREATE DATABASE statement syntax, states that SHOW CREATE SCHEMA is a synonym, and provides example SQL and output.

## Official Source Content

# SHOW CREATE DATABASE

`SHOW CREATE DATABASE` is used to show the exact SQL statement for re-creating an existing database. `SHOW CREATE SCHEMA` is a synonym for it.
## Synopsis

**ShowCreateDatabaseStmt:**

```ebnf+diagram
ShowCreateDatabaseStmt ::=
    "SHOW" "CREATE" ("DATABASE" | "SCHEMA") ("IF" "NOT" "EXISTS")? DBName
```
## Examples

```sql
CREATE DATABASE test;
```

```sql
Query OK, 0 rows affected (0.12 sec)
```

```sql
SHOW CREATE DATABASE test;
```

```sql
+----------+------------------------------------------------------------------+
| Database | Create Database                                                  |
+----------+------------------------------------------------------------------+
| test     | CREATE DATABASE `test` /*!40100 DEFAULT CHARACTER SET utf8mb4 */ |
+----------+------------------------------------------------------------------+
1 row in set (0.00 sec)
```

```sql
SHOW CREATE SCHEMA IF NOT EXISTS test;
```

```sql
+----------+-------------------------------------------------------------------------------------------+
| Database | Create Database                                                                           |
+----------+-------------------------------------------------------------------------------------------+
| test     | CREATE DATABASE /*!32312 IF NOT EXISTS*/ `test` /*!40100 DEFAULT CHARACTER SET utf8mb4 */ |
+----------+-------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

`SHOW CREATE DATABASE` is expected to be fully compatible with MySQL. If you find any compatibility differences, you can [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table)
* [DROP TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table)
* [SHOW TABLES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-tables)
* [SHOW COLUMNS FROM](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-columns-from)
