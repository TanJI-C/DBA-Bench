# peewee code snippets for TiDB CRUD

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-python-peewee.md`
- Source Title: `Connect to TiDB with peewee`
- Source Heading Path: `Connect to TiDB with peewee > Sample code snippets | Connect to TiDB with peewee > Sample code snippets > Connect to TiDB | Connect to TiDB with peewee > Sample code snippets > Define a table | Connect to TiDB with peewee > Sample code snippets > Insert data | Connect to TiDB with peewee > Sample code snippets > Query data | Connect to TiDB with peewee > Sample code snippets > Update data | Connect to TiDB with peewee > Sample code snippets > Delete data | Connect to TiDB with peewee > Next steps`
- Source Line Ranges: `189-307`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `code-snippets`, `connection`, `model-definition`, `insert`, `query`, `update`, `delete`, `crud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0171_532d85fcc8`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-python-peewee.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ed35750fdd68dcf30ab12211e855fa2790abde51296cb43af0b51d5fac0b40e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-peewee#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-python-peewee.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants peewee code examples for connecting to TiDB and performing basic CRUD operations with a sample Player model.
- Retrieval Keywords: Sample code snippets, MySQLDatabase, get_db_engine, ssl_verify_cert, ssl_verify_identity, ssl_ca, BaseModel, Player, table_name = "players", Player.create, insert_many, Player.select, Player.get, where(Player.coins == 100), Player.update, player.save(), player.delete_instance(), Player.delete().where, Define a table, Insert data, Query data, Update data, Delete data
- Follow-up Guidance: The chunk points to the tidb-samples/tidb-python-peewee-quickstart repository and related Developer guide topics such as Insert data, Update data, Delete data, Single table reading, Transactions, and SQL performance optimization.
- Classification Note: This is reference content because it supplies example code patterns and named APIs for connection setup, model definition, and CRUD usage with peewee and TiDB.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-python-peewee-quickstart](https://github.com/tidb-samples/tidb-python-peewee-quickstart) repository.
### Connect to TiDB

```python
from peewee import MySQLDatabase

def get_db_engine():
    config = Config()
    connect_params = {}
    if ${ca_path}:
        connect_params = {
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
            "ssl_ca": ${ca_path},
        }
    return MySQLDatabase(
        ${tidb_db_name},
        host=${tidb_host},
        port=${tidb_port},
        user=${tidb_user},
        password=${tidb_password},
        **connect_params,
    )
```

When using this function, you need to replace `${tidb_host}`, `${tidb_port}`, `${tidb_user}`, `${tidb_password}`, `${tidb_db_name}` and `${ca_path}` with the actual values of your TiDB cluster.
### Define a table

```python
from peewee import Model, CharField, IntegerField

db = get_db_engine()

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    name = CharField(max_length=32, unique=True)
    coins = IntegerField(default=0)
    goods = IntegerField(default=0)

    class Meta:
        table_name = "players"
```

For more information, refer to [peewee documentation: Models and Fields](https://docs.peewee-orm.com/en/latest/peewee/models.html).
### Insert data

```python
# Insert a single record
Player.create(name="test", coins=100, goods=100)

# Insert multiple records
Player.insert_many(
    [
        {"name": "test1", "coins": 100, "goods": 100},
        {"name": "test2", "coins": 100, "goods": 100},
    ]
).execute()
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

```python
# Query all records
players = Player.select()

# Query a single record
player = Player.get(Player.name == "test")

# Query multiple records
players = Player.select().where(Player.coins == 100)
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

```python
# Update a single record
player = Player.get(Player.name == "test")
player.coins = 200
player.save()

# Update multiple records
Player.update(coins=200).where(Player.coins == 100).execute()
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

```python
# Delete a single record
player = Player.get(Player.name == "test")
player.delete_instance()

# Delete multiple records
Player.delete().where(Player.coins == 100).execute()
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Next steps

- Learn more usage of peewee from [the documentation of peewee](https://docs.peewee-orm.com/).
- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
