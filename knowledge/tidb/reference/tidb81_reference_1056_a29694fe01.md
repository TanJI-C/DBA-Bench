# View creation and query example with limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/views.md`
- Source Title: `Views`
- Source Heading Path: `Views > Example | Views > Limitations | Views > See also`
- Source Line Ranges: `153-247`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `views`, `create-view`, `query-example`, `drop-view`, `limitations`, `read-only`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1056_a29694fe01`
- Source ID: `tidb-docs-8.1:views.md#example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `946e5e9c3eeb3b06a1b77abc52ad086cbd550508e499aaa9b9f122cf044ecbfc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/views#example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/views.md

## Retrieval Guidance

- Use When: Use this content when you need an example of creating, querying, and dropping a view in TiDB or when checking documented limitations of views.
- Retrieval Keywords: create view v as select s.a from t left join s on t.a = s.a, select * from v, drop view v, views limitations, materialized views are not supported yet, views are read-only, UPDATE, INSERT, DELETE, TRUNCATE, DROP [VIEW | TABLE], CREATE VIEW, DROP VIEW
- Follow-up Guidance: The source includes a full SQL example with create table, insert, create view, select from the view, and drop view statements.
- Classification Note: This is reference content because it provides a worked SQL example and states explicit documented limitations and supported DDL for views.

## Official Source Content

## Example

The following example creates a view, queries this view, and delete this view:

```sql
create table t(a int, b int);
```

```
Query OK, 0 rows affected (0.01 sec)
```

```sql
insert into t values(1, 1),(2,2),(3,3);
```

```
Query OK, 3 rows affected (0.00 sec)
Records: 3  Duplicates: 0  Warnings: 0
```

```sql
create table s(a int);
```

```
Query OK, 0 rows affected (0.01 sec)
```

```sql
insert into s values(2),(3);
```

```
Query OK, 2 rows affected (0.01 sec)
Records: 2  Duplicates: 0  Warnings: 0
```

```sql
create view v as select s.a from t left join s on t.a = s.a;
```

```
Query OK, 0 rows affected (0.01 sec)
```

```sql
select * from v;
```

```
+------+
| a    |
+------+
| NULL |
|    2 |
|    3 |
+------+
3 rows in set (0.00 sec)
```

```sql
drop view v;
```

```
Query OK, 0 rows affected (0.02 sec)
```
## Limitations

Currently, views in TiDB are subject to the following limitations:

* Materialized views are not supported yet.
* Views in TiDB are read-only and do not support write operations such as `UPDATE`, `INSERT`, `DELETE`, and `TRUNCATE`.
* For created views, the only supported DDL operation is `DROP [VIEW | TABLE]`
## See also

- [CREATE VIEW](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-view)
- [DROP VIEW](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-view)
