# View vector index build progress

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-index.md`
- Source Title: `Vector Search Index`
- Source Heading Path: `Vector Search Index > View index build progress`
- Source Line Ranges: `99-130`
- Source Scope: `cloud`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`, `cloud`
- Topic Tags: `index-build-progress`, `information-schema`, `tiflash-indexes`, `delta-layer`, `stable-layer`, `compaction`, `ddl-jobs`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0107_60725e8b51`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-index.md#view-index-build-progress`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ce4a27a5d086841071ebbe5139d61b4f3de1c96232374c4e86e15952d336b29b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index#view-index-build-progress
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-index.md

## Retrieval Guidance

- Use When: Use this chunk when locating how to inspect TiFlash vector index build progress and understand indexed versus not indexed rows for HNSW indexes after data insertion.
- Retrieval Keywords: View index build progress, INFORMATION_SCHEMA.TIFLASH_INDEXES, TIFLASH_INDEXES, ROWS_STABLE_INDEXED, ROWS_STABLE_NOT_INDEXED, ROWS_DELTA_INDEXED, ROWS_DELTA_NOT_INDEXED, ERROR_MESSAGE, TIFLASH_INSTANCE, INDEX_KIND HNSW, ALTER TABLE <TABLE_NAME> COMPACT, Delta layer, Stable layer, Compaction, ADMIN SHOW DDL JOBS, row count
- Follow-up Guidance: The source also notes that vector searches still return complete results while indexing is incomplete, though performance is suboptimal until indexes are fully built.
- Classification Note: This is classified as observability because the content focuses on monitoring vector index build status through INFORMATION_SCHEMA.TIFLASH_INDEXES and related progress indicators such as stable and delta row counts.

## Official Source Content

## View index build progress

After you insert a large volume of data, some of it might not be instantly persisted to TiFlash. For vector data that has already been persisted, the vector search index is built synchronously. For data that has not yet been persisted, the index will be built once the data is persisted. This process does not affect the accuracy and consistency of the data. You can still perform vector searches at any time and get complete results. However, performance will be suboptimal until vector indexes are fully built.

To view the index build progress, you can query the `INFORMATION_SCHEMA.TIFLASH_INDEXES` table as follows:

```sql
SELECT * FROM INFORMATION_SCHEMA.TIFLASH_INDEXES;
+---------------+------------+----------+-------------+---------------+-----------+----------+------------+---------------------+-------------------------+--------------------+------------------------+---------------+------------------+
| TIDB_DATABASE | TIDB_TABLE | TABLE_ID | COLUMN_NAME | INDEX_NAME    | COLUMN_ID | INDEX_ID | INDEX_KIND | ROWS_STABLE_INDEXED | ROWS_STABLE_NOT_INDEXED | ROWS_DELTA_INDEXED | ROWS_DELTA_NOT_INDEXED | ERROR_MESSAGE | TIFLASH_INSTANCE |
+---------------+------------+----------+-------------+---------------+-----------+----------+------------+---------------------+-------------------------+--------------------+------------------------+---------------+------------------+
| test          | tcff1d827  |      219 | col1fff     | 0a452311      |         7 |        1 | HNSW       |               29646 |                       0 |                  0 |                      0 |               | 127.0.0.1:3930   |
| test          | foo        |      717 | embedding   | idx_embedding |         2 |        1 | HNSW       |                   0 |                       0 |                  0 |                      3 |               | 127.0.0.1:3930   |
+---------------+------------+----------+-------------+---------------+-----------+----------+------------+---------------------+-------------------------+--------------------+------------------------+---------------+------------------+
```

- You can check the `ROWS_STABLE_INDEXED` and `ROWS_STABLE_NOT_INDEXED` columns for the index build progress. When `ROWS_STABLE_NOT_INDEXED` becomes 0, the index build is complete.

  As a reference, indexing a 500 MiB vector dataset with 768 dimensions might take up to 20 minutes. The indexer can run in parallel for multiple tables. Currently, adjusting the indexer priority or speed is not supported.

- You can check the `ROWS_DELTA_NOT_INDEXED` column for the number of rows in the Delta layer. Data in the storage layer of TiFlash is stored in two layers: Delta layer and Stable layer. The Delta layer stores recently inserted or updated rows and is periodically merged into the Stable layer according to the write workload. This merge process is called Compaction.

  The Delta layer is always not indexed. To achieve optimal performance, you can force the merge of the Delta layer into the Stable layer so that all data can be indexed:

  ```sql
  ALTER TABLE <TABLE_NAME> COMPACT;
  ```

  For more information, see [`ALTER TABLE ... COMPACT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact).

In addition, you can monitor the execution progress of the DDL job by executing `ADMIN SHOW DDL JOBS;` and checking the `row count`. However, this method is not fully accurate, because the `row count` value is obtained from the `rows_stable_indexed` field in `TIFLASH_INDEXES`. You can use this approach as a reference for tracking the progress of indexing.
