# Metadata lock overview, usage, impact, and observability

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/metadata-lock.md`
- Source Title: `Metadata Lock`
- Source Heading Path: `Metadata Lock | Metadata Lock > Concept | Metadata Lock > Scenarios | Metadata Lock > Usage | Metadata Lock > Impact | Metadata Lock > Observability`
- Source Line Ranges: `5-105`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `metadata-lock`, `ddl`, `dml`, `schema-change`, `transactions`, `system-variable`, `observability`, `blocked-ddl`, `kill`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0160_2517deed7c`
- Source ID: `tidb-docs-8.1:metadata-lock.md#metadata-lock`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fe644cde329fc663c2ea8a000d02f0ec552b732c24754bdf57edc76e04b62ba9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/metadata-lock#metadata-lock
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/metadata-lock.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what metadata lock is in TiDB, which DDL statements it applies to, how it affects DML and DDL, or how to inspect and identify a blocked DDL transaction.
- Retrieval Keywords: Metadata Lock, metadata lock, Information schema is changed, ERROR 8028 (HY000): public column a has changed, tidb_enable_metadata_lock, mysql.tidb_mdl_view, PROCESS privilege, KILL, blocked DDL, ALTER TABLE t ADD INDEX idx(a), ADD COLUMN, DROP COLUMN, DROP INDEX, DROP PARTITION, TRUNCATE TABLE, EXCHANGE PARTITION, CHANGE COLUMN, MODIFY COLUMN, SESSION ID, SQL_DIGESTS
- Follow-up Guidance: The source shows that you can query `mysql.tidb_mdl_view` with the `PROCESS` privilege to find the blocking `SESSION ID` and executed `SQL_DIGESTS`, and a global `KILL` can make the blocked DDL continue to execute.
- Classification Note: This is classified as operation because the content covers metadata lock behavior during DDL and DML, the `tidb_enable_metadata_lock` system variable, performance impact, and observability with `mysql.tidb_mdl_view` and `KILL`.

## Official Source Content

# Metadata Lock

This document introduces the metadata lock in TiDB.
## Concept

TiDB uses the online asynchronous schema change algorithm to support changing metadata objects. When a transaction is executed, it obtains the corresponding metadata snapshot at the transaction start. If the metadata is changed during a transaction, to ensure data consistency, TiDB returns an `Information schema is changed` error and the transaction fails to commit.

To solve the problem, TiDB v6.3.0 introduces metadata lock into the online DDL algorithm. To avoid most DML errors, TiDB coordinates the priority of DMLs and DDLs during table metadata change and makes executing DDLs wait for the DMLs with old metadata to commit.
## Scenarios

The metadata lock in TiDB applies to all DDL statements, such as:

- [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index)
- [`ADD COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column)
- [`DROP COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-column)
- [`DROP INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index)
- [`DROP PARTITION`](https://docs.pingcap.com/tidb/stable/partitioned-table#partition-management)
- [`TRUNCATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-truncate)
- [`EXCHANGE PARTITION`](https://docs.pingcap.com/tidb/stable/partitioned-table#partition-management)
- [`CHANGE COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-column)
- [`MODIFY COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-modify-column)

Enabling metadata lock might have some performance impact on the execution of the DDL task in TiDB. To reduce the impact, the following lists some scenarios that do not require metadata lock:

+ `SELECT` queries with auto-commit enabled
+ Stale Read is enabled
+ Access temporary tables
## Usage

Starting from v6.5.0, TiDB enables metadata lock by default. When you upgrade your existing cluster from v6.4.0 or earlier to v6.5.0 or later, TiDB automatically enables metadata lock. To disable metadata lock, you can set the system variable [`tidb_enable_metadata_lock`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_metadata_lock-new-in-v630) to `OFF`.
## Impact

- For DMLs, metadata lock does not block its execution, nor causes any deadlock.
- When metadata lock is enabled, the information of a metadata object in a transaction is determined on the first access and does not change after that.
- For DDLs, when changing metadata state, DDLs might be blocked by old transactions. The following is an example:

    | Session 1 | Session 2 |
    |:---------------------------|:----------|
    | `CREATE TABLE t (a INT);`  |           |
    | `INSERT INTO t VALUES(1);` |           |
    | `BEGIN;`                   |           |
    |                            | `ALTER TABLE t ADD COLUMN b INT;` |
    | `SELECT * FROM t;`<br/>(Uses the current metadata version of table `t`. Returns `(a=1, b=NULL)` and locks table `t`.)         |           |
    |                            | `ALTER TABLE t ADD COLUMN c INT;` (blocked by Session 1) |

    At the repeatable read isolation level, from the transaction start to the timepoint of determining the metadata of a table, if a DDL that requires data changes is performed, such as adding an index, or changing column types, the DDL returns an error as follows:

    | Session 1                  | Session 2                                 |
    |:---------------------------|:------------------------------------------|
    | `CREATE TABLE t (a INT);`  |                                           |
    | `INSERT INTO t VALUES(1);` |                                           |
    | `BEGIN;`                   |                                           |
    |                            | `ALTER TABLE t ADD INDEX idx(a);`         |
    | `SELECT * FROM t;` (index `idx` is not available) |                    |
    | `COMMIT;`                  |                                           |
    | `BEGIN;`                   |                                           |
    |                            | `ALTER TABLE t MODIFY COLUMN a CHAR(10);` |
    | `SELECT * FROM t;` (returns `ERROR 8028 (HY000): public column a has changed`) | |
## Observability

TiDB v6.3.0 introduces the `mysql.tidb_mdl_view` view to help you obtain the information of the current blocked DDL.

> **Note:**
>
> To select the `mysql.tidb_mdl_view` view, the [`PROCESS` privilege](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html#priv_process) is required.

The following takes adding an index for table `t` as an example. Assume that there is a DDL statement `ALTER TABLE t ADD INDEX idx(a)`:

```sql
SELECT * FROM mysql.tidb_mdl_view\G
*************************** 1. row ***************************
    JOB_ID: 141
   DB_NAME: test
TABLE_NAME: t
     QUERY: ALTER TABLE t ADD INDEX idx(a)
SESSION ID: 2199023255957
  TxnStart: 08-30 16:35:41.313(435643624013955072)
SQL_DIGESTS: ["begin","select * from `t`"]
1 row in set (0.02 sec)
```

From the preceding output, you can see that the transaction whose `SESSION ID` is `2199023255957` blocks the `ADD INDEX` DDL. `SQL_DIGEST` shows the SQL statements executed by this transaction, which is ``["begin","select * from `t`"]``. To make the blocked DDL continue to execute, you can use the following global `KILL` statement to kill the `2199023255957` transaction:

```sql
mysql> KILL 2199023255957;
Query OK, 0 rows affected (0.00 sec)
```

After killing the transaction, you can select the `mysql.tidb_mdl_view` view again. At this time, the preceding transaction is not shown in the output, which means the DDL is not blocked.

```sql
SELECT * FROM mysql.tidb_mdl_view\G
Empty set (0.01 sec)
```
