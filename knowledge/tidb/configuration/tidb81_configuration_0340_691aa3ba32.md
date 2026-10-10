# TiDB Lightning error tolerance for type and conflict errors

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-error-resolution.md`
- Source Title: `TiDB Lightning Error Resolution`
- Source Heading Path: `TiDB Lightning Error Resolution | TiDB Lightning Error Resolution > Type error | TiDB Lightning Error Resolution > Conflict errors`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`
- Topic Tags: `error-tolerance`, `type-errors`, `conflict-errors`, `import-configuration`, `deprecated-settings`, `physical-import`, `logical-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0340_691aa3ba32`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-error-resolution.md#tidb-lightning-error-resolution`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1eabac55bdc4a916f0de5ea8230acde04f2f96fdefd4fa99343354d717af4d06`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-error-resolution#tidb-lightning-error-resolution
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-error-resolution.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB Lightning tolerates and skips type errors or conflict errors during import and which configuration items control those limits.
- Retrieval Keywords: lightning.max-error, conflict.strategy, conflict.threshold, conflict.max-record-rows, tikv-importer.duplicate-resolution, deprecated in v8.0.0, lightning.task-info-schema-name, type error, conflict errors, invalid type conversion, unique key conflicts, physical import mode, logical import mode, skip errors, error tolerance
- Follow-up Guidance: The source says skipped errors are recorded in a database or table, a report is generated, and more details are in the Error report section.
- Classification Note: This is classified as configuration because the content centers on TiDB Lightning settings that define tolerance thresholds and conflict handling behavior.

## Official Source Content

# TiDB Lightning Error Resolution

Starting from v5.4.0, you can configure TiDB Lightning to skip errors like invalid type conversion and unique key conflicts, and to continue the data processing as if those wrong row data does not exist. A report will be generated for you to read and manually fix errors afterward. This is ideal for importing from a slightly dirty data source, where locating the errors manually is difficult and restarting TiDB Lightning on every encounter is costly.

This document introduces TiDB Lightning error types, how to query the errors, and provides an example. The following configuration items are involved:

- `lightning.max-error`: the tolerance threshold of type error
- `conflict.strategy`, `conflict.threshold`, and `conflict.max-record-rows`: configurations related to conflicting data
- `tikv-importer.duplicate-resolution` (deprecated in v8.0.0 and will be removed in a future release): the conflict handling configuration that can only be used in the physical import mode
- `lightning.task-info-schema-name`: the database where conflicting data is stored when TiDB Lightning detects conflicts

For more information, see [TiDB Lightning (Task)](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task).
## Type error

You can use the `lightning.max-error` configuration to increase the tolerance of errors related to data types. If this configuration is set to *N*, TiDB Lightning allows and skips up to *N* type errors from the data source before it exists. The default value `0` means that no error is allowed.

These errors are recorded in a database. After the import is completed, you can view the errors in the database and process them manually. For more information, see [Error Report](#error-report).

```toml
[lightning]
max-error = 0
```

The above configuration covers the following errors:

* Invalid values (example: set `'Text'` to an INT column).
* Numeric overflow (example: set `500` to a TINYINT column)
* String overflow (example: set `'Very Long Text'` to a VARCHAR(5) column).
* Zero date-time (namely `'0000-00-00'` and `'2021-12-00'`).
* Set NULL to a NOT NULL column.
* Failed to evaluate a generated column expression.
* Column count mismatch. The number of values in the row does not match the number of columns of the table.
* Any other SQL errors.

The following errors are always fatal, and cannot be skipped by changing `lightning.max-error`:

* Syntax error (such as unclosed quotation marks) in the original CSV, SQL or Parquet file.
* I/O, network or system permission errors.
## Conflict errors

You can use the [`conflict.threshold`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) configuration item to increase the tolerance of errors related to data conflict. If this configuration item is set to *N*, TiDB Lightning allows and skips up to *N* conflict errors from the data source before it exits. The default value is `10000`, which means that 10000 errors are tolerant.

These errors are recorded in a table. After the import is completed, you can view the errors in the database and process them manually. For more information, see [Error Report](#error-report)
