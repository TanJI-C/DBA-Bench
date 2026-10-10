# Node_exporter host alert rules: disk, memory, CPU, TCP, and latency alerts

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/alert-rules.md`
- Source Title: `TiDB Cluster Alert Rules`
- Source Heading Path: `TiDB Cluster Alert Rules > Node_exporter host alert rules | TiDB Cluster Alert Rules > Node_exporter host alert rules > Emergency-level alerts | TiDB Cluster Alert Rules > Node_exporter host alert rules > Emergency-level alerts > `NODE_disk_used_more_than_80%` | TiDB Cluster Alert Rules > Node_exporter host alert rules > Emergency-level alerts > `NODE_disk_inode_more_than_80%` | TiDB Cluster Alert Rules > Node_exporter host alert rules > Emergency-level alerts > `NODE_disk_readonly` | TiDB Cluster Alert Rules > Node_exporter host alert rules > Critical-level alerts | TiDB Cluster Alert Rules > Node_exporter host alert rules > Critical-level alerts > `NODE_memory_used_more_than_80%` | TiDB Cluster Alert Rules > Node_exporter host alert rules > Warning-level alerts | TiDB Cluster Alert Rules > Node_exporter host alert rules > Warning-level alerts > `NODE_node_overload` | TiDB Cluster Alert Rules > Node_exporter host alert rules > Warning-level alerts > `NODE_cpu_used_more_than_80%` | TiDB Cluster Alert Rules > Node_exporter host alert rules > Warning-level alerts > `NODE_tcp_estab_num_more_than_50000` | TiDB Cluster Alert Rules > Node_exporter host alert rules > Warning-level alerts > `NODE_disk_read_latency_more_than_32ms``
- Source Line Ranges: `786-916`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `alert-rules`, `node-exporter`, `host-monitoring`, `disk-space`, `inode`, `read-only`, `memory`, `cpu`, `load`, `tcp`, `disk-latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0006_4ce723ffa6`
- Source ID: `tidb-docs-8.1:alert-rules.md#node-exporter-host-alert-rules`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `12dd9ceb81afe9ce40787e33645e4530f55dc3bbff4c56595968b3f1e367c96b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/alert-rules#node-exporter-host-alert-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving Node_exporter host alert rules, thresholds, metrics, and troubleshooting steps for disk, inode, read-only filesystem, memory, CPU load, TCP established connections, or disk read latency.
- Retrieval Keywords: Node_exporter host alert rules, NODE_disk_used_more_than_80%, node_filesystem_avail_bytes, df -h, NODE_disk_inode_more_than_80%, node_filesystem_files_free, df -i, NODE_disk_readonly, node_filesystem_readonly, NODE_memory_used_more_than_80%, node_memory_MemTotal_bytes, free -m, NODE_node_overload, node_load5, top, NODE_cpu_used_more_than_80%, node_cpu_seconds_total{mode="idle"}, NODE_tcp_estab_num_more_than_50000, node_netstat_Tcp_CurrEstab, ss -s, netstat, NODE_disk_read_latency_more_than_32ms, node_disk_read_time_seconds_total, node_disk_reads_completed_total, Disk Performance dashboard, Disk Latency panel, Disk I/O Utilization panel
- Follow-up Guidance: The source provides follow-up checks such as Grafana Node Exporter and Disk Performance dashboards plus host commands including `df -h`, `df -i`, `free -m`, `top`, `ss -s`, and `netstat`.
- Classification Note: The supplied content is observability documentation because it lists Node_exporter alert rules with Prometheus expressions, severity levels, descriptions, and concrete diagnostic steps.

## Official Source Content

## Node_exporter host alert rules

This section gives the alert rules for the Node_exporter host.
### Emergency-level alerts
#### `NODE_disk_used_more_than_80%`

* Alert rule:

    `node_filesystem_avail_bytes{fstype=~"(ext.|xfs)", mountpoint!~"/boot"} / node_filesystem_size_bytes{fstype=~"(ext.|xfs)", mountpoint!~"/boot"} * 100 <= 20`

