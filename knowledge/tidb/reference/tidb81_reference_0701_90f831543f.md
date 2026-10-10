# Statement summary field reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statement-summary-tables.md`
- Source Title: `Statement Summary Tables`
- Source Heading Path: `Statement Summary Tables > Fields description | Statement Summary Tables > Fields description > `statements_summary` fields description | Statement Summary Tables > Fields description > `statements_summary_evicted` fields description`
- Source Line Ranges: `325-431`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `sql`
- Topic Tags: `statement-summary`, `fields`, `schema`, `latency-metrics`, `coprocessor`, `transactions`, `resource-control`, `eviction`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0701_90f831543f`
- Source ID: `tidb-docs-8.1:statement-summary-tables.md#fields-description`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `637220519f66b549f1d8a5d184785cf45c1e79f1d744774c92afe6ab08de95d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statement-summary-tables#fields-description
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statement-summary-tables.md

## Retrieval Guidance

- Use When: Use this chunk when you need the field meanings for statements_summary or statements_summary_evicted columns while interpreting statement summary data.
- Retrieval Keywords: statements_summary fields description, statements_summary_evicted fields description, DIGEST_TEXT, QUERY_SAMPLE_TEXT, PLAN_DIGEST, BINARY_PLAN, SELECT tidb_decode_binary_plan('xxx...'), PLAN_CACHE_HITS, PLAN_IN_CACHE, SUMMARY_BEGIN_TIME, EXEC_COUNT, SUM_LATENCY, AVG_LATENCY, SUM_COP_TASK_NUM, MAX_COP_PROCESS_ADDRESS, AVG_PROCESSED_KEYS, AVG_PREWRITE_TIME, AVG_COMMIT_TIME, BACKOFF_TYPES, PREV_SAMPLE_TEXT, AVG_REQUEST_UNIT_WRITE, AVG_QUEUED_RC_TIME, RESOURCE_GROUP, EVICTED_COUNT
- Follow-up Guidance: The source includes that BINARY_PLAN can be parsed by executing SELECT tidb_decode_binary_plan('xxx...').
- Classification Note: This is classified as reference because it enumerates and defines the columns in the statements_summary and statements_summary_evicted tables, including latency, Coprocessor, transaction, Resource Control, and eviction fields.

## Official Source Content

## Fields description
### `statements_summary` fields description

The following are descriptions of fields in the `statements_summary` table.

Basic fields:

- `STMT_TYPE`: SQL statement type.
- `SCHEMA_NAME`: The current schema in which SQL statements of this category are executed.
- `DIGEST`: The digest of SQL statements of this category.
- `DIGEST_TEXT`: The normalized SQL statement.
- `QUERY_SAMPLE_TEXT`: The original SQL statements of the SQL category. Only one original statement is taken.
- `TABLE_NAMES`: All tables involved in SQL statements. If there is more than one table, each is separated by a comma.
- `INDEX_NAMES`: All SQL indexes used in SQL statements. If there is more than one index, each is separated by a comma.
- `SAMPLE_USER`: The users who execute SQL statements of this category. Only one user is taken.
- `PLAN_DIGEST`: The digest of the execution plan.
- `PLAN`: The original execution plan. If there are multiple statements, the plan of only one statement is taken.
- `BINARY_PLAN`: The original execution plan encoded in binary format. If there are multiple statements, the plan of only one statement is taken. Execute the [`SELECT tidb_decode_binary_plan('xxx...')`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_decode_binary_plan) statement to parse the specific execution plan.
- `PLAN_CACHE_HITS`: The total number of times that SQL statements of this category hit the plan cache.
- `PLAN_IN_CACHE`: Indicates whether the previous execution of SQL statements of this category hit the plan cache.

Fields related to execution time:

- `SUMMARY_BEGIN_TIME`: The beginning time of the current summary period.
- `SUMMARY_END_TIME`: The ending time of the current summary period.
- `FIRST_SEEN`: The time when SQL statements of this category are seen for the first time.
- `LAST_SEEN`: The time when SQL statements of this category are seen for the last time.

Fields related to TiDB server:

- `EXEC_COUNT`: Total execution times of SQL statements of this category.
- `SUM_ERRORS`: The sum of errors occurred during execution.
- `SUM_WARNINGS`: The sum of warnings occurred during execution.
- `SUM_LATENCY`: The total execution latency of SQL statements of this category.
- `MAX_LATENCY`: The maximum execution latency of SQL statements of this category.
- `MIN_LATENCY`: The minimum execution latency of SQL statements of this category.
- `AVG_LATENCY`: The average execution latency of SQL statements of this category.
- `AVG_PARSE_LATENCY`: The average latency of the parser.
- `MAX_PARSE_LATENCY`: The maximum latency of the parser.
- `AVG_COMPILE_LATENCY`: The average latency of the compiler.
- `MAX_COMPILE_LATENCY`: The maximum latency of the compiler.
- `AVG_MEM`: The average memory (byte) used.
- `MAX_MEM`: The maximum memory (byte) used.
- `AVG_DISK`: The average disk space (byte) used.
- `MAX_DISK`: The maximum disk space (byte) used.

Fields related to TiKV Coprocessor task:

- `SUM_COP_TASK_NUM`: The total number of Coprocessor requests sent.
- `MAX_COP_PROCESS_TIME`: The maximum execution time of Coprocessor tasks.
- `MAX_COP_PROCESS_ADDRESS`: The address of the Coprocessor task with the maximum execution time.
- `MAX_COP_WAIT_TIME`: The maximum waiting time of Coprocessor tasks.
- `MAX_COP_WAIT_ADDRESS`: The address of the Coprocessor task with the maximum waiting time.
- `AVG_PROCESS_TIME`: The average processing time of SQL statements in TiKV.
- `MAX_PROCESS_TIME`: The maximum processing time of SQL statements in TiKV.
- `AVG_WAIT_TIME`: The average waiting time of SQL statements in TiKV.
- `MAX_WAIT_TIME`: The maximum waiting time of SQL statements in TiKV.
- `AVG_BACKOFF_TIME`: The average waiting time before retry when a SQL statement encounters an error that requires a retry.
- `MAX_BACKOFF_TIME`: The maximum waiting time before retry when a SQL statement encounters an error that requires a retry.
- `AVG_TOTAL_KEYS`: The average number of keys that Coprocessor has scanned.
- `MAX_TOTAL_KEYS`: The maximum number of keys that Coprocessor has scanned.
- `AVG_PROCESSED_KEYS`: The average number of keys that Coprocessor has processed. Compared with `avg_total_keys`, `avg_processed_keys` does not include the old versions of MVCC. A great difference between `avg_total_keys` and `avg_processed_keys` indicates that many old versions exist.
- `MAX_PROCESSED_KEYS`: The maximum number of keys that Coprocessor has processed.

Transaction-related fields:

- `AVG_PREWRITE_TIME`: The average time of the prewrite phase.
- `MAX_PREWRITE_TIME`: The longest time of the prewrite phase.
- `AVG_COMMIT_TIME`: The average time of the commit phase.
- `MAX_COMMIT_TIME`: The longest time of the commit phase.
- `AVG_GET_COMMIT_TS_TIME`: The average time of getting `commit_ts`.
- `MAX_GET_COMMIT_TS_TIME`: The longest time of getting `commit_ts`.
- `AVG_COMMIT_BACKOFF_TIME`: The average waiting time before retry when a SQL statement encounters an error that requires a retry during the commit phase.
- `MAX_COMMIT_BACKOFF_TIME`: The maximum waiting time before retry when a SQL statement encounters an error that requires a retry during the commit phase.
- `AVG_RESOLVE_LOCK_TIME`: The average time for resolving lock conflicts occurred between transactions.
- `MAX_RESOLVE_LOCK_TIME`: The longest time for resolving lock conflicts occurred between transactions.
- `AVG_LOCAL_LATCH_WAIT_TIME`: The average waiting time of the local transaction.
- `MAX_LOCAL_LATCH_WAIT_TIME`: The maximum waiting time of the local transaction.
- `AVG_WRITE_KEYS`: The average count of written keys.
- `MAX_WRITE_KEYS`: The maximum count of written keys.
- `AVG_WRITE_SIZE`: The average amount of written data (in byte).
- `MAX_WRITE_SIZE`: The maximum amount of written data (in byte).
- `AVG_PREWRITE_REGIONS`: The average number of Regions involved in the prewrite phase.
- `MAX_PREWRITE_REGIONS`: The maximum number of Regions during the prewrite phase.
- `AVG_TXN_RETRY`: The average number of transaction retries.
- `MAX_TXN_RETRY`: The maximum number of transaction retries.
- `SUM_BACKOFF_TIMES`: The sum of retries when SQL statements of this category encounter errors that require a retry.
- `BACKOFF_TYPES`: All types of errors that require retries and the number of retries for each type. The format of the field is `type:number`. If there is more than one error type, each is separated by a comma, like `txnLock:2,pdRPC:1`.
- `AVG_AFFECTED_ROWS`: The average number of rows affected.
- `PREV_SAMPLE_TEXT`: When the current SQL statement is `COMMIT`, `PREV_SAMPLE_TEXT` is the previous statement to `COMMIT`. In this case, SQL statements are grouped by the digest and `prev_sample_text`. This means that `COMMIT` statements with different `prev_sample_text` are grouped to different rows. When the current SQL statement is not `COMMIT`, the `PREV_SAMPLE_TEXT` field is an empty string.

Fields related to Resource Control:

- `AVG_REQUEST_UNIT_WRITE`: the average number of write RUs consumed by SQL statements.
- `MAX_REQUEST_UNIT_WRITE`: the maximum number of write RUs consumed by SQL statements.
- `AVG_REQUEST_UNIT_READ`: the average number of read RUs consumed by SQL statements.
- `MAX_REQUEST_UNIT_READ`: the maximum number of read RUs consumed by SQL statements.
- `AVG_QUEUED_RC_TIME`: the average waiting time for available RU when executing SQL statements.
- `MAX_QUEUED_RC_TIME`: the maximum waiting time for available RU when executing SQL statements.
- `RESOURCE_GROUP`: the resource group bound to SQL statements.
### `statements_summary_evicted` fields description

- `BEGIN_TIME`: Records the starting time.
- `END_TIME`: Records the ending time.
- `EVICTED_COUNT`: The number of SQL categories that are evicted during the record period.
