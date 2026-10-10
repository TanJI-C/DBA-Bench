# Check vector index usage with EXPLAIN and warnings

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-index.md`
- Source Title: `Vector Search Index`
- Source Heading Path: `Vector Search Index > Check whether the vector index is used`
- Source Line Ranges: `131-194`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`, `tiflash`
- Topic Tags: `explain`, `explain-analyze`, `query-plan`, `vector-index`, `annindex`, `warnings`, `topk`, `distance-function`, `order-by`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0097_b5d04db010`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-index.md#check-whether-the-vector-index-is-used`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3b7305c61d00e3f33c51315bd61c85788843e1d944ea8e85980c94ca3eaa6ba8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index#check-whether-the-vector-index-is-used
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-index.md

## Retrieval Guidance

- Use When: Use this content when checking whether a vector search query uses the vector index and interpreting EXPLAIN output or ANN index warnings.
- Retrieval Keywords: EXPLAIN, EXPLAIN ANALYZE, annIndex:, operator info, TableFullScan, vector index is used, Top K, LIMIT 10, ORDER BY VEC_COSINE_DISTANCE, SHOW WARNINGS, ANN index not used, not ordering by COSINE distance, vec_cosine_distance() in ASC order, DESC
- Follow-up Guidance: If the vector index cannot be used, SHOW WARNINGS can reveal causes such as not ordering by COSINE distance or not using vec_cosine_distance() in ASC order.
- Classification Note: This is classified as diagnosis because the official content explains how to verify vector index usage from query plans and warnings.

## Official Source Content

## Check whether the vector index is used

Use the [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) or [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) statement to check whether a query is using the vector index. When `annIndex:` is presented in the `operator info` column for the `TableFullScan` executor, it means this table scan is utilizing the vector index.

**Example: the vector index is used**

```sql
[tidb]> EXPLAIN SELECT * FROM vector_table_with_index
ORDER BY VEC_COSINE_DISTANCE(embedding, '[1, 2, 3]')
LIMIT 10;
+-----+-------------------------------------------------------------------------------------+
| ... | operator info                                                                       |
+-----+-------------------------------------------------------------------------------------+
| ... | ...                                                                                 |
| ... | Column#5, offset:0, count:10                                                        |
| ... | ..., vec_cosine_distance(test.vector_table_with_index.embedding, [1,2,3])->Column#5 |
| ... | MppVersion: 1, data:ExchangeSender_16                                               |
| ... | ExchangeType: PassThrough                                                           |
| ... | ...                                                                                 |
| ... | Column#4, offset:0, count:10                                                        |
| ... | ..., vec_cosine_distance(test.vector_table_with_index.embedding, [1,2,3])->Column#4 |
| ... | annIndex:COSINE(test.vector_table_with_index.embedding..[1,2,3], limit:10), ...     |
+-----+-------------------------------------------------------------------------------------+
9 rows in set (0.01 sec)
```

**Example: The vector index is not used because of not specifying a Top K**

```sql
[tidb]> EXPLAIN SELECT * FROM vector_table_with_index
     -> ORDER BY VEC_COSINE_DISTANCE(embedding, '[1, 2, 3]');
+--------------------------------+-----+--------------------------------------------------+
| id                             | ... | operator info                                    |
+--------------------------------+-----+--------------------------------------------------+
| Projection_15                  | ... | ...                                              |
| └─Sort_4                       | ... | Column#4                                         |
|   └─Projection_16              | ... | ..., vec_cosine_distance(..., [1,2,3])->Column#4 |
|     └─TableReader_14           | ... | MppVersion: 1, data:ExchangeSender_13            |
|       └─ExchangeSender_13      | ... | ExchangeType: PassThrough                        |
|         └─TableFullScan_12     | ... | keep order:false, stats:pseudo                   |
+--------------------------------+-----+--------------------------------------------------+
6 rows in set, 1 warning (0.01 sec)
```

When the vector index cannot be used, a warning occurs in some cases to help you learn the cause:

```sql
-- Using a wrong distance function:
[tidb]> EXPLAIN SELECT * FROM vector_table_with_index
ORDER BY VEC_L2_DISTANCE(embedding, '[1, 2, 3]')
LIMIT 10;

[tidb]> SHOW WARNINGS;
ANN index not used: not ordering by COSINE distance

-- Using a wrong order:
[tidb]> EXPLAIN SELECT * FROM vector_table_with_index
ORDER BY VEC_COSINE_DISTANCE(embedding, '[1, 2, 3]') DESC
LIMIT 10;

[tidb]> SHOW WARNINGS;
ANN index not used: index can be used only when ordering by vec_cosine_distance() in ASC order
```
