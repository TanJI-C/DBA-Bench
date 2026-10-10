# Identify problematic SQL statements with ADMIN SHOW SLOW

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/identify-slow-queries.md`
- Source Title: `Identify Slow Queries`
- Source Heading Path: `Identify Slow Queries > Identify problematic SQL statements | Identify Slow Queries > Identify problematic SQL statements > `ADMIN SHOW SLOW` command`
- Source Line Ranges: `570-623`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `slow-query`, `problematic-sql`, `process-time`, `wait-time`, `admin-show-slow`, `recent`, `top`, `internal-sql`, `memory-limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0049_3bf227e4f2`
- Source ID: `tidb-docs-8.1:identify-slow-queries.md#identify-problematic-sql-statements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `debe8ef682d565005ce6f570586e1ed2d15b66d5838ac3feb6c04a1f0cdb1a0d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/identify-slow-queries#identify-problematic-sql-statements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/identify-slow-queries.md

## Retrieval Guidance

- Use When: Use this chunk when you need to identify problematic SQL statements with `ADMIN SHOW SLOW` and distinguish large `process_time` from large `wait_time` when reviewing recent or top slow queries.
- Retrieval Keywords: ADMIN SHOW SLOW, ADMIN SHOW SLOW recent N, ADMIN SHOW SLOW TOP [internal | all] N, ADMIN SHOW SLOW recent 10, ADMIN SHOW SLOW top 3, ADMIN SHOW SLOW top internal 3, ADMIN SHOW SLOW top all 5, process_time, wait_time, problematic SQL statements, internal SQL, slow query records, limited memory, digest, conn_id, transaction_ts, table_ids, index_ids
- Follow-up Guidance: The content explains the output columns of `ADMIN SHOW SLOW`, including `start`, `duration`, `details`, `succ`, `conn_id`, `transaction_ts`, `user`, `db`, `table_ids`, `index_ids`, `internal`, `digest`, and `sql`.
- Classification Note: This is classified as diagnosis for TiDB because the official content focuses on identifying and interpreting slow query records using `ADMIN SHOW SLOW`.

## Official Source Content

## Identify problematic SQL statements

Not all of the `SLOW_QUERY` statements are problematic. Only those whose `process_time` is very large increase the pressure on the entire cluster.

The statements whose `wait_time` is very large and `process_time` is very small are usually not problematic. This is because the statement is blocked by real problematic statements and it has to wait in the execution queue, which leads to a much longer response time.
### `ADMIN SHOW SLOW` command

In addition to the TiDB log file, you can identify slow queries by running the `ADMIN SHOW SLOW` command:

```sql
ADMIN SHOW SLOW recent N
ADMIN SHOW SLOW TOP [internal | all] N
```

`recent N` shows the recent N slow query records, for example:

```sql
ADMIN SHOW SLOW recent 10
```

`top N` shows the slowest N query records recently (within a few days). If the `internal` option is provided, the returned results would be the inner SQL executed by the system; If the `all` option is provided, the returned results would be the user's SQL combined with inner SQL; Otherwise, this command would only return the slow query records from the user's SQL.

```sql
ADMIN SHOW SLOW top 3
ADMIN SHOW SLOW top internal 3
ADMIN SHOW SLOW top all 5
```

TiDB stores only a limited number of slow query records because of the limited memory. If the value of `N` in the query command is greater than the records count, the number of returned records is smaller than `N`.

The following table shows output details:

| Column name | Description |
|:------|:---- |
| start | The starting time of the SQL execution |
| duration | The duration of the SQL execution |
| details | The details of the SQL execution |
| succ | Whether the SQL statement is executed successfully. `1` means success and `0` means failure. |
| conn_id | The connection ID for the session |
| transaction_ts | The `start ts` of the transaction |
| user | The user name for the execution of the statement |
| db | The database involved when the statement is executed |
| table_ids | The ID of the table involved when the SQL statement is executed |
| index_ids | The ID of the index involved when the SQL statement is executed |
| internal | This is a TiDB internal SQL statement |
| digest | The fingerprint of the SQL statement |
| sql | The SQL statement that is being executed or has been executed |
