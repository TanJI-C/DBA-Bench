# PD schedule configuration options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-configuration-file.md`
- Source Title: `PD Configuration File`
- Source Heading Path: `PD Configuration File > `schedule` | PD Configuration File > `schedule` > `max-merge-region-size` | PD Configuration File > `schedule` > `max-merge-region-keys` | PD Configuration File > `schedule` > `patrol-region-interval` | PD Configuration File > `schedule` > `split-merge-interval` | PD Configuration File > `schedule` > `max-movable-hot-peer-size` <span class="version-mark">New in v6.1.0</span> | PD Configuration File > `schedule` > `max-snapshot-count` | PD Configuration File > `schedule` > `max-pending-peer-count` | PD Configuration File > `schedule` > `max-store-down-time` | PD Configuration File > `schedule` > `max-store-preparing-time` <span class="version-mark">New in v6.1.0</span> | PD Configuration File > `schedule` > `leader-schedule-limit` | PD Configuration File > `schedule` > `region-schedule-limit` | PD Configuration File > `schedule` > `enable-diagnostic` <span class="version-mark">New in v6.3.0</span> | PD Configuration File > `schedule` > `hot-region-schedule-limit` | PD Configuration File > `schedule` > `hot-region-cache-hits-threshold` | PD Configuration File > `schedule` > `replica-schedule-limit` | PD Configuration File > `schedule` > `merge-schedule-limit` | PD Configuration File > `schedule` > `high-space-ratio` | PD Configuration File > `schedule` > `low-space-ratio` | PD Configuration File > `schedule` > `tolerant-size-ratio` | PD Configuration File > `schedule` > `enable-cross-table-merge` | PD Configuration File > `schedule` > `region-score-formula-version` <span class="version-mark">New in v5.0</span> | PD Configuration File > `schedule` > `store-limit-version` <span class="version-mark">New in v7.1.0</span> | PD Configuration File > `schedule` > `enable-joint-consensus` <span class="version-mark">New in v5.0</span> | PD Configuration File > `schedule` > `hot-regions-write-interval` <span class="version-mark">New in v5.4.0</span> | PD Configuration File > `schedule` > `hot-regions-reserved-days` <span class="version-mark">New in v5.4.0</span> | PD Configuration File > `schedule` > `enable-heartbeat-breakdown-metrics` <span class="version-mark">New in v8.0.0</span> | PD Configuration File > `schedule` > `enable-heartbeat-concurrent-runner` <span class="version-mark">New in v8.0.0</span>`
- Source Line Ranges: `272-440`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `scheduling`, `region-merge`, `replica-checker`, `hot-region`, `snapshots`, `store-down-time`, `diagnostic`, `space-ratio`, `joint-consensus`, `heartbeat`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0127_e6ffc28fa9`
- Source ID: `tidb-docs-8.1:pd-configuration-file.md#schedule`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `65bff6077a519f78da0408cbe97c19e83c91ca8deb84c78cc082efe02b05238b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-configuration-file#schedule
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-configuration-file.md

## Retrieval Guidance

- Use When: Use this when looking up PD `schedule` configuration items for Region Merge, replicaChecker frequency, hot Region scheduling, store downtime, scheduling limits, diagnostic settings, space ratios, Joint Consensus, or Region heartbeat processing.
- Retrieval Keywords: PD `schedule`, max-merge-region-size, max-merge-region-keys, patrol-region-interval, split-merge-interval, max-movable-hot-peer-size, max-snapshot-count, max-pending-peer-count, max-store-down-time, max-store-preparing-time, leader-schedule-limit, region-schedule-limit, enable-diagnostic, hot-region-schedule-limit, hot-region-cache-hits-threshold, replica-schedule-limit, merge-schedule-limit, high-space-ratio, low-space-ratio, tolerant-size-ratio, enable-cross-table-merge, region-score-formula-version, store-limit-version, enable-joint-consensus, hot-regions-write-interval, hot-regions-reserved-days, enable-heartbeat-breakdown-metrics, enable-heartbeat-concurrent-runner, PD Control, schedule configuration items
- Follow-up Guidance: For existing clusters, use PD Control to change PD configuration items related to `schedule`, because direct modifications in the configuration file do not take effect on existing clusters.
- Classification Note: This is a PD scheduling configuration section because the content groups many `schedule` options that control scheduling behavior, limits, merge behavior, diagnostics, space handling, and heartbeat processing.

