# Index types and vector index concepts

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/database-schema-concepts.md`
- Source Title: `Database Schema`
- Source Heading Path: `Database Schema > Indexes | Database Schema > Indexes > Unique indexes | Database Schema > Indexes > Primary key index | Database Schema > Indexes > Composite index | Database Schema > Indexes > Invisible indexes | Database Schema > Indexes > Clustered indexes | Database Schema > Indexes > Secondary index | Database Schema > Indexes > Vector index`
- Source Line Ranges: `76-131`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`, `tiflash`
- Topic Tags: `indexes`, `unique-indexes`, `primary-key`, `composite-indexes`, `invisible-indexes`, `clustered-indexes`, `secondary-indexes`, `vector-indexes`, `ann`, `knn`, `hnsw`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0798_d211808e2b`
- Source ID: `tidb-docs-8.1:tidb-cloud/database-schema-concepts.md#indexes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9dfc5674eb24ad5e27ea34c465e819b446fc62d7bc19a89a48f9cb1098b43ab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/database-schema-concepts#indexes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/database-schema-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB index types or retrieval terms such as unique indexes, primary key indexes, composite indexes, invisible indexes, clustered indexes, secondary indexes, or vector indexes.
- Retrieval Keywords: Indexes, unique index, primary key index, composite index, invisible indexes, tidb_opt_use_invisible_indexes, clustered indexes, secondary index, vector index, approximate nearest neighbor, ANN, K-nearest neighbors, KNN, HNSW, TiFlash replicas
- Follow-up Guidance: It includes the note that invisible indexes can be selected by the optimizer through the `tidb_opt_use_invisible_indexes` system variable and that vector indexes rely on TiFlash replicas.
- Classification Note: This is reference content because it explains the definitions and characteristics of index types, including vector indexes and optimizer visibility, rather than a single task procedure.

## Official Source Content

## Indexes

An index is a copy of selected columns in a table. You can create an index using one or more columns of a [table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview#table). With indexes, TiDB can quickly locate data without having to search every row in a table every time, which greatly improves your query performance.

There are two common types of indexes:

- Primary Key: indexes on the primary key column.

- Secondary Index: indexes on non-primary key column
### Unique indexes

A unique index in TiDB enforces uniqueness on one or more columns, ensuring that no two rows in a table can have the same values in the indexed column(s). This constraint provides a way to maintain data integrity by preventing duplicate values, making unique indexes ideal for fields that should naturally be unique, like email addresses, usernames, or product codes.
### Primary key index

A primary key index is a unique index on one or more columns in a table, which serves as the primary identifier for each row. In TiDB, every table must have a primary key, and it can be defined explicitly by the user or implicitly by TiDB if no primary key is specified.
### Composite index

A composite index is an index built on two or more columns of a table, which is particularly useful for queries that filter or sort data by multiple fields. For example, creating a composite index on `last_name` and `first_name` in a person table allows TiDB to quickly locate records based on both names.
### Invisible indexes

Invisible indexes are indexes that exist in the database but are hidden from the query optimizer, meaning they are ignored in query plans. In TiDB, invisible indexes are useful for testing and debugging, allowing you to assess the impact of an index on performance without fully dropping it.

Starting from TiDB v8.0.0, you can make the optimizer select invisible indexes by modifying the [`tidb_opt_use_invisible_indexes`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_use_invisible_indexes-new-in-v800) system variable.
### Clustered indexes

In clustered indexes, the term clustered refers to the organization of how data is stored and not a group of database servers working together. Some database management systems refer to clustered indexes as index-organized tables (IOT).

This feature controls how data is stored in tables containing primary keys. It provides TiDB with the ability to organize tables in a way that can improve the performance of certain queries.

For more information, see [Clustered Indexes](https://docs.pingcap.com/tidb/stable/clustered-indexes).
### Secondary index

A secondary index is a logical object in a TiDB cluster. You can simply regard it as a sorting type of data that TiDB uses to improve the query performance. In TiDB, creating a secondary index is an online operation, which does not block any data read and write operations on a table. For each index, TiDB creates references for each row in a table and sorts the references by selected columns instead of by data directly.

For more information about secondary indexes, see [Secondary Indexes](https://docs.pingcap.com/tidb/stable/tidb-best-practices#secondary-index).

In TiDB, you can either [add a secondary index to an existing table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes#add-a-secondary-index-to-an-existing-table) or [create a secondary index when creating a new table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes#create-a-secondary-index-when-creating-a-new-table).
### Vector index

For the following TiDB deployment options, TiDB supports vector data types and vector search indexes.

- TiDB Cloud Serverless

- TiDB Self-Managed v8.4.0 or later versions

In TiDB, a vector index is a specialized index designed for efficient approximate nearest neighbor (ANN) searches over columns containing vector data. Vector indexes, particularly the HNSW (Hierarchical Navigable Small World) algorithm, allow K-nearest neighbors (KNN) searches to identify the closest data points in a vector space quickly. This significantly speeds up query performance, enabling results in milliseconds compared to brute-force methods.

Vector indexes rely on TiFlash replicas for data storage and search functionality. Before creating and using vector indexes, make sure that TiFlash nodes are available in your cluster.
