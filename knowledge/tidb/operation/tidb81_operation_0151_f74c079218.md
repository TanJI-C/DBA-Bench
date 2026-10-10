# SQL semantics, transactions, compatibility, and post-delete behavior

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/sql-faq.md`
- Source Title: `SQL FAQs`
- Source Heading Path: `SQL FAQs > The order of results is different from MySQL when `ORDER BY` is omitted | SQL FAQs > Does TiDB support `SELECT FOR UPDATE`? | SQL FAQs > Can the codec of TiDB guarantee that the UTF-8 string is memcomparable? Is there any coding suggestion if our key needs to support UTF-8? | SQL FAQs > What is the maximum number of statements in a transaction? | SQL FAQs > Why does the auto-increment ID of the later inserted data is smaller than that of the earlier inserted data in TiDB? | SQL FAQs > How do I modify the `sql_mode` in TiDB? | SQL FAQs > Error: `java.sql.BatchUpdateException:statement count 5001 exceeds the transaction limitation` while using Sqoop to write data into TiDB in batches | SQL FAQs > Does TiDB have a function like the Flashback Query in Oracle? Does it support DDL? | SQL FAQs > Does TiDB release space immediately after deleting data? | SQL FAQs > Why does the query speed get slow after data is deleted?`
- Source Line Ranges: `63-190`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `ecosystem`, `shared`
- Topic Tags: `order-by`, `determinism`, `select-for-update`, `locking`, `utf8mb4`, `memcomparable`, `transaction-limit`, `auto-increment`, `sql-mode`, `sqoop`, `historical-read`, `gc`, `space-reclamation`, `region-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0151_f74c079218`
- Source ID: `tidb-docs-8.1:faq/sql-faq.md#the-order-of-results-is-different-from-mysql-when-order-by-is-omitted`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4c9c81e40cbfa90a49b8e3515e674633a47340c034bf4e6255c1f871309893e6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/sql-faq#the-order-of-results-is-different-from-mysql-when-order-by-is-omitted
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/sql-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about SQL result ordering, `SELECT FOR UPDATE`, UTF-8 memcomparable strings, transaction statement limits, auto-increment behavior, `sql_mode`, Sqoop batch transaction errors, historical reads, and post-delete space or performance behavior.
- Retrieval Keywords: ORDER BY omitted, implementation-dependent ordering, non-deterministic ORDER BY, tidb_enable_ordered_result_mode, SELECT FOR UPDATE, pessimistic locking, optimistic locking, utf8mb4, memcomparable, maximum number of statements in a transaction, 5000, stmt-count-limit, AUTO_INCREMENT, sql_mode, SESSION, GLOBAL, java.sql.BatchUpdateException:statement count 5001 exceeds the transaction limitation, Sqoop, -Dsqoop.export.records.per.statement=10, AS OF TIMESTAMP, DELETE TRUNCATE DROP space release, GC 10 minutes by default, compaction, Region Merge
- Follow-up Guidance: The chunk provides the exact Sqoop option `-Dsqoop.export.records.per.statement=10` and points to `AS OF TIMESTAMP` for historical reads including DDL.
- Classification Note: Classified as operation for the sql component because the content covers SQL semantics, transaction and locking behavior, compatibility settings, batch write limits, and operational effects after deleting data.

## Official Source Content

## The order of results is different from MySQL when `ORDER BY` is omitted

It is not a bug. The default order of records depends on various situations without any guarantee of consistency.

The order of results in MySQL might appear stable because queries are executed in a single thread. However, it is common that query plans can change when upgrading to new versions. It is recommended to use `ORDER BY` whenever an order of results is desired.

