# Query block hints for ordered index access, coprocessor pushdown, storage selection, and index merge

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in query blocks > ORDER_INDEX(t1_name, idx1_name [, idx2_name ...]) | Optimizer Hints > Hints that take effect in query blocks > NO_ORDER_INDEX(t1_name, idx1_name [, idx2_name ...]) | Optimizer Hints > Hints that take effect in query blocks > AGG_TO_COP() | Optimizer Hints > Hints that take effect in query blocks > LIMIT_TO_COP() | Optimizer Hints > Hints that take effect in query blocks > READ_FROM_STORAGE(TIFLASH[t1_name [, tl_name ...]], TIKV[t2_name [, tl_name ...]]) | Optimizer Hints > Hints that take effect in query blocks > USE_INDEX_MERGE(t1_name, idx1_name [, idx2_name ...])`
- Source Line Ranges: `452-558`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `optimizer-hints`, `index-access`, `order-by`, `coprocessor-pushdown`, `storage-engine-selection`, `index-merge`, `query-plans`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0456_f573a2364e`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#order-index-t1-name-idx1-name-idx2-name`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aa6dafc4dc94881146efd08cbc667bb5e7db061fcc28f2bd1bf7834666a9017b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#order-index-t1-name-idx1-name-idx2-name
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when looking for query block optimizer hints that control ordered or unordered index access, aggregate or Limit/TopN coprocessor pushdown, storage engine selection with TiFlash or TiKV, or index merge plan selection.
- Retrieval Keywords: ORDER_INDEX, NO_ORDER_INDEX, AGG_TO_COP, LIMIT_TO_COP, READ_FROM_STORAGE, READ_FROM_STORAGE(TIFLASH[t1], TIKV[t2]), USE_INDEX_MERGE, Can't find a proper physical plan for this query, keep order:true, keep order:false, TopN + IndexScan, Limit + IndexScan, coprocessor pushdown, TIFLASH, TIKV, index merge, primary
- Follow-up Guidance: The content notes that `show warnings` is not involved here, but it does include warnings and notes such as removing `ORDER_INDEX` if `Can't find a proper physical plan for this query` occurs and that `USE_INDEX_MERGE` parameters are index names, with the primary key index name as `primary`.
- Classification Note: This is a SQL optimizer hint reference section because it defines the syntax, effect, examples, warnings, and notes for query block hints in execution plan selection.

## Official Source Content

### ORDER_INDEX(t1_name, idx1_name [, idx2_name ...])

The `ORDER_INDEX(t1_name, idx1_name [, idx2_name ...])` hint tells the optimizer to use only the given index for a specified table and read the specified index in order.

> **Warning:**
>
> This hint might cause SQL statements to fail. It is recommended to test it first. If an error occurs during the test, remove the hint. If the test runs normally, you can continue using it.

This hint is usually applied in the following scenario:

```sql
CREATE TABLE t(a INT, b INT, key(a), key(b));
EXPLAIN SELECT /*+ ORDER_INDEX(t, a) */ a FROM t ORDER BY a LIMIT 10;
```

```sql
+----------------------------+---------+-----------+---------------------+-------------------------------+
| id                         | estRows | task      | access object       | operator info                 |
+----------------------------+---------+-----------+---------------------+-------------------------------+
| Limit_10                   | 10.00   | root      |                     | offset:0, count:10            |
| └─IndexReader_14           | 10.00   | root      |                     | index:Limit_13                |
|   └─Limit_13               | 10.00   | cop[tikv] |                     | offset:0, count:10            |
|     └─IndexFullScan_12     | 10.00   | cop[tikv] | table:t, index:a(a) | keep order:true, stats:pseudo |
+----------------------------+---------+-----------+---------------------+-------------------------------+
```

The optimizer generates two types of plan for this query: `Limit + IndexScan(keep order: true)` and `TopN + IndexScan(keep order: false)`. When the `ORDER_INDEX` hint is used, the optimizer chooses the first plan that reads the index in order.

> **Note:**
>
> - If the query itself does not need to read the index in order (that is, without a hint, the optimizer does not generate a plan that reads the index in order in any situation), when the `ORDER_INDEX` hint is used, the error `Can't find a proper physical plan for this query` occurs. In this case, you need to remove the corresponding `ORDER_INDEX` hint.
> - The index on a partitioned table cannot be read in order, so do not use the `ORDER_INDEX` hint on the partitioned table and its related indexes.
### NO_ORDER_INDEX(t1_name, idx1_name [, idx2_name ...])

