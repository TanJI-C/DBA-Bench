# JSON search functions and path operators

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions/json-functions-search.md`
- Source Title: `JSON Functions That Search JSON Values`
- Source Heading Path: `JSON Functions That Search JSON Values | JSON Functions That Search JSON Values > [JSON_CONTAINS()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-contains) | JSON Functions That Search JSON Values > [JSON_CONTAINS_PATH()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-contains-path) | JSON Functions That Search JSON Values > [JSON_EXTRACT()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-extract) | JSON Functions That Search JSON Values > [->](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_json-column-path) | JSON Functions That Search JSON Values > [->>](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_json-inline-path)`
- Source Line Ranges: `5-206`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `functions`, `search`, `path`, `operators`, `examples`, `sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0322_5e2b782581`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions/json-functions-search.md#json-functions-that-search-json-values`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b14927a8044d303528be796ebac151679510b1d2675cdfa84a456c2936220f68`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json-functions-that-search-json-values
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions/json-functions-search.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL reference examples of JSON search functions and path operators such as checking containment, checking whether a path exists, extracting a JSON value, or comparing `->` and `->>` behavior.
- Retrieval Keywords: JSON_CONTAINS(json_doc, candidate [,path]), JSON_CONTAINS_PATH(json_doc, all_or_one, path [,path, ...]), JSON_EXTRACT(json_doc, path[, path] ...), column->path, column->>path, JSON_UNQUOTE(JSON_EXTRACT(doc, path_literal)), $.foo, $.aaa, $.bar, SELECT JSON_CONTAINS('["a","b","c"]','"a"');, SELECT JSON_CONTAINS('{"foo": "bar", "aaa": 5}','"bar"', '$.foo');, SELECT JSON_CONTAINS_PATH('{"foo": "bar", "aaa": 5}','all','$.foo', '$.aaa');, SELECT JSON_EXTRACT('{"foo": "bar", "aaa": 5}', '$.foo');, JSON path operators, JSON search functions
- Follow-up Guidance: The examples show that `->` is an alias for `JSON_EXTRACT()` and `->>` is an alias for `JSON_UNQUOTE(JSON_EXTRACT(doc, path_literal))`.
- Classification Note: This is reference content because it defines JSON search functions and path operators and illustrates their return values with SQL examples.

## Official Source Content

# JSON Functions That Search JSON Values

This document describes JSON functions that search JSON values.
## [JSON_CONTAINS()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-contains)

By returning `1` or `0`, the `JSON_CONTAINS(json_doc, candidate [,path])` function indicates whether a given `candidate` JSON document is contained within a target JSON document.

Examples:

Here `a` is contained in the target document.

```sql
SELECT JSON_CONTAINS('["a","b","c"]','"a"');
```

```
+--------------------------------------+
| JSON_CONTAINS('["a","b","c"]','"a"') |
+--------------------------------------+
|                                    1 |
+--------------------------------------+
1 row in set (0.00 sec)
```

Here `e` is not contained in the target document.

```sql
SELECT JSON_CONTAINS('["a","b","c"]','"e"');
```

```
+--------------------------------------+
| JSON_CONTAINS('["a","b","c"]','"e"') |
+--------------------------------------+
|                                    0 |
+--------------------------------------+
1 row in set (0.00 sec)
```

Here `{"foo": "bar"}` is contained in the target document.

```sql
SELECT JSON_CONTAINS('{"foo": "bar", "aaa": 5}','{"foo": "bar"}');
```

```
+------------------------------------------------------------+
| JSON_CONTAINS('{"foo": "bar", "aaa": 5}','{"foo": "bar"}') |
+------------------------------------------------------------+
|                                                          1 |
+------------------------------------------------------------+
1 row in set (0.00 sec)
```

Here `"bar"` is not contained in the root of the target document.

```sql
SELECT JSON_CONTAINS('{"foo": "bar", "aaa": 5}','"bar"');
```

```
+---------------------------------------------------+
| JSON_CONTAINS('{"foo": "bar", "aaa": 5}','"bar"') |
+---------------------------------------------------+
|                                                 0 |
+---------------------------------------------------+
1 row in set (0.00 sec)
```

Here `"bar"` is contained in the `$.foo` attribute of the target document.

```sql
SELECT JSON_CONTAINS('{"foo": "bar", "aaa": 5}','"bar"', '$.foo');
```

```
+------------------------------------------------------------+
| JSON_CONTAINS('{"foo": "bar", "aaa": 5}','"bar"', '$.foo') |
+------------------------------------------------------------+
|                                                          1 |
+------------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_CONTAINS_PATH()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-contains-path)

