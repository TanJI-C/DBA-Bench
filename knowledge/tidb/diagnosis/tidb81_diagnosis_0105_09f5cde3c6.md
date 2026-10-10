# Service unavailable and latency troubleshooting map

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map | TiDB Troubleshooting Map > 1. Service Unavailable | TiDB Troubleshooting Map > 1. Service Unavailable > 1.1 The client reports `Region is Unavailable` error | TiDB Troubleshooting Map > 1. Service Unavailable > 1.2 PD errors cause service unavailable | TiDB Troubleshooting Map > 2. Latency increases significantly | TiDB Troubleshooting Map > 2. Latency increases significantly > 2.1 Transient increase | TiDB Troubleshooting Map > 2. Latency increases significantly > 2.2 Persistent and significant increase`
- Source Line Ranges: `5-52`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `service-unavailable`, `region-unavailable`, `backoff`, `leader`, `oom`, `latency`, `execution-plan`, `leader-election`, `grpc`, `hibernate-region`, `slow-write`, `cpu-load`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0105_09f5cde3c6`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#tidb-troubleshooting-map`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `754ce2b9b6764fd7e0626765097d586c3d4cf781f162a62cddb27c170d0f7316`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#tidb-troubleshooting-map
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this content when troubleshooting TiDB service unavailable symptoms such as `Region is Unavailable` or major latency increases involving TiDB, TiKV, or PD.
- Retrieval Keywords: Region is Unavailable, TiKV server is busy, not leader, epoch not match, backoff, 20s by default, PD errors cause service unavailable, PD Leader election, PD OOM, Leader drops, wrong execution plan, Hibernate Region, gRPC CPU Per Thread, raft store CPU, Async apply CPU, TiKV slow write, CPU load increases
- Follow-up Guidance: The source points to related sections for `TiKV server is busy`, PD issues, wrong execution plan, frequent Leader drops, and TiKV slow write when those symptoms are involved.
- Classification Note: This is classified as diagnosis because the content maps observable service unavailable and latency symptoms to possible causes, retries, metrics, and related troubleshooting sections.

## Official Source Content

# TiDB Troubleshooting Map

This document summarizes common issues in TiDB and other components. You can use this map to diagnose and solve issues when you encounter related problems.
## 1. Service Unavailable
### 1.1 The client reports `Region is Unavailable` error

- 1.1.1 The `Region is Unavailable` error is usually because a Region is not available for a period of time. You might encounter `TiKV server is busy`, or the request to TiKV fails due to `not leader` or `epoch not match`, or the request to TiKV time out. In such cases, TiDB performs a `backoff` retry mechanism. When the `backoff` exceeds a threshold (20s by default), the error will be sent to the client. Within the `backoff` threshold, this error is not visible to the client.

- 1.1.2 Multiple TiKV instances are OOM at the same time, which causes no Leader during the OOM period. See [case-991](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case991.md) in Chinese.

- 1.1.3 TiKV reports `TiKV server is busy`, and exceeds the `backoff` time. For more details, refer to [4.3](#43-the-client-reports-the-server-is-busy-error). `TiKV server is busy` is a result of the internal flow control mechanism and should not be counted in the `backoff` time. This issue will be fixed.

- 1.1.4 Multiple TiKV instances failed to start, which causes no Leader in a Region. When multiple TiKV instances are deployed in a physical machine, the failure of the physical machine can cause no Leader in a Region if the label is not properly configured. See [case-228](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case228.md) in Chinese.

- 1.1.5 When a Follower apply is lagged in a previous epoch, after the Follower becomes a Leader, it rejects the request with `epoch not match`. See [case-958](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case958.md) in Chinese (TiKV needs to optimize its mechanism).
### 1.2 PD errors cause service unavailable

Refer to [5 PD issues](#5-pd-issues).
## 2. Latency increases significantly
### 2.1 Transient increase

- 2.1.1 Wrong TiDB execution plan causes latency increase. Refer to [3.3](#33-wrong-execution-plan).
- 2.1.2 PD Leader election issue or OOM. Refer to [5.2](#52-pd-election) and [5.3](#53-pd-oom).
- 2.1.3 A significant number of Leader drops in some TiKV instances. Refer to [4.4](#44-some-tikv-nodes-drop-leader-frequently).
- 2.1.4 For other causes, see [Troubleshoot Increased Read and Write Latency](https://docs.pingcap.com/tidb/stable/troubleshoot-cpu-issues).
### 2.2 Persistent and significant increase

- 2.2.1 TiKV single thread bottleneck

    - Too many Regions in a TiKV instance causes a single gRPC thread to be the bottleneck (Check the **Grafana** -> **TiKV-details** -> **Thread CPU/gRPC CPU Per Thread** metric). In v3.x or later versions, you can enable `Hibernate Region` to resolve the issue. See [case-612](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case612.md) in Chinese.

    - For versions earlier than v3.0, when the raftstore thread or the apply thread becomes the bottleneck (**Grafana** -> **TiKV-details** -> **Thread CPU/raft store CPU** and **Async apply CPU** metrics exceed `80%`), you can scale out TiKV (v2.x) instances or upgrade to v3.x with multi-threading. <!-- See [case-517](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case517.md) in Chinese. -->

- 2.2.2 CPU load increases.

- 2.2.3 TiKV slow write. Refer to [4.5](#45-tikv-write-is-slow).

- 2.2.4 TiDB wrong execution plan. Refer to [3.3](#33-wrong-execution-plan).

- 2.2.5 For other causes, see [Troubleshoot Increased Read and Write Latency](https://docs.pingcap.com/tidb/stable/troubleshoot-cpu-issues).
