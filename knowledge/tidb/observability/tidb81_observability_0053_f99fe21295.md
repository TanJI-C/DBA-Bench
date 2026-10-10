# TiFlash performance overview metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-performance-overview-dashboard.md`
- Source Title: `Key Metrics on Performance Overview`
- Source Heading Path: `Key Metrics on Performance Overview > TiFlash`
- Source Line Ranges: `168-190`
- Source Scope: `shared`
- Primary Component: `tiflash`
- Related Components: `dashboard`
- Topic Tags: `cpu`, `memory`, `io`, `mpp`, `qps`, `coprocessor`, `executors`, `request-duration`, `raft`, `throughput`, `read-flow`, `write-flow`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0053_f99fe21295`
- Source ID: `tidb-docs-8.1:grafana-performance-overview-dashboard.md#tiflash`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63003e33224612eb5c39066c424d6d7bdd196f65d1009879993aca9eb0b6f4d2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard#tiflash
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-performance-overview-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what TiFlash metrics are shown on the Performance Overview dashboard for CPU, memory, IO, MPP, coprocessor requests, executors, request durations, Raft read timing, and disk throughput or flow.
- Retrieval Keywords: TiFlash performance overview metrics, Performance Overview TiFlash, CPU utilization per TiFlash instance, Memory usage per TiFlash instance, IO utilization per TiFlash instance, MPP Query count, Request QPS, batch, batch_cop, cop, cop_dag, super_batch, Executor QPS, table_scan, selection, aggregation, top_n, limit, Request Duration Overview, Request Duration, Request Handle Duration, Raft Wait Index Duration, wait_index, read_index, Raft Batch Read Index Duration, Write Throughput By Instance, Write flow, Read flow
- Follow-up Guidance: The chunk further distinguishes Request Duration from Request Handle Duration and defines the Request QPS and Executor QPS subtypes shown on the dashboard.
- Classification Note: This is classified as observability for the TiFlash component because the content enumerates dashboard metrics and their meanings on the Performance Overview page.

## Official Source Content

## TiFlash

- CPU: The CPU utilization per TiFlash instance.
- Memory: The memory usage per TiFlash instance.
- IO utilization: The IO utilization per TiFlash instance.
- MPP Query count: The number of TiFlash MPP queries per second per TiFlash instance.
- Request QPS: The number of coprocessor requests received by all TiFlash instances.

    - `batch`: Number of batch requests.
    - `batch_cop`: Number of coprocessor requests in the batch requests.
    - `cop`: Number of coprocessor requests that are sent directly via the coprocessor interface.
    - `cop_dag`: Number of dag requests in all coprocessor requests.
    - `super_batch`: Number of requests that enable the Super Batch feature.
- Executor QPS: The number of each type of dag executors in the requests received by all TiFlash instances. `table_scan` is the table scan executor. `selection` is the selection executor. `aggregation` is the aggregation executor. `top_n` is the `TopN` executor. `limit` is the limit executor.
- Request Duration Overview: Provides a stacked chart of total processing time per second for all request types in all TiFlash instances.
- Request Duration: The total processing duration for each MPP and coprocessor request type in all TiFlash instances. It is from the time that the coprocessor request is received to the time that the response of the request is completed, which includes the average latency and p99 latency.
- Request Handle Duration: The actual processing duration for each MPP and coprocessor request type in all TiFlash instances. It is from the start of executing the coprocessor request to the completion of the execution, which includes the average latency and p99 latency.
- Raft Wait Index Duration: The time used by `wait_index` for all TiFlash instances, namely the time used to wait until Region index >= `read_index` after the `read_index` request is received.
- Raft Batch Read Index Duration: The time used by `read_index` for all TiFlash instances. Most time is used for interaction with the Region leader and retry.
- Write Throughput By Instance: The throughput of write by instance. It includes the throughput by applying the Raft write commands and Raft snapshots.
- Write flow: The traffic of disk writes by all TiFlash instances.
- Read flow: The traffic of disk reads by all TiFlash instances.
