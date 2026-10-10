# JSON modification SQL functions reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions/json-functions-modify.md`
- Source Title: `JSON Functions That Modify JSON Values`
- Source Heading Path: `JSON Functions That Modify JSON Values | JSON Functions That Modify JSON Values > [JSON_APPEND()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-append) | JSON Functions That Modify JSON Values > [JSON_ARRAY_APPEND()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-array-append) | JSON Functions That Modify JSON Values > [JSON_ARRAY_INSERT()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-array-insert) | JSON Functions That Modify JSON Values > [JSON_INSERT()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-insert) | JSON Functions That Modify JSON Values > [JSON_MERGE_PATCH()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-merge-patch) | JSON Functions That Modify JSON Values > [JSON_MERGE_PRESERVE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-merge-preserve) | JSON Functions That Modify JSON Values > [JSON_MERGE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-merge) | JSON Functions That Modify JSON Values > [JSON_REMOVE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-remove)`
- Source Line Ranges: `5-217`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `sql-functions`, `json-array-append`, `json-array-insert`, `json-insert`, `json-merge-patch`, `json-merge-preserve`, `json-merge`, `json-remove`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0318_e0ec437d45`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions/json-functions-modify.md#json-functions-that-modify-json-values`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8ca132b53ab8cd541786a30b5815603dd37c4488c174c47fb4aab3b3c2203c07`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json-functions-that-modify-json-values
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions/json-functions-modify.md

## Retrieval Guidance

- Use When: Use this reference when looking for TiDB SQL functions that modify JSON values, including appending to arrays, inserting values, merging JSON documents, removing paths, or understanding deprecated JSON modification aliases.
- Retrieval Keywords: JSON_APPEND(), JSON_ARRAY_APPEND(), JSON_ARRAY_INSERT(), JSON_INSERT(), JSON_MERGE_PATCH(), JSON_MERGE_PRESERVE(), JSON_MERGE(), JSON_REMOVE(), JSON modification functions, modify JSON values, appends values to the end of the indicated arrays, inserts one or more values into a JSON document, does not overwrite values of existing attributes, without preserving values of duplicate keys, preserving all values associated with each key, deprecated alias, removes data of the specified path
- Follow-up Guidance: The page includes SQL examples showing root-path and nested-path array append, index-based array insert, multi-path JSON_INSERT, duplicate-key behavior for JSON_MERGE_PATCH and JSON_MERGE_PRESERVE, and JSON_REMOVE with one or more paths.
- Classification Note: This chunk is reference content because it lists JSON modification SQL functions with exact signatures, aliases, deprecation status, behavior notes, and example statements.

## Official Source Content

# JSON Functions That Modify JSON Values

This document describes JSON functions that modify JSON values.
## [JSON_APPEND()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-append)

An alias to [`JSON_ARRAY_APPEND()`](#json_array_append).
## [JSON_ARRAY_APPEND()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-array-append)

The `JSON_ARRAY_APPEND(json_array, path, value [,path, value] ...)` function appends values to the end of the indicated arrays within a JSON document at the specified `path` and returns the result.

This function takes arguments in pairs, where each pair is a `path` and a `value`.

Examples:

The following example adds an item to an array, which is the root of the JSON document.

```sql
SELECT JSON_ARRAY_APPEND('["Car", "Boat", "Train"]', '$', "Airplane") AS "Transport options";
```

```
+--------------------------------------+
| Transport options                    |
+--------------------------------------+
| ["Car", "Boat", "Train", "Airplane"] |
+--------------------------------------+
1 row in set (0.00 sec)
```

The following example adds an item to an array at the specified path.

```sql
SELECT JSON_ARRAY_APPEND('{"transport_options": ["Car", "Boat", "Train"]}', '$.transport_options', "Airplane") AS "Transport options";
```

```
+-------------------------------------------------------------+
| Transport options                                           |
+-------------------------------------------------------------+
| {"transport_options": ["Car", "Boat", "Train", "Airplane"]} |
+-------------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_ARRAY_INSERT()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-array-insert)

The `JSON_ARRAY_INSERT(json_array, path, value [,path, value] ...)` function inserts a `value` into the specified position of the `json_array` in the `path` and returns the result.

This function takes arguments in pairs, where each pair is a `path` and a `value`.

Examples:

The following example inserts a value at the position of index 0 in the array.

```sql
SELECT JSON_ARRAY_INSERT('["Car", "Boat", "Train"]', '$[0]', "Airplane") AS "Transport options";
```

```
+--------------------------------------+
| Transport options                    |
+--------------------------------------+
| ["Airplane", "Car", "Boat", "Train"] |
+--------------------------------------+
1 row in set (0.01 sec)
```

