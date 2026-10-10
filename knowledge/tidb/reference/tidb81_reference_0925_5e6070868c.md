# Django ORM sample code for TiDB vector storage and search

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-django-orm.md`
- Source Title: `Integrate TiDB Vector Search with Django ORM`
- Source Heading Path: `Integrate TiDB Vector Search with Django ORM > Sample code snippets | Integrate TiDB Vector Search with Django ORM > Sample code snippets > Connect to the TiDB cluster | Integrate TiDB Vector Search with Django ORM > Sample code snippets > Create vector tables | Integrate TiDB Vector Search with Django ORM > Sample code snippets > Create vector tables > Define a vector column | Integrate TiDB Vector Search with Django ORM > Sample code snippets > Store documents with embeddings | Integrate TiDB Vector Search with Django ORM > Sample code snippets > Search the nearest neighbor documents | Integrate TiDB Vector Search with Django ORM > Sample code snippets > Search documents within a certain distance | Integrate TiDB Vector Search with Django ORM > See also`
- Source Line Ranges: `133-221`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `cloud`, `sql`
- Topic Tags: `django`, `orm`, `sample-code`, `database-connection`, `ssl`, `vectorfield`, `embeddings`, `nearest-neighbor`, `cosine-distance`, `distance-filter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0925_5e6070868c`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-django-orm.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `99716c8fd1f15208e7ec13f85ef56a61b0fdc08e5f6af96b9433a8a1b10929b6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-django-orm#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-django-orm.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs Django ORM sample code for connecting to a TiDB cluster, defining a vector column, storing embeddings, or running vector distance queries.
- Retrieval Keywords: sample_project/settings.py, DATABASES, ENGINE django_tidb, TIDB_CA_PATH, ssl_mode VERIFY_IDENTITY, VectorField(dimensions=3), Document(models.Model), Document.objects.create, L1Distance, L2Distance, CosineDistance, NegativeInnerProduct, annotate(distance=CosineDistance('embedding', [1, 2, 3])), order_by('distance')[:3], filter(distance__lt=0.2), embedding, Vector Data Types, Vector Search Index
- Follow-up Guidance: The source also links to the Vector Data Types and Vector Search Index documentation.
- Classification Note: This is classified as a reference chunk because it provides code snippets and exact identifiers for configuration, model definition, data insertion, and query patterns.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.
### Connect to the TiDB cluster

In the file `sample_project/settings.py`, add the following configurations:

```python
dotenv.load_dotenv()

DATABASES = {
    "default": {
        # https://github.com/pingcap/django-tidb
        "ENGINE": "django_tidb",
        "HOST": os.environ.get("TIDB_HOST", "127.0.0.1"),
        "PORT": int(os.environ.get("TIDB_PORT", 4000)),
        "USER": os.environ.get("TIDB_USERNAME", "root"),
        "PASSWORD": os.environ.get("TIDB_PASSWORD", ""),
        "NAME": os.environ.get("TIDB_DATABASE", "test"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

TIDB_CA_PATH = os.environ.get("TIDB_CA_PATH", "")
if TIDB_CA_PATH:
    DATABASES["default"]["OPTIONS"]["ssl_mode"] = "VERIFY_IDENTITY"
    DATABASES["default"]["OPTIONS"]["ssl"] = {
        "ca": TIDB_CA_PATH,
    }
```

You can create a `.env` file in the root directory of your project and set up the environment variables `TIDB_HOST`, `TIDB_PORT`, `TIDB_USERNAME`, `TIDB_PASSWORD`, `TIDB_DATABASE`, and `TIDB_CA_PATH` with the actual values of your TiDB cluster.
### Create vector tables
#### Define a vector column

`tidb-django` provides a `VectorField` to store vector embeddings in a table.

Create a table with a column named `embedding` that stores a 3-dimensional vector.

```python
class Document(models.Model):
   content = models.TextField()
   embedding = VectorField(dimensions=3)
```
### Store documents with embeddings

```python
Document.objects.create(content="dog", embedding=[1, 2, 1])
Document.objects.create(content="fish", embedding=[1, 2, 4])
Document.objects.create(content="tree", embedding=[1, 0, 0])
```
### Search the nearest neighbor documents

TiDB Vector support the following distance functions:

- `L1Distance`
- `L2Distance`
- `CosineDistance`
- `NegativeInnerProduct`

Search for the top-3 documents that are semantically closest to the query vector `[1, 2, 3]` based on the cosine distance function.

```python
results = Document.objects.annotate(
   distance=CosineDistance('embedding', [1, 2, 3])
).order_by('distance')[:3]
```
### Search documents within a certain distance

Search for the documents whose cosine distance from the query vector `[1, 2, 3]` is less than 0.2.

```python
results = Document.objects.annotate(
   distance=CosineDistance('embedding', [1, 2, 3])
).filter(distance__lt=0.2).order_by('distance')[:3]
```
## See also

- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)
- [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index)
