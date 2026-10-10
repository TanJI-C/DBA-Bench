# JSON utility SQL functions reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions/json-functions-utility.md`
- Source Title: `JSON Utility Functions`
- Source Heading Path: `JSON Utility Functions | JSON Utility Functions > [JSON_PRETTY()](https://dev.mysql.com/doc/refman/8.0/en/json-utility-functions.html#function_json-pretty) | JSON Utility Functions > [JSON_STORAGE_FREE()](https://dev.mysql.com/doc/refman/8.0/en/json-utility-functions.html#function_json-storage-free) | JSON Utility Functions > [JSON_STORAGE_SIZE()](https://dev.mysql.com/doc/refman/8.0/en/json-utility-functions.html#function_json-storage-size) | JSON Utility Functions > See also`
- Source Line Ranges: `5-73`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `json`, `functions`, `sql`, `compatibility`, `storage`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0324_37aa20c97e`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions/json-functions-utility.md#json-utility-functions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0a1dd71e1a3c3d89b6c419ad9fd1f4ce08b250403ad4284e28fff846f94df14a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-utility#json-utility-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions/json-functions-utility.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL reference details and examples for the JSON utility functions JSON_PRETTY(), JSON_STORAGE_FREE(), and JSON_STORAGE_SIZE(), including compatibility notes about storage behavior.
- Retrieval Keywords: JSON_PRETTY(), JSON_STORAGE_FREE(), JSON_STORAGE_SIZE(), JSON utility functions, pretty formatting of a JSON document, always returns 0, compatibility with MySQL 8.0, TiDB does not do in-place updates, RocksDB space usage, approximate size of bytes required to store the JSON value, TiKV using compression, not strictly compatible with MySQL, SELECT JSON_PRETTY, SELECT JSON_STORAGE_FREE('{}'), SELECT JSON_STORAGE_SIZE('{}')
- Follow-up Guidance: The source also points to JSON Functions Overview and JSON Data Type for related JSON documentation.
- Classification Note: This is a SQL reference chunk because it defines JSON utility SQL functions, shows example SELECT statements, and notes TiDB compatibility and storage-related behavior.

## Official Source Content

# JSON Utility Functions

This document describes JSON utility functions.
## [JSON_PRETTY()](https://dev.mysql.com/doc/refman/8.0/en/json-utility-functions.html#function_json-pretty)

The `JSON_PRETTY(json_doc)` function does pretty formatting of a JSON document.

```sql
SELECT JSON_PRETTY('{"person":{"name":{"first":"John","last":"Doe"},"age":23}}')\G
```

```
*************************** 1. row ***************************
JSON_PRETTY('{"person":{"name":{"first":"John","last":"Doe"},"age":23}}'): {
  "person": {
    "age": 23,
    "name": {
      "first": "John",
      "last": "Doe"
    }
  }
}
1 row in set (0.00 sec)
```
## [JSON_STORAGE_FREE()](https://dev.mysql.com/doc/refman/8.0/en/json-utility-functions.html#function_json-storage-free)

The `JSON_STORAGE_FREE(json_doc)` function returns how much storage space is freed in the binary representation of the JSON value after it is updated in place. 

> **Note:**
>
> Because TiDB has a different storage architecture from MySQL, this function always returns `0` for a valid JSON value, and it is implemented for [compatibility with MySQL 8.0](https://docs.pingcap.com/tidb/stable/mysql-compatibility). Note that TiDB does not do in-place updates. For more information, see [RocksDB space usage](https://docs.pingcap.com/tidb/stable/storage-engine/rocksdb-overview#rocksdb-space-usage).

```sql
SELECT JSON_STORAGE_FREE('{}');
```

```
+-------------------------+
| JSON_STORAGE_FREE('{}') |
+-------------------------+
|                       0 |
+-------------------------+
1 row in set (0.00 sec)
```
## [JSON_STORAGE_SIZE()](https://dev.mysql.com/doc/refman/8.0/en/json-utility-functions.html#function_json-storage-size)

The `JSON_STORAGE_SIZE(json_doc)` function returns an approximate size of bytes required to store the JSON value. Because the size does not account for TiKV using compression, the output of this function is not strictly compatible with MySQL.

```sql
SELECT JSON_STORAGE_SIZE('{}');
```

```
+-------------------------+
| JSON_STORAGE_SIZE('{}') |
+-------------------------+
|                       9 |
+-------------------------+
1 row in set (0.00 sec)
```
## See also

- [JSON Functions Overview](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [JSON Data Type](https://docs.pingcap.com/tidb/stable/data-type-json)
