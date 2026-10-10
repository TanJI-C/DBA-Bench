# SQLAlchemy sample code for connection and CRUD

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-python-sqlalchemy.md`
- Source Title: `Connect to TiDB with SQLAlchemy`
- Source Heading Path: `Connect to TiDB with SQLAlchemy > Sample code snippets | Connect to TiDB with SQLAlchemy > Sample code snippets > Connect to TiDB | Connect to TiDB with SQLAlchemy > Sample code snippets > Define a table | Connect to TiDB with SQLAlchemy > Sample code snippets > Insert data | Connect to TiDB with SQLAlchemy > Sample code snippets > Query data | Connect to TiDB with SQLAlchemy > Sample code snippets > Update data | Connect to TiDB with SQLAlchemy > Sample code snippets > Delete data`
- Source Line Ranges: `195-294`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `python`, `sqlalchemy`, `pymysql`, `engine`, `session`, `orm`, `table-definition`, `crud`, `insert`, `query`, `update`, `delete`, `tls`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0175_88dbc94dc2`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-python-sqlalchemy.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `efb5818c44a8ecec75312752aa5730445d7aa3d1876897042297b092e2a99fc1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-sqlalchemy#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-python-sqlalchemy.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs SQLAlchemy sample snippets for creating a TiDB engine with PyMySQL and optional TLS settings, defining the Player ORM table, or performing basic CRUD with Session.
- Retrieval Keywords: Sample code snippets, create_engine, URL.create, mysql+pymysql, sessionmaker, connect_args, ssl_verify_cert, ssl_verify_identity, ssl_ca, declarative_base, Player, __tablename__ = "players", Column, Integer, String, session.add, session.commit, session.query, filter_by, one, session.delete, Insert data, Query data, Update data, Delete data
- Follow-up Guidance: The source links to the tidb-samples/tidb-python-sqlalchemy-quickstart repository and to related TiDB docs for Insert data, Query data, Update data, and Delete data.
- Classification Note: This chunk is classified as reference because the official content provides code examples for connection setup, ORM table definition, and CRUD operations rather than step-by-step environment configuration.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-python-sqlalchemy-quickstart](https://github.com/tidb-samples/tidb-python-sqlalchemy-quickstart) repository.
### Connect to TiDB

```python
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

def get_db_engine():
    connect_args = {}
    if ${ca_path}:
        connect_args = {
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
            "ssl_ca": ${ca_path},
        }
    return create_engine(
        URL.create(
            drivername="mysql+pymysql",
            username=${tidb_user},
            password=${tidb_password},
            host=${tidb_host},
            port=${tidb_port},
            database=${tidb_db_name},
        ),
        connect_args=connect_args,
    )

engine = get_db_engine()
Session = sessionmaker(bind=engine)
```

When using this function, you need to replace `${tidb_host}`, `${tidb_port}`, `${tidb_user}`, `${tidb_password}`, `${tidb_db_name}` and `${ca_path}` with the actual values of your TiDB cluster.
### Define a table

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Player(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    coins = Column(Integer)
    goods = Column(Integer)

    __tablename__ = "players"
```

For more information, refer to [SQLAlchemy documentation: Mapping classes with declarative](https://docs.sqlalchemy.org/en/20/orm/declarative_mapping.html).
### Insert data

```python
with Session() as session:
    player = Player(name="test", coins=100, goods=100)
    session.add(player)
    session.commit()
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

```python
with Session() as session:
    player = session.query(Player).filter_by(name == "test").one()
    print(player)
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

```python
with Session() as session:
    player = session.query(Player).filter_by(name == "test").one()
    player.coins = 200
    session.commit()
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

```python
with Session() as session:
    player = session.query(Player).filter_by(name == "test").one()
    session.delete(player)
    session.commit()
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
