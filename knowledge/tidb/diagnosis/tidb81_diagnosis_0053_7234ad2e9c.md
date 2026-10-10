# Latency breakdown for SQL layer and read-query paths

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/latency-breakdown.md`
- Source Title: `Latency Breakdown`
- Source Heading Path: `Latency Breakdown | Latency Breakdown > General SQL layer | Latency Breakdown > Read queries | Latency Breakdown > Read queries > Point get | Latency Breakdown > Read queries > Batch point get | Latency Breakdown > Read queries > Table scan & Index scan`
- Source Line Ranges: `5-253`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `latency`, `metrics`, `sql-layer`, `read-queries`, `point-get`, `batch-point-get`, `table-scan`, `index-scan`, `tso`, `batch-client`, `snapshot`, `prometheus`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0053_7234ad2e9c`
- Source ID: `tidb-docs-8.1:latency-breakdown.md#latency-breakdown`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e674285a89eace84df40dca0b10ebbb5068af282184bc5c564703960ccf5031f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/latency-breakdown#latency-breakdown
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/latency-breakdown.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiDB read-query or general SQL layer latency by breaking down e2e duration into Prometheus metrics for point get, batch point get, table scan, or index scan paths.
- Retrieval Keywords: e2e duration, tidb_server_get_token_duration_seconds, tidb_session_parse_duration_seconds, tidb_session_compile_duration_seconds, tidb_session_execute_duration_seconds{type="general"}, General SQL layer, Read queries, Point get, Batch point get, Table scan, Index scan, pd_client_cmd_handle_cmds_duration_seconds{type="wait"}, TSO wait duration, tidb_tikvclient_txn_cmd_duration_seconds{type="get"}, tidb_tikvclient_txn_cmd_duration_seconds{type="batch_get"}, tidb_tikvclient_request_seconds{type="Get"}, tidb_tikvclient_request_seconds{type="BatchGet"}, tidb_tikvclient_batch_wait_duration, tidb_tikvclient_batch_send_latency, tidb_tikvclient_rpc_net_latency_seconds{store="?"}, tikv_grpc_msg_duration_seconds{type="kv_get"}, tikv_grpc_msg_duration_seconds{type="kv_batch_get"}, tikv_grpc_msg_duration_seconds{type="coprocessor"}, tikv_storage_engine_async_request_duration_seconds{type="snapshot"}, tikv_engine_seek_micro_seconds{type="seek_average"}, tikv_engine_seek_micro_seconds{type="seek_max"}, tikv_storage_rocksdb_perf, block_read_time, block_read_count, req="get/batch_get_command", req="batch_get", tidb_distsql_handle_query_duration_seconds{sql_type="general"}, tidb_distsql_scan_keys_partial_num_count, tikv_coprocessor_request_wait_seconds{type="snapshot"}, tikv_coprocessor_request_wait_seconds{type="schedule"}, tikv_coprocessor_request_handler_build_seconds{type="index/select"}, tikv_coprocessor_request_handle_seconds{type="index/select"}, req_per_copr, Prometheus dashboard
- Follow-up Guidance: The content points to the Batch client and TiKV snapshot sections for more details about batch client durations and snapshot duration.
- Classification Note: This chunk is classified as diagnosis because it decomposes latency into specific TiDB, TiKV, and PD metrics and explains how to analyze critical-path time cost for SQL and read-query execution.

## Official Source Content

# Latency Breakdown

This document breaks down the latency into metrics and then analyzes it from the user's perspective from the following aspects:

