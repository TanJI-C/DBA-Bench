# Null-aware anti semi join EXPLAIN behavior and related subquery EXPLAIN links

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-subqueries.md`
- Source Title: `Explain Statements That Use Subqueries`
- Source Heading Path: `Explain Statements That Use Subqueries > Null-aware anti semi join (`NOT IN` and `!= ALL` subqueries) | Explain Statements That Use Subqueries > Explain statements using other types of subqueries`
- Source Line Ranges: `199-270`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `subqueries`, `anti-semi-join`, `null-aware-join`, `hash-join`, `not-in`, `any`, `execution-plan`, `mpp`, `indexes`, `joins`, `aggregation`, `views`, `partitions`, `index-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0272_cb8ca73076`
- Source ID: `tidb-docs-8.1:explain-subqueries.md#null-aware-anti-semi-join-not-in-and-all-subqueries`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `188b7d570b8503d8386965ef0b4ab7f8a14215304e430ea71d3ffc078c957efd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-subqueries#null-aware-anti-semi-join-not-in-and-all-subqueries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-subqueries.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting EXPLAIN output for NOT IN or != ALL subqueries that show null-aware anti semi join or null-aware anti left outer semi join behavior.
- Retrieval Keywords: NOT IN, != ALL, Null-aware anti semi join, Null-aware anti left outer semi join, NAAJ, NA-EQ, HashJoin, EXPLAIN SELECT (a, b) NOT IN (SELECT * FROM s) FROM t, EXPLAIN SELECT * FROM t WHERE (a, b) NOT IN (SELECT * FROM s), anti semi join, anti left outer semi join, Not Exists, hash join, build table should be fixed to the right table, Explain Statements in the MPP Mode, Explain Statements That Use Indexes, Explain Statements That Use Joins, Explain Statements That Use Aggregation, Explain Statements Using Views, Explain Statements Using Partitions, Explain Statements Using Index Merge
- Follow-up Guidance: The source also links to EXPLAIN references for MPP mode, indexes, joins, aggregation, views, partitions, and index merge.
- Classification Note: This is classified as reference content because it explains how TiDB displays and optimizes null-aware anti semi joins in EXPLAIN output and points to related EXPLAIN documentation.

## Official Source Content

## Null-aware anti semi join (`NOT IN` and `!= ALL` subqueries)

The value of the `NOT IN` or `!= ALL` set operator is three-valued (`true`, `false`, and `NULL`). For the join type converted from either of the two operators, TiDB needs to be aware of the `NULL` on both sides of the join key and process it in a special way.

