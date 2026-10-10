# Python full-text search tutorial with pytidb on TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-full-text-search-python.md`
- Source Title: `Full-Text Search with Python`
- Source Heading Path: `Full-Text Search with Python | Full-Text Search with Python > Prerequisites | Full-Text Search with Python > Get started | Full-Text Search with Python > Get started > Step 1. Install the [pytidb](https://github.com/pingcap/pytidb) Python SDK | Full-Text Search with Python > Get started > Step 2. Connect to TiDB | Full-Text Search with Python > Get started > Step 3. Create a table and a full-text index | Full-Text Search with Python > Get started > Step 4. Insert data | Full-Text Search with Python > Get started > Step 5. Perform a full-text search | Full-Text Search with Python > See also | Full-Text Search with Python > Feedback & Help`
- Source Line Ranges: `6-173`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`, `tidb`
- Topic Tags: `full-text-search`, `python-sdk`, `pytidb`, `rag`, `vector-search`, `serverless`, `connection`, `table-creation`, `index-creation`, `data-insert`, `search-query`, `bm25`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0311_0b1dfc1f0b`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-full-text-search-python.md#full-text-search-with-python`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a959e438c94eb82526dafbd32ac9248c17632a39715efd2d4febd32f0993e8c6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-full-text-search-python#full-text-search-with-python
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-full-text-search-python.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Serverless Python tutorial for full-text search with pytidb, including connection setup, table and full-text index creation, data insertion, and a BM25-ranked search example.
- Retrieval Keywords: Full-Text Search with Python, pytidb, TiDBClient.connect, TiDB Cloud Serverless, Frankfurt (eu-central-1), Singapore (ap-southeast-1), create_fts_index, has_fts_index, table.search("brown fox", search_type="fulltext"), bulk_insert, chunks table, BM25 ranking, vector search, Hybrid Search, Full-Text Search with SQL
- Follow-up Guidance: The source also points to Full-Text Search with SQL for SQL usage, Hybrid Search for combining full-text search and vector search, and the pytidb full-text search demo for a complete example.
- Classification Note: This is classified under cloud configuration because the content is a TiDB Cloud Serverless tutorial that shows prerequisites, connection parameters from the TiDB Cloud console, and Python SDK setup for full-text search.

## Official Source Content

# Full-Text Search with Python

Unlike [Vector Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview), which focuses on semantic similarity, full-text search lets you retrieve documents for exact keywords. In Retrieval-Augmented Generation (RAG) scenarios, you can use full-text search together with vector search to improve the retrieval quality.

The full-text search feature in TiDB provides the following capabilities:

- **Query text data directly**: you can search any string columns directly without the embedding process.

- **Support for multiple languages**: no need to specify the language for high-quality search. TiDB supports documents in multiple languages stored in the same table and automatically chooses the best text analyzer for each document.

- **Order by relevance**: the search result can be ordered by relevance using the widely adopted [BM25 ranking](https://en.wikipedia.org/wiki/Okapi_BM25) algorithm.

- **Fully compatible with SQL**: all SQL features, such as pre-filtering, post-filtering, grouping, and joining, can be used with full-text search.

> **Tip:**
>
> For SQL usage, see [Full-Text Search with SQL](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-full-text-search-sql).
>
> To use full-text search and vector search together in your AI apps, see [Hybrid Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-hybrid-search).
## Prerequisites

Full-text search is still in the early stages, and we are continuously rolling it out to more customers. Currently, Full-text search is only available for the following product option and regions:

- TiDB Cloud Serverless: `Frankfurt (eu-central-1)` and `Singapore (ap-southeast-1)`

To complete this tutorial, make sure you have a TiDB Cloud Serverless cluster in a supported region. If you don't have one, follow [Creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create it.
## Get started
### Step 1. Install the [pytidb](https://github.com/pingcap/pytidb) Python SDK

[pytidb](https://github.com/pingcap/pytidb) is the official Python SDK for TiDB, designed to help developers build AI applications efficiently. It includes built-in support for vector search and full-text search.

To install the SDK, run the following command:

```shell
pip install pytidb

# (Alternative) To use the built-in embedding functions and rerankers:
# pip install "pytidb[models]"

# (Optional) To convert query results into pandas DataFrames:
# pip install pandas
```
### Step 2. Connect to TiDB

```python
from pytidb import TiDBClient

db = TiDBClient.connect(
    host="HOST_HERE",
    port=4000,
    username="USERNAME_HERE",
    password="PASSWORD_HERE",
    database="DATABASE_HERE",
)
```

You can get these connection parameters from the [TiDB Cloud console](https://tidbcloud.com):

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed, with connection parameters listed.

   For example, if the connection parameters are displayed as follows:

   ```text
   HOST:     gateway01.us-east-1.prod.shared.aws.tidbcloud.com
   PORT:     4000
   USERNAME: 4EfqPF23YKBxaQb.root
   PASSWORD: abcd1234
   DATABASE: test
   CA:       /etc/ssl/cert.pem
   ```

   The corresponding Python code to connect to the TiDB Cloud Serverless cluster would be as follows:

   ```python
   db = TiDBClient.connect(
       host="gateway01.us-east-1.prod.shared.aws.tidbcloud.com",
       port=4000,
       username="4EfqPF23YKBxaQb.root",
       password="abcd1234",
       database="test",
   )
   ```

   Note that the preceding example is for demonstration purposes only. You need to fill in the parameters with your own values and keep them secure.
### Step 3. Create a table and a full-text index

As an example, create a table named `chunks` with the following columns:

- `id` (int): the ID of the chunk.
- `text` (text): the text content of the chunk.
- `user_id` (int): the ID of the user who created the chunk.

```python
from pytidb.schema import TableModel, Field

class Chunk(TableModel, table=True):
    __tablename__ = "chunks"

    id: int = Field(primary_key=True)
    text: str = Field()
    user_id: int = Field()

table = db.create_table(schema=Chunk)

if not table.has_fts_index("text"):
    table.create_fts_index("text")   # 👈 Create a fulltext index on the text column.
```
### Step 4. Insert data

```python
table.bulk_insert(
    [
        Chunk(id=2, text="the quick brown", user_id=2),
        Chunk(id=3, text="fox jumps", user_id=3),
        Chunk(id=4, text="over the lazy dog", user_id=4),
    ]
)
```
### Step 5. Perform a full-text search

After inserting data, you can perform a full-text search as follows:

```python
df = (
  table.search("brown fox", search_type="fulltext")
    .limit(2)
    .to_pandas() # optional
)

#    id             text  user_id
# 0   3        fox jumps        3
# 1   2  the quick brown        2
```

For a complete example, see [pytidb full-text search demo](https://github.com/pingcap/pytidb/blob/main/examples/fulltext_search).
## See also

- [pytidb Python SDK Documentation](https://github.com/pingcap/pytidb)

- [Hybrid Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-hybrid-search)
## Feedback & Help

Full-text search is still in the early stages with limited accessibility. If you would like to try full-text search in a region that is not yet available, or if you have feedback or need help, feel free to reach out to us:

- [Join our Discord](https://discord.gg/zcqexutz2R)

- [Join our Discord](https://discord.gg/zcqexutz2R)
- [Visit our Support Portal](https://tidb.support.pingcap.com/)
