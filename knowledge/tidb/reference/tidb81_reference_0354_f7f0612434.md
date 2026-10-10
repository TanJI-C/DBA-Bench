# SQL digest encode and decode functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/tidb-functions.md`
- Source Title: `TiDB Specific Functions`
- Source Heading Path: `TiDB Specific Functions > TIDB_DECODE_SQL_DIGESTS | TiDB Specific Functions > TIDB_ENCODE_SQL_DIGEST`
- Source Line Ranges: `289-373`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `sql-digest`, `normalized-sql`, `statement-summary`, `process-privilege`, `truncation`, `function-overhead`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0354_f7f0612434`
- Source ID: `tidb-docs-8.1:functions-and-operators/tidb-functions.md#tidb-decode-sql-digests`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e85f151e4b5a9ae41f59fee4c3af403816f7e18c0a4e2e23fe77e2f4d0d84d25`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb-decode-sql-digests
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/tidb-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how to convert between SQL digests and normalized SQL statements, including JSON array input or output, truncation behavior, PROCESS privilege requirements, and statement summary table lookup limits.
- Retrieval Keywords: TIDB_DECODE_SQL_DIGESTS, TIDB_ENCODE_SQL_DIGEST, SQL digest, normalized SQL statements, JSON string array, stmtTruncateLength, PROCESS privilege, statement summary tables, STATEMENTS_SUMMARY, STATEMENTS_SUMMARY_HISTORY, CLUSTER_STATEMENTS_SUMMARY, CLUSTER_STATEMENTS_SUMMARY_HISTORY, high overhead, no vectorization, null for missing digest, TIDB_TRX, cluster_tidb_trx
- Follow-up Guidance: The source also points to Statement Summary Tables and INFORMATION_SCHEMA.TIDB_TRX for related context about where decoded statements come from and example usage.
- Classification Note: This is a reference chunk because it defines the behavior, arguments, return values, privilege note, and examples for the SQL functions TIDB_DECODE_SQL_DIGESTS and TIDB_ENCODE_SQL_DIGEST.

## Official Source Content

## TIDB_DECODE_SQL_DIGESTS

The `TIDB_DECODE_SQL_DIGESTS()` function is used to query the normalized SQL statements (a form without formats and arguments) corresponding to the set of SQL digests in the cluster. This function accepts 1 or 2 arguments:

* `digests`: A string. This parameter is in the format of a JSON string array, and each string in the array is a SQL digest.
* `stmtTruncateLength`: An integer (optional). It is used to limit the length of each SQL statement in the returned result. If a SQL statement exceeds the specified length, the statement is truncated. `0` means that the length is unlimited.

This function returns a string, which is in the format of a JSON string array. The *i*-th item in the array is the normalized SQL statement corresponding to the *i*-th element in the `digests` parameter. If an element in the `digests` parameter is not a valid SQL digest or the system cannot find the corresponding SQL statement, the corresponding item in the returned result is `null`. If the truncation length is specified (`stmtTruncateLength > 0`), for each statement in the returned result that exceeds this length, the first `stmtTruncateLength` characters are retained and the suffix `"..."` is added at the end to indicate the truncation. If the `digests` parameter is `NULL`, the returned value of the function is `NULL`.

> **Note:**
>
> * Only users with the [PROCESS](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html#priv_process) privilege can use this function.
> * When `TIDB_DECODE_SQL_DIGESTS` is executed, TiDB queries the statement corresponding to each SQL digest from the statement summary tables, so there is no guarantee that the corresponding statement can always be found for any SQL digest. Only the statements that have been executed in the cluster can be found, and whether these SQL statements can be queried or not is also affected by the related configuration of the statement summary tables. For the detailed description of the statement summary table, see [Statement Summary Tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables).
> * This function has a high overhead. In queries with a large number of rows (for example, querying the full table of `information_schema.cluster_tidb_trx` on a large and busy cluster), using this function might cause the queries to run for too long. Use it with caution.
>     * This function has a high overhead because every time it is called, it internally queries the `STATEMENTS_SUMMARY`, `STATEMENTS_SUMMARY_HISTORY`, `CLUSTER_STATEMENTS_SUMMARY`, and `CLUSTER_STATEMENTS_SUMMARY_HISTORY` tables, and the query involves the `UNION` operation. This function currently does not support vectorization, that is, when calling this function for multiple rows of data, the above query is performed separately for each row.

```sql
SET @digests = '["e6f07d43b5c21db0fbb9a31feac2dc599787763393dd5acbfad80e247eb02ad5","38b03afa5debbdf0326a014dbe5012a62c51957f1982b3093e748460f8b00821","e5796985ccafe2f71126ed6c0ac939ffa015a8c0744a24b7aee6d587103fd2f7"]';

SELECT TIDB_DECODE_SQL_DIGESTS(@digests);
```

```sql
+------------------------------------+
| TIDB_DECODE_SQL_DIGESTS(@digests)  |
+------------------------------------+
| ["begin",null,"select * from `t`"] |
+------------------------------------+
1 row in set (0.00 sec)
```

In the above example, the parameter is a JSON array containing 3 SQL digests, and the corresponding SQL statements are the three items in the query results. But the SQL statement corresponding to the second SQL digest cannot be found from the cluster, so the second item in the result is `null`.

```sql
SELECT TIDB_DECODE_SQL_DIGESTS(@digests, 10);
```

```sql
+---------------------------------------+
| TIDB_DECODE_SQL_DIGESTS(@digests, 10) |
+---------------------------------------+
| ["begin",null,"select * f..."]        |
+---------------------------------------+
1 row in set (0.01 sec)
```

The above call specifies the second parameter (that is, the truncation length) as 10, and the length of the third statement in the query result is greater than 10. Therefore, only the first 10 characters are retained, and `"..."` is added at the end, which indicates the truncation.

See also:

- [Statement summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables)
- [`INFORMATION_SCHEMA.TIDB_TRX`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-trx)
## TIDB_ENCODE_SQL_DIGEST

The `TIDB_ENCODE_SQL_DIGEST(query_str)` returns the SQL digest for a query string.

In the following example you can see that both queries get the same query digest, which is because the digest will be `select ?` for both of them.

```sql
SELECT TIDB_ENCODE_SQL_DIGEST('SELECT 1');
```

```
+------------------------------------------------------------------+
| TIDB_ENCODE_SQL_DIGEST('SELECT 1')                               |
+------------------------------------------------------------------+
| e1c71d1661ae46e09b7aaec1c390957f0d6260410df4e4bc71b9c8d681021471 |
+------------------------------------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT TIDB_ENCODE_SQL_DIGEST('SELECT 2');
```

```
+------------------------------------------------------------------+
| TIDB_ENCODE_SQL_DIGEST('SELECT 2')                               |
+------------------------------------------------------------------+
| e1c71d1661ae46e09b7aaec1c390957f0d6260410df4e4bc71b9c8d681021471 |
+------------------------------------------------------------------+
1 row in set (0.00 sec)
```