Subqueries containing `NOT IN` and `! = ALL` operators are converted to anti semi join and anti left outer semi join respectively. In the preceding example of [Anti semi join](#anti-semi-join-not-in-subquery), since columns `test.t3.t1_id` and `test.t1.id` on both sides of the join key are `not NULL`, the anti semi join does not need to be considered as null-aware (`NULL` is not processed specially).

TiDB v6.3.0 optimizes null-aware anti join (NAAJ) as follows:

- Build hash join using the null-aware equality condition (NA-EQ)

    Set operators introduce the equality condition, which requires a special process for the `NULL` value of operators on both sides of the condition. The equality condition that requires null-aware is called NA-EQ. Different from earlier versions, TiDB v6.3.0 no longer processes NA-EQ as before, but places it in other conditions after join, and then determines the legitimacy of the result set after matching the Cartesian product.

    Since TiDB v6.3.0, NA-EQ, a weakened equality condition, is still used to build hash join. This reduces the matching amount of data that needs to be traversed and speeds up the matching process. The acceleration is more significant when the percentage of total `DISTINCT()` values of the build table is almost 100%.

- Speed up the return of matching results using the special property of `NULL`

    Since anti semi join is a conjunctive normal form (CNF), a `NULL` on either side of the join leads to a definite result. This property can be used to speed up the return of the entire matching process.

The following is an example:

```sql
CREATE TABLE t(a INT, b INT);
CREATE TABLE s(a INT, b INT);
EXPLAIN SELECT (a, b) NOT IN (SELECT * FROM s) FROM t;
EXPLAIN SELECT * FROM t WHERE (a, b) NOT IN (SELECT * FROM s);
```

```sql
tidb> EXPLAIN SELECT (a, b) NOT IN (SELECT * FROM s) FROM t;
+-----------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
| id                          | estRows  | task      | access object | operator info                                                                               |
+-----------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
| HashJoin_8                  | 10000.00 | root      |               | Null-aware anti left outer semi join, equal:[eq(test.t.b, test.s.b) eq(test.t.a, test.s.a)] |
| ├─TableReader_12(Build)     | 10000.00 | root      |               | data:TableFullScan_11                                                                       |
| │ └─TableFullScan_11        | 10000.00 | cop[tikv] | table:s       | keep order:false, stats:pseudo                                                              |
| └─TableReader_10(Probe)     | 10000.00 | root      |               | data:TableFullScan_9                                                                        |
|   └─TableFullScan_9         | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                              |
+-----------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------+
5 rows in set (0.00 sec)

tidb> EXPLAIN SELECT * FROM t WHERE (a, b) NOT IN (SELECT * FROM s);
+-----------------------------+----------+-----------+---------------+----------------------------------------------------------------------------------+
| id                          | estRows  | task      | access object | operator info                                                                    |
+-----------------------------+----------+-----------+---------------+----------------------------------------------------------------------------------+
| HashJoin_8                  | 8000.00  | root      |               | Null-aware anti semi join, equal:[eq(test.t.b, test.s.b) eq(test.t.a, test.s.a)] |
| ├─TableReader_12(Build)     | 10000.00 | root      |               | data:TableFullScan_11                                                            |
| │ └─TableFullScan_11        | 10000.00 | cop[tikv] | table:s       | keep order:false, stats:pseudo                                                   |
| └─TableReader_10(Probe)     | 10000.00 | root      |               | data:TableFullScan_9                                                             |
|   └─TableFullScan_9         | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                   |
+-----------------------------+----------+-----------+---------------+----------------------------------------------------------------------------------+
5 rows in set (0.00 sec)
```

In the first query statement `EXPLAIN SELECT (a, b) NOT IN (SELECT * FROM s) FROM t;`, since columns `a` and `b` of tables `t` and `s` are NULLABLE, the left outer semi join converted by `NOT IN` subquery is null-aware. The difference is that NAAJ optimization also uses the NA-EQ as the hash join condition, which greatly speeds up the join calculation.

In the second query statement `EXPLAIN SELECT * FROM t WHERE (a, b) NOT IN (SELECT * FROM s);`, since columns `a` and `b` of tables `t` and `s` are NULLABLE, the anti semi join converted by `NOT IN` subquery is null-aware. The difference is that NAAJ optimization also uses the NA-EQ as the hash join condition, which greatly speeds up the join calculation.

Currently, TiDB can only be null-aware of anti semi join and anti left outer semi join. Only the hash join type is supported and its build table should be fixed to the right table.

> **Note:**
>
> The `Not Exists` operator is also converted to the anti semi join, but it is not null-aware.
## Explain statements using other types of subqueries

+ [Explain Statements in the MPP Mode](https://docs.pingcap.com/tidb/stable/explain-mpp)
+ [Explain Statements That Use Indexes](https://docs.pingcap.com/tidb/stable/explain-indexes)
+ [Explain Statements That Use Joins](https://docs.pingcap.com/tidb/stable/explain-joins)
+ [Explain Statements That Use Aggregation](https://docs.pingcap.com/tidb/stable/explain-aggregation)
+ [Explain Statements Using Views](https://docs.pingcap.com/tidb/stable/explain-views)
+ [Explain Statements Using Partitions](https://docs.pingcap.com/tidb/stable/explain-partitions)
+ [Explain Statements Using Index Merge](https://docs.pingcap.com/tidb/stable/explain-index-merge)
