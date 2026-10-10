# CLIENT_ERRORS_SUMMARY_BY_USER table definition and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/client-errors-summary-by-user.md`
- Source Title: `CLIENT_ERRORS_SUMMARY_BY_USER`
- Source Heading Path: `CLIENT_ERRORS_SUMMARY_BY_USER`
- Source Line Ranges: `5-87`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `information_schema`, `client-errors`, `warnings`, `per-user-summary`, `flush`, `schema-reference`, `error-counts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0371_9f7c41cdf6`
- Source ID: `tidb-docs-8.1:information-schema/client-errors-summary-by-user.md#client-errors-summary-by-user`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e785b0f025a50497e9a52addf39241b4cbef5eccc43db619c928dc997cc35222`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/client-errors-summary-by-user#client-errors-summary-by-user
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/client-errors-summary-by-user.md

## Retrieval Guidance

- Use When: Use this chunk when you need the schema, purpose, or reset behavior of INFORMATION_SCHEMA.CLIENT_ERRORS_SUMMARY_BY_USER for inspecting SQL errors and warnings returned to clients on a per-user basis.
- Retrieval Keywords: INFORMATION_SCHEMA.CLIENT_ERRORS_SUMMARY_BY_USER, CLIENT_ERRORS_SUMMARY_BY_USER, FLUSH CLIENT_ERRORS_SUMMARY, DESC CLIENT_ERRORS_SUMMARY_BY_USER, USER, ERROR_NUMBER, ERROR_MESSAGE, ERROR_COUNT, WARNING_COUNT, FIRST_SEEN, LAST_SEEN, client errors summary by user, per-user SQL errors and warnings, Division by 0, Malformed SQL statements, duplicate key values, Permission errors, table does not exist
- Follow-up Guidance: The content also shows an example using SELECT 0/0, querying CLIENT_ERRORS_SUMMARY_BY_USER, and then resetting the summary with FLUSH CLIENT_ERRORS_SUMMARY.
- Classification Note: This is reference content because it defines the CLIENT_ERRORS_SUMMARY_BY_USER table, lists its columns and meanings, and documents its in-memory local summary behavior and reset statement.

## Official Source Content

# CLIENT_ERRORS_SUMMARY_BY_USER

The table `CLIENT_ERRORS_SUMMARY_BY_USER` provides a summary of SQL errors and warnings that have been returned to clients that connect to a TiDB server. These include:

* Malformed SQL statements.
* Division by zero errors.
* The attempt to insert out-of-range or duplicate key values.
* Permission errors.
* A table that does not exist.

Client errors are returned to the client via the MySQL server protocol, where applications are expected to take appropriate action. The `INFORMATION_SCHEMA.CLIENT_ERRORS_SUMMARY_BY_USER` table provides a useful method to inspect errors in the scenario where applications are not correctly handling (or logging) errors returned by the TiDB server.

Because `CLIENT_ERRORS_SUMMARY_BY_USER` summarizes the errors on a per-user basis, it can be useful to diagnose scenarios where one user server is generating more errors than other servers. Possible scenarios include:

* Permission errors.
* Missing tables, or relational objects.
* Incorrect SQL syntax, or incompatibilities between the application and the version of TiDB.

The summarized counts can be reset with the statement `FLUSH CLIENT_ERRORS_SUMMARY`. The summary is local to each TiDB server and is only retained in memory. Summaries will be lost if the TiDB server restarts.

```sql
USE INFORMATION_SCHEMA;
DESC CLIENT_ERRORS_SUMMARY_BY_USER;
```

The output is as follows:

```sql
+---------------+---------------+------+------+---------+-------+
| Field         | Type          | Null | Key  | Default | Extra |
+---------------+---------------+------+------+---------+-------+
| USER          | varchar(64)   | NO   |      | NULL    |       |
| ERROR_NUMBER  | bigint(64)    | NO   |      | NULL    |       |
| ERROR_MESSAGE | varchar(1024) | NO   |      | NULL    |       |
| ERROR_COUNT   | bigint(64)    | NO   |      | NULL    |       |
| WARNING_COUNT | bigint(64)    | NO   |      | NULL    |       |
| FIRST_SEEN    | timestamp     | YES  |      | NULL    |       |
| LAST_SEEN     | timestamp     | YES  |      | NULL    |       |
+---------------+---------------+------+------+---------+-------+
7 rows in set (0.00 sec)
```

Field description:

* `USER`: The authenticated user.
* `ERROR_NUMBER`: The MySQL-compatible error number that was returned.
* `ERROR_MESSAGE`: The error message which matches the error number (in prepared statement form).
* `ERROR_COUNT`: The number of times this error was returned to the user.
* `WARNING_COUNT`: The number of times this warning was returned to the user.
* `FIRST_SEEN`: The first time this error (or warning) was sent to the user.
* `LAST_SEEN`: The most recent time this error (or warning) was sent to the user.

The following example shows a warning being generated when the client connects to a local TiDB server. The summary is reset after executing `FLUSH CLIENT_ERRORS_SUMMARY`:

```sql
SELECT 0/0;
SELECT * FROM CLIENT_ERRORS_SUMMARY_BY_USER;
FLUSH CLIENT_ERRORS_SUMMARY;
SELECT * FROM CLIENT_ERRORS_SUMMARY_BY_USER;
```

The output is as follows:

```sql
+-----+
| 0/0 |
+-----+
| NULL |
+-----+
1 row in set, 1 warning (0.00 sec)

+------+--------------+---------------+-------------+---------------+---------------------+---------------------+
| USER | ERROR_NUMBER | ERROR_MESSAGE | ERROR_COUNT | WARNING_COUNT | FIRST_SEEN          | LAST_SEEN           |
+------+--------------+---------------+-------------+---------------+---------------------+---------------------+
| root |         1365 | Division by 0 |           0 |             1 | 2021-03-18 13:05:36 | 2021-03-18 13:05:36 |
+------+--------------+---------------+-------------+---------------+---------------------+---------------------+
1 row in set (0.00 sec)

Query OK, 0 rows affected (0.00 sec)

Empty set (0.00 sec)
```
