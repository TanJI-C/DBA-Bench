# Metadata filter support, syntax, and search example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-langchain.md`
- Source Title: `Integrate Vector Search with LangChain`
- Source Heading Path: `Integrate Vector Search with LangChain > Search with metadata filters | Integrate Vector Search with LangChain > Search with metadata filters > Supported metadata types | Integrate Vector Search with LangChain > Search with metadata filters > Metadata filter syntax | Integrate Vector Search with LangChain > Search with metadata filters > Example`
- Source Line Ranges: `288-413`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`, `tidb`
- Topic Tags: `metadata-filters`, `json`, `filter-syntax`, `similarity-search`, `document-metadata`, `vector-store`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0926_c458bf2ffc`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-langchain.md#search-with-metadata-filters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2109d3ed4ce3438bf978c8619f08f7939e6b09258ecd1cb2e0581b64067c74a4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-langchain#search-with-metadata-filters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-langchain.md

## Retrieval Guidance

- Use When: Use this chunk when looking for supported metadata types, metadata filter operators, or an example of similarity search with a metadata filter in `TiDBVectorStore`.
- Retrieval Keywords: Search with metadata filters, Supported metadata types, JSON object, String, Number, Boolean, metadata filter syntax, $or, $and, $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, TiDB treats each key-value pair as a separate filter clause, AND logical operator, vector_store.add_texts, metadatas, title, similarity_search_with_score, filter={"title": "TiDB Vector functionality"}, Introduction to TiDB Vector
- Follow-up Guidance: It includes an example that adds documents with `title` metadata and then calls `vector_store.similarity_search_with_score("Introduction to TiDB Vector", filter={"title": "TiDB Vector functionality"}, k=4)`.
- Classification Note: This is classified as reference because the content defines supported metadata types, lists filter operators, explains filter semantics, and provides a syntax example.

## Official Source Content

## Search with metadata filters

To refine your searches, you can use metadata filters to retrieve specific nearest-neighbor results that match the applied filters.
### Supported metadata types

Each document in the TiDB vector store can be paired with metadata, structured as key-value pairs within a JSON object. Keys are always strings, while values can be any of the following types:

- String
- Number: integer or floating point
- Boolean: `true` or `false`

For example, the following is a valid metadata payload:

```json
{
  "page": 12,
  "book_title": "Siddhartha"
}
```
### Metadata filter syntax

Available filters include the following:

- `$or`: Selects vectors that match any one of the specified conditions.
- `$and`: Selects vectors that match all the specified conditions.
- `$eq`: Equal to the specified value.
- `$ne`: Not equal to the specified value.
- `$gt`: Greater than the specified value.
- `$gte`: Greater than or equal to the specified value.
- `$lt`: Less than the specified value.
- `$lte`: Less than or equal to the specified value.
- `$in`: In the specified array of values.
- `$nin`: Not in the specified array of values.

If the metadata of a document is as follows:

```json
{
  "page": 12,
  "book_title": "Siddhartha"
}
```

The following metadata filters can match this document:

```json
{ "page": 12 }
```

```json
{ "page": { "$eq": 12 } }
```

```json
{
  "page": {
    "$in": [11, 12, 13]
  }
}
```

```json
{ "page": { "$nin": [13] } }
```

```json
{ "page": { "$lt": 11 } }
```

```json
{
  "$or": [{ "page": 11 }, { "page": 12 }],
  "$and": [{ "page": 12 }, { "page": 13 }]
}
```

In a metadata filter, TiDB treats each key-value pair as a separate filter clause and combines these clauses using the `AND` logical operator.
### Example

The following example adds two documents to `TiDBVectorStore` and adds a `title` field to each document as the metadata:

```python
vector_store.add_texts(
    texts=[
        "TiDB Vector offers advanced, high-speed vector processing capabilities, enhancing AI workflows with efficient data handling and analytics support.",
        "TiDB Vector, starting as low as $10 per month for basic usage",
    ],
    metadatas=[
        {"title": "TiDB Vector functionality"},
        {"title": "TiDB Vector Pricing"},
    ],
)
```

The expected output is as follows:

```plain
[UUID('c782cb02-8eec-45be-a31f-fdb78914f0a7'),
 UUID('08dcd2ba-9f16-4f29-a9b7-18141f8edae3')]
```

Perform a similarity search with metadata filters:

```python
docs_with_score = vector_store.similarity_search_with_score(
    "Introduction to TiDB Vector", filter={"title": "TiDB Vector functionality"}, k=4
)
for doc, score in docs_with_score:
    print("-" * 80)
    print("Score: ", score)
    print(doc.page_content)
    print("-" * 80)
```

The expected output is as follows:

```plain
--------------------------------------------------------------------------------
Score:  0.12761409169211535
TiDB Vector offers advanced, high-speed vector processing capabilities, enhancing AI workflows with efficient data handling and analytics support.
--------------------------------------------------------------------------------
```
