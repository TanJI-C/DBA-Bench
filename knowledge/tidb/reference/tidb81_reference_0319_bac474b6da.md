# JSON_REPLACE and JSON_SET semantics and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions/json-functions-modify.md`
- Source Title: `JSON Functions That Modify JSON Values`
- Source Heading Path: `JSON Functions That Modify JSON Values > [JSON_REPLACE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-replace) | JSON Functions That Modify JSON Values > [JSON_SET()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-set)`
- Source Line Ranges: `218-293`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `json_replace`, `json_set`, `sql-functions`, `path-value-pairs`, `document-update`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0319_bac474b6da`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions/json-functions-modify.md#json-replace-https-dev-mysql-com-doc-refman-8-0-en-json-modification-functions-html-function-json-replace`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dd208c83d7ac6f3764fa099eaf446cb27473759acf731be30f74de66a7375ddb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json-replace-https-dev-mysql-com-doc-refman-8-0-en-json-modification-functions-html-function-json-replace
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions/json-functions-modify.md

## Retrieval Guidance

- Use When: Use this chunk when comparing how JSON_REPLACE and JSON_SET handle path-value pairs in a JSON document, especially whether non-existent paths are ignored or added.
- Retrieval Keywords: JSON_REPLACE(json_doc, path, value [, path, value] ...), JSON_SET(json_doc, path, value [,path, value] ...), path-value pairs, specified path does not exist, replaces values in specified paths, inserts or updates data in a JSON document, SELECT JSON_REPLACE('{"a": 41, "b": 62}','$.b',42), SELECT JSON_REPLACE('{"a": 41, "b": 62}','$.b',42,'$.c',43), SELECT JSON_SET('{"version": 1.1, "name": "example"}','$.version',1.2), SELECT JSON_SET('{"version": 1.1, "name": "example"}','$.version',1.2,'$.branch', "main"), $.b, $.c, $.version, $.branch
- Follow-up Guidance: The examples show JSON_REPLACE updating $.b but not adding $.c, while JSON_SET updates $.version and adds the previously missing $.branch.
- Classification Note: This is reference content because it defines the semantics of JSON_REPLACE() and JSON_SET() and illustrates them with exact SQL examples and returned JSON results.

## Official Source Content

## [JSON_REPLACE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-replace)

The `JSON_REPLACE(json_doc, path, value [, path, value] ...)` function replaces values in specified paths of a JSON document and returns the result. If a specified path does not exist, the value corresponding to the path is not added to the result.

This function takes arguments in pairs, where each pair is a `path` and a `value`.

Examples:

In the following example, you change the value at `$.b` from `62` to `42`.

```sql
SELECT JSON_REPLACE('{"a": 41, "b": 62}','$.b',42);
```

```
+---------------------------------------------+
| JSON_REPLACE('{"a": 41, "b": 62}','$.b',42) |
+---------------------------------------------+
| {"a": 41, "b": 42}                          |
+---------------------------------------------+
1 row in set (0.00 sec)
```

In the following example, you can change the value at `$.b` from `62` to `42`.  In addition, this statement tries to replace the value at `$.c` with `43`, but it does not work because the `$.c` path does not exist in `{"a": 41, "b": 62}`.

```sql
SELECT JSON_REPLACE('{"a": 41, "b": 62}','$.b',42,'$.c',43);
```

```
+------------------------------------------------------+
| JSON_REPLACE('{"a": 41, "b": 62}','$.b',42,'$.c',43) |
+------------------------------------------------------+
| {"a": 41, "b": 42}                                   |
+------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_SET()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-set)

The `JSON_SET(json_doc, path, value [,path, value] ...)` function inserts or updates data in a JSON document and returns the result.

This function takes arguments in pairs, where each pair is a `path` and a `value`.

Examples:

In the following example, you can update the `$.version` from `1.1` to `1.2`.

```sql
SELECT JSON_SET('{"version": 1.1, "name": "example"}','$.version',1.2);
```

```
+-----------------------------------------------------------------+
| JSON_SET('{"version": 1.1, "name": "example"}','$.version',1.2) |
+-----------------------------------------------------------------+
| {"name": "example", "version": 1.2}                             |
+-----------------------------------------------------------------+
1 row in set (0.00 sec)
```

In the following example, you can update the `$.version` from `1.1` to `1.2`. And you can update `$.branch`, which does not exist before, to `main`.

```sql
SELECT JSON_SET('{"version": 1.1, "name": "example"}','$.version',1.2,'$.branch', "main");
```

```
+------------------------------------------------------------------------------------+
| JSON_SET('{"version": 1.1, "name": "example"}','$.version',1.2,'$.branch', "main") |
+------------------------------------------------------------------------------------+
| {"branch": "main", "name": "example", "version": 1.2}                              |
+------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
