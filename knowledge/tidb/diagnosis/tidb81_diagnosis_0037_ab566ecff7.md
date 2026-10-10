# Index join performance after re-adding index

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-joins.md`
- Source Title: `Explain Statements That Use Joins`
- Source Heading Path: `Explain Statements That Use Joins > Index Join`
- Source Line Ranges: `122-133`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `explain analyze`, `index join`, `join hints`, `indexing`, `performance comparison`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0037_ab566ecff7`
- Source ID: `tidb-docs-8.1:explain-joins.md#index-join`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2e63af262beb1b607c9a4bd10e3272080e2f0fe24a23f7d39ee3db4edbe1a6af`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-joins#index-join
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-joins.md

## Retrieval Guidance

- Use When: Use this chunk when comparing join performance with EXPLAIN ANALYZE after re-adding an index for an index join query with join hints.
- Retrieval Keywords: EXPLAIN ANALYZE, Index Join, INL_JOIN(t1, t2), HASH_JOIN(t1, t2), ALTER TABLE t2 ADD INDEX (t1_id), t1.int_col, t1.id = t2.t1_id, performance improves from 0.3 sec to 0.06 sec, missing index on t1.int_col
- Follow-up Guidance: The example follows the index addition with EXPLAIN ANALYZE for INL_JOIN, HASH_JOIN, and the unhinted INNER JOIN query on t1 and t2.
- Classification Note: This is classified as diagnosis because the content diagnoses join performance by showing how adding an index changes EXPLAIN ANALYZE results for an index join query.

## Official Source Content

In the above example, the index join operation is missing an index on `t1.int_col`. Once this index is added, the performance of the operation improves from `0.3 sec` to `0.06 sec`, as the following result shows:

```sql
-- Re-add index
ALTER TABLE t2 ADD INDEX (t1_id);

EXPLAIN ANALYZE SELECT /*+ INL_JOIN(t1, t2) */  * FROM t1 INNER JOIN t2 ON t1.id = t2.t1_id WHERE t1.int_col = 1;
EXPLAIN ANALYZE SELECT /*+ HASH_JOIN(t1, t2) */  * FROM t1 INNER JOIN t2 ON t1.id = t2.t1_id WHERE t1.int_col = 1;
EXPLAIN ANALYZE SELECT * FROM t1 INNER JOIN t2 ON t1.id = t2.t1_id WHERE t1.int_col = 1;
```
