# TiFlash resource utilization overview

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash-performance-tuning-methods.md`
- Source Title: `TiFlash Performance Analysis and Tuning Methods`
- Source Heading Path: `TiFlash Performance Analysis and Tuning Methods | TiFlash Performance Analysis and Tuning Methods > Resource utilization of a TiFlash cluster`
- Source Line Ranges: `5-23`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `dashboard`
- Topic Tags: `resource utilization`, `cpu`, `memory`, `io utilization`, `performance overview`, `ch-benchmark`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0115_2360e85581`
- Source ID: `tidb-docs-8.1:tiflash-performance-tuning-methods.md#tiflash-performance-analysis-and-tuning-methods`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e4ceb1518b2a9c57a206492b42a0f3e9c26df416053651efad7f0b94df1c8b6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash-performance-tuning-methods#tiflash-performance-analysis-and-tuning-methods
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash-performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of TiFlash cluster resource utilization from the Performance Overview dashboard and want the core CPU, memory, and IO utilization metrics per TiFlash instance.
- Retrieval Keywords: TiFlash panel, Performance Overview dashboard, TiFlash resource utilization, CPU utilization per TiFlash instance, memory usage per TiFlash instance, IO utilization per TiFlash instance, CH-benCHmark workload, resources approaching saturation
- Follow-up Guidance: The source points to the TiFlash panel on the Performance Overview dashboard for monitoring and evaluating TiFlash cluster performance.
- Classification Note: This is classified as observability because the content describes dashboard metrics for monitoring TiFlash CPU, memory, and IO resource usage.

## Official Source Content

# TiFlash Performance Analysis and Tuning Methods

This document introduces TiFlash resource utilization and key performance metrics. You can monitor and evaluate the TiFlash cluster performance through the [TiFlash panel](https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard#tiflash) on the Performance Overview dashboard.
## Resource utilization of a TiFlash cluster

With the following three metrics, you can quickly get the resource utilization of a TiFlash cluster:

- CPU: the CPU utilization per TiFlash instance.
- Memory: the memory usage per TiFlash instance.
- IO utilization: the IO utilization per TiFlash instance.

Example: Resource utilization during [CH-benCHmark workload](https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-ch)

This TiFlash cluster consists of two nodes, each node configured with 16 cores and 48 GB of memory. During the CH-benCHmark workload, CPU utilization can reach up to 1500%, memory usage can reach up to 20 GB, and IO utilization can reach up to 91%. These metrics indicate that TiFlash node resources are approaching saturation.

![CH-TiFlash-MPP](/media/performance/tiflash/tiflash-resource-usage.png)
