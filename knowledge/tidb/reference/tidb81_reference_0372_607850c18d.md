# CLIENT_ERRORS_SUMMARY_GLOBAL table overview and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/client-errors-summary-global.md`
- Source Title: `CLIENT_ERRORS_SUMMARY_GLOBAL`
- Source Heading Path: `CLIENT_ERRORS_SUMMARY_GLOBAL`
- Source Line Ranges: `5-79`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `client_errors`, `sql_errors`, `warnings`, `error_summary`, `flush`, `mysql_protocol`, `in_memory`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0372_607850c18d`
- Source ID: `tidb-docs-8.1:information-schema/client-errors-summary-global.md#client-errors-summary-global`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `beb716b6496c8ad215c365f8e07feb51ea7eb53c019d3a54096a10795b471fab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/client-errors-summary-global#client-errors-summary-global
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/client-errors-summary-global.md

## Retrieval Guidance

- Use When: Use this when you need the INFORMATION_SCHEMA table that summarizes SQL errors and warnings returned to clients connected to a TiDB server.
- Retrieval Keywords: CLIENT_ERRORS_SUMMARY_GLOBAL, INFORMATION_SCHEMA.CLIENT_ERRORS_SUMMARY_GLOBAL, FLUSH CLIENT_ERRORS_SUMMARY, ERROR_NUMBER, ERROR_MESSAGE, ERROR_COUNT, WARNING_COUNT, FIRST_SEEN, LAST_SEEN, MySQL server protocol, Division by 0
- Follow-up Guidance: Use `USE INFORMATION_SCHEMA;` and `DESC CLIENT_ERRORS_SUMMARY_GLOBAL;` to inspect the table definition, or `SELECT * FROM CLIENT_ERRORS_SUMMARY_GLOBAL;` to view the summary.
- Classification Note: This is a reference table description for `CLIENT_ERRORS_SUMMARY_GLOBAL`, including its columns, reset statement, and example output.

## Official Source Content

# CLIENT_ERRORS_SUMMARY_GLOBAL

The table `CLIENT_ERRORS_SUMMARY_GLOBAL` provides a global summary of all SQL errors and warnings that have been returned to clients that connect to a TiDB server. These include:

* Malformed SQL statements.
* Division by zero errors.
* The attempt to insert out-of-range of duplicate key values.
* Permission errors.
* A table does not exist.

Client errors are returned to the client via the MySQL server protocol, where applications are expected to take appropriate action. The `INFORMATION_SCHEMA.CLIENT_ERRORS_SUMMARY_GLOBAL` table provides a high-level overview, and is useful in the scenario where applications are not correctly handling (or logging) errors returned by the TiDB server.

The summarized counts can be reset with the statement `FLUSH CLIENT_ERRORS_SUMMARY`. The summary is local to each TiDB server and is only retained in memory. Summaries will be lost if the TiDB server restarts.

```sql
USE INFORMATION_SCHEMA;
DESC CLIENT_ERRORS_SUMMARY_GLOBAL;
```

The output is as follows:

```sql
+---------------+---------------+------+------+---------+-------+
| Field         | Type          | Null | Key  | Default | Extra |
+---------------+---------------+------+------+---------+-------+
| ERROR_NUMBER  | bigint(64)    | NO   |      | NULL    |       |
| ERROR_MESSAGE | varchar(1024) | NO   |      | NULL    |       |
| ERROR_COUNT   | bigint(64)    | NO   |      | NULL    |       |
| WARNING_COUNT | bigint(64)    | NO   |      | NULL    |       |
| FIRST_SEEN    | timestamp     | YES  |      | NULL    |       |
| LAST_SEEN     | timestamp     | YES  |      | NULL    |       |
+---------------+---------------+------+------+---------+-------+
6 rows in set (0.00 sec)
```

Field description:

* `ERROR_NUMBER`: The MySQL-compatible error number that was returned.
* `ERROR_MESSAGE`: The error message which matches the error number (in prepared statement form).
* `ERROR_COUNT`: The number of times this error was returned.
* `WARNING_COUNT`: The number of times this warning was returned.
* `FIRST_SEEN`: The first time this error (or warning) was sent.
* `LAST_SEEN`: The most recent time this error (or warning) was sent.

The following example shows a warning being generated when connecting to a local TiDB server. The summary is reset after executing `FLUSH CLIENT_ERRORS_SUMMARY`:

```sql
SELECT 0/0;
SELECT * FROM CLIENT_ERRORS_SUMMARY_GLOBAL;
FLUSH CLIENT_ERRORS_SUMMARY;
SELECT * FROM CLIENT_ERRORS_SUMMARY_GLOBAL;
```

The output is as follows:

```sql
+-----+
| 0/0 |
+-----+
| NULL |
+-----+
1 row in set, 1 warning (0.00 sec)

+--------------+---------------+-------------+---------------+---------------------+---------------------+
| ERROR_NUMBER | ERROR_MESSAGE | ERROR_COUNT | WARNING_COUNT | FIRST_SEEN          | LAST_SEEN           |
+--------------+---------------+-------------+---------------+---------------------+---------------------+
|         1365 | Division by 0 |           0 |             1 | 2021-03-18 13:10:51 | 2021-03-18 13:10:51 |
+--------------+---------------+-------------+---------------+---------------------+---------------------+
1 row in set (0.00 sec)

Query OK, 0 rows affected (0.00 sec)

Empty set (0.00 sec)
```
