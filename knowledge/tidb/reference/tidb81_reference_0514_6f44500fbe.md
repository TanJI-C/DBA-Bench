# ADMIN SHOW DDL JOB QUERIES range examples and references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-show-ddl.md`
- Source Title: `ADMIN SHOW DDL [JOBS|JOB QUERIES] | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN SHOW DDL [JOBS|JOB QUERIES] > Examples > `ADMIN SHOW DDL JOB QUERIES LIMIT m OFFSET n` | ADMIN SHOW DDL [JOBS|JOB QUERIES] > MySQL compatibility | ADMIN SHOW DDL [JOBS|JOB QUERIES] > See also`
- Source Line Ranges: `187-246`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ddl`, `admin`, `job-queries`, `limit`, `offset`, `mysql-compatibility`, `examples`, `history-queue`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0514_6f44500fbe`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-show-ddl.md#admin-show-ddl-job-queries-limit-m-offset-n`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ecee9b4575bf6fc3377da86f0b0d70c86d2bd79d242e111f2261d70e94ea55a4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl#admin-show-ddl-job-queries-limit-m-offset-n
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-show-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax and examples for retrieving original SQL statements of DDL jobs from a specified range in the DDL history job queue with `ADMIN SHOW DDL JOB QUERIES LIMIT` and `OFFSET`.
- Retrieval Keywords: ADMIN SHOW DDL JOB QUERIES, ADMIN SHOW DDL JOB QUERIES LIMIT m OFFSET n, ADMIN SHOW DDL JOB QUERIES LIMIT n, m, JOB_ID, QUERY, DDL history job queue, Retrieve rows [n+1, n+m], last ten results, TiDB extension to MySQL syntax, INFORMATION_SCHEMA.DDL_JOBS
- Follow-up Guidance: The see also section references DDL introduction, `ADMIN CANCEL DDL`, `ADMIN PAUSE DDL`, `ADMIN RESUME DDL`, and `INFORMATION_SCHEMA.DDL_JOBS`.
- Classification Note: This is reference content because it defines the exact SQL syntax, parameter range rules for `n` and `m`, result-range behavior, and concrete output examples for `ADMIN SHOW DDL JOB QUERIES`.

## Official Source Content

### `ADMIN SHOW DDL JOB QUERIES LIMIT m OFFSET n`

 To view the original SQL statements of the DDL job within a specified range `[n+1, n+m]` corresponding to `job_id`, use `ADMIN SHOW DDL JOB QUERIES LIMIT m OFFSET n`:

```sql
 ADMIN SHOW DDL JOB QUERIES LIMIT m;  # Retrieve first m rows
 ADMIN SHOW DDL JOB QUERIES LIMIT n, m;  # Retrieve rows [n+1, n+m]
 ADMIN SHOW DDL JOB QUERIES LIMIT m OFFSET n;  # Retrieve rows [n+1, n+m]
 ```

 where `n` and `m` are integers greater or equal to 0.

 ```sql
 ADMIN SHOW DDL JOB QUERIES LIMIT 3;  # Retrieve first 3 rows
 +--------+--------------------------------------------------------------+
 | JOB_ID | QUERY                                                        |
 +--------+--------------------------------------------------------------+
 |     59 | ALTER TABLE t1 ADD INDEX index2 (col2)                       |
 |     60 | ALTER TABLE t2 ADD INDEX index1 (col1)                       |
 |     58 | CREATE TABLE t2 (id INT NOT NULL PRIMARY KEY auto_increment) |
 +--------+--------------------------------------------------------------+
 3 rows in set (0.00 sec)
 ```

 ```sql
 ADMIN SHOW DDL JOB QUERIES LIMIT 6, 2;  # Retrieve rows 7-8
 +--------+----------------------------------------------------------------------------+
 | JOB_ID | QUERY                                                                      |
 +--------+----------------------------------------------------------------------------+
 |     52 | ALTER TABLE t1 ADD INDEX index1 (col1)                                     |
 |     51 | CREATE TABLE IF NOT EXISTS t1 (id INT NOT NULL PRIMARY KEY auto_increment) |
 +--------+----------------------------------------------------------------------------+
 3 rows in set (0.00 sec)
 ```

 ```sql
 ADMIN SHOW DDL JOB QUERIES LIMIT 3 OFFSET 4;  # Retrieve rows 5-7
 +--------+----------------------------------------+
 | JOB_ID | QUERY                                  |
 +--------+----------------------------------------+
 |     54 | DROP TABLE IF EXISTS t3                |
 |     53 | ALTER TABLE t1 DROP INDEX index1       |
 |     52 | ALTER TABLE t1 ADD INDEX index1 (col1) |
 +--------+----------------------------------------+
 3 rows in set (0.00 sec)
 ```

 You can search the running DDL job corresponding to `job_id` within an arbitrarily specified range of results in the DDL history job queue. This syntax does not have the limitation of the last ten results of `ADMIN SHOW DDL JOB QUERIES`.
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [DDL introduction](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction)
* [ADMIN CANCEL DDL](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl)
* [ADMIN PAUSE DDL](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-pause-ddl)
* [ADMIN RESUME DDL](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-resume-ddl)
* [INFORMATION_SCHEMA.DDL_JOBS](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-ddl-jobs)
