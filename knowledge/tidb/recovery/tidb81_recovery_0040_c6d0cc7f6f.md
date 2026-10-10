# FLASHBACK DATABASE syntax, limits, and examples

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-flashback-database.md`
- Source Title: `FLASHBACK DATABASE`
- Source Heading Path: `FLASHBACK DATABASE | FLASHBACK DATABASE > Syntax | FLASHBACK DATABASE > Syntax > Synopsis | FLASHBACK DATABASE > Notes | FLASHBACK DATABASE > Example | FLASHBACK DATABASE > MySQL compatibility`
- Source Line Ranges: `5-69`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `flashback`, `database-restore`, `drop-database`, `gc-safe-point`, `retention`, `syntax`, `limitations`, `binlog`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0040_c6d0cc7f6f`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-flashback-database.md#flashback-database`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a2835cc4b7a5e839b699f08e10a9387ffab8af2c5c1476fc088b1f4e73e4610`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-database#flashback-database
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-flashback-database.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to restore a database deleted by DROP within the GC life time, what FLASHBACK DATABASE syntax supports, or what limits and errors apply around tikv_gc_safe_point.
- Retrieval Keywords: FLASHBACK DATABASE, FLASHBACK DATABASE DBName [TO newDBName], DROP DATABASE, tidb_gc_life_time, tikv_gc_safe_point, SELECT * FROM mysql.tidb WHERE variable_name = 'tikv_gc_safe_point';, ERROR 1105 (HY000): Can't find dropped database, GC safe point, restore deleted database, rename restored database, TiDB Binlog, MySQL compatibility
- Follow-up Guidance: The source also notes binlog-related conditions, including downstream support for FLASHBACK DATABASE, GC life time requirements between primary and secondary databases, and handling replication errors by filtering out the database and manually importing full data.
- Classification Note: This chunk is classified as recovery for the SQL component because it documents the FLASHBACK DATABASE statement used to restore a dropped database and its data within the GC retention window.

## Official Source Content

# FLASHBACK DATABASE

TiDB v6.4.0 introduces the `FLASHBACK DATABASE` syntax. You can use `FLASHBACK DATABASE` to restore a database and its data that are deleted by the `DROP` statement within the Garbage Collection (GC) life time.

You can set the retention time of historical data by configuring the [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) system variable. The default value is `10m0s`. You can query the current `safePoint`, that is, the time point GC has been performed up to, using the following SQL statement:

```sql
SELECT * FROM mysql.tidb WHERE variable_name = 'tikv_gc_safe_point';
```

As long as a database is deleted by `DROP` after the `tikv_gc_safe_point` time, you can use `FLASHBACK DATABASE` to restore the database.
## Syntax

```sql
FLASHBACK DATABASE DBName [TO newDBName]
```
### Synopsis

```ebnf+diagram
FlashbackDatabaseStmt ::=
    'FLASHBACK' DatabaseSym DBName FlashbackToNewName
FlashbackToNewName ::=
    ( 'TO' Identifier )?
```
## Notes

* If the database is deleted before the `tikv_gc_safe_point` time, you cannot restore the data using the `FLASHBACK DATABASE` statement. The `FLASHBACK DATABASE` statement returns an error similar to `ERROR 1105 (HY000): Can't find dropped database 'test' in GC safe point 2022-11-06 16:10:10 +0800 CST`.

* You cannot restore the same database multiple times using the `FLASHBACK DATABASE` statement. Because the database restored by `FLASHBACK DATABASE` has the same schema ID as the original database, restoring the same database multiple times leads to duplicate schema IDs. In TiDB, the database schema ID must be globally unique.

* When TiDB Binlog is enabled, note the following when you use `FLASHBACK DATABASE`:

    * The downstream secondary database must support `FLASHBACK DATABASE`.
    * The GC life time of the secondary database must be longer than that of the primary database. Otherwise, the latency between the upstream and the downstream might lead to data restoration failure in the downstream.
    * If TiDB Binlog replication encounters an error, you need to filter out the database in TiDB Binlog and then manually import full data for this database.
## Example

- Restore the `test` database that is deleted by `DROP`:

    ```sql
    DROP DATABASE test;
    ```

    ```sql
    FLASHBACK DATABASE test;
    ```

- Restore the `test` database that is deleted by `DROP` and rename it to `test1`:

    ```sql
    DROP DATABASE test;
    ```

    ```sql
    FLASHBACK DATABASE test TO test1;
    ```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
