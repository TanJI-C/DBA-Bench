# Index selection optimizer hints

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in query blocks > USE_INDEX(t1_name, idx1_name [, idx2_name ...]) | Optimizer Hints > Hints that take effect in query blocks > FORCE_INDEX(t1_name, idx1_name [, idx2_name ...]) | Optimizer Hints > Hints that take effect in query blocks > IGNORE_INDEX(t1_name, idx1_name [, idx2_name ...])`
- Source Line Ranges: `411-451`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `optimizer-hints`, `index-selection`, `use-index`, `force-index`, `ignore-index`, `query-planning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0125_3e218e1f6d`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#use-index-t1-name-idx1-name-idx2-name`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3dfc991f3400d85000336530a3227910e15aa4e0fb1624bf295dacbed70c8bb7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#use-index-t1-name-idx1-name-idx2-name
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when looking for optimizer hints that restrict, force, or ignore index choices for a table in a query block.
- Retrieval Keywords: USE_INDEX, FORCE_INDEX, IGNORE_INDEX, USE_INDEX(t1_name, idx1_name [, idx2_name ...]), FORCE_INDEX(t1_name, idx1_name [, idx2_name ...]), IGNORE_INDEX(t1_name, idx1_name [, idx2_name ...]), use index(idx1), force index(idx1), ignore index(idx1, idx2), index selection, full table scan
- Follow-up Guidance: The source states that specifying only the table name but not an index name in USE_INDEX causes execution to consider no index and scan the entire table.
- Classification Note: This is classified as performance content because it covers optimizer hints that influence index selection during query planning.

## Official Source Content

### USE_INDEX(t1_name, idx1_name [, idx2_name ...])

The `USE_INDEX(t1_name, idx1_name [, idx2_name ...])` hint tells the optimizer to use only the given index(es) for a specified `t1_name` table. For example, applying the following hint has the same effect as executing the `select * from t t1 use index(idx1, idx2);` statement.

```sql
SELECT /*+ USE_INDEX(t1, idx1, idx2) */ * FROM t1;
```

> **Note:**
>
> If you specify only the table name but not index name in this hint, the execution does not consider any index but scan the entire table.
### FORCE_INDEX(t1_name, idx1_name [, idx2_name ...])

The `FORCE_INDEX(t1_name, idx1_name [, idx2_name ...])` hint tells the optimizer to use only the given index(es).

The usage and effect of `FORCE_INDEX(t1_name, idx1_name [, idx2_name ...])` are the same as the usage and effect of `USE_INDEX(t1_name, idx1_name [, idx2_name ...])`.

The following 4 queries have the same effect:

```sql
SELECT /*+ USE_INDEX(t, idx1) */ * FROM t;
SELECT /*+ FORCE_INDEX(t, idx1) */ * FROM t;
SELECT * FROM t use index(idx1);
SELECT * FROM t force index(idx1);
```
### IGNORE_INDEX(t1_name, idx1_name [, idx2_name ...])

The `IGNORE_INDEX(t1_name, idx1_name [, idx2_name ...])` hint tells the optimizer to ignore the given index(es) for a specified `t1_name` table. For example, applying the following hint has the same effect as executing the `select * from t t1 ignore index(idx1, idx2);` statement.

```sql
select /*+ IGNORE_INDEX(t1, idx1, idx2) */ * from t t1;
```
