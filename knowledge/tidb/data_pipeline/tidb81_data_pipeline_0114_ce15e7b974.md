# Travel agent example and data preparation

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-langchain.md`
- Source Title: `Integrate Vector Search with LangChain`
- Source Heading Path: `Integrate Vector Search with LangChain > Advanced usage example: travel agent | Integrate Vector Search with LangChain > Advanced usage example: travel agent > Prepare data`
- Source Line Ranges: `414-483`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`, `tidb`
- Topic Tags: `travel-agent`, `sample-data`, `table-creation`, `sql-querying`, `semantic-search`, `metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0114_ce15e7b974`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-langchain.md#advanced-usage-example-travel-agent`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1efedc523d59302d18cabcd16716ff3e043780420fcc47c0d3e6b9d19a285656`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-langchain#advanced-usage-example-travel-agent
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-langchain.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the travel agent advanced usage example that combines semantic search over airport reviews with SQL route data preparation.
- Retrieval Keywords: Advanced usage example: travel agent, Prepare data, personalized travel reports, airport reviews, specific amenities, clean lounges, vegetarian options, semantic search, SQL query, airport codes, route information, vector_store.tidb_vector_client.execute, CREATE TABLE airplan_routes, INSERT INTO airplan_routes, airport_code, airline_code, destination_code, route_details, duration, frequency, airplane_type, price, layover, vector_store.add_texts, metadata airport_code, JFK, LAX, EFGH
- Follow-up Guidance: It shows creating the `airplan_routes` table, inserting sample route rows, and adding review texts with `airport_code` metadata to the vector store.
- Classification Note: This is classified as data_pipeline because the content prepares relational and vector data for a multi-step workflow that joins semantic search results with SQL route information.

## Official Source Content

## Advanced usage example: travel agent

This section demonstrates a use case of integrating vector search with Langchain for a travel agent. The goal is to create personalized travel reports for clients, helping them find airports with specific amenities, such as clean lounges and vegetarian options.

The process involves two main steps:

1. Perform a semantic search across airport reviews to identify airport codes that match the desired amenities.
2. Execute a SQL query to merge these codes with route information, highlighting airlines and destinations that align with user's preferences.
### Prepare data

First, create a table to store airport route data:

```python
# Create a table to store flight plan data.
vector_store.tidb_vector_client.execute(
    """CREATE TABLE airplan_routes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        airport_code VARCHAR(10),
        airline_code VARCHAR(10),
        destination_code VARCHAR(10),
        route_details TEXT,
        duration TIME,
        frequency INT,
        airplane_type VARCHAR(50),
        price DECIMAL(10, 2),
        layover TEXT
    );"""
)

# Insert some sample data into airplan_routes and the vector table.
vector_store.tidb_vector_client.execute(
    """INSERT INTO airplan_routes (
        airport_code,
        airline_code,
        destination_code,
        route_details,
        duration,
        frequency,
        airplane_type,
        price,
        layover
    ) VALUES
    ('JFK', 'DL', 'LAX', 'Non-stop from JFK to LAX.', '06:00:00', 5, 'Boeing 777', 299.99, 'None'),
    ('LAX', 'AA', 'ORD', 'Direct LAX to ORD route.', '04:00:00', 3, 'Airbus A320', 149.99, 'None'),
    ('EFGH', 'UA', 'SEA', 'Daily flights from SFO to SEA.', '02:30:00', 7, 'Boeing 737', 129.99, 'None');
    """
)
vector_store.add_texts(
    texts=[
        "Clean lounges and excellent vegetarian dining options. Highly recommended.",
        "Comfortable seating in lounge areas and diverse food selections, including vegetarian.",
        "Small airport with basic facilities.",
    ],
    metadatas=[
        {"airport_code": "JFK"},
        {"airport_code": "LAX"},
        {"airport_code": "EFGH"},
    ],
)
```

The expected output is as follows:

```plain
[UUID('6dab390f-acd9-4c7d-b252-616606fbc89b'),
 UUID('9e811801-0e6b-4893-8886-60f4fb67ce69'),
 UUID('f426747c-0f7b-4c62-97ed-3eeb7c8dd76e')]
```
