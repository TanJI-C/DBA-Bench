# SQLAlchemy vector table definition and query examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-sqlalchemy.md`
- Source Title: `Integrate TiDB Vector Search with SQLAlchemy`
- Source Heading Path: `Integrate TiDB Vector Search with SQLAlchemy > Sample code snippets | Integrate TiDB Vector Search with SQLAlchemy > Sample code snippets > Create vector tables | Integrate TiDB Vector Search with SQLAlchemy > Sample code snippets > Create vector tables > Connect to TiDB cluster | Integrate TiDB Vector Search with SQLAlchemy > Sample code snippets > Create vector tables > Define a vector column | Integrate TiDB Vector Search with SQLAlchemy > Sample code snippets > Store documents with embeddings | Integrate TiDB Vector Search with SQLAlchemy > Sample code snippets > Search the nearest neighbor documents | Integrate TiDB Vector Search with SQLAlchemy > Sample code snippets > Search documents within a certain distance | Integrate TiDB Vector Search with SQLAlchemy > See also`
- Source Line Ranges: `112-185`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`, `cloud`
- Topic Tags: `sqlalchemy`, `vector-search`, `python`, `code-snippets`, `connection`, `vector-column`, `embeddings`, `nearest-neighbor`, `cosine-distance`, `query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0928_e7f11b292f`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-sqlalchemy.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e4f72ca9f56164c16bad322263a3af99fd38ab1cc6a3d8528c5ed2adc258b4b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-sqlalchemy#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-sqlalchemy.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs SQLAlchemy code examples for connecting to TiDB, defining a vector column, storing embeddings, and querying nearest neighbors or distance-filtered results.
- Retrieval Keywords: Sample code snippets, create_engine, dotenv.load_dotenv(), TIDB_DATABASE_URL, Session(engine), declarative_base, VectorType, embedding, VectorType(3), sqlalchemy_demo_documents, Document, cosine_distance, label('distance'), order_by(distance).limit(3).all(), filter(distance < 0.2), top-3 documents, query vector [1, 2, 3], Store documents with embeddings
- Follow-up Guidance: The chunk points to related topics `Vector Data Types` and `Vector Search Index` in the See also section.
- Classification Note: This is classified as a reference chunk because it provides reusable code snippets and exact identifiers for table definition, connection setup, and vector search queries.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to develop your application.
### Create vector tables
#### Connect to TiDB cluster

```python
import os
import dotenv

from sqlalchemy import Column, Integer, create_engine, Text
from sqlalchemy.orm import declarative_base, Session
from tidb_vector.sqlalchemy import VectorType

dotenv.load_dotenv()

tidb_connection_string = os.environ['TIDB_DATABASE_URL']
engine = create_engine(tidb_connection_string)
```
#### Define a vector column

Create a table with a column named `embedding` that stores a 3-dimensional vector.

```python
Base = declarative_base()

class Document(Base):
    __tablename__ = 'sqlalchemy_demo_documents'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    embedding = Column(VectorType(3))
```
### Store documents with embeddings

```python
with Session(engine) as session:
   session.add(Document(content="dog", embedding=[1, 2, 1]))
   session.add(Document(content="fish", embedding=[1, 2, 4]))
   session.add(Document(content="tree", embedding=[1, 0, 0]))
   session.commit()
```
### Search the nearest neighbor documents

Search for the top-3 documents that are semantically closest to the query vector `[1, 2, 3]` based on the cosine distance function.

```python
with Session(engine) as session:
   distance = Document.embedding.cosine_distance([1, 2, 3]).label('distance')
   results = session.query(
      Document, distance
   ).order_by(distance).limit(3).all()
```
### Search documents within a certain distance

Search for documents whose cosine distance from the query vector `[1, 2, 3]` is less than 0.2.

```python
with Session(engine) as session:
    distance = Document.embedding.cosine_distance([1, 2, 3]).label('distance')
    results = session.query(
        Document, distance
    ).filter(distance < 0.2).order_by(distance).limit(3).all()
```
## See also

- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)
- [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index)