The following example inserts a value at the position of index 1 in the array.

```sql
SELECT JSON_ARRAY_INSERT('["Car", "Boat", "Train"]', '$[1]', "Airplane") AS "Transport options";
```

```
+--------------------------------------+
| Transport options                    |
+--------------------------------------+
| ["Car", "Airplane", "Boat", "Train"] |
+--------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_INSERT()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-insert)

The `JSON_INSERT(json_doc, path, value [,path, value] ...)` function inserts one or more values into a JSON document and returns the result.

This function takes arguments in pairs, where each pair is a `path` and a `value`.

```sql
SELECT JSON_INSERT(
    '{"language": ["Go", "Rust", "C++"]}',
    '$.architecture', 'riscv',
    '$.os', JSON_ARRAY("linux","freebsd")
) AS "Demo";
```

```
+------------------------------------------------------------------------------------------+
| Demo                                                                                     |
+------------------------------------------------------------------------------------------+
| {"architecture": "riscv", "language": ["Go", "Rust", "C++"], "os": ["linux", "freebsd"]} |
+------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

Note that this function does not overwrite values of existing attributes. For example, the following statement appears to overwrite the `"a"` attribute, but it does not actually do so.

```sql
SELECT JSON_INSERT('{"a": 61, "b": 62}', '$.a', 41, '$.c', 63);
```

```
+---------------------------------------------------------+
| JSON_INSERT('{"a": 61, "b": 62}', '$.a', 41, '$.c', 63) |
+---------------------------------------------------------+
| {"a": 61, "b": 62, "c": 63}                             |
+---------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_MERGE_PATCH()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-merge-patch)

The `JSON_MERGE_PATCH(json_doc, json_doc [,json_doc] ...)` function merges two or more JSON documents into a single JSON document, without preserving values of duplicate keys. For `json_doc` arguments with duplicated keys, only the values from the later specified `json_doc` argument are preserved in the merged result.

Examples:

In the following example, you can see that the value of `a` gets overwritten by argument 2 and that `c` is added as a new attribute in the merged result.

```sql
SELECT JSON_MERGE_PATCH(
    '{"a": 1, "b": 2}',
    '{"a": 100}',
    '{"c": 300}'
);
```

```
+-----------------------------------------------------------------+
| JSON_MERGE_PATCH('{"a": 1, "b": 2}','{"a": 100}', '{"c": 300}') |
+-----------------------------------------------------------------+
| {"a": 100, "b": 2, "c": 300}                                    |
+-----------------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_MERGE_PRESERVE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-merge-preserve)

The `JSON_MERGE_PRESERVE(json_doc, json_doc [,json_doc] ...)` function merges two or more JSON documents while preserving all values associated with each key and returns the merged result.

Examples:

In the following example, you can see that the value of argument 2 is appended to `a` and that `c` is added as a new attribute.

```sql
SELECT JSON_MERGE_PRESERVE('{"a": 1, "b": 2}','{"a": 100}', '{"c": 300}');
```

```
+--------------------------------------------------------------------+
| JSON_MERGE_PRESERVE('{"a": 1, "b": 2}','{"a": 100}', '{"c": 300}') |
+--------------------------------------------------------------------+
| {"a": [1, 100], "b": 2, "c": 300}                                  |
+--------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_MERGE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-merge)

> **Warning:**
>
> This function is deprecated.

A deprecated alias for [`JSON_MERGE_PRESERVE()`](#json_merge_preserve).
## [JSON_REMOVE()](https://dev.mysql.com/doc/refman/8.0/en/json-modification-functions.html#function_json-remove)

The `JSON_REMOVE(json_doc, path [,path] ...)` function removes data of the specified `path` from a JSON document and returns the result.

Examples:

This example removes the `b` attribute from the JSON document.

```sql
SELECT JSON_REMOVE('{"a": 61, "b": 62, "c": 63}','$.b');
```

```
+--------------------------------------------------+
| JSON_REMOVE('{"a": 61, "b": 62, "c": 63}','$.b') |
+--------------------------------------------------+
| {"a": 61, "c": 63}                               |
+--------------------------------------------------+
1 row in set (0.00 sec)
```

This example removes the `b` and `c` attributes from the JSON document.

```sql
SELECT JSON_REMOVE('{"a": 61, "b": 62, "c": 63}','$.b','$.c');
```

```
+--------------------------------------------------------+
| JSON_REMOVE('{"a": 61, "b": 62, "c": 63}','$.b','$.c') |
+--------------------------------------------------------+
| {"a": 61}                                              |
+--------------------------------------------------------+
1 row in set (0.00 sec)
```
