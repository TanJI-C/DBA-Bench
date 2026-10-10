# Query block hints for hash joins, semi-join rewrite, and MPP joins

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in query blocks > HASH_JOIN(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > NO_HASH_JOIN(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > HASH_JOIN_BUILD(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > HASH_JOIN_PROBE(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > SEMI_JOIN_REWRITE() | Optimizer Hints > Hints that take effect in query blocks > SHUFFLE_JOIN(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > BROADCAST_JOIN(t1_name [, tl_name ...])`
- Source Line Ranges: `185-300`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`, `tikv`
- Topic Tags: `optimizer-hints`, `hash-join`, `semi-join`, `mpp`, `shuffle-join`, `broadcast-join`, `join-build-side`, `join-probe-side`, `query-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0455_1100becee3`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#hash-join-t1-name-tl-name`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0bdc4cc5ccfaec92ab3ae4efa3b8e5b84dfcf90ce8b151d0298a03b2e1ff833f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#hash-join-t1-name-tl-name
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when looking up optimizer hints that control hash join selection, hash join build or probe side, semi-join rewrite for EXISTS subqueries, or MPP shuffle and broadcast joins in TiDB SQL.
- Retrieval Keywords: HASH_JOIN, NO_HASH_JOIN, HASH_JOIN_BUILD, HASH_JOIN_PROBE, SEMI_JOIN_REWRITE, SHUFFLE_JOIN, BROADCAST_JOIN, TIDB_HJ, EXISTS subquery, semi join rewrite to ordinary join, Shuffle Join algorithm, Broadcast Join algorithm, MPP mode, TiFlash MPP mode, build side, probe side, IndexJoin, hash join algorithm
- Follow-up Guidance: The source notes that SHUFFLE_JOIN and BROADCAST_JOIN only take effect in MPP mode and can be combined with HASH_JOIN_BUILD and HASH_JOIN_PROBE to control the Build side and Probe side.
- Classification Note: This is reference content because it defines the exact SQL optimizer hint names, their effects on query planning, and example statements and EXPLAIN outputs.

## Official Source Content

### HASH_JOIN(t1_name [, tl_name ...])

The `HASH_JOIN(t1_name [, tl_name ...])` hint tells the optimizer to use the hash join algorithm for the given table(s). This algorithm allows the query to be executed concurrently with multiple threads, which achieves a higher processing speed but consumes more memory. For example:

```sql
select /*+ HASH_JOIN(t1, t2) */ * from t1, t2 where t1.id = t2.id;
```

> **Note:**
>
> `TIDB_HJ` is the alias for `HASH_JOIN` in TiDB 3.0.x and earlier versions. If you are using any of these versions, you must apply the `TIDB_HJ(t1_name [, tl_name ...])` syntax for the hint. For the later versions of TiDB, `TIDB_HJ` and `HASH_JOIN` are both valid names for the hint, but `HASH_JOIN` is recommended.
### NO_HASH_JOIN(t1_name [, tl_name ...])

The `NO_HASH_JOIN(t1_name [, tl_name ...])` hint tells the optimizer not to use the hash join algorithm for the given table(s). For example:

```sql
SELECT /*+ NO_HASH_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```
### HASH_JOIN_BUILD(t1_name [, tl_name ...])

The `HASH_JOIN_BUILD(t1_name [, tl_name ...])` hint tells the optimizer to use the hash join algorithm on specified tables with these tables working as the build side. In this way, you can build hash tables using specific tables. For example:

```sql
SELECT /*+ HASH_JOIN_BUILD(t1) */ * FROM t1, t2 WHERE t1.id = t2.id;
```
### HASH_JOIN_PROBE(t1_name [, tl_name ...])

The `HASH_JOIN_PROBE(t1_name [, tl_name ...])` hint tells the optimizer to use the hash join algorithm on specified tables with these tables working as the probe side. In this way, you can execute the hash join algorithm with specific tables as the probe side. For example:

```sql
SELECT /*+ HASH_JOIN_PROBE(t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```
### SEMI_JOIN_REWRITE()

The `SEMI_JOIN_REWRITE()` hint tells the optimizer to rewrite the semi-join query to an ordinary join query. Currently, this hint only works for `EXISTS` subqueries.

If this hint is not used to rewrite the query, when the hash join is selected in the execution plan, the semi-join query can only use the subquery to build a hash table. In this case, when the result of the subquery is bigger than that of the outer query, the execution speed might be slower than expected.

Similarly, when the index join is selected in the execution plan, the semi-join query can only use the outer query as the driving table. In this case, when the result of the subquery is smaller than that of the outer query, the execution speed might be slower than expected.

When `SEMI_JOIN_REWRITE()` is used to rewrite the query, the optimizer can extend the selection range to select a better execution plan.

```sql
-- Does not use SEMI_JOIN_REWRITE() to rewrite the query.
EXPLAIN SELECT * FROM t WHERE EXISTS (SELECT 1 FROM t1 WHERE t1.a = t.a);
```

```sql
+-----------------------------+---------+-----------+------------------------+---------------------------------------------------+
| id                          | estRows | task      | access object          | operator info                                     |
+-----------------------------+---------+-----------+------------------------+---------------------------------------------------+
| MergeJoin_9                 | 7992.00 | root      |                        | semi join, left key:test.t.a, right key:test.t1.a |
| ├─IndexReader_25(Build)     | 9990.00 | root      |                        | index:IndexFullScan_24                            |
| │ └─IndexFullScan_24        | 9990.00 | cop[tikv] | table:t1, index:idx(a) | keep order:true, stats:pseudo                     |
| └─IndexReader_23(Probe)     | 9990.00 | root      |                        | index:IndexFullScan_22                            |
|   └─IndexFullScan_22        | 9990.00 | cop[tikv] | table:t, index:idx(a)  | keep order:true, stats:pseudo                     |
+-----------------------------+---------+-----------+------------------------+---------------------------------------------------+
```

```sql
-- Uses SEMI_JOIN_REWRITE() to rewrite the query.
EXPLAIN SELECT * FROM t WHERE EXISTS (SELECT /*+ SEMI_JOIN_REWRITE() */ 1 FROM t1 WHERE t1.a = t.a);
```

```sql
+------------------------------+---------+-----------+------------------------+---------------------------------------------------------------------------------------------------------------+
| id                           | estRows | task      | access object          | operator info                                                                                                 |
+------------------------------+---------+-----------+------------------------+---------------------------------------------------------------------------------------------------------------+
| IndexJoin_16                 | 1.25    | root      |                        | inner join, inner:IndexReader_15, outer key:test.t1.a, inner key:test.t.a, equal cond:eq(test.t1.a, test.t.a) |
| ├─StreamAgg_39(Build)        | 1.00    | root      |                        | group by:test.t1.a, funcs:firstrow(test.t1.a)->test.t1.a                                                      |
| │ └─IndexReader_34           | 1.00    | root      |                        | index:IndexFullScan_33                                                                                        |
| │   └─IndexFullScan_33       | 1.00    | cop[tikv] | table:t1, index:idx(a) | keep order:true                                                                                               |
| └─IndexReader_15(Probe)      | 1.25    | root      |                        | index:Selection_14                                                                                            |
|   └─Selection_14             | 1.25    | cop[tikv] |                        | not(isnull(test.t.a))                                                                                         |
|     └─IndexRangeScan_13      | 1.25    | cop[tikv] | table:t, index:idx(a)  | range: decided by [eq(test.t.a, test.t1.a)], keep order:false, stats:pseudo                                   |
+------------------------------+---------+-----------+------------------------+---------------------------------------------------------------------------------------------------------------+
```

From the preceding example, you can see that when using the `SEMI_JOIN_REWRITE()` hint, TiDB can select the execution method of IndexJoin based on the driving table `t1`.
### SHUFFLE_JOIN(t1_name [, tl_name ...])

The `SHUFFLE_JOIN(t1_name [, tl_name ...])` hint tells the optimizer to use the Shuffle Join algorithm on specified tables. This hint only takes effect in the MPP mode. For example:

```sql
SELECT /*+ SHUFFLE_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```

> **Note:**
>
> - Before using this hint, make sure that the current TiDB cluster can support using TiFlash MPP mode in the query. For details, refer to [Use TiFlash MPP Mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode).
> - This hint can be used in combination with the [`HASH_JOIN_BUILD` hint](#hash_join_buildt1_name--tl_name-) and [`HASH_JOIN_PROBE` hint](#hash_join_probet1_name--tl_name-) to control the Build side and Probe side of the Shuffle Join algorithm.
### BROADCAST_JOIN(t1_name [, tl_name ...])

`BROADCAST_JOIN(t1_name [, tl_name ...])` hint tells the optimizer to use the Broadcast Join algorithm on specified tables. This hint only takes effect in the MPP mode. For example:

```sql
SELECT /*+ BROADCAST_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```

> **Note:**
>
> - Before using this hint, make sure that the current TiDB cluster can support using TiFlash MPP mode in the query. For details, refer to [Use TiFlash MPP Mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode).
>- This hint can be used in combination with the [`HASH_JOIN_BUILD` hint](#hash_join_buildt1_name--tl_name-) and [`HASH_JOIN_PROBE` hint](#hash_join_probet1_name--tl_name-) to control the Build side and Probe side of the Broadcast Join algorithm.