- [General SQL layer](#general-sql-layer)
- [Read queries](#read-queries)
- [Write queries](#write-queries)
- [Batch client](#batch-client)
- [TiKV snapshot](#tikv-snapshot)
- [Async write](#async-write)

These analyses provide you with a deep insight into time cost during TiDB SQL queries. This is a guide to TiDB's critical path diagnosis. Besides, the [Diagnosis use cases](#diagnosis-use-cases) section introduces how to analyze latency in real use cases.

It's better to read [Performance Analysis and Tuning](https://docs.pingcap.com/tidb/stable/performance-tuning-methods) before this document. Note that when breaking down latency into metrics, the average value of duration or latency is calculated instead of some specific slow queries. Many metrics are shown as histogram, which is a distribution of the duration or latency. To calculate the average latency, you need to use the following sum and count counter.

```
avg = ${metric_name}_sum / ${metric_name}_count
```

Metrics described in this document can be read directly from the Prometheus dashboard of TiDB.
## General SQL layer

This general SQL layer latency exists on the top level of TiDB and is shared by all SQL queries. The following is the time cost diagram of general SQL layer operation:

```railroad+diagram
Diagram(
    NonTerminal("Token wait duration"),
    Choice(
        0,
        Comment("Prepared statement"),
        NonTerminal("Parse duration"),
    ),
    OneOrMore(
        Sequence(
        Choice(
            0,
            NonTerminal("Optimize prepared plan duration"),
            Sequence(
            Comment("Plan cache miss"),
            NonTerminal("Compile duration"),
            ),
        ),
        NonTerminal("TSO wait duration"),
        NonTerminal("Execution duration"),
        ),
        Comment("Retry"),
    ),
)
```

The general SQL layer latency can be observed as the `e2e duration` metric and is calculated as:

```text
e2e duration =
    tidb_server_get_token_duration_seconds +
    tidb_session_parse_duration_seconds +
    tidb_session_compile_duration_seconds +
    tidb_session_execute_duration_seconds{type="general"}
```

- `tidb_server_get_token_duration_seconds` records the duration of Token waiting. This is usually less than 1 millisecond and is small enough to be ignored.
- `tidb_session_parse_duration_seconds` records the duration of parsing SQL queries to an Abstract Syntax Tree (AST), which can be skipped by [`PREPARE/EXECUTE` statements](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-best-practices#use-prepare).
- `tidb_session_compile_duration_seconds` records the duration of compiling an AST to an execution plan, which can be skipped by [SQL prepared execution plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).
- `tidb_session_execute_duration_seconds{type="general"}` records the duration of execution, which mixes all types of user queries. This needs to be broken down into fine-grained durations for analyzing performance issues or bottlenecks.

Generally, OLTP (Online Transactional Processing) workload can be divided into read and write queries, which share some critical code. The following sections describe latency in [read queries](#read-queries) and [write queries](#write-queries), which are executed differently.
## Read queries

Read queries have only a single process form.
### Point get

The following is the time cost diagram of [point get](https://docs.pingcap.com/tidb/stable/glossary#point-get) operations:

```railroad+diagram
Diagram(
    Choice(
        0,
        NonTerminal("Resolve TSO"),
        Comment("Read by clustered PK in auto-commit-txn mode or snapshot read"),
    ),
    Choice(
        0,
        NonTerminal("Read handle by index key"),
        Comment("Read by clustered PK, encode handle by key"),
    ),
    NonTerminal("Read value by handle"),
)
```

During point get, the `tidb_session_execute_duration_seconds{type="general"}` duration is calculated as:

```text
tidb_session_execute_duration_seconds{type="general"} =
    pd_client_cmd_handle_cmds_duration_seconds{type="wait"} +
    read handle duration +
    read value duration
```

`pd_client_cmd_handle_cmds_duration_seconds{type="wait"}` records the duration of fetching [TSO (Timestamp Oracle)](https://docs.pingcap.com/tidb/stable/glossary#tso) from PD. When reading in an auto-commit transaction mode with a clustered primary index or from a snapshot, the value will be zero.

The `read handle duration` and `read value duration` are calculated as:

```text
read handle duration = read value duration =
    tidb_tikvclient_txn_cmd_duration_seconds{type="get"} =
    send request duration =
    tidb_tikvclient_request_seconds{type="Get"} =
    tidb_tikvclient_batch_wait_duration +
    tidb_tikvclient_batch_send_latency +
    tikv_grpc_msg_duration_seconds{type="kv_get"} +
    tidb_tikvclient_rpc_net_latency_seconds{store="?"}
```

The `tidb_tikvclient_request_seconds{type="Get"}` records a duration of get requests which are sent directly to TiKV via a batched gRPC wrapper. For more details about the preceding batch client duration, such as `tidb_tikvclient_batch_wait_duration`, `tidb_tikvclient_batch_send_latency`, and `tidb_tikvclient_rpc_net_latency_seconds{store="?"}`, refer to the [Batch client](#batch-client) section.

The `tikv_grpc_msg_duration_seconds{type="kv_get"}` duration is calculated as:

```text
tikv_grpc_msg_duration_seconds{type="kv_get"} =
    tikv_storage_engine_async_request_duration_seconds{type="snapshot"} +
    tikv_engine_seek_micro_seconds{type="seek_average"} +
    read value duration +
    read value duration(non-short value)
```

At this time, requests are in TiKV. TiKV processes get requests by one seek and one or two read actions (short values are encoded in a write column family, and reading it once is enough). TiKV gets a snapshot before processing the read request. For more details about the TiKV snapshot duration, refer to the [TiKV snapshot](#tikv-snapshot) section.

The `read value duration(from disk)` is calculated as:

```text
read value duration(from disk) =
    sum(rate(tikv_storage_rocksdb_perf{metric="block_read_time",req="get/batch_get_command"})) / sum(rate(tikv_storage_rocksdb_perf{metric="block_read_count",req="get/batch_get_command"}))
```

TiKV uses RocksDB as its storage engine. When the required value is missing from the block cache, TiKV needs to load the value from the disk. For `tikv_storage_rocksdb_perf`, the get request can be either `get` or `batch_get_command`.
### Batch point get

The following is the time cost diagram of batch point get operations:

```railroad+diagram
Diagram(
  NonTerminal("Resolve TSO"),
  Choice(
    0,
    NonTerminal("Read all handles by index keys"),
    Comment("Read by clustered PK, encode handle by keys"),
  ),
  NonTerminal("Read values by handles"),
)
```

During batch point get, the `tidb_session_execute_duration_seconds{type="general"}` is calculated as:

```text
tidb_session_execute_duration_seconds{type="general"} =
    pd_client_cmd_handle_cmds_duration_seconds{type="wait"} +
    read handles duration +
    read values duration
```

The process of batch point get is almost the same as [Point get](#point-get) except that batch point get reads multiple values at the same time.

The `read handles duration` and `read values duration` are calculated as:

```text
read handles duration = read values duration =
    tidb_tikvclient_txn_cmd_duration_seconds{type="batch_get"} =
    send request duration =
    tidb_tikvclient_request_seconds{type="BatchGet"} =
    tidb_tikvclient_batch_wait_duration(transaction) +
    tidb_tikvclient_batch_send_latency(transaction) +
    tikv_grpc_msg_duration_seconds{type="kv_batch_get"} +
    tidb_tikvclient_rpc_net_latency_seconds{store="?"}(transaction)
```

For more details about the preceding batch client duration, such as `tidb_tikvclient_batch_wait_duration(transaction)`, `tidb_tikvclient_batch_send_latency(transaction)`, and `tidb_tikvclient_rpc_net_latency_seconds{store="?"}(transaction)`, refer to the [Batch client](#batch-client) section.

The `tikv_grpc_msg_duration_seconds{type="kv_batch_get"}` duration is calculated as:

```text
tikv_grpc_msg_duration_seconds{type="kv_batch_get"} =
    tikv_storage_engine_async_request_duration_seconds{type="snapshot"} +
    n * (
        tikv_engine_seek_micro_seconds{type="seek_max"} +
        read value duration +
        read value duration(non-short value)
    )

read value duration(from disk) =
    sum(rate(tikv_storage_rocksdb_perf{metric="block_read_time",req="batch_get"})) / sum(rate(tikv_storage_rocksdb_perf{metric="block_read_count",req="batch_get"}))
```

After getting a snapshot, TiKV reads multiple values from the same snapshot. The read duration is the same as [Point get](#point-get). When TiKV loads data from disk, the average duration can be calculated by `tikv_storage_rocksdb_perf` with `req="batch_get"`.
### Table scan & Index scan

The following is the time cost diagram of table scan and index scan operations:

```railroad+diagram
Diagram(
    Stack(
        NonTerminal("Resolve TSO"),
        NonTerminal("Load region cache for related table/index ranges"),
        OneOrMore(
            NonTerminal("Wait for result"),
            Comment("Next loop: drain the result"),
        ),
    ),
)
```

During table scan and index scan, the `tidb_session_execute_duration_seconds{type="general"}` duration is calculated as:

```text
tidb_session_execute_duration_seconds{type="general"} =
    pd_client_cmd_handle_cmds_duration_seconds{type="wait"} +
    req_per_copr * (
        tidb_distsql_handle_query_duration_seconds{sql_type="general"}
    )
    tidb_distsql_handle_query_duration_seconds{sql_type="general"} <= send request duration
```

Table scan and index scan are processed in the same way. `req_per_copr` is the distributed task count. Because coprocessor execution and data responding to client are in different threads, `tidb_distsql_handle_query_duration_seconds{sql_type="general"}` is the wait time and it is less than the `send request duration`.

The `send request duration` and `req_per_copr` are calculated as:

```text
send request duration =
    tidb_tikvclient_batch_wait_duration +
    tidb_tikvclient_batch_send_latency +
    tikv_grpc_msg_duration_seconds{type="coprocessor"} +
    tidb_tikvclient_rpc_net_latency_seconds{store="?"}

tikv_grpc_msg_duration_seconds{type="coprocessor"} =
    tikv_coprocessor_request_wait_seconds{type="snapshot"} +
    tikv_coprocessor_request_wait_seconds{type="schedule"} +
    tikv_coprocessor_request_handler_build_seconds{type="index/select"} +
    tikv_coprocessor_request_handle_seconds{type="index/select"}

req_per_copr = rate(tidb_distsql_handle_query_duration_seconds_count) / rate(tidb_distsql_scan_keys_partial_num_count)
```

In TiKV, the table scan type is `select` and the index scan type is `index`. The details of `select` and `index` type duration are the same.