The reference can be found in [ISO/IEC 9075:1992, Database Language SQL- July 30, 1992](http://www.contrib.andrew.cmu.edu/~shadow/sql/sql1992.txt), which states as follows:

> If an `<order by clause>` is not specified, then the table specified by the `<cursor specification>` is T and the ordering of rows in T is implementation-dependent.

In the following two queries, both results are considered legal:

```sql
> select * from t;
+------+------+
| a    | b    |
+------+------+
|    1 |    1 |
|    2 |    2 |
+------+------+
2 rows in set (0.00 sec)
```

```sql
> select * from t; -- the order of results is not guaranteed
+------+------+
| a    | b    |
+------+------+
|    2 |    2 |
|    1 |    1 |
+------+------+
2 rows in set (0.00 sec)
```

If the list of columns used in the `ORDER BY` is non-unique, the statement is also considered non-deterministic. In the following example, the column `a` has duplicate values. Thus, only `ORDER BY a, b` is guaranteed deterministic:

```sql
> select * from t order by a;
+------+------+
| a    | b    |
+------+------+
|    1 |    1 |
|    2 |    1 |
|    2 |    2 |
+------+------+
3 rows in set (0.00 sec)
```

In the following statement, the order of column `a` is guaranteed, but the order of `b` is not guaranteed.

```sql
> select * from t order by a;
+------+------+
| a    | b    |
+------+------+
|    1 |    1 |
|    2 |    2 |
|    2 |    1 |
+------+------+
3 rows in set (0.00 sec)
```

In TiDB, you can also use the system variable [`tidb_enable_ordered_result_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_ordered_result_mode) to sort the final output result automatically.
## Does TiDB support `SELECT FOR UPDATE`?

Yes. When using pessimistic locking (the default since TiDB v3.0.8) the `SELECT FOR UPDATE` execution behaves similar to MySQL.

When using optimistic locking, `SELECT FOR UPDATE` does not lock data when the transaction is started, but checks conflicts when the transaction is committed. If the check reveals conflicts, the committing transaction rolls back.

For details, see [description of the `SELECT` syntax elements](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select#description-of-the-syntax-elements).
## Can the codec of TiDB guarantee that the UTF-8 string is memcomparable? Is there any coding suggestion if our key needs to support UTF-8?

The default character set in TiDB is `utf8mb4`. The strings are in memcomparable format. For more information about the character set in TiDB, see [Character Set and Collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation).
## What is the maximum number of statements in a transaction?

The maximum number of statements in a transaction is 5000 by default.

In the optimistic transaction mode, When transaction retry is enabled, the default upper limit is 5000. You can adjust the limit by using the [`stmt-count-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#stmt-count-limit) parameter.
## Why does the auto-increment ID of the later inserted data is smaller than that of the earlier inserted data in TiDB?

The auto-increment ID feature in TiDB is only guaranteed to be automatically incremental and unique but is not guaranteed to be allocated sequentially. Currently, TiDB is allocating IDs in batches. If data is inserted into multiple TiDB servers simultaneously, the allocated IDs are not sequential. When multiple threads concurrently insert data to multiple `tidb-server` instances, the auto-increment ID of the later inserted data might be smaller. TiDB allows specifying `AUTO_INCREMENT` for the integer field, but allows only one `AUTO_INCREMENT` field in a single table. For details, see [Auto-increment ID](https://docs.pingcap.com/tidb/stable/mysql-compatibility#auto-increment-id) and [the AUTO_INCREMENT attribute](https://docs.pingcap.com/tidb/stable/auto-increment).
## How do I modify the `sql_mode` in TiDB?

TiDB supports modifying the [`sql_mode`](https://docs.pingcap.com/tidb/stable/system-variables#sql_mode) system variables on a SESSION or GLOBAL basis.

- Changes to [`GLOBAL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable) scoped variables propagate to the rest servers of the cluster and persist across restarts. This means that you do not need to change the `sql_mode` value on each TiDB server.
- Changes to `SESSION` scoped variables only affect the current client session. After restarting a server, the changes are lost.
## Error: `java.sql.BatchUpdateException:statement count 5001 exceeds the transaction limitation` while using Sqoop to write data into TiDB in batches

In Sqoop, `--batch` means committing 100 statements in each batch, but by default each statement contains 100 SQL statements. So, 100 * 100 = 10000 SQL statements, which exceeds 5000, the maximum number of statements allowed in a single TiDB transaction.

Two solutions:

- Add the `-Dsqoop.export.records.per.statement=10` option as follows:

    ```bash
    sqoop export \
        -Dsqoop.export.records.per.statement=10 \
        --connect jdbc:mysql://mysql.example.com/sqoop \
        --username sqoop ${user} \
        --password ${passwd} \
        --table ${tab_name} \
        --export-dir ${dir} \
        --batch
    ```

- You can also increase the limited number of statements in a single TiDB transaction, but this will consume more memory. For details, see [Limitations on SQL statements](https://docs.pingcap.com/tidb/stable/tidb-limitations#limitations-on-sql-statements).
## Does TiDB have a function like the Flashback Query in Oracle? Does it support DDL?

 Yes, it does. And it supports DDL as well. For details, see [Read Historical Data Using the `AS OF TIMESTAMP` Clause](https://docs.pingcap.com/tidb/stable/as-of-timestamp).
## Does TiDB release space immediately after deleting data?

None of the `DELETE`, `TRUNCATE` and `DROP` operations release data immediately. For the `TRUNCATE` and `DROP` operations, after the TiDB GC (Garbage Collection) time (10 minutes by default), the data is deleted and the space is released. For the `DELETE` operations, the data is deleted but the space is not immediately released until the compaction is performed.
## Why does the query speed get slow after data is deleted?

Deleting a large amount of data leaves a lot of useless keys, affecting the query efficiency. To solve the problem, you can use the [Region Merge](https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#method-3-enable-region-merge) feature. For details, see the [deleting data section in TiDB Best Practices](https://www.pingcap.com/blog/tidb-best-practice/#write).
