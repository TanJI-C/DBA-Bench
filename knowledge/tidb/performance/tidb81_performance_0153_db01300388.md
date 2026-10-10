# Performance features

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Feature details > Performance`
- Source Line Ranges: `84-121`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `tikv`
- Topic Tags: `pessimistic locking`, `lock queues`, `batch requests`, `plan cache`, `limit clause`, `data exchange`, `compression`, `stale read`, `regexp_replace`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0153_db01300388`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5264d20d6511a28584ffaf56a8c31f854d7a981e8531332821066a4a3cfa3d1c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.6.0 performance features such as pessimistic lock queue wake-up, batch aggregate data requests, plan cache support for variable LIMIT, TiFlash exchange compression, TiFlash Stale Read, or regexp_replace pushdown.
- Retrieval Keywords: tidb_pessimistic_txn_aggressive_locking, stable wake-up model for pessimistic lock queues, single-point pessimistic lock conflicts, lock acquisition timeout, long-tail latency, P99 response time, batch aggregate data requests, tidb_store_batch_size, merge data requests sent to the same TiKV instance, RPC requests, LIMIT ?, LIMIT 10, ?, plan cache, TiFlash data exchange with compression, Stale Read, AS OF TIMESTAMP, tidb_read_staleness, TiFlash replica, regexp_replace, push down regexp_replace to TiFlash
- Follow-up Guidance: The content points to related documentation for tidb_pessimistic_txn_aggressive_locking, tidb_store_batch_size, SQL prepared plan cache, MPP exchange data compression, AS OF TIMESTAMP, tidb_read_staleness, and stale read.
- Classification Note: This is classified as performance because every listed change is described as improving execution efficiency, reducing latency, reducing RPC overhead, or improving query or data exchange performance.

## Official Source Content

### Performance

* Support a stable wake-up model for pessimistic lock queues [#13298](https://github.com/tikv/tikv/issues/13298) @[MyonKeminta](https://github.com/MyonKeminta)

    If an application encounters frequent single-point pessimistic lock conflicts, the existing wake-up mechanism cannot guarantee the time for transactions to acquire locks, which causes high long-tail latency and even lock acquisition timeout. Starting from v6.6.0, you can enable a stable wake-up model for pessimistic locks by setting the value of the system variable [`tidb_pessimistic_txn_aggressive_locking`](https://docs.pingcap.com/tidb/v6.6/system-variables#tidb_pessimistic_txn_aggressive_locking-new-in-v660) to `ON`. In this wake-up model, the wake-up sequence of a queue can be strictly controlled to avoid the waste of resources caused by invalid wake-ups. In scenarios with serious lock conflicts, the stable wake-up model can reduce long-tail latency and the P99 response time.

    Tests indicate this reduces tail latency 40-60%.

    For more information, see [documentation](https://docs.pingcap.com/tidb/v6.6/system-variables#tidb_pessimistic_txn_aggressive_locking-new-in-v660).

* Batch aggregate data requests [#39361](https://github.com/pingcap/tidb/issues/39361) @[cfzjywxk](https://github.com/cfzjywxk) @[you06](https://github.com/you06)

    When TiDB sends a data request to TiKV, TiDB compiles the request into different sub-tasks according to the Region where the data is located, and each sub-task only processes the request of a single Region. When the data to be accessed is highly dispersed, even if the size of the data is not large, many sub-tasks will be generated, which in turn will generate many RPC requests and consume extra time. Starting from v6.6.0, TiDB supports partially merging data requests that are sent to the same TiKV instance, which reduces the number of sub-tasks and the overhead of RPC requests. In the case of high data dispersion and insufficient gRPC thread pool resources, batching requests can improve performance by more than 50%.

    This feature is enabled by default. You can set the batch size of requests using the system variable [`tidb_store_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_store_batch_size).

* Remove the limit on `LIMIT` clauses [#40219](https://github.com/pingcap/tidb/issues/40219) @[fzzf678](https://github.com/fzzf678)

    Starting from v6.6.0, TiDB plan cache supports caching execution plans with a variable as the `LIMIT` parameter, such as `LIMIT ?` or `LIMIT 10, ?`. This feature allows more SQL statements to benefit from plan cache, thus improving execution efficiency. Currently, for security considerations, TiDB can only cache execution plans with `?` not greater than 10000.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache).

* TiFlash supports data exchange with compression [#6620](https://github.com/pingcap/tiflash/issues/6620) @[solotzg](https://github.com/solotzg)

    To cooperate with multiple nodes for computing, the TiFlash engine needs to exchange data among different nodes. When the size of the data to be exchanged is very large, the performance of data exchange might affect the overall computing efficiency. In v6.6.0, the TiFlash engine introduces a compression mechanism to compress the data that needs to be exchanged when necessary, and then to perform the exchange, thereby improving the efficiency of data exchange.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/explain-mpp#mpp-version-and-exchange-data-compression).

* TiFlash supports the Stale Read feature [#4483](https://github.com/pingcap/tiflash/issues/4483) @[hehechen](https://github.com/hehechen)

   The Stale Read feature has been generally available (GA) since v5.1.1, which allows you to read historical data at a specific timestamp or within a specified time range. Stale read can reduce read latency and improve query performance by reading data from local TiKV replicas directly. Before v6.6.0, TiFlash does not support Stale Read. Even if a table has TiFlash replicas, Stale Read can only read its TiKV replicas.

   Starting from v6.6.0, TiFlash supports the Stale Read feature. When you query the historical data of a table using the [`AS OF TIMESTAMP`](https://docs.pingcap.com/tidb/stable/as-of-timestamp) syntax or the [`tidb_read_staleness`](https://docs.pingcap.com/tidb/stable/tidb-read-staleness) system variable, if the table has a TiFlash replica, the optimizer now can choose to read the corresponding data from the TiFlash replica, thus further improving query performance.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/stale-read).

* Support pushing down the `regexp_replace` string function to TiFlash [#6115](https://github.com/pingcap/tiflash/issues/6115) @[xzhangxian1008](https://github.com/xzhangxian1008)