## Official Source Content

## `schedule`

Configuration items related to scheduling

> **Note:**
>
> To modify these PD configuration items related to `schedule`, choose one of the following methods based on your cluster status:
>
> - For clusters to be newly deployed, you can modify the PD configuration file directly.
> - For existing clusters, use the command-line tool [PD Control](https://docs.pingcap.com/tidb/stable/pd-control) to make changes instead. Direct modifications to these PD configuration items related to `schedule` in the configuration file do not take effect on existing clusters.
### `max-merge-region-size`

+ Controls the size limit of `Region Merge`. When the Region size is greater than the specified value, PD does not merge the Region with the adjacent Regions.
+ Default value: `20`
+ Unit: MiB
### `max-merge-region-keys`

+ Specifies the upper limit of the `Region Merge` key. When the Region key is greater than the specified value, the PD does not merge the Region with its adjacent Regions.
+ Default value: `200000`
### `patrol-region-interval`

+ Controls the running frequency at which `replicaChecker` checks the health state of a Region. The smaller this value is, the faster `replicaChecker` runs. Normally, you do not need to adjust this parameter.
+ Default value: `10ms`
### `split-merge-interval`

+ Controls the time interval between the `split` and `merge` operations on the same Region. That means a newly split Region will not be merged for a while.
+ Default value: `1h`
### `max-movable-hot-peer-size` New in v6.1.0

+ Controls the maximum Region size that can be scheduled for hot Region scheduling.
+ Default value: `512`
+ Unit: MiB
### `max-snapshot-count`

+ Controls the maximum number of snapshots that a single store receives or sends at the same time. PD schedulers depend on this configuration to prevent the resources used for normal traffic from being preempted.
+ Default value value: `64`
### `max-pending-peer-count`

+ Controls the maximum number of pending peers in a single store. PD schedulers depend on this configuration to prevent too many Regions with outdated logs from being generated on some nodes.
+ Default value: `64`
### `max-store-down-time`

+ The downtime after which PD judges that the disconnected store cannot be recovered. When PD fails to receive the heartbeat from a store after the specified period of time, it adds replicas at other nodes.
+ Default value: `30m`
### `max-store-preparing-time` New in v6.1.0

+ Controls the maximum waiting time for the store to go online. During the online stage of a store, PD can query the online progress of the store. When the specified time is exceeded, PD assumes that the store has been online and cannot query the online progress of the store again. But this does not prevent Regions from transferring to the new online store. In most scenarios, you do not need to adjust this parameter.
+ Default value: `48h`
### `leader-schedule-limit`

+ The number of Leader scheduling tasks performed at the same time
+ Default value: `4`
### `region-schedule-limit`

+ The number of Region scheduling tasks performed at the same time
+ Default value: `2048`
### `enable-diagnostic` New in v6.3.0

+ Controls whether to enable the diagnostic feature. When it is enabled, PD records the state during scheduling to help diagnose. If enabled, it might slightly affect the scheduling speed and consume more memory when there are many stores.
+ Default value: Starting from v7.1.0, the default value is changed from `false` to `true`. If your cluster is upgraded from a version earlier than v7.1.0 to v7.1.0 or later, the default value does not change.
### `hot-region-schedule-limit`

+ Controls the hot Region scheduling tasks that are running at the same time. It is independent of the Region scheduling.
+ Default value: `4`
### `hot-region-cache-hits-threshold`

+ The threshold used to set the number of minutes required to identify a hot Region. PD can participate in the hotspot scheduling only after the Region is in the hotspot state for more than this number of minutes.
+ Default value: `3`
### `replica-schedule-limit`

+ The number of Replica scheduling tasks performed at the same time
+ Default value: `64`
### `merge-schedule-limit`

+ The number of the `Region Merge` scheduling tasks performed at the same time. Set this parameter to `0` to disable `Region Merge`.
+ Default value: `8`
### `high-space-ratio`

+ The threshold ratio below which the capacity of the store is sufficient. If the space occupancy ratio of the store is smaller than this threshold value, PD ignores the remaining space of the store when performing scheduling, and balances load mainly based on the Region size. This configuration takes effect only when `region-score-formula-version` is set to `v1`.
+ Default value: `0.7`
+ Minimum value: greater than `0`
+ Maximum value: less than `1`
### `low-space-ratio`

+ The threshold ratio above which the capacity of the store is insufficient. If the space occupancy ratio of a store exceeds this threshold value, PD avoids migrating data to this store as much as possible. Meanwhile, to avoid the disk space of the corresponding store being exhausted, PD performs scheduling mainly based on the remaining space of the store.
+ Default value: `0.8`
+ Minimum value: greater than `0`
+ Maximum value: less than `1`
### `tolerant-size-ratio`

+ Controls the `balance` buffer size
+ Default value: `0` (automatically adjusts the buffer size)
+ Minimum value: `0`
### `enable-cross-table-merge`

+ Determines whether to enable the merging of cross-table Regions
+ Default value: `true`
### `region-score-formula-version` New in v5.0

+ Controls the version of the Region score formula
+ Default value: `v2`
+ Optional values: `v1` and `v2`. Compared to v1, the changes in v2 are smoother, and the scheduling jitter caused by space reclaim is improved.

> **Note:**
>
> If you have upgraded your cluster from a TiDB 4.0 version to the current version, the new formula version is automatically disabled by default to ensure consistent PD behavior before and after the upgrading. If you want to change the formula version, you need to manually switch through the `pd-ctl` setting. For details, refer to [PD Control](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules).
### `store-limit-version` New in v7.1.0

> **Warning:**
>
> Setting this configuration item to `"v2"` is an experimental feature. It is not recommended to use it in production environments.

+ Controls the version of the store limit formula
+ Default value: `v1`
+ Value options:
    + `v1`: In v1 mode, you can manually modify the `store limit` to limit the scheduling speed of a single TiKV.
    + `v2`: (experimental feature) In v2 mode, you do not need to manually set the `store limit` value, as PD dynamically adjusts it based on the capability of TiKV snapshots. For more details, refer to [Principles of store limit v2](https://docs.pingcap.com/tidb/stable/configure-store-limit#principles-of-store-limit-v2).
### `enable-joint-consensus` New in v5.0

+ Controls whether to use Joint Consensus for replica scheduling. If this configuration is disabled, PD schedules one replica at a time.
+ Default value: `true`
### `hot-regions-write-interval` New in v5.4.0

+ The time interval at which PD stores hot Region information.
+ Default value: `10m`

> **Note:**
>
> The information about hot Regions is updated every three minutes. If the interval is set to less than three minutes, updates during the interval might be meaningless.
### `hot-regions-reserved-days` New in v5.4.0

+ Specifies how many days the hot Region information is retained.
+ Default value: `7`
### `enable-heartbeat-breakdown-metrics` New in v8.0.0

+ Controls whether to enable breakdown metrics for Region heartbeats. These metrics measure the time consumed in each stage of Region heartbeat processing, facilitating analysis through monitoring.
+ Default value: `true`
### `enable-heartbeat-concurrent-runner` New in v8.0.0

+ Controls whether to enable asynchronous concurrent processing for Region heartbeats. When enabled, an independent executor handles Region heartbeat requests asynchronously and concurrently, which can improve heartbeat processing throughput and reduce latency.
+ Default value: `true`
