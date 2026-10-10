# Unstable result sets from non-full GROUP BY and ONLY_FULL_GROUP_BY

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-unstable-result-set.md`
- Source Title: `Unstable Result Set`
- Source Heading Path: `Unstable Result Set | Unstable Result Set > GROUP BY`
- Source Line Ranges: `5-115`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `unstable-result-set`, `group-by`, `full-group-by`, `only-full-group-by`, `sql-mode`, `aggregation`, `order-by`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0023_7b3c70c9db`
- Source ID: `tidb-docs-8.1:develop/dev-guide-unstable-result-set.md#unstable-result-set`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2024d28a4e92c6ba8d26233d7cd8355c070ed5ad7f0181d554f4a6ea4e2e9a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-unstable-result-set#unstable-result-set
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-unstable-result-set.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing unstable result sets or ERROR 1055 caused by a GROUP BY query that selects or orders by nonaggregated columns not declared in the GROUP BY clause.
- Retrieval Keywords: GROUP BY, FULL GROUP BY, NON-FULL GROUP BY, ONLY_FULL_GROUP_BY, sql_mode, ERROR 1055 (42000), Expression #2 of ORDER BY is not in GROUP BY clause, not functionally dependent on columns in GROUP BY clause, select a.class, a.stuname, max(b.courscore), group by a.class, order by a.class, a.stuname, stu_info, stu_score
- Follow-up Guidance: The source shows that setting @@sql_mode to include ONLY_FULL_GROUP_BY changes the example query from returning a result to returning ERROR 1055.
- Classification Note: This is classified as diagnosis because the content explains why NON-FULL GROUP BY causes ambiguous and unstable results and how ONLY_FULL_GROUP_BY exposes the issue as a syntax check.

## Official Source Content

# Unstable Result Set

This document describes how to solve unstable result set errors.
## GROUP BY

For convenience, MySQL "extends" the `GROUP BY` syntax to allow the `SELECT` clause to refer to non-aggregated fields not declared in the `GROUP BY` clause, that is, the `NON-FULL GROUP BY` syntax. In other databases, this is considered a syntax **_ERROR_** because it causes unstable result sets.

For example, you have two tables:

- `stu_info` stores the student information
- `stu_score` stores the student test scores.

Then you can write a SQL query statement like this:

```sql
SELECT
    `a`.`class`,
    `a`.`stuname`,
    max( `b`.`courscore` )
FROM
    `stu_info` `a`
    JOIN `stu_score` `b` ON `a`.`stuno` = `b`.`stuno`
GROUP BY
    `a`.`class`,
    `a`.`stuname`
ORDER BY
    `a`.`class`,
    `a`.`stuname`;
```

Result:

```sql
+------------+--------------+------------------+
| class      | stuname      | max(b.courscore) |
+------------+--------------+------------------+
| 2018_CS_01 | MonkeyDLuffy |             95.5 |
| 2018_CS_03 | PatrickStar  |             99.0 |
| 2018_CS_03 | SpongeBob    |             95.0 |
+------------+--------------+------------------+
3 rows in set (0.00 sec)
```

The `a`.`class` and `a`.`stuname` fields are specified in the `GROUP BY` statement, and the selected columns are `a`.`class`, `a`.`stuname` and `b`.`courscore`. The only column that is not in the `GROUP BY` condition, `b`.`courscore`, is also specified with a unique value using the `max()` function. There is **_ONLY ONE_** result that satisfies this SQL statement without any ambiguity, which is called the `FULL GROUP BY` syntax.

A counterexample is the `NON-FULL GROUP BY` syntax. For example, in these two tables, write the following SQL query (delete `a`.`stuname` in `GROUP BY`).

```sql
SELECT
    `a`.`class`,
    `a`.`stuname`,
    max( `b`.`courscore` )
FROM
    `stu_info` `a`
    JOIN `stu_score` `b` ON `a`.`stuno` = `b`.`stuno`
GROUP BY
    `a`.`class`
ORDER BY
    `a`.`class`,
    `a`.`stuname`;
```

Then two values that match this SQL are returned.

The first returned value:

```sql
+------------+--------------+------------------------+
| class      | stuname      | max( `b`.`courscore` ) |
+------------+--------------+------------------------+
| 2018_CS_01 | MonkeyDLuffy |                   95.5 |
| 2018_CS_03 | PatrickStar  |                   99.0 |
+------------+--------------+------------------------+
```

The second returned value:

```sql
+------------+--------------+------------------+
| class      | stuname      | max(b.courscore) |
+------------+--------------+------------------+
| 2018_CS_01 | MonkeyDLuffy |             95.5 |
| 2018_CS_03 | SpongeBob    |             99.0 |
+------------+--------------+------------------+
```

There are two results because you did **_NOT_** specify how to get the value of the `a`.`stuname` field in SQL, and two results are both satisfied by SQL semantics. It results in an unstable result set. Therefore, if you want to guarantee the stability of the result set of the `GROUP BY` statement, use the `FULL GROUP BY` syntax.

MySQL provides a `sql_mode` switch `ONLY_FULL_GROUP_BY` to control whether to check the `FULL GROUP BY` syntax or not. TiDB is also compatible with this `sql_mode` switch.

```sql
mysql> select a.class, a.stuname, max(b.courscore) from stu_info a join stu_score b on a.stuno=b.stuno group by a.class order by a.class, a.stuname;
+------------+--------------+------------------+
| class      | stuname      | max(b.courscore) |
+------------+--------------+------------------+
| 2018_CS_01 | MonkeyDLuffy |             95.5 |
| 2018_CS_03 | PatrickStar  |             99.0 |
+------------+--------------+------------------+
2 rows in set (0.01 sec)

mysql> set @@sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION,ONLY_FULL_GROUP_BY';
Query OK, 0 rows affected (0.01 sec)

mysql> select a.class, a.stuname, max(b.courscore) from stu_info a join stu_score b on a.stuno=b.stuno group by a.class order by a.class, a.stuname;
ERROR 1055 (42000): Expression #2 of ORDER BY is not in GROUP BY clause and contains nonaggregated column '' which is not functionally dependent on columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by
```

**Run results**: The above example shows the effect when you set `ONLY_FULL_GROUP_BY` for `sql_mode`.
