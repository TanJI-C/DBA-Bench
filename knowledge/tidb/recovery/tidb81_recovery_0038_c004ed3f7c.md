# ADMIN RECOVER INDEX syntax, recovery example, and cautions

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-recover.md`
- Source Title: `ADMIN RECOVER INDEX`
- Source Heading Path: `ADMIN RECOVER INDEX | ADMIN RECOVER INDEX > Synopsis | ADMIN RECOVER INDEX > Examples | ADMIN RECOVER INDEX > MySQL compatibility | ADMIN RECOVER INDEX > See also`
- Source Line Ranges: `5-91`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `index-recovery`, `data-consistency`, `sql-syntax`, `admin-statements`, `non-atomic`, `single-threaded`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0038_c004ed3f7c`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-recover.md#admin-recover-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc4edb06d2788f49491cd7d67a587e101d914531b9fbf4166d92cf41a4b05ceb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-recover#admin-recover-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-recover.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, example output, and cautions for repairing inconsistent row data and index data with `ADMIN RECOVER INDEX` in TiDB.
- Retrieval Keywords: ADMIN RECOVER INDEX, AdminRecoverStmt, ADMIN RECOVER INDEX tbl idx;, ADMIN CHECK INDEX, inconsistent index idx handle count 2 isn't equal to value count 3, handle != record:<nil>, ADDED_COUNT, SCAN_COUNT, row data and index data are inconsistent, redundant indexes, single thread, not atomic, ADMIN CLEANUP INDEX, foreign key constraints
- Follow-up Guidance: The source also points to `ADMIN CHECK TABLE/INDEX` and `ADMIN CLEANUP INDEX`, and notes that if execution is interrupted it is recommended to execute `ADMIN RECOVER INDEX` again until it succeeds.
- Classification Note: This is classified as recovery for the SQL component because the statement recovers consistency between table row data and index data by supplementing missing index entries and documents execution limitations and compatibility notes.

## Official Source Content

# ADMIN RECOVER INDEX

When the row data and index data are inconsistent, you can use the `ADMIN RECOVER INDEX` statement to recover the consistency based on the redundant indexes. Note that this syntax does not support [foreign key constraints](https://docs.pingcap.com/tidb/stable/foreign-key) yet.
## Synopsis

```ebnf+diagram
AdminRecoverStmt ::=
    'ADMIN' 'RECOVER' 'INDEX' TableName IndexName
```
## Examples

Assume that the `tbl` table in a database has inconsistent row data and index due to some reasons (for example, some row data is lost in the cluster in a disaster recovery scenario):

```sql
SELECT * FROM tbl;
ERROR 1105 (HY000): inconsistent index idx handle count 2 isn't equal to value count 3

ADMIN CHECK INDEX tbl idx ;
ERROR 1105 (HY000): handle &kv.CommonHandle{encoded:[]uint8{0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf8}, colEndOffsets:[]uint16{0xa}}, index:types.Datum{k:0x5, decimal:0x0, length:0x0, i:0, collation:"utf8mb4_bin", b:[]uint8{0x0}, x:interface {}(nil)} != record:<nil>
```

It can be seen from the error message of the `SELECT` query that, the `tbl` table contains three rows of data and two rows of index data, which means inconsistent row data and index data. At the same time, at least one row of data has no corresponding index. In this case, you can use the `ADMIN RECOVER INDEX` statement to supplement the missing index:

```sql
ADMIN RECOVER INDEX tbl idx;
```

The execution result is as follows:

```sql
ADMIN RECOVER INDEX tbl idx;
+-------------+------------+
| ADDED_COUNT | SCAN_COUNT |
+-------------+------------+
|           1 |          3 |
+-------------+------------+
1 row in set (0.00 sec)
```

You can execute the `ADMIN CHECK INDEX` statement again to check the consistency of data and index, and verify whether the data has been restored to normal state:

```sql
ADMIN CHECK INDEX tbl idx;
Query OK, 0 rows affected (0.01 sec)
```

> **Note:**
>
> When the data and index are inconsistent due to the loss of replicas:
>
> - There might be a loss of both row data and index data. To address the issue, use the [`ADMIN CLEANUP INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cleanup) and `ADMIN RECOVER INDEX` statements together to recover the consistency of row data and index data.
> - The `ADMIN RECOVER INDEX` statement is always executed in a single thread. When the table data is large, it is recommended to recover the index data by rebuilding the index.
> - When you execute the `ADMIN RECOVER INDEX` statement, the corresponding table or index is not locked and TiDB allows other sessions to modify the table records at the same time. However, in this case, `ADMIN RECOVER INDEX` might not be able to handle all table records correctly. Therefore, when you execute `ADMIN RECOVER INDEX`, avoid modifying the table data at the same time.
> - If you use the enterprise edition of TiDB, you can [submit a request](https://docs.pingcap.com/tidb/stable/support) to contact the support engineer for help.
>
> The `ADMIN RECOVER INDEX` statement is not atomic: if the statement is interrupted during execution, it is recommended to execute it again until it succeeds.

> **Note:**
>
> When the data and index are inconsistent due to the loss of replicas:
>
> - There might be a loss of both row data and index data. To address the issue, use the [`ADMIN CLEANUP INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cleanup) and `ADMIN RECOVER INDEX` statements together to recover the consistency of row data and index data.
> - The `ADMIN RECOVER INDEX` statement is always executed in a single thread. When the table data is large, it is recommended to recover the index data by rebuilding the index.
> - When you execute the `ADMIN RECOVER INDEX` statement, the corresponding table or index is not locked and TiDB allows other sessions to modify the table records at the same time. However, in this case, `ADMIN RECOVER INDEX` might not be able to handle all table records correctly. Therefore, when you execute `ADMIN RECOVER INDEX`, avoid modifying the table data at the same time.
> - If you use the enterprise edition of TiDB, you can [submit a request](https://tidb.support.pingcap.com/) to contact the support engineer for help.
>
> The `ADMIN RECOVER INDEX` statement is not atomic: if the statement is interrupted during execution, it is recommended to execute it again until it succeeds.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ADMIN CHECK TABLE/INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-check-table-index)
* [`ADMIN CLEANUP INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cleanup)
