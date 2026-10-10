# ADMIN CLEANUP INDEX syntax, usage example, and related statements

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-cleanup.md`
- Source Title: `ADMIN CLEANUP INDEX`
- Source Heading Path: `ADMIN CLEANUP INDEX | ADMIN CLEANUP INDEX > Synopsis | ADMIN CLEANUP INDEX > Examples | ADMIN CLEANUP INDEX > MySQL compatibility | ADMIN CLEANUP INDEX > See also`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `admin cleanup index`, `index inconsistency`, `dangling index`, `syntax`, `examples`, `mysql compatibility`, `admin check index`, `admin recover index`, `single-threaded execution`, `non-atomic execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0223_86fd946185`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-cleanup.md#admin-cleanup-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0ce8386f618f9432287bee1acd219cbf29ec08b459e077b99519ce9c158fdd7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cleanup#admin-cleanup-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-cleanup.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, example output, and operational notes for deleting dangling index entries with ADMIN CLEANUP INDEX after data and index inconsistency errors.
- Retrieval Keywords: ADMIN CLEANUP INDEX, ADMIN CLEANUP INDEX tbl idx;, AdminCleanupStmt, ADMIN CLEANUP INDEX syntax, ADMIN CLEANUP TABLE LOCK, redundant indexes, dangling index, inconsistent data and index, ERROR 1105 (HY000): inconsistent index idx handle count 3 isn't equal to value count 2, ADMIN CHECK INDEX tbl idx, REMOVED_COUNT, ADMIN RECOVER INDEX, single thread, not atomic, TiDB extension to MySQL syntax, foreign key constraints not support yet
- Follow-up Guidance: The source also points to ADMIN CHECK TABLE/INDEX and ADMIN RECOVER INDEX, and notes that if execution is interrupted it is recommended to execute ADMIN CLEANUP INDEX again until it succeeds.
- Classification Note: This is classified as an operation chunk because the official content centers on the SQL statement syntax, execution example, result output, and runtime notes for ADMIN CLEANUP INDEX in TiDB.

## Official Source Content

# ADMIN CLEANUP INDEX

The `ADMIN CLEANUP INDEX` statement is used to delete redundant indexes from a table when the table has inconsistent data and index. Note that this syntax does not support [foreign key constraints](https://docs.pingcap.com/tidb/stable/foreign-key) yet.
## Synopsis

```ebnf+diagram
AdminCleanupStmt ::=
    'ADMIN' 'CLEANUP' ( 'INDEX' TableName IndexName | 'TABLE' 'LOCK' TableNameList )

TableNameList ::=
    TableName ( ',' TableName )*
```
## Examples

Assume that the `tbl` table in a database has inconsistent data and index due to some reasons (for example, some row data is lost in the cluster in a disaster recovery scenario):

```sql
SELECT * FROM tbl;
ERROR 1105 (HY000): inconsistent index idx handle count 3 isn't equal to value count 2

ADMIN CHECK INDEX tbl idx ;
ERROR 1105 (HY000): handle &kv.CommonHandle{encoded:[]uint8{0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf8}, colEndOffsets:[]uint16{0xa}}, index:types.Datum{k:0x5, decimal:0x0, length:0x0, i:0, collation:"utf8mb4_bin", b:[]uint8{0x0}, x:interface {}(nil)} != record:<nil>
```

It can be seen from the error message of the `SELECT` query that, the `tbl` table contains two rows of data and three rows of index data, which means inconsistent row and index data. At the same time, at least one index is in dangling state. In this case, you can use the `ADMIN CLEANUP INDEX` statement to delete the dangling index:

```sql
ADMIN CLEANUP INDEX tbl idx;
```

The execution result is as follows:

```sql
ADMIN CLEANUP INDEX tbl idx;
+---------------+
| REMOVED_COUNT |
+---------------+
|             1 |
+---------------+
```

You can execute the `ADMIN CHECK INDEX` statement again to check the consistency of data and index, and verify whether the data has been restored to a normal state:

```sql
ADMIN CHECK INDEX tbl idx;
Query OK, 0 rows affected (0.01 sec)
```

> **Note:**
>
> When the data and index are inconsistent due to the loss of replicas:
>
> - There might be a loss of both row data and index data. To restore the consistency, use the `ADMIN CLEANUP INDEX` and [`ADMIN RECOVER INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-recover) statements together.
> - The `ADMIN CLEANUP INDEX` statement is always executed in a single thread. When the table data is large, it is recommended to recover the index data by rebuilding the index.
> - When you execute the `ADMIN CLEANUP INDEX` statement, the corresponding table or index is not locked and TiDB allows other sessions to modify the table records at the same time. However, in this case, `ADMIN CLEANUP INDEX` might not be able to handle all table records correctly. Therefore, when you execute `ADMIN CLEANUP INDEX`, avoid modifying the table data at the same time.
> - If you use the enterprise edition of TiDB, you can [submit a request](https://docs.pingcap.com/tidb/stable/support) to contact the support engineer for help.
>
> The `ADMIN CLEANUP INDEX` statement is not atomic: if the statement is interrupted during execution, it is recommended to execute it again until it succeeds.

> **Note:**
>
> When the data and index are inconsistent due to the loss of replicas:
>
> - There might be a loss of both row data and index data. To restore the consistency, use the `ADMIN CLEANUP INDEX` and [`ADMIN RECOVER INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-recover) statements together.
> - The `ADMIN CLEANUP INDEX` statement is always executed in a single thread. When the table data is large, it is recommended to recover the index data by rebuilding the index.
> - When you execute the `ADMIN CLEANUP INDEX` statement, the corresponding table or index is not locked and TiDB allows other sessions to modify the table records at the same time. However, in this case, `ADMIN CLEANUP INDEX` might not be able to handle all table records correctly. Therefore, when you execute `ADMIN CLEANUP INDEX`, avoid modifying the table data at the same time.
> - If you use the enterprise edition of TiDB, you can [submit a request](https://tidb.support.pingcap.com/) to contact the support engineer for help.
>
> The `ADMIN CLEANUP INDEX` statement is not atomic: if the statement is interrupted during execution, it is recommended to execute it again until it succeeds.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`ADMIN CHECK TABLE/INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-check-table-index)
* [`ADMIN RECOVER INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-recover)
