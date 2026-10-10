# JSON_UNQUOTE usage and related JSON references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions/json-functions-modify.md`
- Source Title: `JSON Functions That Modify JSON Values`
- Source Heading Path: `JSON Functions That Modify JSON Values > [JSON_UNQUOTE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-unquote) | JSON Functions That Modify JSON Values > See also`
- Source Line Ranges: `294-346`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `json_unquote`, `json_extract`, `json_quote`, `arrow-operator`, `sql-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0320_5afed4e929`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions/json-functions-modify.md#json-unquote-https-dev-mysql-com-doc-refman-8-0-en-json-modification-functions-html-function-json-unquote`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4d2d47abed801021db4e857e43f82b7c069a5246874188875110f4745ab9c750`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json-unquote-https-dev-mysql-com-doc-refman-8-0-en-json-modification-functions-html-function-json-unquote
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions/json-functions-modify.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how JSON_UNQUOTE returns a JSON value as a string or how it is used with JSON_EXTRACT or the ->> operator.
- Retrieval Keywords: JSON_UNQUOTE(json), unquotes a JSON value and returns the result as a string, JSON_QUOTE(), JSON_EXTRACT(), ->> operator, SELECT JSON_UNQUOTE('"foo"'), SELECT JSON_EXTRACT('{"database": "TiDB"}', '$.database'), SELECT JSON_UNQUOTE(JSON_EXTRACT('{"database": "TiDB"}', '$.database')), "foo", foo, "TiDB", TiDB, JSON Functions Overview, JSON Data Type
- Follow-up Guidance: The source notes that JSON_UNQUOTE(JSON_EXTRACT(...)) can be replaced with the ->> operator and points to JSON Functions Overview and JSON Data Type for related references.
- Classification Note: This is reference content because it explains the behavior of JSON_UNQUOTE(), its relation to JSON_QUOTE(), and its usage alongside JSON_EXTRACT() and the ->> operator with concrete SQL examples.

## Official Source Content

## [JSON_UNQUOTE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-unquote)

The `JSON_UNQUOTE(json)` function unquotes a JSON value and returns the result as a string. This is the opposite of the [`JSON_QUOTE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-create#json_quote) function.

Examples:

In the example, `"foo"` is unquoted to `foo`.

```sql
SELECT JSON_UNQUOTE('"foo"');
```

```
+-----------------------+
| JSON_UNQUOTE('"foo"') |
+-----------------------+
| foo                   |
+-----------------------+
1 row in set (0.00 sec)
```

This function is often used together with [`JSON_EXTRACT()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json_extract). For the following examples, you can extract a JSON value with quotes in the first example and then use the two functions together to unquote the value in the second example. Note that instead of `JSON_UNQUOTE(JSON_EXTRACT(...))`, you can use the [`->>`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#--1) operator.

```sql
SELECT JSON_EXTRACT('{"database": "TiDB"}', '$.database');
```

```
+----------------------------------------------------+
| JSON_EXTRACT('{"database": "TiDB"}', '$.database') |
+----------------------------------------------------+
| "TiDB"                                             |
+----------------------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT JSON_UNQUOTE(JSON_EXTRACT('{"database": "TiDB"}', '$.database'));
```

```
+------------------------------------------------------------------+
| JSON_UNQUOTE(JSON_EXTRACT('{"database": "TiDB"}', '$.database')) |
+------------------------------------------------------------------+
| TiDB                                                             |
+------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## See also

- [JSON Functions Overview](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [JSON Data Type](https://docs.pingcap.com/tidb/stable/data-type-json)