* Description:

    The disk space usage of the machine exceeds 80%.

* Solution:

    * Log in to the machine, run the `df -h` command to check the disk space usage.
    * Make a plan to increase the disk capacity or delete some data or increase cluster node depending on different situations.
#### `NODE_disk_inode_more_than_80%`

* Alert rule:

    `node_filesystem_files_free{fstype=~"(ext.|xfs)"} / node_filesystem_files{fstype=~"(ext.|xfs)"} * 100 < 20`

* Description:

    The inode usage of the filesystem on the machine exceeds 80%.

* Solution:

    * Log in to the machine and run the `df -i` command to view the node usage of the filesystem.
    * Make a plan to increase the disk capacity or delete some data or increase cluster node depending on different situations.
#### `NODE_disk_readonly`

* Alert rule:

    `node_filesystem_readonly{fstype=~"(ext.|xfs)"} == 1`

* Description:

    The filesystem is read-only and data cannot be written in it. It is often caused by disk failure or filesystem corruption.

* Solution:

    * Log in to the machine and create a file to test whether it is normal.
    * Check whether the disk LED is normal. If not, replace the disk and repair the filesystem of the machine.
### Critical-level alerts
#### `NODE_memory_used_more_than_80%`

* Alert rule:

    `(((node_memory_MemTotal_bytes-node_memory_MemFree_bytes-node_memory_Cached_bytes)/(node_memory_MemTotal_bytes)*100)) >= 80`

* Description:

    The memory usage of the machine exceeds 80%.

* Solution:

    * View the Memory panel of the host in the Grafana Node Exporter dashboard, and see whether Used memory is too high and Available memory is too low.
    * Log in to the machine and run the `free -m` command to view the memory usage. You can run `top` to check whether there is any abnormal process that has an overly high memory usage.
### Warning-level alerts
#### `NODE_node_overload`

* Alert rule:

    `(node_load5 / count without (cpu, mode) (node_cpu_seconds_total{mode="system"})) > 1`

* Description:

    The CPU load on the machine is relatively high.

* Solution:

    * View the CPU Usage and Load Average of the host in the Grafana Node Exporter dashboard to check whether they are too high.
    * Log in to the machine and run `top` to check the load average and the CPU usage, and see whether there is any abnormal process that has an overly high CPU usage.
#### `NODE_cpu_used_more_than_80%`

* Alert rule:

    `avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) by(instance) * 100 <= 20`

* Description:

    The CPU usage of the machine exceeds 80%.

* Solution:

    * View the CPU Usage and Load Average of the host on the Grafana Node Exporter dashboard to check whether they are too high.
    * Log in to the machine and run `top` to check the Load Average and the CPU Usage, and see whether there is any abnormal process that has an overly high CPU usage.
#### `NODE_tcp_estab_num_more_than_50000`

* Alert rule:

    `node_netstat_Tcp_CurrEstab > 50000`

* Description:

    There are more than 50,000 TCP links in the "establish" status on the machine.

* Solution:

    * Log in to the machine and run `ss -s` to check the number of TCP links in the "estab" status in the current system.
    * Run `netstat` to check whether there is any abnormal link.
#### `NODE_disk_read_latency_more_than_32ms`

* Alert rule:

    `((rate(node_disk_read_time_seconds_total{device=~".+"}[5m]) / rate(node_disk_reads_completed_total{device=~".+"}[5m])) or (irate(node_disk_read_time_seconds_total{device=~".+"}[5m]) / irate(node_disk_reads_completed_total{device=~".+"}[5m])) ) * 1000 > 32`

* Description:

    The read latency of the disk exceeds 32 ms.

* Solution:

    * Check the disk status by viewing the Grafana Disk Performance dashboard.
    * Check the read latency of the disk by viewing the Disk Latency panel.
    * Check the I/O usage by viewing the Disk I/O Utilization panel.