The `NO_ORDER_INDEX(t1_name, idx1_name [, idx2_name ...])` hint tells the optimizer to use only the given index for a specified table and not to read the specified index in order. This hint is usually applied in the following scenario.

The following example shows that the effect of the query statement is equivalent to `SELECT * FROM t t1 use index(idx1, idx2);`:

```sql
CREATE TABLE t(a INT, b INT, key(a), key(b));
EXPLAIN SELECT /*+ NO_ORDER_INDEX(t, a) */ a FROM t ORDER BY a LIMIT 10;
```

```sql
+----------------------------+----------+-----------+---------------------+--------------------------------+
| id                         | estRows  | task      | access object       | operator info                  |
+----------------------------+----------+-----------+---------------------+--------------------------------+
| TopN_7                     | 10.00    | root      |                     | test.t.a, offset:0, count:10   |
| └─IndexReader_14           | 10.00    | root      |                     | index:TopN_13                  |
|   └─TopN_13                | 10.00    | cop[tikv] |                     | test.t.a, offset:0, count:10   |
|     └─IndexFullScan_12     | 10000.00 | cop[tikv] | table:t, index:a(a) | keep order:false, stats:pseudo |
+----------------------------+----------+-----------+---------------------+--------------------------------+
```

The same as the example of `ORDER_INDEX` hint, the optimizer generates two types of plans for this query: `Limit + IndexScan(keep order: true)` and `TopN + IndexScan(keep order: false)`. When the `NO_ORDER_INDEX` hint is used, the optimizer will choose the latter plan to read the index out of order.
### AGG_TO_COP()

The `AGG_TO_COP()` hint tells the optimizer to push down the aggregate operation in the specified query block to the coprocessor. If the optimizer does not push down some aggregate function that is suitable for pushdown, then it is recommended to use this hint. For example:

```sql
select /*+ AGG_TO_COP() */ sum(t1.a) from t t1;
```
### LIMIT_TO_COP()

The `LIMIT_TO_COP()` hint tells the optimizer to push down the `Limit` and `TopN` operators in the specified query block to the coprocessor. If the optimizer does not perform such an operation, it is recommended to use this hint. For example:

```sql
SELECT /*+ LIMIT_TO_COP() */ * FROM t WHERE a = 1 AND b > 10 ORDER BY c LIMIT 1;
```
### READ_FROM_STORAGE(TIFLASH[t1_name [, tl_name ...]], TIKV[t2_name [, tl_name ...]])

The `READ_FROM_STORAGE(TIFLASH[t1_name [, tl_name ...]], TIKV[t2_name [, tl_name ...]])` hint tells the optimizer to read specific table(s) from specific storage engine(s). Currently, this hint supports two storage engine parameters - `TIKV` and `TIFLASH`. If a table has an alias, use the alias as the parameter of `READ_FROM_STORAGE()`; if the table does not have an alias, use the table's original name as the parameter. For example:

```sql
select /*+ READ_FROM_STORAGE(TIFLASH[t1], TIKV[t2]) */ t1.a from t t1, t t2 where t1.a = t2.a;
```
### USE_INDEX_MERGE(t1_name, idx1_name [, idx2_name ...])

The `USE_INDEX_MERGE(t1_name, idx1_name [, idx2_name ...])` hint tells the optimizer to access a specific table with the index merge method. Index merge has two types: intersection type and union type. For details, see [Explain Statements Using Index Merge](https://docs.pingcap.com/tidb/stable/explain-index-merge).

If you explicitly specify the list of indexes, TiDB selects indexes from the list to build index merge; if you do not specify the list of indexes, TiDB selects indexes from all available indexes to build index merge.

For the intersection-type index merge, the given list of indexes is a required parameter in the hint. For the union-type index merge, the given list of indexes is an optional parameter in the hint. See the following example.

```sql
SELECT /*+ USE_INDEX_MERGE(t1, idx_a, idx_b, idx_c) */ * FROM t1 WHERE t1.a > 10 OR t1.b > 10;
```

When multiple `USE_INDEX_MERGE` hints are made to the same table, the optimizer tries to select the index from the union of the index sets specified by these hints.

> **Note:**
>
> The parameters of `USE_INDEX_MERGE` refer to index names, rather than column names. The index name of the primary key is `primary`.
