# RECOVER TABLE syntax, behavior, examples, and implementation

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-recover-table.md`
- Source Title: `RECOVER TABLE`
- Source Heading Path: `RECOVER TABLE | RECOVER TABLE > Syntax | RECOVER TABLE > Synopsis | RECOVER TABLE > Examples | RECOVER TABLE > Implementation principle | RECOVER TABLE > MySQL compatibility`
- Source Line Ranges: `5-128`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `recover-table`, `drop-table`, `gc-lifetime`, `ddl-jobs`, `binlog-replication`, `snapshot-read`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0042_b78c3f301d`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-recover-table.md#recover-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6e2790b7095050d0b0bd191d9f2f57427bd0d4aa018083584a9dbf9d4e1d0446`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-recover-table#recover-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-recover-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how `RECOVER TABLE` works, its syntax, GC lifetime limits, DDL job based recovery, Binlog replication caveats, or MySQL compatibility in TiDB.
- Retrieval Keywords: RECOVER TABLE, RECOVER TABLE table_name, RECOVER TABLE BY JOB JOB_ID, RecoverTableStmt, DROP TABLE, GC life time, snapshot is older than GC safe point, ADMIN SHOW DDL JOBS 1, DDL JOB ID, drop table, mysql.gc_delete_range, GC Worker, snapshot read, Read Historical Data, TiDB Binlog, full import of the deleted table, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also describes using `ADMIN SHOW DDL JOBS 1` to find a `DDL JOB ID` and notes that TiDB Binlog replication can be resumed with a full import of the deleted table in the listed interruption situations.
- Classification Note: The official content is classified under recovery because it explains recovering a deleted table and its data within the GC life time after `DROP TABLE`.

## Official Source Content

# RECOVER TABLE

`RECOVER TABLE` is used to recover a deleted table and the data on it within the GC (Garbage Collection) life time after the `DROP TABLE` statement is executed.
## Syntax

```sql
RECOVER TABLE table_name;
```

```sql
RECOVER TABLE BY JOB JOB_ID;
```
## Synopsis

```ebnf+diagram
RecoverTableStmt ::=
    'RECOVER' 'TABLE' ( 'BY' 'JOB' Int64Num | TableName Int64Num? )

TableName ::=
    Identifier ( '.' Identifier )?

Int64Num ::= NUM

NUM ::= intLit
```

> **Note:**
>
> + If a table is deleted and the GC lifetime is out, the table cannot be recovered with `RECOVER TABLE`. Execution of `RECOVER TABLE` in this scenario returns an error like: `snapshot is older than GC safe point 2019-07-10 13:45:57 +0800 CST`.
>
> + If the TiDB version is 3.0.0 or later, it is not recommended for you to use `RECOVER TABLE` when TiDB Binlog is used.
>
> + `RECOVER TABLE` is supported in the Binlog version 3.0.1, so you can use `RECOVER TABLE` in the following three situations:
>
>     - Binlog version is 3.0.1 or later.
>     - TiDB 3.0 is used both in the upstream cluster and the downstream cluster.
>     - The GC life time of the secondary cluster must be longer than that of the primary cluster. However, as latency occurs during data replication between upstream and downstream databases, data recovery might fail in the downstream.

**Troubleshoot errors during TiDB Binlog replication**

When you use `RECOVER TABLE` in the upstream TiDB during TiDB Binlog replication, TiDB Binlog might be interrupted in the following three situations:

+ The downstream database does not support the `RECOVER TABLE` statement. An error instance: `check the manual that corresponds to your MySQL server version for the right syntax to use near 'RECOVER TABLE table_name'`.

+ The GC life time is not consistent between the upstream database and the downstream database. An error instance: `snapshot is older than GC safe point 2019-07-10 13:45:57 +0800 CST`.

+ Latency occurs during replication between upstream and downstream databases. An error instance: `snapshot is older than GC safe point 2019-07-10 13:45:57 +0800 CST`.

For the above three situations, you can resume data replication from TiDB Binlog with a [full import of the deleted table](https://docs.pingcap.com/tidb/stable/ecosystem-tool-user-guide#backup-and-restore---backup--restore-br).
## Examples

+ Recover the deleted table according to the table name.

    ```sql
    DROP TABLE t;
    ```

    ```sql
    RECOVER TABLE t;
    ```

    This method searches the recent DDL job history and locates the first DDL operation of the `DROP TABLE` type, and then recovers the deleted table with the name identical to the one table name specified in the `RECOVER TABLE` statement.

+ Recover the deleted table according to the table's `DDL JOB ID` used.

    Suppose that you had deleted the table `t` and created another `t`, and again you deleted the newly created `t`. Then, if you want to recover the `t` deleted in the first place, you must use the method that specifies the `DDL JOB ID`.

    ```sql
    DROP TABLE t;
    ```

    ```sql
    ADMIN SHOW DDL JOBS 1;
    ```

    The second statement above is used to search for the table's `DDL JOB ID` to delete `t`. In the following example, the ID is `53`.

    ```
    +--------+---------+------------+------------+--------------+-----------+----------+-----------+-----------------------------------+--------+
    | JOB_ID | DB_NAME | TABLE_NAME | JOB_TYPE   | SCHEMA_STATE | SCHEMA_ID | TABLE_ID | ROW_COUNT | START_TIME                        | STATE  |
    +--------+---------+------------+------------+--------------+-----------+----------+-----------+-----------------------------------+--------+
    | 53     | test    |            | drop table | none         | 1         | 41       | 0         | 2019-07-10 13:23:18.277 +0800 CST | synced |
    +--------+---------+------------+------------+--------------+-----------+----------+-----------+-----------------------------------+--------+
    ```

    ```sql
    RECOVER TABLE BY JOB 53;
    ```

    This method recovers the deleted table via the `DDL JOB ID`. If the corresponding DDL job is not of the `DROP TABLE` type, an error occurs.
## Implementation principle

When deleting a table, TiDB only deletes the table metadata, and writes the table data (row data and index data) to be deleted to the `mysql.gc_delete_range` table. The GC Worker in the TiDB background periodically removes from the `mysql.gc_delete_range` table the keys that exceed the GC life time.

Therefore, to recover a table, you only need to recover the table metadata and delete the corresponding row record in the `mysql.gc_delete_range` table before the GC Worker deletes the table data. You can use a snapshot read of TiDB to recover the table metadata. Refer to [Read Historical Data](https://docs.pingcap.com/tidb/stable/read-historical-data) for details.

Table recovery is done by TiDB obtaining the table metadata through snapshot read, and then going through the process of table creation similar to `CREATE TABLE`. Therefore, `RECOVER TABLE` itself is, in essence, a kind of DDL operation.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
