# JSON search functions: keys, search, membership, overlaps, and references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions/json-functions-search.md`
- Source Title: `JSON Functions That Search JSON Values`
- Source Heading Path: `JSON Functions That Search JSON Values > [JSON_KEYS()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-keys) | JSON Functions That Search JSON Values > [JSON_SEARCH()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-search) | JSON Functions That Search JSON Values > [MEMBER OF()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_member-of) | JSON Functions That Search JSON Values > [JSON_OVERLAPS()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-overlaps) | JSON Functions That Search JSON Values > See also`
- Source Line Ranges: `207-360`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `json_keys`, `json_search`, `member_of`, `json_overlaps`, `sql-functions`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0323_f95400d651`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions/json-functions-search.md#json-keys-https-dev-mysql-com-doc-refman-8-0-en-json-search-functions-html-function-json-keys`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `93b2c62217cd17a91e223f77a15b27e205f9aea8e7aea01a1ae2f4ce72bdc161`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json-keys-https-dev-mysql-com-doc-refman-8-0-en-json-search-functions-html-function-json-keys
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions/json-functions-search.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB SQL JSON search functions that return object keys, locate matching string paths, test array membership, or determine whether two JSON documents overlap.
- Retrieval Keywords: JSON_KEYS(), JSON_SEARCH(), MEMBER OF(), JSON_OVERLAPS(), JSON search functions, top-level keys of a JSON object, JSON_KEYS(json_doc [,path]), JSON_SEARCH(json_doc, one_or_all, str), str MEMBER OF (json_array), JSON_OVERLAPS(json_doc, json_doc), 'one' and 'all' JSON_SEARCH, JSON path $.name, "$.a[2]", ["$.a[2]", "$.b[0]"], returns 1 returns 0 returns NULL
- Follow-up Guidance: The source also points to JSON Functions Overview and JSON Data Type for related JSON function and data type information.
- Classification Note: This is reference content because it defines the behavior of JSON_KEYS(), JSON_SEARCH(), MEMBER OF(), and JSON_OVERLAPS() with SQL syntax and result examples.

## Official Source Content

## [JSON_KEYS()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-keys)

The `JSON_KEYS(json_doc [,path])` function returns the top-level keys of a JSON object as a JSON array. If a `path` argument is given, it returns the top-level keys from the selected path.

Examples:

The following example returns the two top-level keys in the JSON document.

```sql
SELECT JSON_KEYS('{"name": {"first": "John", "last": "Doe"}, "type": "Person"}');
```

```
+---------------------------------------------------------------------------+
| JSON_KEYS('{"name": {"first": "John", "last": "Doe"}, "type": "Person"}') |
+---------------------------------------------------------------------------+
| ["name", "type"]                                                          |
+---------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

The following example returns the top-level keys that are in the `$.name` path of the JSON document.

```sql
SELECT JSON_KEYS('{"name": {"first": "John", "last": "Doe"}, "type": "Person"}', '$.name');
```

```
+-------------------------------------------------------------------------------------+
| JSON_KEYS('{"name": {"first": "John", "last": "Doe"}, "type": "Person"}', '$.name') |
+-------------------------------------------------------------------------------------+
| ["first", "last"]                                                                   |
+-------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## [JSON_SEARCH()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-search)

The `JSON_SEARCH(json_doc, one_or_all, str)` function searches a JSON document for one or all matches of a string.

Examples:

In the following example, you can search for the first result for `cc`, which is at the position of index 2 in the `a` array.

```sql
SELECT JSON_SEARCH('{"a": ["aa", "bb", "cc"], "b": ["cc", "dd"]}','one','cc');
```

```
+------------------------------------------------------------------------+
| JSON_SEARCH('{"a": ["aa", "bb", "cc"], "b": ["cc", "dd"]}','one','cc') |
+------------------------------------------------------------------------+
| "$.a[2]"                                                               |
+------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

Now you do the same, but set `one_or_all` to `all` to get not just the first result, but all results.

```sql
SELECT JSON_SEARCH('{"a": ["aa", "bb", "cc"], "b": ["cc", "dd"]}','all','cc');
```

```
+------------------------------------------------------------------------+
| JSON_SEARCH('{"a": ["aa", "bb", "cc"], "b": ["cc", "dd"]}','all','cc') |
+------------------------------------------------------------------------+
| ["$.a[2]", "$.b[0]"]                                                   |
+------------------------------------------------------------------------+
1 row in set (0.01 sec)
```
## [MEMBER OF()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_member-of)

The `str MEMBER OF (json_array)` function tests if the passed value `str` is an element of the `json_array`, it returns `1`. Otherwise, it returns `0`. It returns `NULL` if any of the arguments is `NULL`.

```
SELECT '🍍' MEMBER OF ('["🍍","🥥","🥭"]') AS 'Contains pineapple';
```

```
+--------------------+
| Contains pineapple |
+--------------------+
|                  1 |
+--------------------+
1 row in set (0.00 sec)

```
## [JSON_OVERLAPS()](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#function_json-overlaps)

The `JSON_OVERLAPS(json_doc, json_doc)` function indicates whether two JSON documents have overlapping part. If yes, it returns `1`. If not, it returns `0`. It returns `NULL` if any of the arguments is `NULL`.

Examples:

The following example shows that there is no overlap because the array value does not have the same number of elements.

```sql
SELECT JSON_OVERLAPS(
    '{"languages": ["Go","Rust","C#"]}',
    '{"languages": ["Go","Rust"]}'
) AS 'Overlaps';
```

```
+----------+
| Overlaps |
+----------+
|        0 |
+----------+
1 row in set (0.00 sec)
```

The following example shows that both JSON documents overlap as they are identical.

```sql
SELECT JSON_OVERLAPS(
    '{"languages": ["Go","Rust","C#"]}',
    '{"languages": ["Go","Rust","C#"]}'
) AS 'Overlaps';
```

```
+----------+
| Overlaps |
+----------+
|        1 |
+----------+
1 row in set (0.00 sec)
```

The following example shows that there is an overlap, while the second document has an extra attribute.

```sql
SELECT JSON_OVERLAPS(
    '{"languages": ["Go","Rust","C#"]}',
    '{"languages": ["Go","Rust","C#"], "arch": ["arm64"]}'
) AS 'Overlaps';
```

```
+----------+
| Overlaps |
+----------+
|        1 |
+----------+
1 row in set (0.00 sec)
```
## See also

- [JSON Functions Overview](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [JSON Data Type](https://docs.pingcap.com/tidb/stable/data-type-json)
