# JSON aggregate functions reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions/json-functions-aggregate.md`
- Source Title: `JSON Functions That Aggregate JSON Values`
- Source Heading Path: `JSON Functions That Aggregate JSON Values | JSON Functions That Aggregate JSON Values > [JSON_ARRAYAGG()](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_json-arrayagg) | JSON Functions That Aggregate JSON Values > [JSON_OBJECTAGG()](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_json-objectagg) | JSON Functions That Aggregate JSON Values > See also`
- Source Line Ranges: `5-132`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `aggregate-functions`, `json_arrayagg`, `json_objectagg`, `sql-examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0316_738748ce95`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions/json-functions-aggregate.md#json-functions-that-aggregate-json-values`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `34af22453c1b11ad33c4ef12cf62c3929553afdcdb8a628f0ee6a44ca2f798f1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-aggregate#json-functions-that-aggregate-json-values
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions/json-functions-aggregate.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL reference examples for aggregate JSON functions that combine rows into a JSON array or JSON object.
- Retrieval Keywords: JSON aggregate functions, JSON Functions That Aggregate JSON Values, JSON_ARRAYAGG(), JSON_OBJECTAGG(), aggregate functions, SELECT JSON_ARRAYAGG(v) FROM (SELECT 1 'v' UNION SELECT 2);, JSON_OBJECTAGG(attribute,value), GROUP BY plant_id, plants, plant_attributes, JSON array, JSON object
- Follow-up Guidance: The page also links to JSON Functions Overview and JSON Data Type.
- Classification Note: This is a SQL reference chunk because it defines the JSON_ARRAYAGG() and JSON_OBJECTAGG() aggregate functions and shows example SQL statements and results.

## Official Source Content

# JSON Functions That Aggregate JSON Values

The functions listed on this page are part of the [aggregate functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions) that TiDB supports, but are specific to working with JSON.
## [JSON_ARRAYAGG()](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_json-arrayagg)

The `JSON_ARRAYAGG(key)` function aggregates values of keys into a JSON array according to the given `key`. `key` is typically an expression or a column name.

Example:

Here the two rows in one column of a table get aggregated into a JSON array.

```sql
SELECT JSON_ARRAYAGG(v) FROM (SELECT 1 'v' UNION SELECT 2);
```

```
+------------------+
| JSON_ARRAYAGG(v) |
+------------------+
| [2, 1]           |
+------------------+
1 row in set (0.00 sec)
```
## [JSON_OBJECTAGG()](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_json-objectagg)

The `JSON_OBJECTAGG(key,value)` function aggregates keys and values of keys into a JSON object according to the given `key` and `value`. Both `key` or `value` are typically an expression or a column name.

Example:

First, create two tables and add a few rows to them.

```sql
CREATE TABLE plants (
    id INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE plant_attributes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    plant_id INT, attribute VARCHAR(255),
    value VARCHAR(255),
    FOREIGN KEY (plant_id) REFERENCES plants(id)
);

INSERT INTO plants
VALUES
(1,"rose"),
(2,"tulip"),
(3,"orchid");

INSERT INTO plant_attributes(plant_id,attribute,value)
VALUES
(1,"color","red"),
(1,"thorns","yes"),
(2,"color","orange"),
(2,"thorns","no"),
(2,"grows_from","bulb"),
(3,"color","white"),
(3, "thorns","no");
```

Now you can check what the created tables look like.

```sql
TABLE plants;
```

```
+----+--------+
| id | name   |
+----+--------+
|  1 | rose   |
|  2 | tulip  |
|  3 | orchid |
+----+--------+
3 rows in set (0.00 sec)
```

```sql
TABLE plant_attributes;
```

```
+----+----------+------------+--------+
| id | plant_id | attribute  | value  |
+----+----------+------------+--------+
|  1 |        1 | color      | red    |
|  2 |        1 | thorns     | yes    |
|  3 |        2 | color      | orange |
|  4 |        2 | thorns     | no     |
|  5 |        2 | grows_from | bulb   |
|  6 |        3 | color      | white  |
|  7 |        3 | thorns     | no     |
+----+----------+------------+--------+
7 rows in set (0.00 sec)
```

You can use the `JSON_OBJECTAGG()` function with this data. Here you can see that for every group multiple key/value pairs are aggregated into a JSON object.

```sql
SELECT
    p.name,
    JSON_OBJECTAGG(attribute,value)
FROM
    plant_attributes pa
    LEFT JOIN plants p ON pa.plant_id=p.id
GROUP BY
    plant_id;
```

```
+--------+-----------------------------------------------------------+
| name   | JSON_OBJECTAGG(attribute,value)                           |
+--------+-----------------------------------------------------------+
| rose   | {"color": "red", "thorns": "yes"}                         |
| orchid | {"color": "white", "thorns": "no"}                        |
| tulip  | {"color": "orange", "grows_from": "bulb", "thorns": "no"} |
+--------+-----------------------------------------------------------+
3 rows in set (0.00 sec)
```
## See also

- [JSON Functions Overview](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [JSON Data Type](https://docs.pingcap.com/tidb/stable/data-type-json)
