# TiKV causal-ts cache and resource control settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > causal-ts <span class="version-mark">New in v6.1.0</span> | TiKV Configuration File > causal-ts <span class="version-mark">New in v6.1.0</span> > `alloc-ahead-buffer` <span class="version-mark">New in v6.4.0</span> | TiKV Configuration File > causal-ts <span class="version-mark">New in v6.1.0</span> > `renew-interval` | TiKV Configuration File > causal-ts <span class="version-mark">New in v6.1.0</span> > `renew-batch-min-size` | TiKV Configuration File > causal-ts <span class="version-mark">New in v6.1.0</span> > `renew-batch-max-size` <span class="version-mark">New in v6.4.0</span> | TiKV Configuration File > resource-control | TiKV Configuration File > resource-control > `enabled` <span class="version-mark">New in v6.6.0</span>`
- Source Line Ranges: `2532-2579`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `tidb`
- Topic Tags: `causal-ts`, `tso`, `api-v2`, `resource-control`, `request-unit`, `scheduling`, `latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0387_a349a7643b`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#causal-ts-span-class-version-mark-new-in-v6-1-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5748965591bd81fa52aff4741ec44948f2fa7b0111ddfff0968d69995e4af445`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#causal-ts-span-class-version-mark-new-in-v6-1-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiKV causal-ts timestamp cache settings for API V2 or for the resource-control enabled switch that schedules foreground requests by Request Unit.
- Retrieval Keywords: causal-ts, storage.api-version = 2, alloc-ahead-buffer, renew-interval, renew-batch-min-size, renew-batch-max-size, TSO cache, timestamp refresh, tso-update-physical-interval, PD leader fails, TiKV-RAW, Causal timestamp, TSO batch size, resource-control, enabled, Request Unit, RU, priority queue, tidb_enable_resource_control
- Follow-up Guidance: The content links causal-ts tuning with PD tso-update-physical-interval and states that TiKV resource-control.enabled only works when tidb_enable_resource_control is enabled on TiDB.
- Classification Note: This is classified as configuration because the content specifies TiKV configuration items and their defaults for causal-ts caching and storage-layer resource control scheduling.

## Official Source Content

## causal-ts New in v6.1.0

Configuration items related to getting the timestamp when TiKV API V2 is enabled (`storage.api-version = 2`).

To reduce write latency, TiKV periodically fetches and caches a batch of timestamps locally. Cached timestamps help avoid frequent access to PD and allow short-term TSO service failure.
### `alloc-ahead-buffer` New in v6.4.0

+ The pre-allocated TSO cache size (in duration).
+ Indicates that TiKV pre-allocates the TSO cache based on the duration specified by this configuration item. TiKV estimates the TSO usage based on the previous period, and requests and caches TSOs satisfying `alloc-ahead-buffer` locally.
+ This configuration item is often used to increase the tolerance of PD failures when TiKV API V2 is enabled (`storage.api-version = 2`).
+ Increasing the value of this configuration item might result in more TSO consumption and memory overhead of TiKV. To obtain enough TSOs, it is recommended to decrease the [`tso-update-physical-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#tso-update-physical-interval) configuration item of PD.
+ According to the test, when `alloc-ahead-buffer` is in its default value, and the PD leader fails and switches to another node, the write request will experience a short-term increase in latency and a decrease in QPS (about 15%).
+ To avoid the impact on the business, you can configure `tso-update-physical-interval = "1ms"` in PD and the following configuration items in TiKV:
    + `causal-ts.alloc-ahead-buffer = "6s"`
    + `causal-ts.renew-batch-max-size = 65536`
    + `causal-ts.renew-batch-min-size = 2048`
+ Default value: `3s`
### `renew-interval`

+ The interval at which the locally cached timestamps are updated.
+ At an interval of `renew-interval`, TiKV starts a batch of timestamp refresh and adjusts the number of cached timestamps according to the timestamp consumption in the previous period and the setting of [`alloc-ahead-buffer`](#alloc-ahead-buffer-new-in-v640). If you set this parameter to too large a value, the latest TiKV workload changes are not reflected in time. If you set this parameter to too small a value, the load of PD increases. If the write traffic is strongly fluctuating, if timestamps are frequently exhausted, and if write latency increases, you can set this parameter to a smaller value. At the same time, you should also consider the load of PD.
+ Default value: `"100ms"`
### `renew-batch-min-size`

+ The minimum number of TSOs in a timestamp request.
+ TiKV adjusts the number of cached timestamps according to the timestamp consumption in the previous period. If only a few TSOs are required, TiKV reduces the TSOs requested until the number reaches `renew-batch-min-size`. If large bursty write traffic often occurs in your application, you can set this parameter to a larger value as appropriate. Note that this parameter is the cache size for a single tikv-server. If you set the parameter to too large a value and the cluster contains many tikv-servers, the TSO consumption will be too fast.
+ In the **TiKV-RAW** \> **Causal timestamp** panel in Grafana, **TSO batch size** is the number of locally cached timestamps that has been dynamically adjusted according to the application workload. You can refer to this metric to adjust `renew-batch-min-size`.
+ Default value: `100`
### `renew-batch-max-size` New in v6.4.0

+ The maximum number of TSOs in a timestamp request.
+ In a default TSO physical time update interval (`50ms`), PD provides at most 262144 TSOs. When requested TSOs exceed this number, PD provides no more TSOs. This configuration item is used to avoid exhausting TSOs and the reverse impact of TSO exhaustion on other businesses. If you increase the value of this configuration item to improve high availability, you need to decrease the value of [`tso-update-physical-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#tso-update-physical-interval) at the same time to get enough TSOs.
+ Default value: `8192`
## resource-control

Configuration items related to resource control of the TiKV storage layer.
### `enabled` New in v6.6.0

+ Controls whether to enable scheduling for user foreground read/write requests according to [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru) of the corresponding resource groups. For information about TiDB resource groups and resource control, see [TiDB resource control](https://docs.pingcap.com/tidb/stable/tidb-resource-control).
+ Enabling this configuration item only works when [`tidb_enable_resource_control](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_resource_control-new-in-v660) is enabled on TiDB. When this configuration item is enabled, TiKV will use the priority queue to schedule the queued read/write requests from foreground users. The scheduling priority of a request is inversely related to the amount of resources already consumed by the resource group that receives this request, and positively related to the quota of the corresponding resource group.
+ Default value: `true`, which means scheduling based on the RU of the resource group is enabled.
