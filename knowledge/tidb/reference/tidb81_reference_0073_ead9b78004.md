# Automatic initialization and update for TIMESTAMP and DATETIME

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/data-type-date-and-time.md`
- Source Title: `Date and Time Types`
- Source Heading Path: `Date and Time Types > Automatic initialization and update of `TIMESTAMP` and `DATETIME``
- Source Line Ranges: `148-171`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `default-values`, `current-timestamp`, `on-update`, `datetime`, `timestamp`, `column-definition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0073_ead9b78004`
- Source ID: `tidb-docs-8.1:data-type-date-and-time.md#automatic-initialization-and-update-of-timestamp-and-datetime`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `293d368478f7fd6ae15daca6653a35f59659d77f8fe05c8133bd0655df6cbbff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/data-type-date-and-time#automatic-initialization-and-update-of-timestamp-and-datetime
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/data-type-date-and-time.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about automatic initialization or auto-update behavior for TIMESTAMP or DATETIME columns using DEFAULT CURRENT_TIMESTAMP or ON UPDATE CURRENT_TIMESTAMP.
- Retrieval Keywords: DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP, automatic initialization, automatic update, TIMESTAMP default, DATETIME default, CREATE TABLE t1, dt1 DATETIME ON UPDATE CURRENT_TIMESTAMP, dt2 DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP, DEFAULT 0, DEFAULT '2000-01-01 00:00:00'
- Follow-up Guidance: The source states that DATETIME defaults to NULL unless specified as NOT NULL, and if it is NOT NULL with no explicit default value, the default is 0.
- Classification Note: This is reference content because it documents column definition behavior for automatic current timestamp defaults and updates on TIMESTAMP and DATETIME types.

## Official Source Content

## Automatic initialization and update of `TIMESTAMP` and `DATETIME`

Columns with `TIMESTAMP` or `DATETIME` value type can be automatically initialized or updated to the current time.

For any column with `TIMESTAMP` or `DATETIME` value type in the table, you can set the default or auto-update value as current timestamp.

These properties can be set by setting `DEFAULT CURRENT_TIMESTAMP` and `ON UPDATE CURRENT_TIMESTAMP` when the column is being defined. DEFAULT can also be set as a specific value, such as `DEFAULT 0` or `DEFAULT '2000-01-01 00:00:00'`.

```sql
CREATE TABLE t1 (
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    dt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

The default value for `DATETIME` is `NULL` unless it is specified as `NOT NULL`. For the latter situation, if no default value is set, the default value is be 0.

```sql
CREATE TABLE t1 (
    dt1 DATETIME ON UPDATE CURRENT_TIMESTAMP,         -- default NULL
    dt2 DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP -- default 0
);
```
