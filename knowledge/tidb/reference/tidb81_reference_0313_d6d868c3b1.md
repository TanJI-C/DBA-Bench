# JSON function categories and function index

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions.md`
- Source Title: `JSON Functions`
- Source Heading Path: `JSON Functions | JSON Functions > Functions that create JSON values | JSON Functions > Functions that search JSON values | JSON Functions > Functions that modify JSON values | JSON Functions > Functions that return JSON value attributes | JSON Functions > Utility functions | JSON Functions > Aggregate functions`
- Source Line Ranges: `5-71`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `functions`, `operators`, `search`, `modify`, `aggregate`, `utility`, `attributes`, `sql-reference`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0313_d6d868c3b1`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions.md#json-functions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d96ea50f0de80c92c49d9a74748ccea3a1f76af2e70b5db62644107e1d609a2e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions#json-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB SQL reference index of JSON function categories and exact JSON function or operator names for creating, searching, modifying, inspecting, formatting, or aggregating JSON values.
- Retrieval Keywords: JSON Functions, JSON_ARRAY(), JSON_OBJECT(), JSON_QUOTE(), JSON_CONTAINS(), JSON_CONTAINS_PATH(), JSON_EXTRACT(), ->, ->>, JSON_KEYS(), JSON_SEARCH(), MEMBER OF(), JSON_OVERLAPS(), JSON_APPEND(), JSON_ARRAY_APPEND(), JSON_ARRAY_INSERT(), JSON_INSERT(), JSON_MERGE_PATCH(), JSON_MERGE_PRESERVE(), JSON_MERGE(), JSON_REMOVE(), JSON_REPLACE(), JSON_SET(), JSON_UNQUOTE(), JSON_DEPTH(), JSON_LENGTH(), JSON_TYPE(), JSON_VALID(), JSON_PRETTY(), JSON_STORAGE_FREE(), JSON_STORAGE_SIZE(), JSON_ARRAYAGG(), JSON_OBJECTAGG(), functions that create JSON values, functions that search JSON values, functions that modify JSON values, functions that return JSON value attributes, utility functions, aggregate functions, JSON data type, sql reference
- Follow-up Guidance: Follow the linked function-specific sections for the exact semantics of each JSON function or operator listed in this index.
- Classification Note: This is classified as reference content because it is an index of JSON function categories, names, aliases, and brief descriptions for TiDB SQL.

## Official Source Content

# JSON Functions

You can use JSON functions to work with data in the [JSON data type](https://docs.pingcap.com/tidb/stable/data-type-json).
## Functions that create JSON values

| Function Name                     | Description |
| --------------------------------- | ----------- |
| [JSON_ARRAY()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-create#json_array) | Evaluates a (possibly empty) list of values and returns a JSON array containing those values |
| [JSON_OBJECT()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-create#json_object) | Evaluates a (possibly empty) list of key-value pairs and returns a JSON object containing those pairs  |
| [JSON_QUOTE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-create#json_quote) | Returns a string as a JSON value with quotes |
## Functions that search JSON values

| Function Name                     | Description |
| --------------------------------- | ----------- |
| [JSON_CONTAINS()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json_contains) | Indicates by returning 1 or 0 whether a given candidate JSON document is contained within a target JSON document |
| [JSON_CONTAINS_PATH()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json_contains_path) | Returns 0 or 1 to indicate whether a JSON document contains data at a given path or paths |
| [JSON_EXTRACT()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json_extract) | Returns data from a JSON document, selected from the parts of the document matched by the `path` arguments |
| [->](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#-)  | Returns the value from a JSON column after the evaluating path; an alias for `JSON_EXTRACT(doc, path_literal)`   |
| [->>](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#--1)  | Returns the value from a JSON column after the evaluating path and unquoting the result; an alias for `JSON_UNQUOTE(JSON_EXTRACT(doc, path_literal))` |
| [JSON_KEYS()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json_keys) | Returns the keys from the top-level value of a JSON object as a JSON array, or, if a path argument is given, the top-level keys from the selected path |
| [JSON_SEARCH()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json_search) | Search a JSON document for one or all matches of a string |
| [MEMBER OF()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#member-of) | If the passed value is an element of the JSON array, returns 1. Otherwise, returns 0. |
| [JSON_OVERLAPS()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json_overlaps) | Indicates whether two JSON documents have overlapping part. If yes, returns 1. If not, returns 0. |
## Functions that modify JSON values

| Function Name                     | Description |
| --------------------------------- | ----------- |
| [JSON_APPEND()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_append) | An alias to `JSON_ARRAY_APPEND()` |
| [JSON_ARRAY_APPEND()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_array_append) | Appends values to the end of the indicated arrays within a JSON document and returns the result |
| [JSON_ARRAY_INSERT()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_array_insert) | Insert values into the specified locations of a JSON document and returns the result |
| [JSON_INSERT()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_insert) | Inserts data into a JSON document and returns the result |
| [JSON_MERGE_PATCH()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_merge_patch)  | Merges two or more JSON documents, without preserving values of duplicate keys |
| [JSON_MERGE_PRESERVE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_merge_preserve)  | Merges two or more JSON documents by preserving all values |
| [JSON_MERGE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_merge)  | A deprecated alias for `JSON_MERGE_PRESERVE()` |
| [JSON_REMOVE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_remove)    | Removes data from a JSON document and returns the result |
| [JSON_REPLACE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_replace) | Replaces existing values in a JSON document and returns the result |
| [JSON_SET()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_set)  | Inserts or updates data in a JSON document and returns the result |
| [JSON_UNQUOTE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-modify#json_unquote) |  Unquotes a JSON value and returns the result as a string |
## Functions that return JSON value attributes

| Function Name                     | Description |
| --------------------------------- | ----------- |
| [JSON_DEPTH()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-return#json_depth) | Returns the maximum depth of a JSON document |
| [JSON_LENGTH()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-return#json_length) | Returns the length of a JSON document, or, if a path argument is given, the length of the value within the path |
| [JSON_TYPE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-return#json_type) | Returns a string indicating the type of a JSON value |
| [JSON_VALID()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-return#json_valid) | Checks if a json\_doc is valid JSON. |
## Utility functions

| Function Name                     | Description |
| --------------------------------- | ----------- |
| [JSON_PRETTY()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-utility#json_pretty) | Pretty formatting of a JSON document |
| [JSON_STORAGE_FREE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-utility#json_storage_free) | Returns how much storage space was freed in the binary representation of the JSON value after it was updated in place. |
| [JSON_STORAGE_SIZE()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-utility#json_storage_size) | Returns an approximate size of bytes required to store the json value. As the size does not account for TiKV using compression, the output of this function is not strictly compatible with MySQL. |
## Aggregate functions

| Function Name                     | Description |
| --------------------------------- | ----------- |
| [JSON_ARRAYAGG()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-aggregate#json_arrayagg) | Provides an aggregation of keys. |
| [JSON_OBJECTAGG()](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-aggregate#json_objectagg) | Provides an aggregation of values for a given key. |
