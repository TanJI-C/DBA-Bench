# TiDB log error analysis

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map > 7. Common log analysis > 7.1 TiDB`
- Source Line Ranges: `566-598`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`
- Topic Tags: `gc`, `coprocessor`, `region cache`, `timeout`, `inconsistent index`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0115_2a3bece52a`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#7-1-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2591d12c5ac298fe1f464f8c8d417ec631e2f8bcebba0f4c629a391e025fc2e2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#7-1-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this chunk when TiDB logs show GC lifetime, coprocessor queueing, region cache timeout, or inconsistent index messages and you need the documented meaning and related checks.
- Retrieval Keywords: GC life time is shorter than transaction duration, tidb_gc_life_time, coprocessor.go request outdated, request outdated, region_cache.go switch region peer to next due to send request fail, context deadline exceeded, grep "<addr> cancelled, send request is cancelled, wait response is cancelled, Grafana TiDB Batch Client, Pending Request Count by TiKV, distsql.go inconsistent index, admin check table <TableName>, SET GLOBAL tidb_gc_enable = 0
- Follow-up Guidance: The content points to checking Grafana Pending Request Count by TiKV, grepping the addr field for cancelled messages, running admin check table <TableName>, and disabling garbage collection with SET GLOBAL tidb_gc_enable = 0 if the index check fails.
- Classification Note: The classification is diagnosis for TiDB in self-managed deployments because the content explains how to interpret specific TiDB log errors and related symptoms across TiDB, TiKV, and PD.

## Official Source Content

### 7.1 TiDB

- 7.1.1 `GC life time is shorter than transaction duration`.

    The transaction duration exceeds the GC lifetime (10 minutes by default).

    You can increase the GC lifetime by modifying the [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) system variable. Generally, it is not recommended to modify this parameter, because changing it might cause many old versions to pile up if this transaction has a large number of `UPDATE` and `DELETE` statements.

- 7.1.2 `coprocessor.go` reports `request outdated`.

    This error is returned when the coprocessor request sent to TiKV waits in a queue at TiKV for over 60 seconds.

    You need to investigate why the TiKV coprocessor is in a long queue.

- 7.1.3 `region_cache.go` reports a large number of `switch region peer to next due to send request fail`, and the error message is `context deadline exceeded`.

    The request for TiKV timed out and triggers the region cache to switch the request to other nodes. You can continue to run the `grep "<addr> cancelled` command on the `addr` field in the log and take the following steps according to the `grep` results:

    - `send request is cancelled`: The request timed out during the sending phase. You can investigate the monitoring **Grafana** -> **TiDB** -> **Batch Client**/`Pending Request Count by TiKV` and see whether the Pending Request Count is greater than 128:

        - If the value is greater than 128, the sending goes beyond the processing capacity of KV, so the sending piles up.
        - If the value is not greater than 128, check the log to see if the report is caused by the operation and maintenance changes of the corresponding KV; otherwise, this error is unexpected, and you need to [report a bug](https://github.com/pingcap/tidb/issues/new?labels=type%2Fbug&template=bug-report.md).

    - `wait response is cancelled`: The request timed out after it is sent to TiKV. You need to check the response time of the corresponding TiKV address and the Region logs in PD and KV at that time.

- 7.1.4 `distsql.go` reports `inconsistent index`.

    The data index seems to be inconsistent. Run the `admin check table <TableName>` command on the table where the reported index is. If the check fails, disable garbage collection by running the following command, and [report a bug](https://github.com/pingcap/tidb/issues/new?labels=type%2Fbug&template=bug-report.md):

    ```sql
    SET GLOBAL tidb_gc_enable = 0;
    ```
