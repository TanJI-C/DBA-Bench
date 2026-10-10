# JSON creation functions: array, object, and quote

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions/json-functions-create.md`
- Source Title: `JSON Functions That Create JSON Values`
- Source Heading Path: `JSON Functions That Create JSON Values | JSON Functions That Create JSON Values > [JSON_ARRAY()](https://dev.mysql.com/doc/refman/8.0/en/json-creation-functions.html#function_json-array) | JSON Functions That Create JSON Values > [JSON_OBJECT()](https://dev.mysql.com/doc/refman/8.0/en/json-creation-functions.html#function_json-object) | JSON Functions That Create JSON Values > [JSON_QUOTE()](https://dev.mysql.com/doc/refman/8.0/en/json-creation-functions.html#function_json-quote) | JSON Functions That Create JSON Values > See also`
- Source Line Ranges: `5-64`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `functions`, `json_array`, `json_object`, `json_quote`, `sql-syntax`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0317_884c8443b8`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions/json-functions-create.md#json-functions-that-create-json-values`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d77ba93848ca607274be260724d5f2aed6693717108c932f6943e9ecc0eab74a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-create#json-functions-that-create-json-values
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions/json-functions-create.md

## Retrieval Guidance

- Use When: Use this chunk when looking for SQL reference examples of creating JSON values with JSON_ARRAY(), JSON_OBJECT(), or JSON_QUOTE() in TiDB.
- Retrieval Keywords: JSON creation functions, JSON_ARRAY(), JSON_OBJECT(), JSON_QUOTE(), JSON Functions That Create JSON Values, SELECT JSON_ARRAY(1,2,3,4,5), SELECT JSON_OBJECT("database", "TiDB", "distributed", TRUE), SELECT JSON_QUOTE('The name is \"O\\'Neil\"'), JSON array containing those values, JSON object containing those pairs, returns a string as a JSON value with quotes
- Follow-up Guidance: The source also links to JSON Functions Overview and JSON Data Type.
- Classification Note: This is reference content because it defines the syntax and return behavior of JSON_ARRAY(), JSON_OBJECT(), and JSON_QUOTE() and shows example SQL results.

## Official Source Content

# JSON Functions That Create JSON Values

This document describes JSON functions that create JSON values.
## [JSON_ARRAY()](https://dev.mysql.com/doc/refman/8.0/en/json-creation-functions.html#function_json-array)

The `JSON_ARRAY([val[, val] ...])` function evaluates a (possibly empty) list of values and returns a JSON array containing those values.

```sql
SELECT JSON_ARRAY(1,2,3,4,5), JSON_ARRAY("foo", "bar");
```

```
+-----------------------+--------------------------+
| JSON_ARRAY(1,2,3,4,5) | JSON_ARRAY("foo", "bar") |
+-----------------------+--------------------------+
| [1, 2, 3, 4, 5]       | ["foo", "bar"]           |
+-----------------------+--------------------------+
1 row in set (0.00 sec)
```
## [JSON_OBJECT()](https://dev.mysql.com/doc/refman/8.0/en/json-creation-functions.html#function_json-object)

The `JSON_OBJECT([key, val[, key, val] ...])` function evaluates a (possibly empty) list of key-value pairs and returns a JSON object containing those pairs.

```sql
SELECT JSON_OBJECT("database", "TiDB", "distributed", TRUE);
```

```
+------------------------------------------------------+
| JSON_OBJECT("database", "TiDB", "distributed", TRUE) |
+------------------------------------------------------+
| {"database": "TiDB", "distributed": true}            |
+------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_QUOTE()](https://dev.mysql.com/doc/refman/8.0/en/json-creation-functions.html#function_json-quote)

The `JSON_QUOTE(str)` function returns a string as a JSON value with quotes.

```sql
SELECT JSON_QUOTE('The name is "O\'Neil"');
```

```
+-------------------------------------+
| JSON_QUOTE('The name is "O\'Neil"') |
+-------------------------------------+
| "The name is \"O'Neil\""            |
+-------------------------------------+
1 row in set (0.00 sec)
```
## See also

- [JSON Functions Overview](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [JSON Data Type](https://docs.pingcap.com/tidb/stable/data-type-json)
