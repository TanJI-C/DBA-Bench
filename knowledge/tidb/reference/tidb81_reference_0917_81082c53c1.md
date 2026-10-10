# Vector type overview, syntax, and dimension handling

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-data-types.md`
- Source Title: `Vector Data Types`
- Source Heading Path: `Vector Data Types | Vector Data Types > Syntax | Vector Data Types > Store vectors with different dimensions`
- Source Line Ranges: `5-79`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `vector`, `data-types`, `syntax`, `dimensions`, `insert`, `validation`, `indexing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0917_81082c53c1`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-data-types.md#vector-data-types`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c435b4e6dc0fc8e24c3c79094e13e8446a2aeaccd5cdec182b17fdc71bcaef8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types#vector-data-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-data-types.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB vector columns are declared, how vector literals are written and validated on INSERT, and how fixed versus variable dimensions affect indexability.
- Retrieval Keywords: VECTOR, VECTOR(D), VECTOR(3), vector data types, '[<float>, <float>, ...]', CREATE TABLE vector_table, INSERT INTO vector_table, Invalid vector text: [5, ], vector has 2 dimensions, does not fit VECTOR(3), Store vectors with different dimensions, embedding VECTOR, embedding VECTOR(3), vector search index, dimension enforcement, cannot build a vector search index
- Follow-up Guidance: It also points to Vector Functions and Operators for available functions and operators and to Vector Search Index for building and using a vector search index.
- Classification Note: This is classified as reference content because it defines the VECTOR and VECTOR(D) types, their syntax, validation behavior, dimension rules, and the indexing limitation for mixed-dimension columns.

## Official Source Content

# Vector Data Types

A vector is a sequence of floating-point numbers, such as `[0.3, 0.5, -0.1, ...]`. TiDB offers Vector data types, specifically optimized for efficiently storing and querying vector embeddings widely used in AI applications.

The following Vector data types are currently available:

- `VECTOR`: A sequence of single-precision floating-point numbers with any dimension.
- `VECTOR(D)`: A sequence of single-precision floating-point numbers with a fixed dimension `D`.

Using vector data types provides the following advantages over using the [`JSON`](https://docs.pingcap.com/tidb/stable/data-type-json) type:

- Vector index support: You can build a [vector search index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index) to speed up vector searching.
- Dimension enforcement: You can specify a dimension to forbid inserting vectors with different dimensions.
- Optimized storage format: Vector data types are optimized for handling vector data, offering better space efficiency and performance compared to `JSON` types.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Syntax

You can use a string in the following syntax to represent a Vector value:

```sql
'[<float>, <float>, ...]'
```

Example:

```sql
CREATE TABLE vector_table (
    id INT PRIMARY KEY,
    embedding VECTOR(3)
);

INSERT INTO vector_table VALUES (1, '[0.3, 0.5, -0.1]');

INSERT INTO vector_table VALUES (2, NULL);
```

Inserting vector values with invalid syntax will result in an error:

```sql
[tidb]> INSERT INTO vector_table VALUES (3, '[5, ]');
ERROR 1105 (HY000): Invalid vector text: [5, ]
```

In the following example, because dimension `3` is enforced for the `embedding` column when the table is created, inserting a vector with a different dimension will result in an error:

```sql
[tidb]> INSERT INTO vector_table VALUES (4, '[0.3, 0.5]');
ERROR 1105 (HY000): vector has 2 dimensions, does not fit VECTOR(3)
```

For available functions and operators over the vector data types, see [Vector Functions and Operators](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-functions-and-operators).

For more information about building and using a vector search index, see [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index).
## Store vectors with different dimensions

You can store vectors with different dimensions in the same column by omitting the dimension parameter in the `VECTOR` type:

```sql
CREATE TABLE vector_table (
    id INT PRIMARY KEY,
    embedding VECTOR
);

INSERT INTO vector_table VALUES (1, '[0.3, 0.5, -0.1]'); -- 3 dimensions vector, OK
INSERT INTO vector_table VALUES (2, '[0.3, 0.5]');       -- 2 dimensions vector, OK
```

However, note that you cannot build a [vector search index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index) for this column, as vector distances can be only calculated between vectors with the same dimensions.
