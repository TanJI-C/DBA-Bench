# INSPECTION_RESULT table usage, examples, and diagnostic rules

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-inspection-result.md`
- Source Title: `INSPECTION_RESULT`
- Source Heading Path: `INSPECTION_RESULT | INSPECTION_RESULT > Diagnostics example | INSPECTION_RESULT > Diagnostic rules | INSPECTION_RESULT > Diagnostic rules > `config` diagnostic rule | INSPECTION_RESULT > Diagnostic rules > `version` diagnostic rule | INSPECTION_RESULT > Diagnostic rules > `critical-error` diagnostic rule`
- Source Line Ranges: `5-273`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `sql`
- Topic Tags: `information_schema`, `inspection_result`, `diagnostic_rules`, `cluster_diagnostics`, `configuration_checks`, `version_consistency`, `critical_errors`, `thresholds`, `time_range`, `metrics_schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0051_bc629a0504`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-inspection-result.md#inspection-result`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9b0a9f8f0421dab9a0843dbc176c73a8ca2f984ac670795d84c4608fc85ea83`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-inspection-result#inspection-result
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-inspection-result.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to query `information_schema.inspection_result`, interpret its fields and built-in diagnostic rules, or filter diagnostics by time range, severity, or rule in TiDB Self-Managed.
- Retrieval Keywords: information_schema.inspection_result, INSPECTION_RESULT, select * from information_schema.inspection_result, /*+ time_range() */, where severity='critical', where rule='critical-error', inspection_rules, information_schema.inspection_rules, config, version, node-load, critical-error, threshold-check, CLUSTER_CONFIG, CLUSTER_INFO, metrics_schema.up, CLUSTER_LOG, log.slow-threshold, raftstore.sync-log, git_hash, server-down, get-token-duration, storage-write-duration, rocksdb-write-duration, tidb_panic_count_total_count, tidb_binlog_error_total_count, tikv_critical_error_total_count, tikv_scheduler_is_busy_total_count, tikv_coprocessor_is_busy_total_count, tikv_channel_full_total_count, tikv_engine_write_stall
- Follow-up Guidance: The source also shows querying `information_schema.inspection_rules where type='inspection'` and includes follow-up SQL in `DETAILS`, such as `SELECT * FROM information_schema.cluster_info WHERE type='tidb'`.
- Classification Note: The classification is diagnosis because the content defines the `INSPECTION_RESULT` diagnostic table, its warning and critical outputs, and the rule-based checks against cluster information, configuration, and monitoring tables.

## Official Source Content

# INSPECTION_RESULT

TiDB has some built-in diagnostic rules for detecting faults and hidden issues in the system.

The `INSPECTION_RESULT` diagnostic table can help you quickly find problems and reduce your repetitive manual work. You can use the `select * from information_schema.inspection_result` statement to trigger the internal diagnostics.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

The structure of the `information_schema.inspection_result` diagnostic result table `information_schema.inspection_result` is as follows:

```sql
USE information_schema;
DESC inspection_result;
```

```sql
+----------------+--------------+------+------+---------+-------+
| Field          | Type         | Null | Key  | Default | Extra |
+----------------+--------------+------+------+---------+-------+
| RULE           | varchar(64)  | YES  |      | NULL    |       |
| ITEM           | varchar(64)  | YES  |      | NULL    |       |
| TYPE           | varchar(64)  | YES  |      | NULL    |       |
| INSTANCE       | varchar(64)  | YES  |      | NULL    |       |
| STATUS_ADDRESS | varchar(64)  | YES  |      | NULL    |       |
| VALUE          | varchar(64)  | YES  |      | NULL    |       |
| REFERENCE      | varchar(64)  | YES  |      | NULL    |       |
| SEVERITY       | varchar(64)  | YES  |      | NULL    |       |
| DETAILS        | varchar(256) | YES  |      | NULL    |       |
+----------------+--------------+------+------+---------+-------+
9 rows in set (0.00 sec)
```

Field description:

* `RULE`: The name of the diagnostic rule. Currently, the following rules are available:
    * `config`: Checks whether the configuration is consistent and proper. If the same configuration is inconsistent on different instances, a `warning` diagnostic result is generated.
    * `version`: The consistency check of version. If the same version is inconsistent on different instances, a `warning` diagnostic result is generated.
    * `node-load`: Checks the server load. If the current system load is too high, the corresponding `warning` diagnostic result is generated.
    * `critical-error`: Each module of the system defines critical errors. If a critical error exceeds the threshold within the corresponding time period, a warning diagnostic result is generated.
    * `threshold-check`: The diagnostic system checks the thresholds of key metrics. If a threshold is exceeded, the corresponding diagnostic information is generated.
* `ITEM`: Each rule diagnoses different items. This field indicates the specific diagnostic items corresponding to each rule.
* `TYPE`: The instance type of the diagnostics. The optional values are `tidb`, `pd`, and `tikv`.
* `INSTANCE`: The specific address of the diagnosed instance.
* `STATUS_ADDRESS`: The HTTP API service address of the instance.
* `VALUE`: The value of a specific diagnostic item.
* `REFERENCE`: The reference value (threshold value) for this diagnostic item. If `VALUE` exceeds the threshold, the corresponding diagnostic information is generated.
* `SEVERITY`: The severity level. The optional values are `warning` and `critical`.
* `DETAILS`: Diagnostic details, which might also contain SQL statement(s) or document links for further diagnostics.
## Diagnostics example

Diagnose issues currently existing in the cluster.

```sql
SELECT * FROM information_schema.inspection_result\G
```

```sql
***************************[ 1. row ]***************************
RULE      | config
ITEM      | log.slow-threshold
TYPE      | tidb
INSTANCE  | 172.16.5.40:4000
VALUE     | 0
REFERENCE | not 0
SEVERITY  | warning
DETAILS   | slow-threshold = 0 will record every query to slow log, it may affect performance
***************************[ 2. row ]***************************
RULE      | version
ITEM      | git_hash
TYPE      | tidb
INSTANCE  |
VALUE     | inconsistent
REFERENCE | consistent
SEVERITY  | critical
DETAILS   | the cluster has 2 different tidb version, execute the sql to see more detail: select * from information_schema.cluster_info where type='tidb'
***************************[ 3. row ]***************************
RULE      | threshold-check
ITEM      | storage-write-duration
TYPE      | tikv
INSTANCE  | 172.16.5.40:23151
VALUE     | 130.417
REFERENCE | < 0.100
SEVERITY  | warning
DETAILS   | max duration of 172.16.5.40:23151 tikv storage-write-duration was too slow
***************************[ 4. row ]***************************
RULE      | threshold-check
ITEM      | rocksdb-write-duration
TYPE      | tikv
INSTANCE  | 172.16.5.40:20151
VALUE     | 108.105
REFERENCE | < 0.100
SEVERITY  | warning
DETAILS   | max duration of 172.16.5.40:20151 tikv rocksdb-write-duration was too slow
```

The following issues can be detected from the diagnostic result above:

* The first row indicates that TiDB's `log.slow-threshold` value is configured to `0`, which might affect performance.
* The second row indicates that two different TiDB versions exist in the cluster.
* The third and fourth rows indicate that the TiKV write delay is too long. The expected delay is no more than 0.1 second, while the actual delay is far longer than expected.

You can also diagnose issues existing within a specified range, such as from "2020-03-26 00:03:00" to "2020-03-26 00:08:00". To specify the time range, use the SQL Hint of `/*+ time_range() */`. See the following query example:

```sql
select /*+ time_range("2020-03-26 00:03:00", "2020-03-26 00:08:00") */ * from information_schema.inspection_result\G
```

```sql
***************************[ 1. row ]***************************
RULE      | critical-error
ITEM      | server-down
TYPE      | tidb
INSTANCE  | 172.16.5.40:4009
VALUE     |
REFERENCE |
SEVERITY  | critical
DETAILS   | tidb 172.16.5.40:4009 restarted at time '2020/03/26 00:05:45.670'
***************************[ 2. row ]***************************
RULE      | threshold-check
ITEM      | get-token-duration
TYPE      | tidb
INSTANCE  | 172.16.5.40:10089
VALUE     | 0.234
REFERENCE | < 0.001
SEVERITY  | warning
DETAILS   | max duration of 172.16.5.40:10089 tidb get-token-duration is too slow
```

The following issues can be detected from the diagnostic result above:

* The first row indicates that the `172.16.5.40:4009` TiDB instance is restarted at `2020/03/26 00:05:45.670`.
* The second row indicates that the maximum `get-token-duration` time of the `172.16.5.40:10089` TiDB instance is 0.234s, but the expected time is less than 0.001s.

You can also specify conditions, for example, to query the `critical` level diagnostic results:

```sql
select * from information_schema.inspection_result where severity='critical';
```

Query only the diagnostic result of the `critical-error` rule:

```sql
select * from information_schema.inspection_result where rule='critical-error';
```
## Diagnostic rules

The diagnostic module contains a series of rules. These rules compare the results with the thresholds after querying the existing monitoring tables and cluster information tables. If the results exceed the thresholds, the diagnostics of `warning` or `critical` is generated and the corresponding information is provided in the `details` column.

You can query the existing diagnostic rules by querying the `inspection_rules` system table:

```sql
select * from information_schema.inspection_rules where type='inspection';
```

```sql
+-----------------+------------+---------+
| NAME            | TYPE       | COMMENT |
+-----------------+------------+---------+
| config          | inspection |         |
| version         | inspection |         |
| node-load       | inspection |         |
| critical-error  | inspection |         |
| threshold-check | inspection |         |
+-----------------+------------+---------+
```
### `config` diagnostic rule

In the `config` diagnostic rule, the following two diagnostic rules are executed by querying the `CLUSTER_CONFIG` system table:

* Check whether the configuration values of the same component are consistent. Not all configuration items has this consistency check. The allowlist of consistency check is as follows:

    ```go
    // The allowlist of the TiDB configuration consistency check
    port
    status.status-port
    host
    path
    advertise-address
    status.status-port
    log.file.filename
    log.slow-query-file
    tmp-storage-path

    // The allowlist of the PD configuration consistency check
    advertise-client-urls
    advertise-peer-urls
    client-urls
    data-dir
    log-file
    log.file.filename
    metric.job
    name
    peer-urls

    // The allowlist of the TiKV configuration consistency check
    server.addr
    server.advertise-addr
    server.status-addr
    log-file
    raftstore.raftdb-path
    storage.data-dir
    storage.block-cache.capacity
    ```

* Check whether the values of the following configuration items are as expected.

    |  Component  | Configuration item | Expected value |
    |  ----  | ----  |  ----  |
    | TiDB | log.slow-threshold | larger than `0` |
    | TiKV | raftstore.sync-log | `true` |
### `version` diagnostic rule

The `version` diagnostic rule checks whether the version hash of the same component is consistent by querying the `CLUSTER_INFO` system table. See the following example:

```sql
SELECT * FROM information_schema.inspection_result WHERE rule='version'\G
```

```sql
***************************[ 1. row ]***************************
RULE      | version
ITEM      | git_hash
TYPE      | tidb
INSTANCE  |
VALUE     | inconsistent
REFERENCE | consistent
SEVERITY  | critical
DETAILS   | the cluster has 2 different tidb versions, execute the sql to see more detail: SELECT * FROM information_schema.cluster_info WHERE type='tidb'
```
### `critical-error` diagnostic rule

In `critical-error` diagnostic rule, the following two diagnostic rules are executed:

* Detect whether the cluster has the following errors by querying the related monitoring system tables in the metrics schema:

    |  Component  | Error name | Monitoring table | Error description |
    |  ----  | ----  |  ----  |  ----  |
    | TiDB | panic-count | tidb_panic_count_total_count | Panic occurs in TiDB. |
    | TiDB | binlog-error | tidb_binlog_error_total_count | An error occurs when TiDB writes binlog. |
    | TiKV | critical-error | tikv_critical_error_total_count | The critical error of TiKV. |
    | TiKV | scheduler-is-busy       | tikv_scheduler_is_busy_total_count | The TiKV scheduler is too busy, which makes TiKV temporarily unavailable. |
    | TiKV | coprocessor-is-busy | tikv_coprocessor_is_busy_total_count | The TiKV Coprocessor is too busy. |
    | TiKV | channel-is-full | tikv_channel_full_total_count | The "channel full" error occurs in TiKV. |
    | TiKV | tikv_engine_write_stall | tikv_engine_write_stall | The "stall" error occurs in TiKV. |

* Check whether any component is restarted by querying the `metrics_schema.up` monitoring table and the `CLUSTER_LOG` system table.
