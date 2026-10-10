# Peewee vector table creation and query code examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-peewee.md`
- Source Title: `Integrate TiDB Vector Search with peewee`
- Source Heading Path: `Integrate TiDB Vector Search with peewee > Sample code snippets | Integrate TiDB Vector Search with peewee > Sample code snippets > Create vector tables | Integrate TiDB Vector Search with peewee > Sample code snippets > Create vector tables > Connect to TiDB cluster | Integrate TiDB Vector Search with peewee > Sample code snippets > Create vector tables > Define a vector column | Integrate TiDB Vector Search with peewee > Sample code snippets > Store documents with embeddings | Integrate TiDB Vector Search with peewee > Sample code snippets > Search the nearest neighbor documents | Integrate TiDB Vector Search with peewee > Sample code snippets > Search documents within a certain distance | Integrate TiDB Vector Search with peewee > See also`
- Source Line Ranges: `124-211`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `sql`
- Topic Tags: `vector-search`, `peewee`, `python`, `sample-code`, `database-connection`, `vector-column`, `embeddings`, `nearest-neighbor`, `cosine-distance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0927_68b4b4921c`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-peewee.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ef13fa2d34d24a519650b14f54550e6c35af6c0721d3a65cf87f54933c1bf537`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-peewee#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-peewee.md

## Retrieval Guidance

- Use When: Use this chunk when looking for peewee sample code to connect to a TiDB cluster, define a VectorField table, insert embeddings, and run cosine distance vector queries.
- Retrieval Keywords: Sample code snippets, MySQLDatabase, pymysql, mysqlclient, ssl_verify_cert, ssl_verify_identity, TIDB_CA_PATH, VectorField(3), peewee_demo_documents, Document.create, embedding=[1, 2, 1], embedding=[1, 2, 4], embedding=[1, 0, 0], cosine_distance([1, 2, 3]), alias('distance'), order_by(distance), limit(3), where(distance_expression < 0.2), nearest neighbor documents, documents within a certain distance
- Follow-up Guidance: The source also links to the related official pages for Vector Data Types and Vector Search Index.
- Classification Note: This is classified as a reference chunk because the official content consists of reusable code examples and exact identifiers for connection, schema definition, data insertion, and query patterns.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to develop your application.
### Create vector tables
#### Connect to TiDB cluster

```python
import os
import dotenv

from peewee import Model, MySQLDatabase, SQL, TextField
from tidb_vector.peewee import VectorField

dotenv.load_dotenv()

# Using `pymysql` as the driver.
connect_kwargs = {
    'ssl_verify_cert': True,
    'ssl_verify_identity': True,
}

# Using `mysqlclient` as the driver.
# connect_kwargs = {
#     'ssl_mode': 'VERIFY_IDENTITY',
#     'ssl': {
#         # Root certificate default path
#         # https://docs.pingcap.com/tidbcloud/secure-connections-to-serverless-clusters/#root-certificate-default-path
#         'ca': os.environ.get('TIDB_CA_PATH', '/path/to/ca.pem'),
#     },
# }

db = MySQLDatabase(
    database=os.environ.get('TIDB_DATABASE', 'test'),
    user=os.environ.get('TIDB_USERNAME', 'root'),
    password=os.environ.get('TIDB_PASSWORD', ''),
    host=os.environ.get('TIDB_HOST', 'localhost'),
    port=int(os.environ.get('TIDB_PORT', '4000')),
    **connect_kwargs,
)
```
#### Define a vector column

Create a table with a column named `peewee_demo_documents` that stores a 3-dimensional vector.

```python
class Document(Model):
    class Meta:
        database = db
        table_name = 'peewee_demo_documents'

    content = TextField()
    embedding = VectorField(3)
```
### Store documents with embeddings

```python
Document.create(content='dog', embedding=[1, 2, 1])
Document.create(content='fish', embedding=[1, 2, 4])
Document.create(content='tree', embedding=[1, 0, 0])
```
### Search the nearest neighbor documents

Search for the top-3 documents that are semantically closest to the query vector `[1, 2, 3]` based on the cosine distance function.

```python
distance = Document.embedding.cosine_distance([1, 2, 3]).alias('distance')
results = Document.select(Document, distance).order_by(distance).limit(3)
```
### Search documents within a certain distance

Search for the documents whose cosine distance from the query vector `[1, 2, 3]` is less than 0.2.

```python
distance_expression = Document.embedding.cosine_distance([1, 2, 3])
distance = distance_expression.alias('distance')
results = Document.select(Document, distance).where(distance_expression < 0.2).order_by(distance).limit(3)
```
## See also

- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)
- [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index)
