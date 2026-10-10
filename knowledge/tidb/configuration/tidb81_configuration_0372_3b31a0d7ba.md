# Raftstore log, region, heartbeat, snapshot, and peer state settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > raftstore > `raft-min-election-timeout-ticks` | TiKV Configuration File > raftstore > `raft-max-election-timeout-ticks` | TiKV Configuration File > raftstore > `raft-max-size-per-msg` | TiKV Configuration File > raftstore > `raft-max-inflight-msgs` | TiKV Configuration File > raftstore > `raft-entry-max-size` | TiKV Configuration File > raftstore > `raft-log-compact-sync-interval` <span class="version-mark">New in v5.3</span> | TiKV Configuration File > raftstore > `raft-log-gc-tick-interval` | TiKV Configuration File > raftstore > `raft-log-gc-threshold` | TiKV Configuration File > raftstore > `raft-log-gc-count-limit` | TiKV Configuration File > raftstore > `raft-log-gc-size-limit` | TiKV Configuration File > raftstore > `raft-log-reserve-max-ticks` <span class="version-mark">New in v5.3</span> | TiKV Configuration File > raftstore > `raft-engine-purge-interval` | TiKV Configuration File > raftstore > `raft-entry-cache-life-time` | TiKV Configuration File > raftstore > `max-apply-unpersisted-log-limit` <span class="version-mark">New in v8.1.0</span> | TiKV Configuration File > raftstore > `hibernate-regions` | TiKV Configuration File > raftstore > `split-region-check-tick-interval` | TiKV Configuration File > raftstore > `region-split-check-diff` | TiKV Configuration File > raftstore > `region-compact-check-interval` | TiKV Configuration File > raftstore > `region-compact-check-step` | TiKV Configuration File > raftstore > `region-compact-min-tombstones` | TiKV Configuration File > raftstore > `region-compact-tombstones-percent` | TiKV Configuration File > raftstore > `region-compact-min-redundant-rows` <span class="version-mark">New in v7.1.0</span> | TiKV Configuration File > raftstore > `region-compact-redundant-rows-percent` <span class="version-mark">New in v7.1.0</span> | TiKV Configuration File > raftstore > `report-region-buckets-tick-interval` <span class="version-mark">New in v6.1.0</span> | TiKV Configuration File > raftstore > `pd-heartbeat-tick-interval` | TiKV Configuration File > raftstore > `pd-store-heartbeat-tick-interval` | TiKV Configuration File > raftstore > `pd-report-min-resolved-ts-interval` <span class="version-mark">New in v7.6.0</span> | TiKV Configuration File > raftstore > `snap-mgr-gc-tick-interval` | TiKV Configuration File > raftstore > `snap-gc-timeout` | TiKV Configuration File > raftstore > `snap-generator-pool-size` <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > raftstore > `lock-cf-compact-interval` | TiKV Configuration File > raftstore > `lock-cf-compact-bytes-threshold` | TiKV Configuration File > raftstore > `notify-capacity` | TiKV Configuration File > raftstore > `messages-per-tick` | TiKV Configuration File > raftstore > `max-peer-down-duration` | TiKV Configuration File > raftstore > `max-leader-missing-duration` | TiKV Configuration File > raftstore > `abnormal-leader-missing-duration` | TiKV Configuration File > raftstore > `peer-stale-state-check-interval` | TiKV Configuration File > raftstore > `leader-transfer-max-log-lag` | TiKV Configuration File > raftstore > `max-snapshot-file-raw-size` <span class="version-mark">New in v6.1.0</span>`
- Source Line Ranges: `669-965`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `raft`, `raftstore`, `election`, `log-gc`, `snapshot`, `region-split`, `compaction`, `deprecated`, `heartbeat`, `resolved-ts`, `peer-state`, `leader-transfer`, `experimental`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0372_3b31a0d7ba`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#raft-min-election-timeout-ticks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `530911d6db7e1893c39febd23ff9afce9a3263f6952d34d2a973f444bbcfa044`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-min-election-timeout-ticks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV raftstore configuration details for Raft election timeouts, log GC and compaction thresholds, heartbeat and resolved-ts reporting intervals, snapshot generation and cleanup, Hibernate Region behavior, peer stale or leader-missing state timing, leader transfer log lag, or deprecated region compaction settings.
- Retrieval Keywords: raft-min-election-timeout-ticks, raft-max-election-timeout-ticks, raft-max-size-per-msg, raft-max-inflight-msgs, raft-entry-max-size, raft-log-compact-sync-interval, raft-log-gc-tick-interval, raft-log-gc-threshold, raft-log-gc-count-limit, raft-log-gc-size-limit, raft-log-reserve-max-ticks, raft-engine-purge-interval, raft-entry-cache-life-time, max-apply-unpersisted-log-limit, hibernate-regions, split-region-check-tick-interval, region-split-check-diff, region-compact-check-interval, region-compact-check-step, region-compact-min-tombstones, region-compact-tombstones-percent, region-compact-min-redundant-rows, region-compact-redundant-rows-percent, report-region-buckets-tick-interval, pd-heartbeat-tick-interval, pd-store-heartbeat-tick-interval, pd-report-min-resolved-ts-interval, snap-mgr-gc-tick-interval, snap-gc-timeout, snap-generator-pool-size, lock-cf-compact-interval, lock-cf-compact-bytes-threshold, notify-capacity, messages-per-tick, max-peer-down-duration, max-leader-missing-duration, abnormal-leader-missing-duration, peer-stale-state-check-interval, leader-transfer-max-log-lag, max-snapshot-file-raw-size, Raft election is initiated, deleting Raft logs is scheduled, Region split is needed, heartbeat to PD is triggered, report Resolved TS to the PD leader, snapshot file will be split into multiple files
- Follow-up Guidance: This chunk also notes renamed, deprecated, experimental, and warning-marked items such as `pd-report-min-resolved-ts-interval`, `region-compact-*`, `report-region-buckets-tick-interval`, and `max-apply-unpersisted-log-limit`.
- Classification Note: The content is classified as TiKV self-managed configuration because it defines raftstore configuration items, defaults, limits, intervals, and deprecation or warning notes in the TiKV configuration file.

## Official Source Content

### `raft-min-election-timeout-ticks`

> **Note:**
>
> This configuration item cannot be queried via SQL statements but can be configured in the configuration file.

+ The minimum number of ticks during which the Raft election is initiated. If the number is `0`, the value of `raft-election-timeout-ticks` is used. The value of this parameter must be greater than or equal to `raft-election-timeout-ticks`.
+ Default value: `0`
+ Minimum value: `0`
### `raft-max-election-timeout-ticks`

> **Note:**
>
> This configuration item cannot be queried via SQL statements but can be configured in the configuration file.

+ The maximum number of ticks during which the Raft election is initiated. If the number is `0`, the value of `raft-election-timeout-ticks` * `2` is used.
+ Default value: `0`
+ Minimum value: `0`
### `raft-max-size-per-msg`

+ The soft limit on the size of a single message packet
+ Default value: `"1MiB"`
+ Minimum value: greater than `0`
+ Maximum value: `3GiB`
+ Unit: KiB|MiB|GiB
### `raft-max-inflight-msgs`

+ The number of Raft logs to be confirmed. If this number is exceeded, the Raft state machine slows down log sending.
+ Default value: `256`
+ Minimum value: greater than `0`
+ Maximum value: `16384`
### `raft-entry-max-size`

+ The hard limit on the maximum size of a single log
+ Default value: `"8MiB"`
+ Minimum value: `0`
+ Unit: MiB|GiB
### `raft-log-compact-sync-interval` New in v5.3

+ The time interval to compact unnecessary Raft logs
+ Default value: `"2s"`
+ Minimum value: `"0s"`
### `raft-log-gc-tick-interval`

+ The time interval at which the polling task of deleting Raft logs is scheduled. `0` means that this feature is disabled.
+ Default value: `"3s"`
+ Minimum value: `"0s"`
### `raft-log-gc-threshold`

+ The soft limit on the maximum allowable count of residual Raft logs
+ Default value: `50`
+ Minimum value: `1`
### `raft-log-gc-count-limit`

+ The hard limit on the allowable number of residual Raft logs
+ Default value: the number of logs that can fit into three-fourths of the Region size, calculated assuming each log is 1 KiB
+ Minimum value: `0`
### `raft-log-gc-size-limit`

+ The hard limit on the allowable size of residual Raft logs
+ Default value: 3/4 of the Region size
+ Minimum value: greater than `0`
### `raft-log-reserve-max-ticks` New in v5.3

+ After the number of ticks set by this configuration item passes, even if the number of residual Raft logs does not reach the value set by `raft-log-gc-threshold`, TiKV still performs garbage collection (GC) to these logs.
+ Default value: `6`
+ Minimum value: greater than `0`
### `raft-engine-purge-interval`

+ The interval for purging old TiKV log files to recycle disk space as soon as possible. Raft engine is a replaceable component, so the purging process is needed for some implementations.
+ Default value: `"10s"`
### `raft-entry-cache-life-time`

+ The maximum remaining time allowed for the log cache in memory
+ Default value: `"30s"`
+ Minimum value: `0`
### `max-apply-unpersisted-log-limit` New in v8.1.0

> **Warning:**
>
> The feature controlled by this variable is not fully functional in the current TiDB version. Do not change the default value.

+ The maximum number of committed but not persisted Raft logs that can be applied.

    + Setting this configuration item to a value greater than `0` enables the TiKV node to apply committed but not persisted Raft logs in advance, effectively reducing long-tail latency caused by IO jitter on that node. However, it might also increase the memory usage of TiKV and the disk space occupied by Raft logs.
    + Setting this configuration item to `0` disables this feature, meaning that TiKV must wait until Raft logs are both committed and persisted before applying them. This default behavior is consistent with the behavior before v8.1.0.

+ Default value: `0`
+ Minimum value: `0`
### `hibernate-regions`

+ Enables or disables Hibernate Region. When this option is enabled, a Region idle for a long time is automatically set as hibernated. This reduces the extra overhead caused by heartbeat messages between the Raft leader and the followers for idle Regions. You can use `peer-stale-state-check-interval` to modify the heartbeat interval between the leader and the followers of hibernated Regions.
+ Default value: `true` in v5.0.2 and later versions; `false` in versions before v5.0.2
### `split-region-check-tick-interval`

+ Specifies the interval at which to check whether the Region split is needed. `0` means that this feature is disabled.
+ Default value: `"10s"`
+ Minimum value: `0`
### `region-split-check-diff`

+ The maximum value by which the Region data is allowed to exceed before Region split
+ Default value: 1/16 of the Region size.
+ Minimum value: `0`
### `region-compact-check-interval`

> **Warning:**
>
> Starting from v7.5.7, this configuration item is deprecated and replaced by [`gc.auto-compaction.check-interval`](#check-interval-new-in-v757).

+ The time interval at which to check whether it is necessary to manually trigger RocksDB compaction. `0` means that this feature is disabled.
+ Default value: `"5m"`
+ Minimum value: `0`
### `region-compact-check-step`

> **Warning:**
>
> Starting from v7.5.7, this configuration item is deprecated.

+ The number of Regions checked at one time for each round of manual compaction
+ Default value:

    + When `storage.engine="raft-kv"`, the default value is `100`.
    + When `storage.engine="partitioned-raft-kv"`, the default value is `5`.
+ Minimum value: `0`
### `region-compact-min-tombstones`

> **Warning:**
>
> Starting from v7.5.7, this configuration item is deprecated and replaced by [`gc.auto-compaction.tombstone-num-threshold`](#tombstone-num-threshold-new-in-v757).

+ The number of tombstones required to trigger RocksDB compaction
+ Default value: `10000`
+ Minimum value: `0`
### `region-compact-tombstones-percent`

> **Warning:**
>
> Starting from v7.5.7, this configuration item is deprecated and replaced by [`gc.auto-compaction.tombstone-percent-threshold`](#tombstone-percent-threshold-new-in-v757).

+ The proportion of tombstone required to trigger RocksDB compaction
+ Default value: `30`
+ Minimum value: `1`
+ Maximum value: `100`
### `region-compact-min-redundant-rows` New in v7.1.0

> **Warning:**
>
> Starting from v7.5.7, this configuration item is deprecated and replaced by [`gc.auto-compaction.redundant-rows-threshold`](#redundant-rows-threshold-new-in-v757).

+ The number of redundant MVCC rows required to trigger RocksDB compaction.
+ Default value: `50000`
+ Minimum value: `0`
### `region-compact-redundant-rows-percent` New in v7.1.0

> **Warning:**
>
> Starting from v7.5.7, this configuration item is deprecated and replaced by [`gc.auto-compaction.redundant-rows-percent-threshold`](#redundant-rows-percent-threshold-new-in-v757).

+ The percentage of redundant MVCC rows required to trigger RocksDB compaction.
+ Default value: `20`
+ Minimum value: `1`
+ Maximum value: `100`
### `report-region-buckets-tick-interval` New in v6.1.0

> **Warning:**
>
> `report-region-buckets-tick-interval` is an experimental feature introduced in TiDB v6.1.0. It is not recommended that you use it in production environments.

+ The interval at which TiKV reports bucket information to PD when `enable-region-bucket` is true.
+ Default value: `10s`
### `pd-heartbeat-tick-interval`

+ The time interval at which a Region's heartbeat to PD is triggered. `0` means that this feature is disabled.
+ Default value: `"1m"`
+ Minimum value: `0`
### `pd-store-heartbeat-tick-interval`

+ The time interval at which a store's heartbeat to PD is triggered. `0` means that this feature is disabled.
+ Default value: `"10s"`
+ Minimum value: `0`
### `pd-report-min-resolved-ts-interval` New in v7.6.0

> **Note:**
>
> This configuration item is renamed from [`report-min-resolved-ts-interval`](https://docs.pingcap.com/tidb/v7.5/tikv-configuration-file/#report-min-resolved-ts-interval-new-in-v600). Starting from v7.6.0, `report-min-resolved-ts-interval` is no longer effective.

+ Specifies the minimum interval for TiKV to report Resolved TS to the PD leader. Setting it to `0` disables the reporting.
+ Default value: `"1s"`, which is the minimum positive value. Before v6.3.0, the default value is `"0s"`.
+ Minimum value: `0`
+ Unit: second
### `snap-mgr-gc-tick-interval`

+ The time interval at which the recycle of expired snapshot files is triggered. `0` means that this feature is disabled.
+ Default value: `"1m"`
+ Minimum value: `0`
### `snap-gc-timeout`

+ The longest time for which a snapshot file is saved
+ Default value: `"4h"`
+ Minimum value: `0`
### `snap-generator-pool-size` New in v5.4.0

+ Configures the size of the `snap-generator` thread pool.
+ To make Regions generate snapshot faster in TiKV in recovery scenarios, you need to increase the count of the `snap-generator` threads of the corresponding worker. You can use this configuration item to increase the size of the `snap-generator` thread pool.
+ Default value: `2`
+ Minimum value: `1`
### `lock-cf-compact-interval`

+ The time interval at which TiKV triggers a manual compaction for the Lock Column Family
+ Default value: `"10m"`
+ Minimum value: `0`
### `lock-cf-compact-bytes-threshold`

+ The size out of which TiKV triggers a manual compaction for the Lock Column Family
+ Default value: `"256MiB"`
+ Minimum value: `0`
+ Unit: MiB
### `notify-capacity`

+ The longest length of the Region message queue.
+ Default value: `40960`
+ Minimum value: `0`
### `messages-per-tick`

+ The maximum number of messages processed per batch
+ Default value: `4096`
+ Minimum value: `0`
### `max-peer-down-duration`

+ The longest inactive duration allowed for a peer. A peer with timeout is marked as `down`, and PD tries to delete it later.
+ Default value: `"10m"`
+ Minimum value: When Hibernate Region is enabled, the minimum value is `peer-stale-state-check-interval * 2`; when Hibernate Region is disabled, the minimum value is `0`.
### `max-leader-missing-duration`

+ The longest duration allowed for a peer to be in the state where a Raft group is missing the leader. If this value is exceeded, the peer verifies with PD whether the peer has been deleted.
+ Default value: `"2h"`
+ Minimum value: greater than `abnormal-leader-missing-duration`
### `abnormal-leader-missing-duration`

+ The longest duration allowed for a peer to be in the state where a Raft group is missing the leader. If this value is exceeded, the peer is seen as abnormal and marked in metrics and logs.
+ Default value: `"10m"`
+ Minimum value: greater than `peer-stale-state-check-interval`
### `peer-stale-state-check-interval`

+ The time interval to trigger the check for whether a peer is in the state where a Raft group is missing the leader.
+ Default value: `"5m"`
+ Minimum value: greater than `2 * election-timeout`
### `leader-transfer-max-log-lag`

+ The maximum number of missing logs allowed for the transferee during a Raft leader transfer
+ Default value: `128`
+ Minimum value: `10`
### `max-snapshot-file-raw-size` New in v6.1.0

+ When the size of a snapshot file exceeds this configuration value, this file will be split into multiple files.
+ Default value: `100MiB`
+ Minimum value: `100MiB`
