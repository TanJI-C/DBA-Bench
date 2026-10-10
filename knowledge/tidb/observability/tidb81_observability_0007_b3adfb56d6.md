# Node exporter disk write latency alert

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/alert-rules.md`
- Source Title: `TiDB Cluster Alert Rules`
- Source Heading Path: `TiDB Cluster Alert Rules > Node_exporter host alert rules > Warning-level alerts > `NODE_disk_write_latency_more_than_16ms``
- Source Line Ranges: `917-932`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `alert-rules`, `node-exporter`, `disk-latency`, `write-latency`, `grafana`, `io-utilization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0007_b3adfb56d6`
- Source ID: `tidb-docs-8.1:alert-rules.md#node-disk-write-latency-more-than-16ms`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a14dbea8474c2e2ae254d0849fb5d5e5440d8621b141c299419c269251343dca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/alert-rules#node-disk-write-latency-more-than-16ms
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when an alert or search concerns the `NODE_disk_write_latency_more_than_16ms` rule, disk write latency above 16ms, or related Grafana disk performance panels.
- Retrieval Keywords: NODE_disk_write_latency_more_than_16ms, disk write latency exceeds 16ms, node_disk_write_time_seconds_total, node_disk_writes_completed_total, Grafana Disk Performance dashboard, Disk Latency panel, Disk I/O Utilization panel, write latency of the disk
- Follow-up Guidance: The source says to check the disk status in the Grafana Disk Performance dashboard, then view the Disk Latency panel and the Disk I/O Utilization panel.
- Classification Note: The official content classifies this as a warning-level Node_exporter host alert rule about disk write latency.

## Official Source Content

#### `NODE_disk_write_latency_more_than_16ms`

* Alert rule:

    `((rate(node_disk_write_time_seconds_total{device=~".+"}[5m]) / rate(node_disk_writes_completed_total{device=~".+"}[5m])) or (irate(node_disk_write_time_seconds_total{device=~".+"}[5m]) / irate(node_disk_writes_completed_total{device=~".+"}[5m])))> 16`

* Description:

    The write latency of the disk exceeds 16ms.

* Solution:

    * Check the disk status by viewing the Grafana Disk Performance dashboard.
    * Check the write latency of the disk by viewing the Disk Latency panel.
    * Check the I/O usage by viewing the Disk I/O Utilization panel.
