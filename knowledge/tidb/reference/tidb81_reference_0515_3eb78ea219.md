# ADMIN overview and DDL-related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin.md`
- Source Title: `ADMIN | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN | ADMIN > DDL related statement`
- Source Line Ranges: `5-42`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `admin`, `ddl`, `checksum`, `consistency-check`, `job-control`, `statement-reference`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0515_3eb78ea219`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin.md#admin`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1cf25c9881408196cf8f61f66aedcfc816f3578642b1c1f0252af1332c837cc1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin#admin
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the ADMIN statement overview or the list of DDL-related ADMIN statements and their purposes.
- Retrieval Keywords: ADMIN, DDL related statement, ADMIN CANCEL DDL JOBS, ADMIN PAUSE DDL JOBS, ADMIN RESUME DDL JOBS, ADMIN CHECKSUM TABLE, ADMIN CHECK TABLE, ADMIN CHECK INDEX, ADMIN SHOW DDL JOBS, ADMIN SHOW DDL QUERIES, CRC64 of all rows + indexes, consistency of a table or index
- Follow-up Guidance: The source points to dedicated statement pages for ADMIN CANCEL DDL JOBS, ADMIN PAUSE DDL JOBS, ADMIN RESUME DDL JOBS, ADMIN CHECKSUM TABLE, ADMIN CHECK [TABLE|INDEX], and ADMIN SHOW DDL [JOBS|QUERIES].
- Classification Note: This is reference content because it summarizes ADMIN extension syntax and catalogs DDL-related SQL statements with short descriptions.

## Official Source Content

# ADMIN

This statement is a TiDB extension syntax, used to view the status of TiDB and check the data of tables in TiDB. This document introduces the following `ADMIN` related statements:

- [`ADMIN RELOAD`](#admin-reload-statement)
- [`ADMIN PLUGINS`](#admin-plugins-related-statement)
- [`ADMIN ... BINDINGS`](#admin-bindings-related-statement)
- [`ADMIN REPAIR`](#admin-repair-statement)
- [`ADMIN SHOW NEXT_ROW_ID`](#admin-show-next_row_id-statement)
- [`ADMIN SHOW SLOW`](#admin-show-slow-statement)
## DDL related statement

| Statement                                                                                | Description                 |
|------------------------------------------------------------------------------------------|-----------------------------|
| [`ADMIN CANCEL DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl)             | Cancels the currently running DDL jobs. |
| [`ADMIN PAUSE DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl)               | Pauses the currently running DDL jobs. |
| [`ADMIN RESUME DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl)             | Resumes the paused DDL jobs. |
| [`ADMIN CHECKSUM TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table)          | Calculates the CRC64 of all rows + indexes of a table. |
| [<code>ADMIN CHECK [TABLE\|INDEX]</code>](/sql-statements/sql-statement-admin-check-table-index.md) | Checks for consistency of a table or index. |
| [<code>ADMIN SHOW DDL [JOBS\|QUERIES]</code>](/sql-statements/sql-statement-admin-show-ddl.md)      | Shows details about currently running or recently completed DDL jobs. |

| Statement                                                                                | Description                 |
|------------------------------------------------------------------------------------------|-----------------------------|
| [`ADMIN CANCEL DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl)             | Cancels a currently running DDL jobs. |
| [`ADMIN CHECKSUM TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table)          | Calculates the CRC64 of all rows + indexes of a table. |
| [<code>ADMIN CHECK [TABLE\|INDEX]</code>](/sql-statements/sql-statement-admin-check-table-index.md) | Checks for consistency of a table or index. |
| [<code>ADMIN SHOW DDL [JOBS\|QUERIES]</code>](/sql-statements/sql-statement-admin-show-ddl.md)      | Shows details about currently running or recently completed DDL jobs. |
