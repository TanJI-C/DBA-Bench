# EXPLAIN plans for null-aware semi join with IN and = ANY subqueries

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-subqueries.md`
- Source Title: `Explain Statements That Use Subqueries`
- Source Heading Path: `Explain Statements That Use Subqueries > Null-aware semi join (`IN` and `= ANY` subqueries)`
- Source Line Ranges: `149-198`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `subqueries`, `semi-join`, `null-aware`, `in`, `any`, `hash-join`, `inner-join`, `cartesian-product`, `filter`, `nullable-columns`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0271_0fa704333c`
- Source ID: `tidb-docs-8.1:explain-subqueries.md#null-aware-semi-join-in-and-any-subqueries`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `57edae5b5c6a68cb7965321193a3ed1c26e1b67caf18e932d4ddfacf4a5bf886`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-subqueries#null-aware-semi-join-in-and-any-subqueries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-subqueries.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting EXPLAIN output for `IN` or `= ANY` subqueries on nullable join keys, especially null-aware semi join, left outer semi join, Cartesian product, filter, or inner join rewrites.
- Retrieval Keywords: Null-aware semi join, `IN` subqueries, `= ANY` subqueries, left outer semi join, semi join, Cartesian product and filter, HashJoin, CARTESIAN left outer semi join, inner join, HashAgg, not(isnull(...)), EXPLAIN SELECT (a,b) IN (SELECT * FROM s) FROM t, EXPLAIN SELECT * FROM t WHERE (a,b) IN (SELECT * FROM s), The `Exists` operator is also converted to semi join, but it is not null-aware
- Follow-up Guidance: The chunk also notes that the `Exists` operator is converted to semi join, but it is not null-aware.
- Classification Note: This is reference content because it explains how TiDB shows and optimizes EXPLAIN plans for null-aware semi join behavior with `IN` and `= ANY` subqueries on nullable columns.

## Official Source Content

## Null-aware semi join (`IN` and `= ANY` subqueries)

The value of the `IN` or `= ANY` set operator is three-valued (`true`, `false`, and `NULL`). For the join type converted from either of the two operators, TiDB needs to be aware of the `NULL` on both sides of the join key and process it in a special way.

Subqueries containing `IN` and `= ANY` operators are converted to semi join and left outer semi join respectively. In the preceding example of [Semi join](#semi-join-correlated-subquery), since columns `test.t1.id` and `test.t2.t1_id` on both sides of the join key are `not NULL`, the semi join does not need to be considered as null-aware (`NULL` is not processed specially). TiDB processes the null-aware semi join based on the Cartesian product and filter without special optimization. The following is an example:

```sql
CREATE TABLE t(a INT, b INT);
CREATE TABLE s(a INT, b INT);
EXPLAIN SELECT (a,b) IN (SELECT * FROM s) FROM t;
EXPLAIN SELECT * FROM t WHERE (a,b) IN (SELECT * FROM s);
```

```sql
tidb> EXPLAIN SELECT (a,b) IN (SELECT * FROM s) FROM t;
+-----------------------------+---------+-----------+---------------+-------------------------------------------------------------------------------------------+
| id                          | estRows | task      | access object | operator info                                                                             |
+-----------------------------+---------+-----------+---------------+-------------------------------------------------------------------------------------------+
| HashJoin_8                  | 1.00    | root      |               | CARTESIAN left outer semi join, other cond:eq(test.t.a, test.s.a), eq(test.t.b, test.s.b) |
| ├─TableReader_12(Build)     | 1.00    | root      |               | data:TableFullScan_11                                                                     |
| │ └─TableFullScan_11        | 1.00    | cop[tikv] | table:s       | keep order:false, stats:pseudo                                                            |
| └─TableReader_10(Probe)     | 1.00    | root      |               | data:TableFullScan_9                                                                      |
|   └─TableFullScan_9         | 1.00    | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                            |
+-----------------------------+---------+-----------+---------------+-------------------------------------------------------------------------------------------+
5 rows in set (0.00 sec)

tidb> EXPLAIN SELECT * FROM t WHERE (a,b) IN (SELECT * FROM s);
+------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------------+
| id                           | estRows | task      | access object | operator info                                                                                       |
+------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------------+
| HashJoin_11                  | 1.00    | root      |               | inner join, equal:[eq(test.t.a, test.s.a) eq(test.t.b, test.s.b)]                                   |
| ├─TableReader_14(Build)      | 1.00    | root      |               | data:Selection_13                                                                                   |
| │ └─Selection_13             | 1.00    | cop[tikv] |               | not(isnull(test.t.a)), not(isnull(test.t.b))                                                        |
| │   └─TableFullScan_12       | 1.00    | cop[tikv] | table:t       | keep order:false, stats:pseudo                                                                      |
| └─HashAgg_17(Probe)          | 1.00    | root      |               | group by:test.s.a, test.s.b, funcs:firstrow(test.s.a)->test.s.a, funcs:firstrow(test.s.b)->test.s.b |
|   └─TableReader_24           | 1.00    | root      |               | data:Selection_23                                                                                   |
|     └─Selection_23           | 1.00    | cop[tikv] |               | not(isnull(test.s.a)), not(isnull(test.s.b))                                                        |
|       └─TableFullScan_22     | 1.00    | cop[tikv] | table:s       | keep order:false, stats:pseudo                                                                      |
+------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------------+
8 rows in set (0.01 sec)
```

In the first query statement `EXPLAIN SELECT (a,b) IN (SELECT * FROM s) FROM t;`, since columns `a` and `b` of tables `t` and `s` are NULLABLE, the left outer semi join converted by the `IN` subquery is null-aware. Specifically, the Cartesian product is calculated first, then the column connected by `IN` or `= ANY` is put into other conditions as a normal equality query for filtering.

In the second query statement `EXPLAIN SELECT * FROM t WHERE (a,b) IN (SELECT * FROM s);`, since columns `a` and `b` of tables `t` and `s` are NULLABLE, the `IN` subquery should have been converted to a null-aware semi join. But TiDB optimizes it by converting semi join to inner join and aggregate. This is because `NULL` and `false` are equivalent in `IN` subqueries for non-scalar output. The `NULL` rows in the push-down filter results in the negative semantics of the `WHERE` clause. Therefore, these rows can be ignored beforehand.

> **Note:**
>
> The `Exists` operator is also converted to semi join, but it is not null-aware.
