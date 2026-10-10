# TiKV anomalies thread bottlenecks and CPU load

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-cpu-issues.md`
- Source Title: `Troubleshoot Increased Read and Write Latency`
- Source Heading Path: `Troubleshoot Increased Read and Write Latency > Common causes > TiKV anomalies | Troubleshoot Increased Read and Write Latency > Common causes > TiKV anomalies > Phenomenon | Troubleshoot Increased Read and Write Latency > Common causes > TiKV anomalies > Possible reasons | Troubleshoot Increased Read and Write Latency > Common causes > Bottleneck of a single TiKV thread | Troubleshoot Increased Read and Write Latency > Common causes > CPU load increases | Troubleshoot Increased Read and Write Latency > Common causes > CPU load increases > Phenomenon | Troubleshoot Increased Read and Write Latency > Common causes > CPU load increases > Possible reasons`
- Source Line Ranges: `69-110`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `dashboard`
- Topic Tags: `latency`, `kv-cmd-duration`, `grpc`, `reelection`, `oom`, `write-stall`, `network-isolation`, `thread-cpu`, `hotspot`, `slow-queries`, `scale-out`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0128_23b2ee3274`
- Source ID: `tidb-docs-8.1:troubleshoot-cpu-issues.md#tikv-anomalies`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `93c98165aa88cccf6798cd9080a6fe22d7ff69b26268be832c215133bd91848c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-cpu-issues#tikv-anomalies
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-cpu-issues.md

## Retrieval Guidance

- Use When: Use this chunk when TiKV-side latency or CPU bottlenecks appear through increased KV Cmd Duration, gRPC duration differences, re-election, OOM, write stall, single-thread saturation, hotspots, or high overall load.
- Retrieval Keywords: TiKV anomalies, KV Cmd Duration, gRPC duration, KV duration, systemd, dmesg, THP, Transparent Hugepage, server is busy, block-cache, storage.block-cache capacity, response size, network outbound, Thread CPU/gRPC CPU Per Thread, raft store CPU, Async apply CPU, Hibernate Region, hotspot issue, slow queries, expensive queries
- Follow-up Guidance: The content suggests checking TiKV logs, dmesg, Grafana TiKV-details panels, and TiDB slow or expensive queries to verify whether the issue is network latency, restart or re-election, OOM, write stall, thread bottlenecks, or high load.
- Classification Note: This is classified as diagnosis content because it maps TiKV latency and CPU symptoms to specific possible reasons and the exact metrics or logs used to confirm them.

## Official Source Content

### TiKV anomalies
#### Phenomenon

The `KV Cmd Duration` metric in the monitor increases abnormally. This metric represents the duration between the time that TiDB sends a request to TiKV and the time that TiDB receives the response.
#### Possible reasons

* Check the `gRPC duration` metric. This metric represents the total duration of a gRPC request in TiKV. You can find out the potential network issue by comparing `gRPC duration` of TiKV and `KV duration` of TiDB. For example, the gRPC duration is short but the KV duration of TiDB is long, which indicates that the network latency between TiDB and TiKV might be high, or that the NIC bandwidth between TiDB and TiKV is fully occupied.

* Re-election because TiKV is restarted.
    * After TiKV panics, it is pulled up by `systemd` and runs normally. You can check whether panic has occurred by viewing the TiKV log. Because this issue is unexpected, [report a bug](https://github.com/tikv/tikv/issues/new?template=bug-report.md) if it happens.
    * TiKV is stopped or killed by a third party and then pulled up by `systemd`. Check the cause by viewing `dmesg` and the TiKV log.
    * TiKV is OOM, which causes restart.
    * TiKV is hung because of dynamically adjusting `THP` (Transparent Hugepage).

* Check monitor: TiKV RocksDB encounters write stall and thus results in re-election. You can check if the monitor **Grafana** -> **TiKV-details** -> **errors** shows `server is busy`.

* Re-election because of network isolation.

* If the `block-cache` configuration is too large, it might cause TiKV OOM. To verify the cause of the problem, check the `block cache size` of RocksDB by selecting the corresponding instance in the monitor **Grafana** -> **TiKV-details**. Meanwhile, check whether the `[storage.block-cache] capacity = # "1GB"`parameter is set properly. By default, TiKV's `block-cache` is set to `45%` of the total memory of the machine. You need to explicitly specify this parameter when you deploy TiKV in the container, because TiKV obtains the memory of the physical machine, which might exceed the memory limit of the container.

* Coprocessor receives many large queries and returns a large volume of data. gRPC fails to send data as quickly as the coprocessor returns data, which results in OOM. To verify the cause, you can check whether `response size` exceeds the `network outbound` traffic by viewing the monitor **Grafana** -> **TiKV-details** -> **coprocessor overview**.
### Bottleneck of a single TiKV thread

There are some single threads in TiKV that might become the bottleneck.

* Too many Regions in a TiKV instance causes a single gRPC thread to be the bottleneck (Check the **Grafana** -> **TiKV-details** -> **Thread CPU/gRPC CPU Per Thread** metric). In v3.x or later versions, you can enable `Hibernate Region` to resolve the issue.
* For versions earlier than v3.0, when the raftstore thread or the apply thread becomes the bottleneck (**Grafana** -> **TiKV-details** -> **Thread CPU/raft store CPU** and **Async apply CPU** metrics exceed `80%`), you can scale out TiKV (v2.x) instances or upgrade to v3.x with multi-threading.
### CPU load increases
#### Phenomenon

The usage of CPU resources becomes the bottleneck.
#### Possible reasons

* Hotspot issue
* High overall load. Check the slow queries and expensive queries of TiDB. Optimize the executing queries by adding indexes or executing queries in batches. Another solution is to scale out the cluster.
