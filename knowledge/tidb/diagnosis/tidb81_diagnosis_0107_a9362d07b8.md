# TiDB OOM issues troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map > 3. TiDB issues > 3.2 OOM issues`
- Source Line Ranges: `102-142`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `oom`, `memory`, `dmesg`, `oom-killer`, `expensive-query`, `memory-quota`, `swap`, `hashjoin`, `update`, `delete`, `union`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0107_a9362d07b8`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#3-2-oom-issues`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `605dd78ad35456e798a682975536444eb45421d2b1761e2c962584e8b37f0f26`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#3-2-oom-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this content when investigating TiDB OOM symptoms such as lost MySQL connection during query, abrupt tidb-server restarts, or sharp memory growth.
- Retrieval Keywords: ERROR 2013 (HY000): Lost connection to MySQL server during query, dmesg -T | grep tidb-server, OOM-killer, Welcome to TiDB, fatal error: runtime: out of memory, cannot allocate memory, fatal error: stack overflow, tidb_stderr.log, expensive_query, memory exceeds quota, tidb_mem_quota_query, SWAP, HashJoin, UPDATE/DELETE, Union
- Follow-up Guidance: The content follows up with log locations for OOM evidence, SQL-location hints using `expensive_query` or `memory exceeds quota`, and typical SQL patterns such as `HashJoin`, large `UPDATE/DELETE`, and `Union` sub-queries.
- Classification Note: This is classified as diagnosis because it describes OOM symptoms, log-based confirmation methods, SQL-location clues, and common query patterns associated with TiDB memory exhaustion.

## Official Source Content

### 3.2 OOM issues

- 3.2.1 Symptom

    - Client: The client reports the error `ERROR 2013 (HY000): Lost connection to MySQL server during query`.

    - Check the log

        - Execute `dmesg -T | grep tidb-server`. The result shows the OOM-killer log around the time point when the error occurs.

        - Grep the "Welcome to TiDB" log in `tidb.log` around the time point after the error occurs (namely, the time when tidb-server restarts).

        - Grep `fatal error: runtime: out of memory` or `cannot allocate memory` in `tidb_stderr.log`.

        - In v2.1.8 or earlier versions, you can grep `fatal error: stack overflow` in the `tidb_stderr.log`.

    - Monitor: The memory usage of tidb-server instances increases sharply in a short period of time.

- 3.2.2 Locate the SQL statement that causes OOM. (Currently all versions of TiDB cannot locate SQL accurately. You still need to analyze whether OOM is caused by the SQL statement after you locate one.)

    - For versions >= v3.0.0, grep "expensive_query" in `tidb.log`. That log message records SQL queries that timed out or exceed memory quota.
    - For versions < v3.0.0, grep "memory exceeds quota" in `tidb.log` to locate SQL queries that exceed memory quota.

  > **Note:**
  >
  > The default threshold for a single SQL memory usage is `1GB`. You can set this parameter by configuring the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query).

- 3.2.3 Mitigate OOM issues

    - By enabling `SWAP`, you can mitigate the OOM issue caused by overuse of memory by large queries. When the memory is insufficient, this method can have impact on the performance of large queries due to the I/O overhead. The degree to which the performance is affected depends on the remaining memory space and the disk I/O speed.

- 3.2.4 Typical reasons for OOM

    - The SQL query has `join`. If you view the SQL statement by using `explain`, you can find that the `join` operation selects the `HashJoin` algorithm and the `inner` table is large.

    - The data volume of a single `UPDATE/DELETE` query is too large. See [case-882](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case882.md) in Chinese.

    - The SQL contains multiple sub-queries connected by `Union`. See [case-1828](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case1828.md) in Chinese.

For more information about troubleshooting OOM, see [Troubleshoot TiDB OOM Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-tidb-oom).
