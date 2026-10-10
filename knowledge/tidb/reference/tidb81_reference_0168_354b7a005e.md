# mysqlclient connection and CRUD code snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-python-mysqlclient.md`
- Source Title: `Connect to TiDB with mysqlclient`
- Source Heading Path: `Connect to TiDB with mysqlclient > Sample code snippets | Connect to TiDB with mysqlclient > Sample code snippets > Connect to TiDB | Connect to TiDB with mysqlclient > Sample code snippets > Insert data | Connect to TiDB with mysqlclient > Sample code snippets > Query data | Connect to TiDB with mysqlclient > Sample code snippets > Update data | Connect to TiDB with mysqlclient > Sample code snippets > Delete data | Connect to TiDB with mysqlclient > Useful notes | Connect to TiDB with mysqlclient > Useful notes > Using driver or ORM framework?`
- Source Line Ranges: `189-278`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `sql`, `tidb`
- Topic Tags: `python`, `mysqlclient`, `code-snippets`, `database-connection`, `crud`, `insert`, `query`, `update`, `delete`, `orm`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0168_354b7a005e`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-python-mysqlclient.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c0de3ec2079cf6242c400d661bd925564be42c53438cfd2e404bd25d2309cf51`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-mysqlclient#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-python-mysqlclient.md

## Retrieval Guidance

- Use When: Use this chunk when you need official mysqlclient Python code examples for connecting to TiDB or performing basic CRUD operations, or when comparing driver usage with ORM frameworks.
- Retrieval Keywords: Sample code snippets, get_mysqlclient_connection, MySQLdb.connect, ssl_mode, VERIFY_IDENTITY, ssl, ca, INSERT INTO players (id, coins, goods) VALUES (%s, %s, %s), SELECT count(*) FROM players, UPDATE players SET goods = goods + %s, coins = coins + %s WHERE id = %s, DELETE FROM players WHERE id = %s, autocommit, mysqlclient, Using driver or ORM framework, SQLAlchemy, Peewee, Django ORM
- Follow-up Guidance: The source also notes that ORM frameworks such as SQLAlchemy, Peewee, and Django ORM can reduce boilerplate for connection and transaction management.
- Classification Note: This is classified as a reference chunk because the content mainly provides reusable code snippets, exact SQL examples, connection parameters, and explanatory notes about driver versus ORM usage.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-python-mysqlclient-quickstart](https://github.com/tidb-samples/tidb-python-mysqlclient-quickstart) repository.
### Connect to TiDB

```python
def get_mysqlclient_connection(autocommit:bool=True) -> MySQLdb.Connection:
    db_conf = {
        "host": ${tidb_host},
        "port": ${tidb_port},
        "user": ${tidb_user},
        "password": ${tidb_password},
        "database": ${tidb_db_name},
        "autocommit": autocommit
    }

    if ${ca_path}:
        db_conf["ssl_mode"] = "VERIFY_IDENTITY"
        db_conf["ssl"] = {"ca": ${ca_path}}

    return MySQLdb.connect(**db_conf)
```

When using this function, you need to replace `${tidb_host}`, `${tidb_port}`, `${tidb_user}`, `${tidb_password}`, `${tidb_db_name}` and `${ca_path}` with the actual values of your TiDB cluster.
### Insert data

```python
with get_mysqlclient_connection(autocommit=True) as conn:
    with conn.cursor() as cur:
        player = ("1", 1, 1)
        cursor.execute("INSERT INTO players (id, coins, goods) VALUES (%s, %s, %s)", player)
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

```python
with get_mysqlclient_connection(autocommit=True) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM players")
        print(cur.fetchone()[0])
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

```python
with get_mysqlclient_connection(autocommit=True) as conn:
    with conn.cursor() as cur:
        player_id, amount, price="1", 10, 500
        cursor.execute(
            "UPDATE players SET goods = goods + %s, coins = coins + %s WHERE id = %s",
            (-amount, price, player_id),
        )
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

```python
with get_mysqlclient_connection(autocommit=True) as conn:
    with conn.cursor() as cur:
        player_id = "1"
        cursor.execute("DELETE FROM players WHERE id = %s", (player_id,))
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Useful notes
### Using driver or ORM framework?

The Python driver provides low-level access to the database, but it requires the developers to:

- Manually establish and release database connections.
- Manually manage database transactions.
- Manually map data rows (represented as tuples in `mysqlclient`) to data objects.

Unless you need to write complex SQL statements, it is recommended to use [ORM](https://en.wikipedia.org/w/index.php?title=Object-relational_mapping) framework for development, such as [SQLAlchemy](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-sqlalchemy), [Peewee](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-peewee), and Django ORM. It can help you:

- Reduce [boilerplate code](https://en.wikipedia.org/wiki/Boilerplate_code) for managing connections and transactions.
- Manipulate data with data objects instead of a number of SQL statements.
