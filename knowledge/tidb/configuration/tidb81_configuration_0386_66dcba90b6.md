# TiKV quota limiter settings for foreground and background workloads

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > quota > `max-delay-duration` <span class="version-mark">New in v6.0.0</span> | TiKV Configuration File > quota > Foreground Quota Limiter | TiKV Configuration File > quota > Foreground Quota Limiter > `foreground-cpu-time` <span class="version-mark">New in v6.0.0</span> | TiKV Configuration File > quota > Foreground Quota Limiter > `foreground-write-bandwidth` <span class="version-mark">New in v6.0.0</span> | TiKV Configuration File > quota > Foreground Quota Limiter > `foreground-read-bandwidth` <span class="version-mark">New in v6.0.0</span> | TiKV Configuration File > quota > Background Quota Limiter | TiKV Configuration File > quota > Background Quota Limiter > `background-cpu-time` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > quota > Background Quota Limiter > `background-write-bandwidth` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > quota > Background Quota Limiter > `background-read-bandwidth` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > quota > Background Quota Limiter > `enable-auto-tune` <span class="version-mark">New in v6.2.0</span>`
- Source Line Ranges: `2469-2531`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `quota`, `resource-limiting`, `foreground-requests`, `background-requests`, `cpu`, `bandwidth`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0386_66dcba90b6`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#max-delay-duration-span-class-version-mark-new-in-v6-0-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e32fa00dd185d8fabd0f8d6ec273646053efb2669cb73d94a149efcaa879217e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#max-delay-duration-span-class-version-mark-new-in-v6-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiKV quota limiter configuration that caps foreground or background CPU time and read/write bandwidth, or for the meaning of max-delay-duration request waiting time.
- Retrieval Keywords: quota, max-delay-duration, foreground Quota Limiter, background Quota Limiter, foreground-cpu-time, foreground-write-bandwidth, foreground-read-bandwidth, background-cpu-time, background-write-bandwidth, background-read-bandwidth, enable-auto-tune, soft limit on CPU resources, soft limit on bandwidth, request is forced to wait, experimental feature
- Follow-up Guidance: The content also states that Background Quota Limiter is an experimental feature introduced in TiDB v6.2.0 and describes enable-auto-tune for dynamically adjusting background quota based on TiKV load.
- Classification Note: This is classified as configuration because the content defines TiKV configuration items, defaults, units, and recommended settings for quota limiting.

## Official Source Content

### `max-delay-duration` New in v6.0.0

+ The maximum time that a single read or write request is forced to wait before it is processed in the foreground.
+ Default value: `500ms`
+ Recommended setting: It is recommended to use the default value in most cases. If out of memory (OOM) or violent performance jitter occurs in the instance, you can set the value to 1S to make the request waiting time shorter than 1 second.
### Foreground Quota Limiter

Configuration items related to foreground Quota Limiter.

Suppose that your machine on which TiKV is deployed has limited resources, for example, with only 4v CPU and 16 G memory. In this situation, the foreground of TiKV might process too many read and write requests so that the CPU resources used by the background are occupied to help process such requests, which affects the performance stability of TiKV. To avoid this situation, you can use the foreground quota-related configuration items to limit the CPU resources to be used by the foreground. When a request triggers Quota Limiter, the request is forced to wait for a while for TiKV to free up CPU resources. The exact waiting time depends on the number of requests, and the maximum waiting time is no longer than the value of [`max-delay-duration`](#max-delay-duration-new-in-v600).
#### `foreground-cpu-time` New in v6.0.0

+ The soft limit on the CPU resources used by TiKV foreground to process read and write requests.
+ Default value: `0` (which means no limit)
+ Unit: millicpu (for example, `1500` means that the foreground requests consume 1.5v CPU)
+ Recommended setting: For the instance with more than 4 cores, use the default value `0`. For the instance with 4 cores, setting the value to the range of `1000` and `1500` can make a balance. For the instance with 2 cores, keep the value smaller than `1200`.
#### `foreground-write-bandwidth` New in v6.0.0

+ The soft limit on the bandwidth with which transactions write data.
+ Default value: `0KiB` (which means no limit)
+ Recommended setting: Use the default value `0` in most cases unless the `foreground-cpu-time` setting is not enough to limit the write bandwidth. For such an exception, it is recommended to set the value smaller than `50MiB` in the instance with 4 or less cores.
#### `foreground-read-bandwidth` New in v6.0.0

+ The soft limit on the bandwidth with which transactions and the Coprocessor read data.
+ Default value: `0KiB` (which means no limit)
+ Recommended setting: Use the default value `0` in most cases unless the `foreground-cpu-time` setting is not enough to limit the read bandwidth. For such an exception, it is recommended to set the value smaller than `20MiB` in the instance with 4 or less cores.
### Background Quota Limiter

Configuration items related to background Quota Limiter.

Suppose that your machine on which TiKV is deployed has limited resources, for example, with only 4v CPU and 16 G memory. In this situation, the background of TiKV might process too many calculations and read and write requests, so that the CPU resources used by the foreground are occupied to help process such requests, which affects the performance stability of TiKV. To avoid this situation, you can use the background quota-related configuration items to limit the CPU resources to be used by the background. When a request triggers Quota Limiter, the request is forced to wait for a while for TiKV to free up CPU resources. The exact waiting time depends on the number of requests, and the maximum waiting time is no longer than the value of [`max-delay-duration`](#max-delay-duration-new-in-v600).

> **Warning:**
>
> - Background Quota Limiter is an experimental feature introduced in TiDB v6.2.0, and it is **NOT** recommended to use it in the production environment.
> - This feature is only suitable for environments with limited resources to ensure that TiKV can run stably in those environments. If you enable this feature in an environment with rich resources, performance degradation might occur when the amount of requests reaches a peak.
#### `background-cpu-time` New in v6.2.0

+ The soft limit on the CPU resources used by TiKV background to process read and write requests.
+ Default value: `0` (which means no limit)
+ Unit: millicpu (for example, `1500` means that the background requests consume 1.5v CPU)
#### `background-write-bandwidth` New in v6.2.0

+ The soft limit on the bandwidth with which background transactions write data.
+ Default value: `0KiB` (which means no limit)
#### `background-read-bandwidth` New in v6.2.0

+ The soft limit on the bandwidth with which background transactions and the Coprocessor read data.
+ Default value: `0KiB` (which means no limit)
#### `enable-auto-tune` New in v6.2.0

+ Determines whether to enable the auto-tuning of quota. If this configuration item is enabled, TiKV dynamically adjusts the quota for the background requests based on the load of TiKV instances.
+ Default value: `false` (which means that the auto-tuning is disabled)