The `JSON_CONTAINS_PATH(json_doc, all_or_one, path [,path, ...])` function returns `0` or `1` to indicate whether a JSON document contains data at a given path or paths.

Examples:

Here the document contains `$.foo`.

```sql
SELECT JSON_CONTAINS_PATH('{"foo": "bar", "aaa": 5}','all','$.foo');
```

```
+--------------------------------------------------------------+
| JSON_CONTAINS_PATH('{"foo": "bar", "aaa": 5}','all','$.foo') |
+--------------------------------------------------------------+
|                                                            1 |
+--------------------------------------------------------------+
1 row in set (0.00 sec)
```

Here the document does not contain `$.bar`.

```sql
SELECT JSON_CONTAINS_PATH('{"foo": "bar", "aaa": 5}','all','$.bar');
```

```
+--------------------------------------------------------------+
| JSON_CONTAINS_PATH('{"foo": "bar", "aaa": 5}','all','$.bar') |
+--------------------------------------------------------------+
|                                                            0 |
+--------------------------------------------------------------+
1 row in set (0.00 sec)
```

Here the document contains both `$.foo` and `$.aaa`.

```sql
SELECT JSON_CONTAINS_PATH('{"foo": "bar", "aaa": 5}','all','$.foo', '$.aaa');
```

```
+-----------------------------------------------------------------------+
| JSON_CONTAINS_PATH('{"foo": "bar", "aaa": 5}','all','$.foo', '$.aaa') |
+-----------------------------------------------------------------------+
|                                                                     1 |
+-----------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_EXTRACT()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-extract)

The `JSON_EXTRACT(json_doc, path[, path] ...)` function extracts data from a JSON document, selected from the parts of the document matched by the `path` arguments.

```sql
SELECT JSON_EXTRACT('{"foo": "bar", "aaa": 5}', '$.foo');
```

```
+---------------------------------------------------+
| JSON_EXTRACT('{"foo": "bar", "aaa": 5}', '$.foo') |
+---------------------------------------------------+
| "bar"                                             |
+---------------------------------------------------+
1 row in set (0.00 sec)
```
## [->](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_json-column-path)

The `column->path` function returns the data in `column` that matches the `path` argument. It is an alias for [`JSON_EXTRACT()`](#json_extract).

```sql
SELECT
    j->'$.foo',
    JSON_EXTRACT(j, '$.foo')
FROM (
    SELECT
        '{"foo": "bar", "aaa": 5}' AS j
    ) AS tbl;
```

```
+------------+--------------------------+
| j->'$.foo' | JSON_EXTRACT(j, '$.foo') |
+------------+--------------------------+
| "bar"      | "bar"                    |
+------------+--------------------------+
1 row in set (0.00 sec)
```
## [->>](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_json-inline-path)

The `column->>path` function unquotes data in `column` that matches the `path` argument. It is an alias for `JSON_UNQUOTE(JSON_EXTRACT(doc, path_literal))`.

```sql
SELECT
    j->'$.foo',
    JSON_EXTRACT(j, '$.foo')
    j->>'$.foo',
    JSON_UNQUOTE(JSON_EXTRACT(j, '$.foo'))
FROM (
    SELECT
        '{"foo": "bar", "aaa": 5}' AS j
    ) AS tbl;
```

```
+------------+--------------------------+-------------+----------------------------------------+
| j->'$.foo' | JSON_EXTRACT(j, '$.foo') | j->>'$.foo' | JSON_UNQUOTE(JSON_EXTRACT(j, '$.foo')) |
+------------+--------------------------+-------------+----------------------------------------+
| "bar"      | "bar"                    | bar         | bar                                    |
+------------+--------------------------+-------------+----------------------------------------+
1 row in set (0.00 sec)
```
