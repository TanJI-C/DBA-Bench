# Travel agent semantic search and route retrieval

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-langchain.md`
- Source Title: `Integrate Vector Search with LangChain`
- Source Heading Path: `Integrate Vector Search with LangChain > Advanced usage example: travel agent > Perform a semantic search | Integrate Vector Search with LangChain > Advanced usage example: travel agent > Retrieve detailed airport information | Integrate Vector Search with LangChain > Advanced usage example: travel agent > Streamline the process`
- Source Line Ranges: `484-568`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`, `tidb`
- Topic Tags: `langchain`, `vector-search`, `semantic-search`, `retriever`, `sql-query`, `metadata`, `embeddings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0115_8e4ce367d4`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-langchain.md#perform-a-semantic-search`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f6b59d6ec4f47d8e0a8f4988358ec838eb1e635e39a544a4d25937d43ee1ec60`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-langchain#perform-a-semantic-search
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-langchain.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how a LangChain retriever performs semantic airport review search and then retrieves route details or combines both steps in one TiDB SQL query.
- Retrieval Keywords: vector_store.as_retriever, search_type="similarity_score_threshold", score_threshold, semantic_query, airport_code, review.metadata, SELECT * FROM airplan_routes WHERE airport_code IN :codes, vector_store.tidb_vector_client.execute, VEC_Cosine_Distance, JSON_UNQUOTE(JSON_EXTRACT(se.meta, '$.airport_code')), embed_query, airport_review, airplan_routes
- Follow-up Guidance: The source also shows an alternative single SQL query that joins airplan_routes with the embedding table using VEC_Cosine_Distance and returns ar.* together with se.document as airport_review.
- Classification Note: This is classified as data_pipeline because the official content demonstrates a retrieval flow from semantic search results and metadata extraction to SQL-based route lookup and a streamlined vector-plus-relational query.

## Official Source Content

### Perform a semantic search

The following code searches for airports with clean facilities and vegetarian options:

```python
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.85},
)
semantic_query = "Could you recommend a US airport with clean lounges and good vegetarian dining options?"
reviews = retriever.invoke(semantic_query)
for r in reviews:
    print("-" * 80)
    print(r.page_content)
    print(r.metadata)
    print("-" * 80)
```

The expected output is as follows:

```plain
--------------------------------------------------------------------------------
Clean lounges and excellent vegetarian dining options. Highly recommended.
{'airport_code': 'JFK'}
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Comfortable seating in lounge areas and diverse food selections, including vegetarian.
{'airport_code': 'LAX'}
--------------------------------------------------------------------------------
```
### Retrieve detailed airport information

Extract airport codes from the search results and query the database for detailed route information:

```python
# Extracting airport codes from the metadata
airport_codes = [review.metadata["airport_code"] for review in reviews]

# Executing a query to get the airport details
search_query = "SELECT * FROM airplan_routes WHERE airport_code IN :codes"
params = {"codes": tuple(airport_codes)}

airport_details = vector_store.tidb_vector_client.execute(search_query, params)
airport_details.get("result")
```

The expected output is as follows:

```plain
[(1, 'JFK', 'DL', 'LAX', 'Non-stop from JFK to LAX.', datetime.timedelta(seconds=21600), 5, 'Boeing 777', Decimal('299.99'), 'None'),
 (2, 'LAX', 'AA', 'ORD', 'Direct LAX to ORD route.', datetime.timedelta(seconds=14400), 3, 'Airbus A320', Decimal('149.99'), 'None')]
```
### Streamline the process

Alternatively, you can streamline the entire process using a single SQL query:

```python
search_query = f"""
    SELECT
        VEC_Cosine_Distance(se.embedding, :query_vector) as distance,
        ar.*,
        se.document as airport_review
    FROM
        airplan_routes ar
    JOIN
        {TABLE_NAME} se ON ar.airport_code = JSON_UNQUOTE(JSON_EXTRACT(se.meta, '$.airport_code'))
    ORDER BY distance ASC
    LIMIT 5;
"""
query_vector = embeddings.embed_query(semantic_query)
params = {"query_vector": str(query_vector)}
airport_details = vector_store.tidb_vector_client.execute(search_query, params)
airport_details.get("result")
```

The expected output is as follows:

```plain
[(0.1219207353407008, 1, 'JFK', 'DL', 'LAX', 'Non-stop from JFK to LAX.', datetime.timedelta(seconds=21600), 5, 'Boeing 777', Decimal('299.99'), 'None', 'Clean lounges and excellent vegetarian dining options. Highly recommended.'),
 (0.14613754359804654, 2, 'LAX', 'AA', 'ORD', 'Direct LAX to ORD route.', datetime.timedelta(seconds=14400), 3, 'Airbus A320', Decimal('149.99'), 'None', 'Comfortable seating in lounge areas and diverse food selections, including vegetarian.'),
 (0.19840519342700513, 3, 'EFGH', 'UA', 'SEA', 'Daily flights from SFO to SEA.', datetime.timedelta(seconds=9000), 7, 'Boeing 737', Decimal('129.99'), 'None', 'Small airport with basic facilities.')]
```
