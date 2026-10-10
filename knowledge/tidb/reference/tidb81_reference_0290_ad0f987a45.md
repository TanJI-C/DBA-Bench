# ONLY_FULL_GROUP_BY behavior, MySQL differences, and related variable

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/aggregate-group-by-functions.md`
- Source Title: `Aggregate (GROUP BY) Functions`
- Source Heading Path: `Aggregate (GROUP BY) Functions > SQL mode support | Aggregate (GROUP BY) Functions > SQL mode support > Differences from MySQL | Aggregate (GROUP BY) Functions > Related system variables`
- Source Line Ranges: `94-178`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `sql-mode`, `only-full-group-by`, `mysql-compatibility`, `distinct`, `order-by`, `having`, `group-by-aliases`, `system-variables`, `group-concat-max-len`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0290_ad0f987a45`
- Source ID: `tidb-docs-8.1:functions-and-operators/aggregate-group-by-functions.md#sql-mode-support`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `96f5b728c1890034e2e4e7e251a09bbf2f8d6f5e991bc2ee1c02bff65f1e2883`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions#sql-mode-support
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/aggregate-group-by-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up `ONLY_FULL_GROUP_BY` behavior in TiDB, documented differences from MySQL for `DISTINCT`, `ORDER BY`, `HAVING`, and `GROUP BY`, or the related `group_concat_max_len` variable.
- Retrieval Keywords: SQL mode support, ONLY_FULL_GROUP_BY, sql_mode, ERROR 1055 (42000), Expression #2 of SELECT list is not in GROUP BY clause, ambiguous non-aggregated columns, Differences from MySQL, select distinct a, b from t order by c, DISTINCT and ORDER BY, HAVING clause, alias in the HAVING clause, noncolumn expressions in GROUP BY clauses, aliases in GROUP BY clauses, group_concat_max_len, GROUP_CONCAT()
- Follow-up Guidance: The content states that TiDB currently enables `ONLY_FULL_GROUP_BY` mode by default and links `group_concat_max_len` to the system variables documentation.
- Classification Note: This is reference content because it describes SQL mode semantics, exact compatibility differences from MySQL, and the related system variable for `GROUP_CONCAT()`.

## Official Source Content

## SQL mode support

TiDB supports the SQL Mode `ONLY_FULL_GROUP_BY`, and when enabled TiDB will refuse queries with ambiguous non-aggregated columns. For example, this query is illegal with `ONLY_FULL_GROUP_BY` enabled because the non-aggregated column "b" in the `SELECT` list does not appear in the `GROUP BY` statement:

```sql
drop table if exists t;
create table t(a bigint, b bigint, c bigint);
insert into t values(1, 2, 3), (2, 2, 3), (3, 2, 3);

mysql> select a, b, sum(c) from t group by a;
+------+------+--------+
| a    | b    | sum(c) |
+------+------+--------+
|    1 |    2 |      3 |
|    2 |    2 |      3 |
|    3 |    2 |      3 |
+------+------+--------+
3 rows in set (0.01 sec)

mysql> set sql_mode = 'ONLY_FULL_GROUP_BY';
Query OK, 0 rows affected (0.00 sec)

mysql> select a, b, sum(c) from t group by a;
ERROR 1055 (42000): Expression #2 of SELECT list is not in GROUP BY clause and contains nonaggregated column 'b' which is not functionally dependent on columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by
```

TiDB currently enables the [`ONLY_FULL_GROUP_BY`](https://docs.pingcap.com/tidb/stable/mysql-compatibility#default-differences) mode by default.
### Differences from MySQL

The current implementation of `ONLY_FULL_GROUP_BY` is less strict than that in MySQL 5.7. For example, suppose that we execute the following query, expecting the results to be ordered by "c":

```sql
drop table if exists t;
create table t(a bigint, b bigint, c bigint);
insert into t values(1, 2, 1), (1, 2, 2), (1, 3, 1), (1, 3, 2);
select distinct a, b from t order by c;
```

To order the result, duplicates must be eliminated first. But to do so, which row should we keep? This choice influences the retained value of "c", which in turn influences ordering and makes it arbitrary as well.

In MySQL, a query that has `DISTINCT` and `ORDER BY` is rejected as invalid if any `ORDER BY` expression does not satisfy at least one of these conditions:

- The expression is equal to one in the `SELECT` list
- All columns referenced by the expression and belonging to the query's selected tables are elements of the `SELECT` list

But in TiDB, the above query is legal, for more information see [#4254](https://github.com/pingcap/tidb/issues/4254).

Another TiDB extension to standard SQL permits references in the `HAVING` clause to aliased expressions in the `SELECT` list. For example, the following query returns "name" values that occur only once in table "orders":

```sql
select name, count(name) from orders
group by name
having count(name) = 1;
```

The TiDB extension permits the use of an alias in the `HAVING` clause for the aggregated column:

```sql
select name, count(name) as c from orders
group by name
having c = 1;
```

Standard SQL permits only column expressions in `GROUP BY` clauses, so a statement such as this is invalid because "FLOOR(value/100)" is a noncolumn expression:

```sql
select id, floor(value/100)
from tbl_name
group by id, floor(value/100);
```

TiDB extends standard SQL to permit noncolumn expressions in `GROUP BY` clauses and considers the preceding statement valid.

Standard SQL also does not permit aliases in `GROUP BY` clauses. TiDB extends standard SQL to permit aliases, so another way to write the query is as follows:

```sql
select id, floor(value/100) as val
from tbl_name
group by id, val;
```
## Related system variables

The [`group_concat_max_len`](https://docs.pingcap.com/tidb/stable/system-variables#group_concat_max_len) variable sets the maximum number of items for the `GROUP_CONCAT()` function.
