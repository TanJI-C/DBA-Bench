# Detect preprocessed subqueries from slow log

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/analyze-slow-queries.md`
- Source Title: `Analyze Slow Queries`
- Source Heading Path: `Analyze Slow Queries > Analyze system issues > Other key stages are slow > Subqueries are executed in advance`
- Source Line Ranges: `134-161`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `slow-query-analysis`, `subqueries`, `explain-analyze`, `slow-log`, `rewrite-time`, `preprocessing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0004_94bf90b423`
- Source ID: `tidb-docs-8.1:analyze-slow-queries.md#subqueries-are-executed-in-advance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f5770ce55c3226c6450b9f99861014decaaecd629bb0f759437c1a7d1f3a76ed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/analyze-slow-queries#subqueries-are-executed-in-advance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/analyze-slow-queries.md

## Retrieval Guidance

- Use When: Use this when a slow log shows Rewrite_time with Preproc_subqueries and you need to identify a non-correlated subquery executed in advance.
- Retrieval Keywords: Preproc_subqueries, Preproc_subqueries_time, Rewrite_time, subqueries are executed in advance, EXPLAIN ANALYZE, non-correlated subqueries, slow log
- Follow-up Guidance: The example slow log record shows `Rewrite_time: 7.765673663 Preproc_subqueries: 1 Preproc_subqueries_time: 7.765231874`.
- Classification Note: This chunk classifies a diagnosis case where a non-correlated subquery is executed during optimization and the slow log exposes it.

## Official Source Content

#### Subqueries are executed in advance

For statements with non-correlated subqueries, the subquery part might be executed in advance. For example, in `select * from t1 where a = (select max(a) from t2)`, the `select max(a) from t2` part might be executed in advance in the optimization stage. The result of `EXPLAIN ANALYZE` does not show the duration of this type of subqueries.

```sql
mysql> explain analyze select count(*) from t where a=(select max(t1.a) from t t1, t t2 where t1.a=t2.a);
+------------------------------+----------+---------+-----------+---------------+--------------------------+----------------------------------+-----------+------+
| id                           | estRows  | actRows | task      | access object | execution info           | operator info                    | memory    | disk |
+------------------------------+----------+---------+-----------+---------------+--------------------------+----------------------------------+-----------+------+
| StreamAgg_59                 | 1.00     | 1       | root      |               | time:4.69267ms, loops:2  | funcs:count(Column#10)->Column#8 | 372 Bytes | N/A  |
| └─TableReader_60             | 1.00     | 1       | root      |               | time:4.690428ms, loops:2 | data:StreamAgg_48                | 141 Bytes | N/A  |
|   └─StreamAgg_48             | 1.00     |         | cop[tikv] |               | time:0ns, loops:0        | funcs:count(1)->Column#10        | N/A       | N/A  |
|     └─Selection_58           | 16384.00 |         | cop[tikv] |               | time:0ns, loops:0        | eq(test.t.a, 1)                  | N/A       | N/A  |
|       └─TableFullScan_57     | 16384.00 | -1      | cop[tikv] | table:t       | time:0s, loops:0         | keep order:false                 | N/A       | N/A  |
+------------------------------+----------+---------+-----------+---------------+--------------------------+----------------------------------+-----------+------+
5 rows in set (7.77 sec)
```

But you can identify this type of subquery execution in the slow log:

```
# Query_time: 7.770634843
...
# Rewrite_time: 7.765673663 Preproc_subqueries: 1 Preproc_subqueries_time: 7.765231874
```

From log record above, you can see that a subquery is executed in advance and takes `7.76s`.
