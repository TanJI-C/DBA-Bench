# Vector search performance best practices

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-improve-performance.md`
- Source Title: `Improve Vector Search Performance`
- Source Heading Path: `Improve Vector Search Performance | Improve Vector Search Performance > Add vector search index for vector columns | Improve Vector Search Performance > Ensure vector indexes are fully built | Improve Vector Search Performance > Reduce vector dimensions or shorten embeddings | Improve Vector Search Performance > Exclude vector columns from the results | Improve Vector Search Performance > Warm up the index`
- Source Line Ranges: `5-36`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`
- Topic Tags: `vector-search`, `ann`, `indexing`, `index-build-progress`, `embeddings`, `dimensions`, `query-results`, `select-clause`, `warm-up`, `cold-access`, `latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0233_d85c38b278`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-improve-performance.md#improve-vector-search-performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bc1c65940dd4bc6833e5b68785d097e8b51b99ff5f8031efee9f24b070c7fd19`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-improve-performance#improve-vector-search-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-improve-performance.md

## Retrieval Guidance

- Use When: Use this chunk when answering how to improve TiDB Cloud vector search query performance, including ANN indexing, index build progress, embedding dimensions, SELECT clause choices, and cold-access latency.
- Retrieval Keywords: Improve Vector Search Performance, TiDB Vector Search, Approximate Nearest Neighbor, ANN queries, vector search index, view index build progress, Delta layer, persisted, reduce vector dimensions, shorten embeddings, OpenAI text-embedding-3-large, exclude vector columns from the results, SELECT clause, SELECT *, warm up the index, cold access, load the entire index from cloud storage or disk, higher query latency
- Follow-up Guidance: The content points to View index build progress for checking whether all vector data has been indexed after large inserts.
- Classification Note: This is classified as performance guidance because the official content lists best practices that improve vector search query speed and reduce latency in TiDB Cloud.

## Official Source Content

# Improve Vector Search Performance

TiDB Vector Search enables you to perform Approximate Nearest Neighbor (ANN) queries that search for results similar to an image, document, or other input. To improve the query performance, review the following best practices.
## Add vector search index for vector columns

The [vector search index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index) dramatically improves the performance of vector search queries, usually by 10x or more, with a trade-off of only a small decrease of recall rate.
## Ensure vector indexes are fully built

After you insert a large volume of vector data, some of it might be in the Delta layer waiting for persistence. The vector index for such data will be built after the data is persisted. Until all vector data is indexed, vector search performance is suboptimal. To check the index build progress, see [View index build progress](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index#view-index-build-progress).
## Reduce vector dimensions or shorten embeddings

The computational complexity of vector search indexing and queries increases significantly as the dimension of vectors grows, requiring more floating-point comparisons.

To optimize performance, consider reducing vector dimensions whenever feasible. This usually needs switching to another embedding model. When switching models, you need to evaluate the impact of the model change on the accuracy of vector queries.

Certain embedding models like OpenAI `text-embedding-3-large` support [shortening embeddings](https://openai.com/index/new-embedding-models-and-api-updates/), which removes some numbers from the end of vector sequences without losing the embedding's concept-representing properties. You can also use such an embedding model to reduce the vector dimensions.
## Exclude vector columns from the results

Vector embedding data is usually large and only used during the search process. By excluding vector columns from query results, you can greatly reduce the data transferred between the TiDB server and your SQL client, thereby improving query performance.

To exclude vector columns, explicitly list the columns you want to retrieve in the `SELECT` clause, instead of using `SELECT *` to retrieve all columns.
## Warm up the index

When accessing an index that has never been used or has not been accessed for a long time (cold access), TiDB needs to load the entire index from cloud storage or disk (instead of from memory). This process takes time and often results in higher query latency. Additionally, if there are no SQL queries for an extended period (for example, several hours), computing resources are reclaimed, causing subsequent access to become cold access.

To avoid such query latency, warm up your index before actual workload by running similar vector search queries that hit the vector index.
