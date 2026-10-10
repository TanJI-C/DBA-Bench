# Resource Manager metrics panels

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-resource-manager.md`
- Source Title: `TiDB Dashboard Resource Manager Page`
- Source Heading Path: `TiDB Dashboard Resource Manager Page > Metrics`
- Source Line Ranges: `70-82`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tikv`
- Topic Tags: `request-unit`, `resource-consumption`, `cpu-quota`, `cpu-usage`, `io-throughput`, `resource-groups`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0033_5dad900e2a`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-resource-manager.md#metrics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d0ed24aa5988e515941af72546d842e48c6bf242cb0ae63f2b5aea933b7fd71d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-resource-manager#metrics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-resource-manager.md

## Retrieval Guidance

- Use When: Use this chunk when you need the meanings of the Resource Manager metrics panels that show real-time RU consumption and TiDB or TiKV CPU and I/O usage.
- Retrieval Keywords: Metrics, Total RU Consumed, RU Consumed by Resource Groups, TiDB CPU Quota, TiDB CPU Usage, TiKV CPU Quota, TiKV CPU Usage, TiKV IO MBps, Request Units consumed in real time, overall resource consumption status
- Follow-up Guidance: The panels cover total Request Units consumed, RU consumed by resource groups, TiDB CPU quota and usage, and TiKV CPU quota, usage, and I/O throughput.
- Classification Note: This is observability content because it defines the monitoring panels and what each metric represents on the Resource Manager page.

## Official Source Content

## Metrics

By observing the metrics on the panels, you can understand the current overall resource consumption status of the cluster. The monitoring metrics and their meanings are as follows:

- Total RU Consumed: The total consumption of Request Units counted in real time.
- RU Consumed by Resource Groups: The number of Request Units consumed by resource groups in real time.
- TiDB
    - CPU Quota: The maximum CPU usage of TiDB.
    - CPU Usage: The total CPU usage of all TiDB instances.
- TiKV
    - CPU Quota: The maximum CPU usage of TiKV.
    - CPU Usage: The total CPU usage of all TiKV instances.
    - IO MBps: The total I/O throughput of all TiKV instances.
