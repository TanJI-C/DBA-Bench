# FLUSH TABLES syntax, behavior, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-flush-tables.md`
- Source Title: `FLUSH TABLES | TiDB SQL Statement Reference`
- Source Heading Path: `FLUSH TABLES | FLUSH TABLES > Synopsis | FLUSH TABLES > Examples | FLUSH TABLES > MySQL compatibility | FLUSH TABLES > See also`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `flush tables`, `sql syntax`, `mysql compatibility`, `read lock`, `historical reads`, `table locking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0597_2894ff0c65`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-flush-tables.md#flush-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0efb5dac51dff4298cdc65da32c20e2e1373a8bd02cbc863bda54cb9b4887859`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-tables#flush-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-flush-tables.md

## Retrieval Guidance

- Use When: Use this chunk when answering what FLUSH TABLES does in TiDB, how FLUSH TABLES WITH READ LOCK behaves, or whether the statement is only present for MySQL compatibility.
- Retrieval Keywords: FLUSH TABLES, FLUSH TABLES WITH READ LOCK, FLUSH TABLES syntax, MySQL compatibility, parsed but ignored, table cache, locking tables, @@tidb_snapshot, ERROR 1105 (HY000): FLUSH TABLES WITH READ LOCK is not supported. Please use @@tidb_snapshot, Historical reads, Read historical data
- Follow-up Guidance: The source points to Historical reads and Read historical data, and the error message says to use @@tidb_snapshot.
- Classification Note: This is reference content because it defines the FLUSH TABLES syntax, shows example output, and states the TiDB compatibility behavior and error semantics for this SQL statement.

## Official Source Content

# FLUSH TABLES

This statement is included for compatibility with MySQL. It has no effective usage in TiDB.
## Synopsis

```ebnf+diagram
FlushStmt ::=
    'FLUSH' NoWriteToBinLogAliasOpt FlushOption

NoWriteToBinLogAliasOpt ::=
    ( 'NO_WRITE_TO_BINLOG' | 'LOCAL' )?

FlushOption ::=
    'PRIVILEGES'
|   'STATUS'
|    'TIDB' 'PLUGINS' PluginNameList
|    'HOSTS'
|    LogTypeOpt 'LOGS'
|    TableOrTables TableNameListOpt WithReadLockOpt

LogTypeOpt ::=
    ( 'BINARY' | 'ENGINE' | 'ERROR' | 'GENERAL' | 'SLOW' )?

TableOrTables ::=
    'TABLE'
|   'TABLES'

TableNameListOpt ::=
    TableNameList?

WithReadLockOpt ::=
    ( 'WITH' 'READ' 'LOCK' )?
```
## Examples

```sql
mysql> FLUSH TABLES;
Query OK, 0 rows affected (0.00 sec)

mysql> FLUSH TABLES WITH READ LOCK;
ERROR 1105 (HY000): FLUSH TABLES WITH READ LOCK is not supported.  Please use @@tidb_snapshot
```
## MySQL compatibility

* TiDB does not have a concept of table cache as in MySQL. Thus, `FLUSH TABLES` is parsed but ignored in TiDB for compatibility.
* The statement `FLUSH TABLES WITH READ LOCK` produces an error, as TiDB does not currently support locking tables. It is recommended to use [Historical reads](https://docs.pingcap.com/tidb/stable/read-historical-data) for this purpose instead.
## See also

* [Read historical data](https://docs.pingcap.com/tidb/stable/read-historical-data)
