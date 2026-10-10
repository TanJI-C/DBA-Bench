# TiFlash throughput and latency metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash-performance-tuning-methods.md`
- Source Title: `TiFlash Performance Analysis and Tuning Methods`
- Source Heading Path: `TiFlash Performance Analysis and Tuning Methods > Key metrics for TiFlash performance | TiFlash Performance Analysis and Tuning Methods > Key metrics for TiFlash performance > Throughput metrics | TiFlash Performance Analysis and Tuning Methods > Key metrics for TiFlash performance > Latency metrics`
- Source Line Ranges: `24-67`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `dashboard`, `tidb`, `tikv`, `sql`
- Topic Tags: `throughput`, `latency`, `mpp`, `coprocessor`, `request qps`, `executor qps`, `request duration`, `query plan`, `pushdown`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0116_3d4203de11`
- Source ID: `tidb-docs-8.1:tiflash-performance-tuning-methods.md#key-metrics-for-tiflash-performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bb56a89039f394a3a4a336be04fe23d58bae41e795a33b1390a87a7f09932030`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash-performance-tuning-methods#key-metrics-for-tiflash-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash-performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiFlash throughput and latency metrics for MPP, coprocessor, and executor activity, or when investigating why `cop` or MPP request types dominate request duration.
- Retrieval Keywords: MPP Query count, Request QPS, Executor QPS, Request Duration Overview, Request Duration, Request Handle Duration, run_mpp_task, dispatch_mpp_task, mpp_establish_conn, batch, cop, cop_execution, remote_read, remote_read_constructed, remote_read_sent, table_scan, selection, aggregation, top_n, limit, join, exchange_sender, exchange_receiver, SQL execution plan, push down to TiFlash
- Follow-up Guidance: If `cop` requests constitute the majority of the total processing duration, the source says to check the SQL execution plan to see why these `cop` requests are generated.
- Classification Note: This is classified as observability because the content focuses on TiFlash dashboard metrics that show throughput, latency, request types, and pushdown behavior.

## Official Source Content

## Key metrics for TiFlash performance
### Throughput metrics

With the following metrics, you can get the throughput of TiFlash:

- MPP Query count: the instant value of MPP query count for each TiFlash instance, reflecting the current number of MPP queries that need to be processed by the TiFlash instance (including those being processed and those awaiting scheduling).
- Request QPS: the number of coprocessor requests received by all TiFlash instances.
    - `run_mpp_task`, `dispatch_mpp_task`, and `mpp_establish_conn` are MPP requests.
    - `batch`: the number of batch requests.
    - `cop`: the number of coprocessor requests that are sent directly via the coprocessor interface.
    - `cop_execution`: the number of coprocessor requests currently being executed.
    - `remote_read`, `remote_read_constructed`, and `remote_read_sent` are remote read-related metrics. An increase in remote reads usually indicates an issue in the system.
- Executor QPS: the number of each type of dag operators in the requests received by all TiFlash instances, where `table_scan` is the table scan operator, `selection` is the selection operator, `aggregation` is the aggregation operator, `top_n` is the TopN operator, `limit` is the limit operator, `join` is a join operator, `exchange_sender` is a data sending operator, and `exchange_receiver` is a data receiving operator.
### Latency metrics

With the following metrics, you can get the latency of TiFlash:

- Request Duration Overview: provides a stacked chart of the total processing duration for all request types in all TiFlash instances per second.

    - If the type of a request is `run_mpp_task`, `dispatch_mpp_task`, or `mpp_establish_conn`, it indicates that the SQL statement execution has been partially or fully pushed down to TiFlash, typically involving join and data distribution operations. This is the most common request type in TiFlash.
    - If the type of a request is `cop`, it indicates that the statement related to this request has not been fully pushed down to TiFlash. Typically, TiDB pushes down the table full scan operator to TiFlash for data access and filtering. If `cop` becomes the most common request type in the stacked chart, you need to check if it is reasonable.

        - If the amount of data queried by a SQL statement is large, the optimizer might estimate that TiFlash full table scans are more cost-effective according to the cost model.
        - If the schema of a queried table lacks suitable indexes, the optimizer can only push the query down to TiFlash for a full table scan, even if the amount of data to be queried is small. In this case, it is more efficient to create proper indexes and access the data through TiKV.

- Request Duration: the total processing duration for each MPP and coprocessor request type in all TiFlash instances, which includes the average latency and p99 latency.
- Request Handle Duration: the time from the start of executing the `cop` and `batch cop` requests to the completion of the execution, excluding waiting time. This metric is only applicable to the `cop` and `batch cop` types of requests, including average and P99 latency.

Example 1: Processing duration overview of TiFlash MPP requests

In the workload of the following diagram, `run_mpp_task` and `mpp_establish_conn` requests constitute the majority of the total processing duration, indicating that most of the requests are MPP tasks that are fully pushed down to TiFlash for execution.

The processing duration of `cop` requests is relatively small, indicating that some of the requests are pushed down to TiFlash for data access and filtering through the coprocessor.

![CH-TiFlash-MPP](/media/performance/tiflash/ch-2tiflash-op.png)

Example 2: TiFlash `cop` requests constitute the majority of the total processing duration

In the workload of the following diagram, `cop` requests constitute the majority of the total processing duration. In this case, you can check the SQL execution plan to see why these `cop` requests are generated.

![Cop](/media/performance/tiflash/tiflash_request_duration_by_type.png)
