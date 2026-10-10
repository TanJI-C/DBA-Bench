# Administrative SQL statements overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-overview.md`
- Source Title: `SQL Statement Overview`
- Source Heading Path: `SQL Statement Overview > Administrative statements`
- Source Line Ranges: `83-123`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `administration`, `ddl`, `integrity-check`, `checksum`, `index-cleanup`, `ddl-jobs`, `session-variables`, `character-set`, `region-splitting`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0614_db5e923b85`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-overview.md#administrative-statements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6bd4520d89923e91116426e1613d9e22c8a0e897734a344fa1cf6c0962299e9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#administrative-statements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview of TiDB administrative SQL statements such as DDL job control, integrity checking, checksum, index cleanup, variable setting, character set setting, or Region splitting.
- Retrieval Keywords: Administrative statements, ADMIN CANCEL DDL, ADMIN CHECK TABLE, ADMIN CHECK INDEX, ADMIN CHECKSUM TABLE, ADMIN CLEANUP INDEX, ADMIN PAUSE DDL, ADMIN RECOVER INDEX, ADMIN RESUME DDL, ADMIN SHOW DDL JOBS, ADMIN SHOW DDL JOB QUERIES, ADMIN, FLUSH TABLES, MySQL compatibility, SET <variable>, SET NAMES, SET CHARACTER SET, SPLIT REGION
- Follow-up Guidance: The overview points to statement-specific pages for operations such as `ADMIN SHOW DDL [JOBS|JOB QUERIES]`, `SET [NAMES|CHARACTER SET]`, and `SPLIT REGION`.
- Classification Note: This chunk is a reference overview because it lists administrative SQL statements and gives a one-line description for each.

## Official Source Content

## Administrative statements

| SQL Statement | Description |
|---------------|-------------|
| [`ADMIN CANCEL DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) | Cancels a DDL job. |
| [`ADMIN CHECK [TABLE\|INDEX]`](/sql-statements/sql-statement-admin-check-table-index.md) | Checks the integrity of a table or index. |
| [`ADMIN CHECKSUM TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table) | Computes the checksum of a table. |
| [`ADMIN CLEANUP INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cleanup) | Cleans up indexes from a table. |
| [`ADMIN PAUSE DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl) | Pauses DDL operations. |
| [`ADMIN RESUME DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl) | Resumes DDL operations. |
| [`ADMIN SHOW DDL [JOBS\|JOB QUERIES]`](/sql-statements/sql-statement-admin-show-ddl.md) | Shows DDL jobs or job queries. |
| [`ADMIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin) | Performs various administrative tasks. |
| [`FLUSH TABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-tables) |  Included for [MySQL compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility). It has no effective usage in TiDB. |
| [`SET <variable>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable) | Modifies a system variable or user variable. |
| [`SET [NAMES\|CHARACTER SET]`](/sql-statements/sql-statement-set-names.md) | Set a character set and collation. |
| [`SPLIT REGION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region) | Splits a Region into smaller Regions. |

| SQL Statement | Description |
|---------------|-------------|
| [`ADMIN CANCEL DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) | Cancels a DDL job. |
| [`ADMIN CHECK [TABLE\|INDEX]`](/sql-statements/sql-statement-admin-check-table-index.md) | Checks the integrity of a table or index. |
| [`ADMIN CHECKSUM TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table) | Computes the checksum of a table. |
| [`ADMIN CLEANUP INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cleanup) | Cleans up indexes from a table. |
| [`ADMIN PAUSE DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl) | Pauses DDL operations. |
| [`ADMIN RECOVER INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-recover) | Recovers the consistency based on the redundant indexes. |
| [`ADMIN RESUME DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl) | Resumes DDL operations. |
| [`ADMIN SHOW DDL [JOBS\|JOB QUERIES]`](/sql-statements/sql-statement-admin-show-ddl.md) | Shows DDL jobs or job queries. |
| [`ADMIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin) | Performs various administrative tasks. |
| [`FLUSH TABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flush-tables) |  Included for [MySQL compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility). It has no effective usage in TiDB. |
| [`SET <variable>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable) | Modifies a system variable or user variable. |
| [`SET [NAMES\|CHARACTER SET]`](/sql-statements/sql-statement-set-names.md) | Set a character set and collation. |
| [`SPLIT REGION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region) | Splits a Region into smaller Regions. |
