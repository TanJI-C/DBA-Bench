# TiDB usage limits and version constraint

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-limitations.md`
- Source Title: `TiDB Limitations`
- Source Heading Path: `TiDB Limitations | TiDB Limitations > Limitations on identifier length | TiDB Limitations > Limitations on the total number of databases, tables, views, and connections | TiDB Limitations > Limitations on a single database | TiDB Limitations > Limitations on a single table | TiDB Limitations > Limitation on a single row | TiDB Limitations > Limitations on data types | TiDB Limitations > Limitations on SQL statements | TiDB Limitations > Limitations on TiKV version`
- Source Line Ranges: `5-94`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `limitations`, `identifier-length`, `table-limits`, `row-size`, `data-types`, `sql-statements`, `configuration`, `version-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0943_a4b7670ef3`
- Source ID: `tidb-docs-8.1:tidb-limitations.md#tidb-limitations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db97620a2946040e2c4ab639b846fd5414d215e36467dd9a48943a9fd65cedd9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-limitations#tidb-limitations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-limitations.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB usage limits such as maximum identifier length, per-table column or index limits, row size limits, data type bounds, SQL statement count limits, or the TiDB and TiKV version constraint.
- Retrieval Keywords: TiDB Limitations, maximum identifier length, Database 64, Table 64, Column 64, Index 64, View 64, Sequence 64, single table Columns defaults to 1017 and can be adjusted up to 4096, single table Indexes defaults to 64 and can be adjusted up to 512, Partitions 8192, txn-entry-size-limit, table-column-count-limit, index-limit, stmt-count-limit, maximum number of SQL statements in a single transaction 5000, VARCHAR 16383 characters, CHAR 255 characters, BINARY 255 bytes, VARBINARY 65535 bytes, TEXT 65535 bytes, BLOB 65535 bytes, TiKV version must be v6.2.0 or later, TiDB component is v6.2.0 or later
- Follow-up Guidance: The content points to MySQL Compatibility and the TiDB configuration items `table-column-count-limit`, `index-limit`, `txn-entry-size-limit`, and `stmt-count-limit` for related limit details.
- Classification Note: This is classified as a reference chunk because it enumerates documented upper limits, configurable caps, and a TiDB-TiKV version requirement without procedural steps.

## Official Source Content

# TiDB Limitations

This document describes the common usage limitations of TiDB, including the maximum identifier length and the maximum number of supported databases, tables, indexes, partitioned tables, and sequences.

> **Note:**
>
> TiDB offers high compatibility with the MySQL protocol and syntax, including many MySQL limitations. For example, a single index can include a maximum of 16 columns. For more information, see [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility) and the official MySQL documentation.
## Limitations on identifier length

| Identifier type | Maximum length (number of characters allowed) |
|:---------|:--------------|
| Database | 64 |
| Table    | 64 |
| Column   | 64 |
| Index    | 64 |
| View     | 64 |
| Sequence | 64 |
## Limitations on the total number of databases, tables, views, and connections

| Type  | Maximum number  |
|:----------|:----------|
| Databases | unlimited |
| Tables    | unlimited |
| Views     | unlimited |
| Connections| unlimited|
## Limitations on a single database

| Type       | Upper limit   |
|:----------|:----------|
| Tables    | unlimited  |
## Limitations on a single table

| Type       | Upper limit (default value)  |
|:----------|:----------|
| Columns   | Defaults to 1017 and can be adjusted up to 4096     |
| Indexes   |  Defaults to 64 and can be adjusted up to 512        |
| Rows      | unlimited |
| Size      | unlimited |
| Partitions | 8192     |

* The upper limit of `Columns` can be modified via [`table-column-count-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#table-column-count-limit-new-in-v50).
* The upper limit of `Indexes` can be modified via [`index-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#index-limit-new-in-v50).
## Limitation on a single row

| Type       | Upper limit (default value)   |
|:----------|:----------|
| Size       | Defaults to 6 MiB and can be adjusted to 120 MiB  |

You can adjust the size limit via the [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500) configuration item.
## Limitations on data types

| Type       | Upper limit   |
|:----------|:----------|
| CHAR       | 255 characters      |
| BINARY     | 255 bytes      |
| VARBINARY  | 65535 bytes    |
| VARCHAR    | 16383 characters    |
| TEXT       | 65535 bytes    |
| BLOB       | 65535 bytes    |
## Limitations on SQL statements

| Type       | Upper limit   |
|:----------|:----------|
| The maximum number of SQL statements in a single transaction |  When the optimistic transaction is used and the transaction retry is enabled, the upper limit is 5000. |

You can modify the limit via the [`stmt-count-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#stmt-count-limit) configuration item.
## Limitations on TiKV version

In your cluster, if the version of the TiDB component is v6.2.0 or later, the version of TiKV must be v6.2.0 or later.
