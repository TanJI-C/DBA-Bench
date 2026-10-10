# Tune PD for high-QPS large-scale TiDB clusters

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/best-practices-on-public-cloud.md`
- Source Title: `TiDB Best Practices on Public Cloud`
- Source Heading Path: `TiDB Best Practices on Public Cloud > Tune PD for a large-scale TiDB cluster with high QPS | TiDB Best Practices on Public Cloud > Tune PD for a large-scale TiDB cluster with high QPS > Symptoms of PD limitation | TiDB Best Practices on Public Cloud > Tune PD for a large-scale TiDB cluster with high QPS > Tune PD performance | TiDB Best Practices on Public Cloud > Tune PD for a large-scale TiDB cluster with high QPS > Tune PD performance > Adjust PD configuration | TiDB Best Practices on Public Cloud > Tune PD for a large-scale TiDB cluster with high QPS > Tune PD performance > Adjust a TiDB global variable | TiDB Best Practices on Public Cloud > Tune PD for a large-scale TiDB cluster with high QPS > Tune PD performance > Adjust TiKV configuration | TiDB Best Practices on Public Cloud > After tuning`
- Source Line Ranges: `155-206`
- Source Scope: `cloud`
- Primary Component: `pd`
- Related Components: `tidb`, `tikv`, `cloud`
- Topic Tags: `high-qps`, `tso`, `cpu-utilization`, `pd-tuning`, `global-variable`, `region-size`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0058_63cb37b821`
- Source ID: `tidb-docs-8.1:best-practices/best-practices-on-public-cloud.md#tune-pd-for-a-large-scale-tidb-cluster-with-high-qps`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b667fc3c3903559593f2fb72986fdb8c8da822221af96bb096e487ac91198f4e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/best-practices-on-public-cloud#tune-pd-for-a-large-scale-tidb-cluster-with-high-qps
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/best-practices-on-public-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about PD tuning for a large-scale TiDB cluster with high QPS, high TSO request load, or high PD leader CPU utilization.
- Retrieval Keywords: Tune PD for a large-scale TiDB cluster with high QPS, PD limitation, Tso, Timestamp Oracle, QPS exceeds 1 million, TSO requests per second exceed 162,000, CPU utilization 4,600%, tso-update-physical-interval, 10ms, 50ms, tidb_tso_client_batch_max_wait_time, set global tidb_tso_client_batch_max_wait_time = 2, region-split-size, 256MB, 96MB, PD server TSO handle time, P999
- Follow-up Guidance: The source also includes the observed results after tuning: TSO requests per second decreased to 64,800, CPU utilization dropped to about 1,400%, and the P999 of PD server TSO handle time decreased from 2ms to 0.5ms.
- Classification Note: This is classified as performance content because it focuses on relieving PD bottlenecks under high-QPS and high-TSO workloads through PD, TiDB, and TiKV tuning parameters.

## Official Source Content

## Tune PD for a large-scale TiDB cluster with high QPS

In a TiDB cluster, a single active Placement Driver (PD) server is used to handle crucial tasks such as serving the TSO (Timestamp Oracle) and processing requests. However, relying on a single active PD server can limit the scalability of TiDB clusters.
### Symptoms of PD limitation

The following diagrams show the symptoms of a large-scale TiDB cluster consisting of three PD servers, each equipped with 56 CPUs. From these diagrams, it is observed that when the query per second (QPS) exceeds 1 million and the TSO (Timestamp Oracle) requests per second exceed 162,000, the CPU utilization reaches approximately 4,600%. This high CPU utilization indicates that the PD leader is experiencing a significant load and is running out of available CPU resources.

![pd-server-cpu](/media/performance/public-cloud-best-practice/baseline_cpu.png)
![pd-server-metrics](/media/performance/public-cloud-best-practice/baseline_metrics.png)
### Tune PD performance

To address the high CPU utilization issue in the PD server, you can make the following tuning adjustments:
#### Adjust PD configuration

[`tso-update-physical-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#tso-update-physical-interval): This parameter controls the interval at which the PD server updates the physical TSO batch. By reducing the interval, the PD server can allocate TSO batches more frequently, thereby reducing the waiting time for the next allocation.

```
tso-update-physical-interval = "10ms" # default: 50ms
```
#### Adjust a TiDB global variable

In addition to the PD configuration, enabling the TSO client batch wait feature can further optimize the TSO client's behavior. To enable this feature, you can set the global variable [`tidb_tso_client_batch_max_wait_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_tso_client_batch_max_wait_time-new-in-v530) to a non-zero value.

```
set global tidb_tso_client_batch_max_wait_time = 2; # default: 0
```
#### Adjust TiKV configuration

To reduce the number of Regions and alleviate the heartbeat overhead on the system, it is recommended to increase the Region size in the TiKV configuration from `96MB` to `256MB`.

```
[coprocessor]
  region-split-size = "256MB"
```
## After tuning

After the tuning, the following effects can be observed:

- The TSO requests per second are decreased to 64,800.
- The CPU utilization is significantly reduced from approximately 4,600% to 1,400%.
- The P999 value of `PD server TSO handle time` is decreased from 2ms to 0.5ms.

These improvements indicate that the tuning adjustments have successfully reduced the CPU utilization of the PD server while maintaining stable TSO handling performance.

![pd-server-cpu](/media/performance/public-cloud-best-practice/after_tuning_cpu.png)
![pd-server-metrics](/media/performance/public-cloud-best-practice/after_tuning_metrics.png)
