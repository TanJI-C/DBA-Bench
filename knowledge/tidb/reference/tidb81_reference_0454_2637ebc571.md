# Join-related query block optimizer hints

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in query blocks > MERGE_JOIN(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > NO_MERGE_JOIN(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > INL_JOIN(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > NO_INDEX_JOIN(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > INL_HASH_JOIN | Optimizer Hints > Hints that take effect in query blocks > NO_INDEX_HASH_JOIN(t1_name [, tl_name ...]) | Optimizer Hints > Hints that take effect in query blocks > INL_MERGE_JOIN | Optimizer Hints > Hints that take effect in query blocks > NO_INDEX_MERGE_JOIN(t1_name [, tl_name ...])`
- Source Line Ranges: `117-184`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `optimizer-hints`, `join-algorithms`, `merge-join`, `index-nested-loop-join`, `index-hash-join`, `index-merge-join`, `join-order`, `aliases`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0454_2637ebc571`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#merge-join-t1-name-tl-name`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0426097251bf53593ae867b37ac69cc4e36c850dd0fae600e8daec14fc5bbb3f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#merge-join-t1-name-tl-name
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when you need reference details for join-related optimizer hints such as MERGE_JOIN, INL_JOIN, INL_HASH_JOIN, INL_MERGE_JOIN, or their NO_* forms, including alias requirements and inner-table candidate semantics.
- Retrieval Keywords: MERGE_JOIN, NO_MERGE_JOIN, INL_JOIN, NO_INDEX_JOIN, INL_HASH_JOIN, NO_INDEX_HASH_JOIN, INL_MERGE_JOIN, NO_INDEX_MERGE_JOIN, sort-merge join, index nested loop join, index nested loop hash join, index nested loop merge join, TIDB_SMJ, TIDB_INLJ, candidate table for the inner table, table alias in INL_JOIN, INL_JOIN hint does not take effect
- Follow-up Guidance: The source notes that in some cases the INL_JOIN hint might not take effect and refers to the INL_JOIN hint does not take effect section for more information.
- Classification Note: This is reference content because it catalogs join-related query block optimizer hints, their meanings, examples, alias rules, and related note text from the official documentation.

## Official Source Content

### MERGE_JOIN(t1_name [, tl_name ...])

The `MERGE_JOIN(t1_name [, tl_name ...])` hint tells the optimizer to use the sort-merge join algorithm for the given table(s). Generally, this algorithm consumes less memory but takes longer processing time. If there is a very large data volume or insufficient system memory, it is recommended to use this hint. For example:

```sql
select /*+ MERGE_JOIN(t1, t2) */ * from t1, t2 where t1.id = t2.id;
```

> **Note:**
>
> `TIDB_SMJ` is the alias for `MERGE_JOIN` in TiDB 3.0.x and earlier versions. If you are using any of these versions, you must apply the `TIDB_SMJ(t1_name [, tl_name ...])` syntax for the hint. For the later versions of TiDB, `TIDB_SMJ` and `MERGE_JOIN` are both valid names for the hint, but `MERGE_JOIN` is recommended.
### NO_MERGE_JOIN(t1_name [, tl_name ...])

The `NO_MERGE_JOIN(t1_name [, tl_name ...])` hint tells the optimizer not to use the sort-merge join algorithm for the given table(s). For example:

```sql
SELECT /*+ NO_MERGE_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```
### INL_JOIN(t1_name [, tl_name ...])

> **Note:**
>
> In some cases, the `INL_JOIN` hint might not take effect. For more information, see [`INL_JOIN` hint does not take effect](#inl_join-hint-does-not-take-effect).

The `INL_JOIN(t1_name [, tl_name ...])` hint tells the optimizer to use the index nested loop join algorithm for the given table(s). This algorithm might consume less system resources and take shorter processing time in some scenarios and might produce an opposite result in other scenarios. If the result set is less than 10,000 rows after the outer table is filtered by the `WHERE` condition, it is recommended to use this hint. For example:

```sql
SELECT /*+ INL_JOIN(t1, t2) */ * FROM t1, t2, t3 WHERE t1.id = t2.id AND t2.id = t3.id;
```

In the preceding SQL statement, the `INL_JOIN(t1, t2)` hint tells the optimizer to use the index nested loop join algorithm for `t1` and `t2`. Note that this does not mean that the index nested loop join algorithm is used between `t1` and `t2`. Instead, the hint indicates that `t1` and `t2` each use the index nested loop join algorithm with another table (`t3`).

The parameter(s) given in `INL_JOIN()` is the candidate table for the inner table when you create the query plan. For example, `INL_JOIN(t1)` means that TiDB only considers using `t1` as the inner table to create a query plan. If the candidate table has an alias, you must use the alias as the parameter in `INL_JOIN()`; if it does not have an alias, use the table's original name as the parameter. For example, in the `select /*+ INL_JOIN(t1) */ * from t t1, t t2 where t1.a = t2.b;` query, you must use the `t` table's alias `t1` or `t2` rather than `t` as `INL_JOIN()`'s parameter.

> **Note:**
>
> `TIDB_INLJ` is the alias for `INL_JOIN` in TiDB 3.0.x and earlier versions. If you are using any of these versions, you must apply the `TIDB_INLJ(t1_name [, tl_name ...])` syntax for the hint. For the later versions of TiDB, `TIDB_INLJ` and `INL_JOIN` are both valid names for the hint, but `INL_JOIN` is recommended.
### NO_INDEX_JOIN(t1_name [, tl_name ...])

The `NO_INDEX_JOIN(t1_name [, tl_name ...])` hint tells the optimizer not to use the index nested loop join algorithm for the given table(s). For example:

```sql
SELECT /*+ NO_INDEX_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```
### INL_HASH_JOIN

The `INL_HASH_JOIN(t1_name [, tl_name])` hint tells the optimizer to use the index nested loop hash join algorithm. The conditions for using this algorithm are the same with the conditions for using the index nested loop join algorithm. The difference between the two algorithms is that `INL_JOIN` creates a hash table on the joined inner table, but `INL_HASH_JOIN` creates a hash table on the joined outer table. `INL_HASH_JOIN` has a fixed limit on memory usage, while the memory used by `INL_JOIN` depends on the number of rows matched in the inner table.
### NO_INDEX_HASH_JOIN(t1_name [, tl_name ...])

The `NO_INDEX_HASH_JOIN(t1_name [, tl_name ...])` hint tells the optimizer not to use the index nested loop hash join algorithm for the given table(s).
### INL_MERGE_JOIN

The `INL_MERGE_JOIN(t1_name [, tl_name])` hint tells the optimizer to use the index nested loop merge join algorithm. The conditions for using this algorithm are the same with the conditions for using the index nested loop join algorithm.
### NO_INDEX_MERGE_JOIN(t1_name [, tl_name ...])

The `NO_INDEX_MERGE_JOIN(t1_name [, tl_name ...])` hint tells the optimizer not to use the index nested loop merge join algorithm for the given table(s).
