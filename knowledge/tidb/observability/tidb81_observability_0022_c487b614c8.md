# Diagnostic report structure, basic sections, and load metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-diagnostics-report.md`
- Source Title: `TiDB Dashboard Diagnostic Report`
- Source Heading Path: `TiDB Dashboard Diagnostic Report | TiDB Dashboard Diagnostic Report > View report | TiDB Dashboard Diagnostic Report > View report > Basic information | TiDB Dashboard Diagnostic Report > View report > Basic information > Diagnostics Time Range | TiDB Dashboard Diagnostic Report > View report > Basic information > Cluster Hardware Info | TiDB Dashboard Diagnostic Report > View report > Basic information > Cluster Topology Info | TiDB Dashboard Diagnostic Report > View report > Diagnostic information | TiDB Dashboard Diagnostic Report > View report > Load Info | TiDB Dashboard Diagnostic Report > View report > Load Info > Node Load Info | TiDB Dashboard Diagnostic Report > View report > Load Info > Instance CPU Usage | TiDB Dashboard Diagnostic Report > View report > Load Info > Instance Memory Usage | TiDB Dashboard Diagnostic Report > View report > Load Info > TiKV Thread CPU Usage | TiDB Dashboard Diagnostic Report > View report > Load Info > `TiDB/PD Goroutines Count` | TiDB Dashboard Diagnostic Report > View report > Overview information`
- Source Line Ranges: `5-136`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `pd`, `tikv`, `shared`
- Topic Tags: `diagnostic-report`, `report-viewing`, `basic-information`, `cluster-hardware`, `cluster-topology`, `automatic-diagnostics`, `load-metrics`, `cpu-usage`, `memory-usage`, `tikv-threads`, `goroutines`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0022_c487b614c8`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-diagnostics-report.md#tidb-dashboard-diagnostic-report`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50f1851c1fb7147c1fa64a79c454cd1979a7a961f8cb078a5b5f6de0ddc927c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-report#tidb-dashboard-diagnostic-report
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-diagnostics-report.md

## Retrieval Guidance

- Use When: Use this chunk when describing what a TiDB Dashboard diagnostic report contains and how to interpret its basic information, diagnostic information, load information, and overview-related monitoring sections.
- Retrieval Keywords: TiDB Dashboard Diagnostic Report, View report, Basic information, Diagnostic information, Load Info, Overview information, Diagnostics Time Range, Cluster Hardware Info, Cluster Topology Info, information_schema.cluster_info, information_schema.inspection-result, Node Load Info, Instance CPU Usage, Instance Memory Usage, TiKV Thread CPU Usage, TiDB/PD Goroutines Count, TOTAL_TIME, TOTAL_COUNT, Prometheus, tidb_get_token, TiDB Grafana, HOST, INSTANCE, CPU_CORES, MEMORY, DISK, UPTIME, TYPE, STATUS_ADDRESS, VERSION, GIT_HASH, START_TIME, CONFIG_KEY, CURRENT_CONFIG_VALUE
- Follow-up Guidance: The source also notes that monitoring metrics basically correspond to the TiDB Grafana monitoring dashboard, and that TOTAL_TIME and TOTAL_COUNT are read from Prometheus so their statistics might be inaccurate.
- Classification Note: This chunk is classified under observability for the dashboard component because it explains the diagnostic report layout and monitoring/load metrics for TiDB, PD, TiKV, and cluster nodes.

## Official Source Content

# TiDB Dashboard Diagnostic Report

This document introduces the content of the diagnostic report and viewing tips. To access the cluster diagnostic page and generate reports, see [TiDB Dashboard Cluster Diagnostics Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-access).
## View report

The diagnostic report consists of the following parts:

* Basic information: Includes the time range of the diagnostic report, hardware information of the cluster, the version information of cluster topology.
* Diagnostic information: Shows the results of automatic diagnostics.
* Load information: Includes CPU, memory and other load information of the server, TiDB, PD, or TiKV.
* Overview information: Includes the consumed time and error information of each TiDB, PD, or TiKV module.
* TiDB/PD/TiKV monitoring information: Includes monitoring information of each component.
* Configuration information: Includes configuration information of each component.

An example of the diagnostic report is as follows:

![Sample report](/media/dashboard/dashboard-diagnostics-example-table.png)

In the image above, **Total Time Consume** in the top blue box is the report name. The information in the red box below explains the content of this report and the meaning of each field in the report.

In this report, some small buttons are described as follows:

* **i** icon: You can move your mouse to the **i** icon to see the explanatory note of the row.
* **expand**: Click **expand** to see details about this monitoring metric. For example, the detailed information of `tidb_get_token` in the image above includes the monitoring information of each TiDB instance's latency.
* **collapse**: Contrary to **expand**, the button is used to fold detailed monitoring information.

