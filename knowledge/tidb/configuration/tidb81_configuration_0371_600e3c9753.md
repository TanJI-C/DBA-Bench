# Raftstore basics, capacity, paths, and election timing

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > raftstore | TiKV Configuration File > raftstore > `prevote` | TiKV Configuration File > raftstore > `capacity` | TiKV Configuration File > raftstore > `raftdb-path` | TiKV Configuration File > raftstore > `raft-base-tick-interval` | TiKV Configuration File > raftstore > `raft-heartbeat-ticks` | TiKV Configuration File > raftstore > `raft-election-timeout-ticks``
- Source Line Ranges: `619-668`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `raftstore`, `prevote`, `capacity`, `raftdb-path`, `heartbeat`, `election-timeout`, `raft-ticks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0371_600e3c9753`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#raftstore`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a17f212fc39e3afa244694e525452b362f82a57490d1f9b6836c1c6e8dc39d72`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raftstore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV `raftstore` configuration for `prevote`, disk `capacity`, `raftdb-path`, or Raft heartbeat and election timing based on tick intervals.
- Retrieval Keywords: raftstore, prevote, network partition, capacity, multiple TiKV instances on the same physical disk, raftdb-path, storage.data-dir/raft, raft-base-tick-interval, raft-heartbeat-ticks, raft-election-timeout-ticks, leader election, heartbeat is sent, cannot be queried via SQL statements
- Follow-up Guidance: For multiple TiKV instances on the same physical disk, the content references the hybrid deployment topology key parameters.
- Classification Note: This is classified as configuration content because it specifies TiKV Raftstore configuration items, defaults, constraints, and timing relationships for heartbeat and leader election.

## Official Source Content

## raftstore

Configuration items related to Raftstore.
### `prevote`

+ Enables or disables `prevote`. Enabling this feature helps reduce jitter on the system after recovery from network partition.
+ Default value: `true`
### `capacity`

+ The storage capacity, which is the maximum size allowed to store data. If `capacity` is left unspecified, the capacity of the current disk prevails. To deploy multiple TiKV instances on the same physical disk, add this parameter to the TiKV configuration. For details, see [Key parameters of the hybrid deployment](https://docs.pingcap.com/tidb/stable/hybrid-deployment-topology#key-parameters).
+ Default value: `0`
+ Unit: KiB|MiB|GiB
### `raftdb-path`

+ The path to the Raft library, which is `storage.data-dir/raft` by default
+ Default value: `""`
### `raft-base-tick-interval`

> **Note:**
>
> This configuration item cannot be queried via SQL statements but can be configured in the configuration file.

+ The time interval at which the Raft state machine ticks
+ Default value: `"1s"`
+ Minimum value: greater than `0`
### `raft-heartbeat-ticks`

> **Note:**
>
> This configuration item cannot be queried via SQL statements but can be configured in the configuration file.

+ The number of passed ticks when the heartbeat is sent. This means that a heartbeat is sent at the time interval of `raft-base-tick-interval` * `raft-heartbeat-ticks`.
+ Default value: `2`
+ Minimum value: greater than `0`
### `raft-election-timeout-ticks`

> **Note:**
>
> This configuration item cannot be queried via SQL statements but can be configured in the configuration file.

+ The number of passed ticks when Raft election is initiated. This means that if Raft group is missing the leader, a leader election is initiated approximately after the time interval of `raft-base-tick-interval` * `raft-election-timeout-ticks`.
+ Default value: `10`
+ Minimum value: `raft-heartbeat-ticks`
