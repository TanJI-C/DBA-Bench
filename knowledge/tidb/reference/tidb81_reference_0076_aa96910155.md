# JSON data type overview, value types, restrictions, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-json.md`
- Source Title: `TiDB Data Type`
- Source Heading Path: `JSON Data Type | JSON Data Type > JSON value types | JSON Data Type > Restrictions | JSON Data Type > MySQL compatibility`
- Source Line Ranges: `5-125`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`, `br`, `shared`
- Topic Tags: `json`, `data-types`, `generated-columns`, `indexing`, `json-type`, `restrictions`, `compatibility`, `tiflash-pushdown`, `backup-restore`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0076_aa96910155`
- Source ID: `tidb-docs-8.1:data-type-json.md#json-data-type`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `73e8a014ceaabe6c2d00048bb0ade5ad5f40baa9d4445e0a9916c9365938394b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-json#json-data-type
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-json.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB JSON data type overview, JSON value types, indexing through generated columns, restrictions involving TiFlash pushdown, BR encoding, replication tools, or MySQL compatibility differences.
- Retrieval Keywords: JSON data type, JSON value types, JSON_TYPE(), generated column, JSON_EXTRACT(detail, '$.population'), CREATE TABLE city, index index_name (population), TiFlash push-down expressions, BR JSON column data is encoded in v6.3.0, replicate data containing non-standard JSON data types, DATE DATETIME TIME JSON, BINARY type mislabeled as STRING, issue #37443, CAST(e AS JSON), ERROR 3140 (22032): Invalid JSON text: The document root must not be followed by other values., issue #9999, ORDER BY sort JSON arrays or JSON objects, This version of MySQL doesn't yet support 'sorting of non-scalar JSON values'., issue #37506, INSERT INTO t VALUES (3), implicitly converts the value of the data to the JSON type
- Follow-up Guidance: The source also points to JSON Functions and Generated Columns for more information.
- Classification Note: This chunk is classified as reference content because it defines TiDB JSON behavior, lists supported JSON value types and restrictions, and documents MySQL compatibility differences with exact SQL examples and error text.

## Official Source Content

# JSON Data Type

TiDB supports the `JSON` (JavaScript Object Notation) data type, which is useful for storing semi-structured data. The `JSON` data type provides the following advantages over storing `JSON`-format strings in a string column:

- Use the Binary format for serialization. The internal format permits quick read access to `JSON` document elements.
- Automatic validation of the JSON documents stored in `JSON` columns. Only valid documents can be stored.

`JSON` columns, like columns of other binary types, are not indexed directly, but you can index the fields in the `JSON` document in the form of generated column:

```sql
CREATE TABLE city (
    id INT PRIMARY KEY,
    detail JSON,
    population INT AS (JSON_EXTRACT(detail, '$.population')),
    index index_name (population)
    );
INSERT INTO city (id,detail) VALUES (1, '{"name": "Beijing", "population": 100}');
SELECT id FROM city WHERE population >= 100;
```

For more information, see [JSON Functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions) and [Generated Columns](https://docs.pingcap.com/tidb/stable/generated-columns).
## JSON value types

The values inside a JSON document have types. This is visible in the output of [`JSON_TYPE`()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-return#json_type).

| Type             | Example                        |
|------------------|--------------------------------|
| ARRAY            | `[]`                           |
| BIT              |                                |
| BLOB             | `0x616263`                     |
| BOOLEAN          | `true`                         |
| DATE             | `"2025-06-14"`                 |
| DATETIME         | `"2025-06-14 09:05:10.000000"` |
| DOUBLE           | `1.14`                         |
| INTEGER          | `5`                            |
| NULL             | `null`                         |
| OBJECT           | `{}`                           |
| OPAQUE           |                                |
| STRING           | `"foobar"`                     |
| TIME             | `"09:10:00.000000"`            |
| UNSIGNED INTEGER | `9223372036854776000`          |
## Restrictions

- Currently, TiDB only supports pushing down limited `JSON` functions to TiFlash. For more information, see [Push-down expressions](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations#push-down-expressions).
- TiDB Backup & Restore (BR) changes how JSON column data is encoded in v6.3.0. Therefore, it is not recommended to use BR to restore data containing JSON columns to a TiDB cluster earlier than v6.3.0.
- Do not use any replication tool to replicate data containing non-standard `JSON` data types, such as `DATE`, `DATETIME`, and `TIME`.
## MySQL compatibility

- When you create JSON columns with data in the `BINARY` type, MySQL mislabels the data as the `STRING` type currently, while TiDB processes it as the `BINARY` type correctly.

    ```sql
    CREATE TABLE test(a json);
    INSERT INTO test SELECT json_objectagg('a', b'01010101');

    -- In TiDB, executing the following SQL statement returns `0, 0`. In MySQL, executing the following SQL statement returns `0, 1`.
    mysql> SELECT JSON_EXTRACT(JSON_OBJECT('a', b'01010101'), '$.a') = "base64:type15:VQ==" AS r1, JSON_EXTRACT(a, '$.a') = "base64:type15:VQ==" AS r2 FROM test;
    +------+------+
    | r1   | r2   |
    +------+------+
    |    0 |    0 |
    +------+------+
    1 row in set (0.01 sec)
    ```

    For more information, see issue [#37443](https://github.com/pingcap/tidb/issues/37443).

- When converting the data type from `ENUM` or `SET` to `JSON`, TiDB checks the correctness of data format. For example, executing the following SQL statements in TiDB will return an error.

    ```sql
    CREATE TABLE t(e ENUM('a'));
    INSERT INTO t VALUES ('a');
    mysql> SELECT CAST(e AS JSON) FROM t;
    ERROR 3140 (22032): Invalid JSON text: The document root must not be followed by other values.
    ```

    For more information, see issue [#9999](https://github.com/pingcap/tidb/issues/9999).

- In TiDB, you can use `ORDER BY` to sort JSON arrays or JSON objects.

    In MySQL, if you use `ORDER BY` to sort JSON arrays or JSON objects, MySQL returns a warning and the sorting result does not match the result of the comparison operation:

    ```sql
    CREATE TABLE t(j JSON);
    INSERT INTO t VALUES ('[1,2,3,4]');
    INSERT INTO t VALUES ('[5]');

    mysql> SELECT j FROM t WHERE j < JSON_ARRAY(5);
    +--------------+
    | j            |
    +--------------+
    | [1, 2, 3, 4] |
    +--------------+
    1 row in set (0.00 sec)

    -- In TiDB, executing the following SQL statement returns the correct sorting result. In MySQL, executing the following SQL statement returns the "This version of MySQL doesn't yet support 'sorting of non-scalar JSON values'." warning and the sorting result is inconsistent with the comparison result of `<`.
    mysql> SELECT j FROM t ORDER BY j;
    +--------------+
    | j            |
    +--------------+
    | [1, 2, 3, 4] |
    | [5]          |
    +--------------+
    2 rows in set (0.00 sec)
    ```

    For more information, see issue [#37506](https://github.com/pingcap/tidb/issues/37506).

- When you insert data to a JSON column, TiDB implicitly converts the value of the data to the `JSON` type.

    ```sql
    CREATE TABLE t(col JSON);

    -- In TiDB, the following INSERT statement is executed successfully. In MySQL, executing the following INSERT statement returns the "Invalid JSON text" error.
    INSERT INTO t VALUES (3);
    ```

For more information about the `JSON` data type, see [JSON functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions) and [Generated Columns](https://docs.pingcap.com/tidb/stable/generated-columns).
