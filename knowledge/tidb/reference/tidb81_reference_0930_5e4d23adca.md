# Vector search limitations and tool compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-limitations.md`
- Source Title: `Vector Search Limitations`
- Source Heading Path: `Vector Search Limitations | Vector Search Limitations > Vector data type limitations | Vector Search Limitations > Vector index limitations | Vector Search Limitations > Compatibility with TiDB tools | Vector Search Limitations > Feedback`
- Source Line Ranges: `5-42`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `vector-search`, `limitations`, `vector-data-type`, `vector-index`, `distance-functions`, `schema-constraints`, `tool-compatibility`, `migration`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0930_5e4d23adca`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-limitations.md#vector-search-limitations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6ab36858a1fecffbf0740dc5a2af0d388d4742f79a5df61505298d929084124b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-limitations#vector-search-limitations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-limitations.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about TiDB Vector Search limitations in TiDB Cloud, including vector data type constraints, vector index restrictions, and tool compatibility for migration.
- Retrieval Keywords: Vector Search Limitations, vector data type limitations, vector index limitations, Compatibility with TiDB tools, each vector supports up to 16383 dimensions, NaN, Infinity, -Infinity, single-precision floating-point numbers, double-precision floating-point numbers, vector columns cannot be used in primary keys, unique indexes, partition keys, drop a vector column with a vector index, drop the vector index first, modifying a vector column to other data types, vector index cannot accelerate range queries or equality queries, multiple vector indexes on the same column, different distance functions, VEC_COSINE_DISTANCE(), VEC_L2_DISTANCE(), vector index as invisible, Data Migration feature, MySQL 9.0 vector data types, TiDB Cloud console
- Follow-up Guidance: The source also points to feedback channels through Discord and the Support Portal.
- Classification Note: This is a reference chunk because it enumerates official TiDB Vector Search limitations, supported distance functions, schema constraints, and TiDB tool compatibility notes.

## Official Source Content

# Vector Search Limitations

This document describes the known limitations of TiDB Vector Search.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Vector data type limitations

- Each [vector](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types) supports up to 16383 dimensions.
- Vector data types cannot store `NaN`, `Infinity`, or `-Infinity` values.
- Vector data types cannot store double-precision floating-point numbers. If you insert or store double-precision floating-point numbers in vector columns, TiDB converts them to single-precision floating-point numbers.
- Vector columns cannot be used in primary keys, unique indexes, or partition keys. To accelerate the vector search performance, use [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index).
- A table can have multiple vector columns. However, there is [a limit on the total number of columns in a table](https://docs.pingcap.com/tidb/stable/tidb-limitations#limitations-on-a-single-table).
- Currently, TiDB does not support dropping a vector column with a vector index. To drop such a column, drop the vector index first, then drop the vector column.
- Currently, TiDB does not support modifying a vector column to other data types such as `JSON` and `VARCHAR`.
## Vector index limitations

- Vector index is used for vector search. It cannot accelerate other queries like range queries or equality queries. Thus, it is not possible to create a vector index on a non-vector column, or on multiple vector columns.
- A table can have multiple vector indexes. However, there is [a limit on the total number of indexes in a table](https://docs.pingcap.com/tidb/stable/tidb-limitations#limitations-on-a-single-table).
- Creating multiple vector indexes on the same column is allowed only if they use different distance functions.
- Currently, only `VEC_COSINE_DISTANCE()` and `VEC_L2_DISTANCE()` are supported as the distance functions for vector indexes.
- Currently, TiDB does not support dropping a vector column with a vector index. To drop such a column, drop the vector index first, then drop the vector column.
- Currently, TiDB does not support setting vector index as [invisible](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index).
## Compatibility with TiDB tools

- The Data Migration feature in the TiDB Cloud console does not support migrating or replicating MySQL 9.0 vector data types to TiDB Cloud.
## Feedback

We value your feedback and are always here to help:

- [Join our Discord](https://discord.gg/zcqexutz2R)
- [Visit our Support Portal](https://tidb.support.pingcap.com/)
