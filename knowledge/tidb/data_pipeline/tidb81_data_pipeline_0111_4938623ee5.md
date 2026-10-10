# Sample code for Jina AI embedding generation and TiDB vector search

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-jinaai-embedding.md`
- Source Title: `Integrate TiDB Vector Search with Jina AI Embeddings API`
- Source Heading Path: `Integrate TiDB Vector Search with Jina AI Embeddings API > Sample code snippets | Integrate TiDB Vector Search with Jina AI Embeddings API > Sample code snippets > Get embeddings from Jina AI | Integrate TiDB Vector Search with Jina AI Embeddings API > Sample code snippets > Connect to the TiDB cluster | Integrate TiDB Vector Search with Jina AI Embeddings API > Sample code snippets > Define the vector table schema | Integrate TiDB Vector Search with Jina AI Embeddings API > Sample code snippets > Create embeddings with Jina AI and store in TiDB | Integrate TiDB Vector Search with Jina AI Embeddings API > Sample code snippets > Perform semantic search with Jina AI embeddings in TiDB | Integrate TiDB Vector Search with Jina AI Embeddings API > See also`
- Source Line Ranges: `112-240`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`, `cloud`
- Topic Tags: `python`, `embeddings`, `api-call`, `sqlalchemy`, `vector-schema`, `data-ingestion`, `semantic-search`, `cosine-distance`, `sample-code`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0111_4938623ee5`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-jinaai-embedding.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `355ea5c5ed6cb832a96706b20a1dd9e660a56d9decd87fc01c527a2a632c9d43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-jinaai-embedding#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-jinaai-embedding.md

## Retrieval Guidance

- Use When: Use this chunk when looking for Python sample code that calls the Jina AI embeddings API, defines a SQLAlchemy vector schema, stores embeddings in TiDB, and performs cosine-distance semantic search.
- Retrieval Keywords: generate_embeddings, https://api.jina.ai/v1/embeddings, jina-embeddings-v2-base-en, dimension 768, TIDB_DATABASE_URL, create_engine, tidb_vector.sqlalchemy, VectorType(dim=768), jinaai_tidb_demo_documents, content_vec, hnsw(distance=cosine), Session(engine), cosine_distance, What is TiDB?
- Follow-up Guidance: The chunk points to related documentation for Vector Data Types and Vector Search Index.
- Classification Note: The official content is a data pipeline example because it shows code for embedding generation, schema definition, data insertion, and semantic query execution.

## Official Source Content

## Sample code snippets
### Get embeddings from Jina AI

Define a `generate_embeddings` helper function to call Jina AI embeddings API:

```python
import os
import requests
import dotenv

dotenv.load_dotenv()

JINAAI_API_KEY = os.getenv('JINAAI_API_KEY')

def generate_embeddings(text: str):
    JINAAI_API_URL = 'https://api.jina.ai/v1/embeddings'
    JINAAI_HEADERS = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JINAAI_API_KEY}'
    }
    JINAAI_REQUEST_DATA = {
        'input': [text],
        'model': 'jina-embeddings-v2-base-en'  # with dimension 768.
    }
    response = requests.post(JINAAI_API_URL, headers=JINAAI_HEADERS, json=JINAAI_REQUEST_DATA)
    return response.json()['data'][0]['embedding']
```
### Connect to the TiDB cluster

Connect to the TiDB cluster through SQLAlchemy:

```python
import os
import dotenv

from tidb_vector.sqlalchemy import VectorType
from sqlalchemy.orm import Session, declarative_base

dotenv.load_dotenv()

TIDB_DATABASE_URL = os.getenv('TIDB_DATABASE_URL')
assert TIDB_DATABASE_URL is not None
engine = create_engine(url=TIDB_DATABASE_URL, pool_recycle=300)
```
### Define the vector table schema

Create a table named `jinaai_tidb_demo_documents` with a `content` column for storing texts and a vector column named `content_vec` for storing embeddings:

```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "jinaai_tidb_demo_documents"

    id = Column(Integer, primary_key=True)
    content = Column(String(255), nullable=False)
    content_vec = Column(
        # DIMENSIONS is determined by the embedding model,
        # for Jina AI's jina-embeddings-v2-base-en model it's 768.
        VectorType(dim=768),
        comment="hnsw(distance=cosine)"
```

> **Note:**
>
> - The dimension of the vector column must match the dimension of the embeddings generated by the embedding model.
> - In this example, the dimension of embeddings generated by the `jina-embeddings-v2-base-en` model is `768`.
### Create embeddings with Jina AI and store in TiDB

Use the Jina AI Embeddings API to generate embeddings for each piece of text and store the embeddings in TiDB:

```python
TEXTS = [
   'Jina AI offers best-in-class embeddings, reranker and prompt optimizer, enabling advanced multimodal AI.',
   'TiDB is an open-source MySQL-compatible database that supports Hybrid Transactional and Analytical Processing (HTAP) workloads.',
]
data = []

for text in TEXTS:
    # Generate embeddings for the texts via Jina AI API.
    embedding = generate_embeddings(text)
    data.append({
        'text': text,
        'embedding': embedding
    })

with Session(engine) as session:
   print('- Inserting Data to TiDB...')
   for item in data:
      print(f'  - Inserting: {item["text"]}')
      session.add(Document(
         content=item['text'],
         content_vec=item['embedding']
      ))
   session.commit()
```
### Perform semantic search with Jina AI embeddings in TiDB

Generate the embedding for the query text via Jina AI embeddings API, and then search for the most relevant document based on the cosine distance between **the embedding of the query text** and **each embedding in the vector table**:

```python
query = 'What is TiDB?'
# Generate the embedding for the query via Jina AI API.
query_embedding = generate_embeddings(query)

with Session(engine) as session:
    print('- The Most Relevant Document and Its Distance to the Query:')
    doc, distance = session.query(
        Document,
        Document.content_vec.cosine_distance(query_embedding).label('distance')
    ).order_by(
        'distance'
    ).limit(1).first()
    print(f'  - distance: {distance}\n'
          f'    content: {doc.content}')
```
## See also

- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)
- [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index)
