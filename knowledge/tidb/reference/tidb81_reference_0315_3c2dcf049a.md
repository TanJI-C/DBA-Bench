# Related references, unsupported JSON functions, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions.md`
- Source Title: `JSON Functions`
- Source Heading Path: `JSON Functions > See also | JSON Functions > Unsupported functions | JSON Functions > MySQL compatibility`
- Source Line Ranges: `138-153`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `json`, `unsupported-functions`, `mysql-compatibility`, `reference-links`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0315_3c2dcf049a`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions.md#see-also`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f582f951f72a568365f62ca944641b0c8ed3e1938c136de50d2be3fd1a35c20`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions#see-also
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need the related JSON Data Type reference, the list of unsupported JSON functions, or the stated MySQL 8.0 compatibility note for JSON functions in TiDB.
- Retrieval Keywords: JSON Data Type, unsupported functions, JSON_SCHEMA_VALID(), JSON_SCHEMA_VALIDATION_REPORT(), JSON_TABLE(), JSON_VALUE(), #14486, MySQL compatibility, MySQL 8.0, JSON functions
- Follow-up Guidance: It links to the JSON Data Type page and issue #14486 for more information.
- Classification Note: This is reference content because it lists related references, enumerates unsupported JSON functions, and states the compatibility note with MySQL 8.0 JSON functions.

## Official Source Content

## See also

* [JSON Data Type](https://docs.pingcap.com/tidb/stable/data-type-json)
## Unsupported functions

- `JSON_SCHEMA_VALID()`
- `JSON_SCHEMA_VALIDATION_REPORT()`
- `JSON_TABLE()`
- `JSON_VALUE()`

For more information, see [#14486](https://github.com/pingcap/tidb/issues/14486).
## MySQL compatibility

- TiDB supports most of the [JSON functions](https://dev.mysql.com/doc/refman/8.0/en/json-functions.html) available in MySQL 8.0.
