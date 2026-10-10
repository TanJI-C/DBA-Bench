# Django code snippets for TiDB connection and CRUD

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-python-django.md`
- Source Title: `Connect to TiDB with Django`
- Source Heading Path: `Connect to TiDB with Django > Sample code snippets | Connect to TiDB with Django > Sample code snippets > Connect to TiDB | Connect to TiDB with Django > Sample code snippets > Define the data model | Connect to TiDB with Django > Sample code snippets > Insert data | Connect to TiDB with Django > Sample code snippets > Query data | Connect to TiDB with Django > Sample code snippets > Update data | Connect to TiDB with Django > Sample code snippets > Delete data`
- Source Line Ranges: `218-325`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `django`, `python`, `code-snippets`, `database-settings`, `ssl`, `orm`, `model-definition`, `insert`, `query`, `update`, `delete`, `crud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0164_63e7a1f40b`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-python-django.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `554f21963dee2cc21f134abbb75b0d70766c006834a36135e075428f42eea5f1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-django#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-python-django.md

## Retrieval Guidance

- Use When: Use this chunk when you need Django sample code for TiDB connection settings and basic ORM CRUD examples such as model definition, insert, query, update, and delete.
- Retrieval Keywords: Sample code snippets, sample_project/settings.py, DATABASES, ENGINE django_tidb, TIDB_CA_PATH, ssl_mode VERIFY_IDENTITY, charset utf8mb4, Player models.Model, Player.objects.create, bulk_create, Player.objects.get, Player.objects.filter, Player.objects.all, player.save, update(coins=200), player.delete, delete multiple objects
- Follow-up Guidance: It points to the tidb-samples/tidb-python-django-quickstart repository for complete sample code and links to related Django models and TiDB CRUD documentation.
- Classification Note: This is classified as reference because the content provides reusable code snippets and exact configuration examples for Django-TiDB connectivity and ORM operations.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-python-django-quickstart](https://github.com/tidb-samples/tidb-python-django-quickstart) repository.
### Connect to TiDB

In the file `sample_project/settings.py`, add the following configurations:

```python
DATABASES = {
    "default": {
        "ENGINE": "django_tidb",
        "HOST": ${tidb_host},
        "PORT": ${tidb_port},
        "USER": ${tidb_user},
        "PASSWORD": ${tidb_password},
        "NAME": ${tidb_db_name},
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

TIDB_CA_PATH = ${ca_path}
if TIDB_CA_PATH:
    DATABASES["default"]["OPTIONS"]["ssl_mode"] = "VERIFY_IDENTITY"
    DATABASES["default"]["OPTIONS"]["ssl"] = {
        "ca": TIDB_CA_PATH,
    }
```

You need to replace `${tidb_host}`, `${tidb_port}`, `${tidb_user}`, `${tidb_password}`, `${tidb_db_name}`, and `${ca_path}` with the actual values of your TiDB cluster.
### Define the data model

```python
from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    coins = models.IntegerField(default=100)
    goods = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

For more information, refer to [Django models](https://docs.djangoproject.com/en/dev/topics/db/models/).
### Insert data

```python
# insert a single object
player = Player.objects.create(name="player1", coins=100, goods=1)

# bulk insert multiple objects
Player.objects.bulk_create([
    Player(name="player1", coins=100, goods=1),
    Player(name="player2", coins=200, goods=2),
    Player(name="player3", coins=300, goods=3),
])
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

```python
# get a single object
player = Player.objects.get(name="player1")

# get multiple objects
filtered_players = Player.objects.filter(name="player1")

# get all objects
all_players = Player.objects.all()
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

```python
# update a single object
player = Player.objects.get(name="player1")
player.coins = 200
player.save()

# update multiple objects
Player.objects.filter(coins=100).update(coins=200)
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

```python
# delete a single object
player = Player.objects.get(name="player1")
player.delete()

# delete multiple objects
Player.objects.filter(coins=100).delete()
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
