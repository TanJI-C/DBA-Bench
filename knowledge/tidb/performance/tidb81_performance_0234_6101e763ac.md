# Analyze vector search performance and related references

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-index.md`
- Source Title: `Vector Search Index`
- Source Heading Path: `Vector Search Index > Analyze vector search performance | Vector Search Index > Limitations | Vector Search Index > See also`
- Source Line Ranges: `195-245`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`, `tiflash`
- Topic Tags: `explain-analyze`, `execution-info`, `vector-index`, `performance-analysis`, `s3`, `cache`, `disk`, `stale-rows`, `limitations`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0234_6101e763ac`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-index.md#analyze-vector-search-performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `690cc231a210ab3dc36a64ce915bf67df235d7739bebd1e9e0d79290dcf83e3e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index#analyze-vector-search-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-index.md

## Retrieval Guidance

- Use When: Use this content when analyzing vector search performance details from EXPLAIN ANALYZE execution info and understanding vector_idx load and search fields.
- Retrieval Keywords: EXPLAIN ANALYZE, execution info, vector_idx, vector_index.load.total, vector_index.load.from_s3, vector_index.load.from_disk, vector_index.load.from_cache, vector_index.search.total, vector_index.search.discarded_nodes, tiflash_task, from_s3, from_disk, from_cache, stale rows, UPDATE, DELETE, Vector index limitations, Improve Vector Search Performance, Vector Data Types, EXPLAIN Walkthrough
- Follow-up Guidance: The source also points to Vector index limitations, Improve Vector Search Performance, Vector Data Types, EXPLAIN, EXPLAIN ANALYZE, and EXPLAIN Walkthrough for related reference information.
- Classification Note: This is classified as performance because the official content focuses on execution timing and vector index load and search metrics for performance analysis.

## Official Source Content

## Analyze vector search performance

To learn detailed information about how a vector index is used, you can execute the [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) statement and check the `execution info` column in the output:

```sql
[tidb]> EXPLAIN ANALYZE SELECT * FROM vector_table_with_index
ORDER BY VEC_COSINE_DISTANCE(embedding, '[1, 2, 3]')
LIMIT 10;
+-----+--------------------------------------------------------+-----+
|     | execution info                                         |     |
+-----+--------------------------------------------------------+-----+
| ... | time:339.1ms, loops:2, RU:0.000000, Concurrency:OFF    | ... |
| ... | time:339ms, loops:2                                    | ... |
| ... | time:339ms, loops:3, Concurrency:OFF                   | ... |
| ... | time:339ms, loops:3, cop_task: {...}                   | ... |
| ... | tiflash_task:{time:327.5ms, loops:1, threads:4}        | ... |
| ... | tiflash_task:{time:327.5ms, loops:1, threads:4}        | ... |
| ... | tiflash_task:{time:327.5ms, loops:1, threads:4}        | ... |
| ... | tiflash_task:{time:327.5ms, loops:1, threads:4}        | ... |
| ... | tiflash_task:{...}, vector_idx:{                       | ... |
|     |   load:{total:68ms,from_s3:1,from_disk:0,from_cache:0},|     |
|     |   search:{total:0ms,visited_nodes:2,discarded_nodes:0},|     |
|     |   read:{vec_total:0ms,others_total:0ms}},...}          |     |
+-----+--------------------------------------------------------+-----+
```

> **Note:**
>
> The execution information is internal. Fields and formats are subject to change without any notification. Do not rely on them.

Explanation of some important fields:

- `vector_index.load.total`: The total duration of loading index. This field might be larger than the actual query time because multiple vector indexes might be loaded in parallel.
- `vector_index.load.from_s3`: Number of indexes loaded from S3.
- `vector_index.load.from_disk`: Number of indexes loaded from disk. The index was already downloaded from S3 previously.
- `vector_index.load.from_cache`: Number of indexes loaded from cache. The index was already downloaded from S3 previously.
- `vector_index.search.total`: The total duration of searching in the index. Large latency usually means the index is cold (never accessed before, or accessed long ago) so that there are heavy I/O operations when searching through the index. This field might be larger than the actual query time because multiple vector indexes might be searched in parallel.
- `vector_index.search.discarded_nodes`: Number of vector rows visited but discarded during the search. These discarded vectors are not considered in the search result. Large values usually indicate that there are many stale rows caused by `UPDATE` or `DELETE` statements.

See [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain), [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze), and [EXPLAIN Walkthrough](https://docs.pingcap.com/tidb/stable/explain-walkthrough) for interpreting the output.
## Limitations

See [Vector index limitations](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-limitations#vector-index-limitations).
## See also

- [Improve Vector Search Performance](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-improve-performance)
- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)

[^1]: The explanation of KNN search is adapted from the [Approximate Nearest Neighbor Search Indexes](https://github.com/ClickHouse/ClickHouse/pull/50661/files#diff-7ebd9e71df96e74230c9a7e604fa7cb443be69ba5e23bf733fcecd4cc51b7576) document authored by [rschu1ze](https://github.com/rschu1ze) in ClickHouse documentation, licensed under the Apache License 2.0.
