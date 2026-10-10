# MEMORY_USAGE system table schema, example query, and related links

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-memory-usage.md`
- Source Title: `MEMORY_USAGE`
- Source Heading Path: `MEMORY_USAGE | MEMORY_USAGE > See also`
- Source Line Ranges: `5-77`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `information_schema`, `memory_usage`, `memory`, `system-table`, `schema`, `sql`, `session-kill`, `gc`, `disk-spill`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0396_e0976227d7`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-memory-usage.md#memory-usage`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `42248558cd65ff24fb2e3bde4530b299becd8acb3648ef29d8bb9c9cadec158b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-memory-usage#memory-usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-memory-usage.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the schema, example query, or column meanings of the information_schema MEMORY_USAGE system table for the current TiDB instance.
- Retrieval Keywords: MEMORY_USAGE, information_schema.memory_usage, DESC memory_usage, SELECT * FROM information_schema.memory_usage, MEMORY_TOTAL, MEMORY_LIMIT, MEMORY_CURRENT, MEMORY_MAX_USED, CURRENT_OPS, SESSION_KILL_LAST, SESSION_KILL_TOTAL, GC_LAST, GC_TOTAL, DISK_USAGE, QUERY_FORCE_DISK, tidb_server_memory_limit, shrinking
- Follow-up Guidance: The source also links to TiDB memory control and Tune TiKV memory parameter performance.
- Classification Note: This is reference content because it defines the MEMORY_USAGE system table, shows example SQL, and describes each returned column from official documentation.

## Official Source Content

# MEMORY_USAGE

The `MEMORY_USAGE` table describes the current memory usage of the current TiDB instance.

```sql
USE information_schema;
DESC memory_usage;
```

```sql
+--------------------+-------------+------+------+---------+-------+
| Field              | Type        | Null | Key  | Default | Extra |
+--------------------+-------------+------+------+---------+-------+
| MEMORY_TOTAL       | bigint(21)  | NO   |      | NULL    |       |
| MEMORY_LIMIT       | bigint(21)  | NO   |      | NULL    |       |
| MEMORY_CURRENT     | bigint(21)  | NO   |      | NULL    |       |
| MEMORY_MAX_USED    | bigint(21)  | NO   |      | NULL    |       |
| CURRENT_OPS        | varchar(50) | YES  |      | NULL    |       |
| SESSION_KILL_LAST  | datetime    | YES  |      | NULL    |       |
| SESSION_KILL_TOTAL | bigint(21)  | NO   |      | NULL    |       |
| GC_LAST            | datetime    | YES  |      | NULL    |       |
| GC_TOTAL           | bigint(21)  | NO   |      | NULL    |       |
| DISK_USAGE         | bigint(21)  | NO   |      | NULL    |       |
| QUERY_FORCE_DISK   | bigint(21)  | NO   |      | NULL    |       |
+--------------------+-------------+------+------+---------+-------+
11 rows in set (0.000 sec)
```

```sql
SELECT * FROM information_schema.memory_usage;
```

```sql
+--------------+--------------+----------------+-----------------+-------------+---------------------+--------------------+---------------------+----------+------------+------------------+
| MEMORY_TOTAL | MEMORY_LIMIT | MEMORY_CURRENT | MEMORY_MAX_USED | CURRENT_OPS | SESSION_KILL_LAST   | SESSION_KILL_TOTAL | GC_LAST             | GC_TOTAL | DISK_USAGE | QUERY_FORCE_DISK |
+--------------+--------------+----------------+-----------------+-------------+---------------------+--------------------+---------------------+----------+------------+------------------+
|  33674170368 |  10737418240 |     5097644032 |     10826604544 | NULL        | 2022-10-17 22:47:47 |                  1 | 2022-10-17 22:47:47 |       20 |          0 |                0 |
+--------------+--------------+----------------+-----------------+-------------+---------------------+--------------------+---------------------+----------+------------+------------------+
2 rows in set (0.002 sec)
```

The columns in the `MEMORY_USAGE` table are described as follows:

* MEMORY_TOTAL: The total available memory of TiDB, in bytes.
* MEMORY_LIMIT: The memory usage limit of TiDB, in bytes. The value is the same as that of the system variable [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640).
* MEMORY_CURRENT: The current memory usage of TiDB, in bytes.
* MEMORY_MAX_USED: The maximum memory usage of TiDB from the time it is started to the current time, in bytes.
* CURRENT_OPS: "shrinking" | null. "shrinking" means that TiDB is performing operations that shrink memory usage.
* SESSION_KILL_LAST: The timestamp of the last time a session is terminated.
* SESSION_KILL_TOTAL: The number of times sessions are terminated, from the time TiDB is started to the current time.
* GC_LAST: The timestamp of the last time Golang GC is triggered by memory usage.
* GC_TOTAL: The number of times Golang GC is triggered by memory usage, from the time TiDB is started to the current time.
* DISK_USAGE: The disk usage for the current data spill operation, in bytes.
* QUERY_FORCE_DISK: The number of times data is spilled to disk, from the time TiDB is started to the current time.
## See also

- [TiDB memory control](https://docs.pingcap.com/tidb/stable/configure-memory-usage)
- [Tune TiKV memory parameter performance](https://docs.pingcap.com/tidb/stable/tune-tikv-memory-performance)

- [TiDB memory control](https://docs.pingcap.com/tidb/stable/configure-memory-usage)
- [Tune TiKV memory parameter performance](https://docs.pingcap.com/tidb/stable/tune-tikv-memory-performance)