All monitoring metrics basically correspond to those on the TiDB Grafana monitoring dashboard. After a module is found to be abnormal, you can view more monitoring information on the TiDB Grafana.

In addition, the `TOTAL_TIME` and `TOTAL_COUNT` metrics in this report are monitoring data read from Prometheus, so calculation inaccuracy might exist in their statistics.

Each part of this report is introduced as follows.
### Basic information
#### Diagnostics Time Range

The time range for generating the diagnostics report includes the start time and end time.

![Report time range](/media/dashboard/dashboard-diagnostics-report-time-range.png)
#### Cluster Hardware Info

Cluster Hardware Info includes information such as CPU, memory, and disk of each server in the cluster.

![Cluster hardware report](/media/dashboard/dashboard-diagnostics-cluster-hardware.png)

The fields in the table above are described as follows:

* `HOST`: The IP address of the server.
* `INSTANCE`: The number of instances deployed on the server. For example, `pd * 1` means that this server has 1 PD instance deployed; `tidb * 2 pd * 1` means that this server has 2 TiDB instances and 1 PD instance deployed.
* `CPU_CORES`: Indicates the number of CPU cores (physical cores or logical cores) of the server.
* `MEMORY`: Indicates the memory size of the server. The unit is GB.
* `DISK`: Indicates the server disk size. The unit is GB.
* `UPTIME`: The uptime of the server. The unit is day.
#### Cluster Topology Info

The `Cluster Info` table shows the cluster topology information. The information in this table are from TiDB [information_schema.cluster_info](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info) system table.

![Cluster info](/media/dashboard/dashboard-diagnostics-cluster-info.png)

The fields in the table above are described as follows:

* `TYPE`: The node type.
* `INSTANCE`: The instance address(es), which is a string in the `IP:PORT` format.
* `STATUS_ADDRESS`: The HTTP API service address.
* `VERSION`: The semantic version number of the corresponding node.
* `GIT_HASH`: Git Commit Hash when compiling the node version, which is used to identify whether the two nodes are absolutely the consistent version.
* `START_TIME`: The start time of the corresponding node.
* `UPTIME`: The uptime of the corresponding node.
### Diagnostic information

TiDB has built-in automatic diagnostic results. For the description of each field, see [information_schema.inspection-result](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-inspection-result) system table.
### Load Info
#### Node Load Info

The `Node Load Info` table shows the load information of the server node, including the average value (AVG), maximum value (MAX), minimum value (MIN) of the following metrics of the server within the time range:

* CPU usage (the maximum value is `100%`)
* Memory usage
* Disk I/O usage
* Disk write latency
* Disk read latency
* Disk read bytes per second
* Disk write bytes per second
* The number of bytes received by the node network per minute
* The number of bytes sent from the node network per minute
* The number of TCP connections in use by the node
* The number of all TCP connections of the node

![Server Load Info report](/media/dashboard/dashboard-diagnostics-node-load-info.png)
#### Instance CPU Usage

The `Instance CPU Usage` table shows the average value (AVG), maximum value (MAX), and minimum value (MIN) of the CPU usage of each TiDB/PD/TiKV process. The maximum CPU usage of the process is `100% * the number of CPU logical cores`.

![Instance CPU Usage report](/media/dashboard/dashboard-diagnostics-process-cpu-usage.png)
#### Instance Memory Usage

The `Instance Memory Usage` table shows the average value (AVG), maximum value (MAX), and minimum value (MIN) of memory bytes occupied by each TiDB/PD/TiKV process.

![Instance memory usage report](/media/dashboard/dashboard-diagnostics-process-memory-usage.png)
#### TiKV Thread CPU Usage

The `TiKV Thread CPU Usage` table shows the average value (AVG), maximum value (MAX) and minimum value (MIN) of CPU usage of each module thread in TiKV. The maximum CPU usage of the process is `100% * the thread count of the corresponding configuration`.

![TiKV Thread CPU Usage report](/media/dashboard/dashboard-diagnostics-thread-cpu-usage.png)

In the table above,

* `CONFIG_KEY`: The relevant thread configuration of the corresponding module.
* `CURRENT_CONFIG_VALUE`: The current value of the configuration when the report is generated.

> **Note:**
>
> `CURRENT_CONFIG_VALUE` is the value when the report is generated, not the value within the time range of this report. Currently, some configuration values ​​of historical time cannot be obtained.
#### `TiDB/PD Goroutines Count`

The `TiDB/PD Goroutines Count` table shows the average value (AVG), maximum value (MAX), and minimum value (MIN) of the number of TiDB or PD goroutines. If the number of goroutines exceeds 2,000, the concurrency of the process is too high, which affects the overall request latency.

![TiDB/PD goroutines count report](/media/dashboard/dashboard-diagnostics-goroutines-count.png)
### Overview information
