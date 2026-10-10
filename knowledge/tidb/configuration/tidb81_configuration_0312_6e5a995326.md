# HNSW vector index creation and query usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-index.md`
- Source Title: `Vector Search Index`
- Source Heading Path: `Vector Search Index | Vector Search Index > Create the HNSW vector index | Vector Search Index > Use the vector index | Vector Search Index > Use the vector index with filters`
- Source Line Ranges: `5-98`
- Source Scope: `cloud`
- Primary Component: `tidb`
- Related Components: `tiflash`, `sql`, `cloud`
- Topic Tags: `vector-search`, `hnsw`, `ann`, `knn`, `index-creation`, `distance-function`, `order-by-limit`, `filters`, `tiflash-replica`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0312_6e5a995326`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-index.md#vector-search-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9f71e39aa5b7a205eba6d182d872a971b678d80746c090736bacd7227bc2028d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index#vector-search-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-index.md

## Retrieval Guidance

- Use When: Use this chunk when locating how to create and query an HNSW vector search index in TiDB Cloud, including distance-function syntax, TiFlash replica requirements, and ORDER BY ... LIMIT behavior with filters.
- Retrieval Keywords: Vector Search Index, HNSW, CREATE VECTOR INDEX, ALTER TABLE ... ADD VECTOR INDEX, USING HNSW, VECTOR INDEX idx_embedding, VEC_COSINE_DISTANCE, VEC_L2_DISTANCE, VECTOR(5), fixed-dimensional vector columns, ORDER BY VEC_COSINE_DISTANCE, LIMIT 10, K-nearest neighbor search, WHERE clause cannot utilize the vector index, TiFlash replica, ALTER TABLE 'table_name' SET TIFLASH REPLICA 1
- Follow-up Guidance: The source also explains that pre-filters in a WHERE clause prevent vector index usage, while filtering after a KNN subquery can be used but might return fewer results than the LIMIT.
- Classification Note: This is classified as configuration because the content defines how to create HNSW vector indexes, choose the distance function, satisfy TiFlash replica prerequisites, and structure queries so the vector index can be used.

## Official Source Content

# Vector Search Index

As described in the [Vector Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview) document, vector search identifies the Top K-Nearest Neighbors (KNN) to a given vector by calculating the distance between the given vector and all vectors stored in the database. While this approach provides accurate results, it can be slow when the table contains a large number of vectors because it involves a full table scan. [^1]

To improve search efficiency, you can create vector search indexes in TiDB for approximate KNN (ANN) search. When using vector indexes for vector search, TiDB can greatly improve query performance with only a slight reduction in accuracy, generally maintaining a search recall rate above 90%.

Currently, TiDB supports the [HNSW (Hierarchical Navigable Small World)](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world) vector search index algorithm.
## Create the HNSW vector index

[HNSW](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world) is one of the most popular vector indexing algorithms. The HNSW index provides good performance with relatively high accuracy, up to 98% in specific cases.

In TiDB, you can create an HNSW index for a column with a [vector data type](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types) in either of the following ways:

- When creating a table, use the following syntax to specify the vector column for the HNSW index:

  ```sql
  CREATE TABLE foo (
      id       INT PRIMARY KEY,
      embedding     VECTOR(5),
      VECTOR INDEX idx_embedding ((VEC_COSINE_DISTANCE(embedding)))
  );
  ```

- For an existing table that already contains a vector column, use the following syntax to create an HNSW index for the vector column:

  ```sql
  CREATE VECTOR INDEX idx_embedding ON foo ((VEC_COSINE_DISTANCE(embedding)));
  ALTER TABLE foo ADD VECTOR INDEX idx_embedding ((VEC_COSINE_DISTANCE(embedding)));

  -- You can also explicitly specify "USING HNSW" to build the vector search index.
  CREATE VECTOR INDEX idx_embedding ON foo ((VEC_COSINE_DISTANCE(embedding))) USING HNSW;
  ALTER TABLE foo ADD VECTOR INDEX idx_embedding ((VEC_COSINE_DISTANCE(embedding))) USING HNSW;
  ```

> **Note:**
>
> The vector search index feature relies on TiFlash replicas for tables.
>
> - If a vector search index is defined when a table is created, TiDB automatically creates a TiFlash replica for the table.
> - If no vector search index is defined when a table is created, and the table currently does not have a TiFlash replica, you need to manually create a TiFlash replica before adding a vector search index to the table. For example: `ALTER TABLE 'table_name' SET TIFLASH REPLICA 1;`.

When creating an HNSW vector index, you need to specify the distance function for the vector:

- Cosine Distance: `((VEC_COSINE_DISTANCE(embedding)))`
- L2 Distance: `((VEC_L2_DISTANCE(embedding)))`

The vector index can only be created for fixed-dimensional vector columns, such as a column defined as `VECTOR(3)`. It cannot be created for non-fixed-dimensional vector columns (such as a column defined as `VECTOR`) because vector distances can only be calculated between vectors with the same dimension.

For other limitations, see [Vector index limitations](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-limitations#vector-index-limitations).
## Use the vector index

The vector search index can be used in K-nearest neighbor search queries by using the `ORDER BY ... LIMIT` clause as follows:

```sql
SELECT *
FROM foo
ORDER BY VEC_COSINE_DISTANCE(embedding, '[1, 2, 3, 4, 5]')
LIMIT 10
```

To use an index in a vector search, make sure that the `ORDER BY ... LIMIT` clause uses the same distance function as the one specified when creating the vector index.
## Use the vector index with filters

Queries that contain a pre-filter (using the `WHERE` clause) cannot utilize the vector index because they are not querying for K-Nearest neighbors according to the SQL semantics. For example:

```sql
-- For the following query, the `WHERE` filter is performed before KNN, so the vector index cannot be used:

SELECT * FROM vec_table
WHERE category = "document"
ORDER BY VEC_COSINE_DISTANCE(embedding, '[1, 2, 3]')
LIMIT 5;
```

To use the vector index with filters, query for the K-Nearest neighbors first using vector search, and then filter out unwanted results:

```sql
-- For the following query, the `WHERE` filter is performed after KNN, so the vector index cannot be used:

SELECT * FROM
(
  SELECT * FROM vec_table
  ORDER BY VEC_COSINE_DISTANCE(embedding, '[1, 2, 3]')
  LIMIT 5
) t
WHERE category = "document";

-- Note that this query might return fewer than 5 results if some are filtered out.
```
