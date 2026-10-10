# ADMIN SHOW DDL JOBS filters and JOB QUERIES usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-show-ddl.md`
- Source Title: `ADMIN SHOW DDL [JOBS|JOB QUERIES] | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN SHOW DDL [JOBS|JOB QUERIES] > Examples > `ADMIN SHOW DDL JOBS` | ADMIN SHOW DDL [JOBS|JOB QUERIES] > Examples > `ADMIN SHOW DDL JOB QUERIES``
- Source Line Ranges: `163-186`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `jobs`, `job-queries`, `sql-text`, `filters`, `history`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0513_45b80279e4`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-show-ddl.md#admin-show-ddl-jobs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `583af580ce2ef35cc2fcde62b5772843f20908fe89b5fe25981c7b1a876c0927`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl#admin-show-ddl-jobs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-show-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when you need the meaning of `NUM` and `WHERE` in `ADMIN SHOW DDL JOBS` or when looking up the original SQL text with `ADMIN SHOW DDL JOB QUERIES` for a specific `job_id`.
- Retrieval Keywords: ADMIN SHOW DDL JOB QUERIES, ADMIN SHOW DDL JOBS, NUM, WHERE, job_id, QUERY, CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY auto_increment), last ten results, DDL history job queue, running DDL job
- Follow-up Guidance: The source states that you can only search the running DDL job corresponding to `job_id` within the last ten results in the DDL history job queue.
- Classification Note: This is reference content because it specifies the filtering arguments for `ADMIN SHOW DDL JOBS` and documents the purpose, syntax, and lookup scope of `ADMIN SHOW DDL JOB QUERIES`.

## Official Source Content

* `NUM`: to view the last `NUM` results in the completed DDL job queue. If not specified, `NUM` is by default 10.
* `WHERE`: to add filter conditions.
### `ADMIN SHOW DDL JOB QUERIES`

To view the original SQL statements of the DDL job corresponding to `job_id`, use `ADMIN SHOW DDL JOB QUERIES`:

```sql
ADMIN SHOW DDL JOBS;
ADMIN SHOW DDL JOB QUERIES 51;
```

```sql
mysql> ADMIN SHOW DDL JOB QUERIES 51;
+--------------------------------------------------------------+
| QUERY                                                        |
+--------------------------------------------------------------+
| CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY auto_increment) |
+--------------------------------------------------------------+
1 row in set (0.02 sec)
```

You can only search the running DDL job corresponding to `job_id` within the last ten results in the DDL history job queue.
