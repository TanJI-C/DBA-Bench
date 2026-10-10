# PD warning alert rules for region health, leader changes, space, time, replicas, and slow TiKV

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/alert-rules.md`
- Source Title: `TiDB Cluster Alert Rules`
- Source Heading Path: `TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_pending_peer_region_count` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_leader_change` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `TiKV_space_used_more_than_80%` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_system_time_slow` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_no_store_for_making_replica` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_cluster_slow_tikv_nums``
- Source Line Ranges: `327-418`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `alert-rules`, `pd`, `warning-alerts`, `region-health`, `leader-change`, `storage-capacity`, `system-time`, `replica-placement`, `slow-node`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0003_2853043842`
- Source ID: `tidb-docs-8.1:alert-rules.md#pd-pending-peer-region-count`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `654506dcab9cebd2f0818963a562cd92032170af522a070401786ae699070980`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/alert-rules#pd-pending-peer-region-count
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting PD warning-level alerts related to pending peers, PD leader changes, cluster space usage, system time slow events, missing target stores for replicas, or slow TiKV nodes.
- Retrieval Keywords: PD_pending_peer_region_count, pd_regions_status{type="pending-peer-region-count"}, pending_peer_region_count, PD_leader_change, pd_tso_events{type="save"}, TiKV_space_used_more_than_80%, pd_cluster_status{type="storage_size"}, pd_cluster_status{type="storage_capacity"}, PD_system_time_slow, pd_tso_events{type="system_time_slow"}, PD_no_store_for_making_replica, pd_checker_event_count{type="replica_checker", name="no_target_store"}, PD_cluster_slow_tikv_nums, pd_cluster_status{type="store_slow_count"}, etcd_server_is_leader, Region health panel, Store Slow Score, raftstore.inspect-interval
- Follow-up Guidance: The content points to checking the Region health panel, network bandwidth between TiKV servers, the TiKV-Details dashboards, store space and label configuration, and the `raftstore.inspect-interval` setting depending on which alert fired.
- Classification Note: The official content classifies these items as PD warning-level alerts for region health, leader switching, storage capacity, system time, replica placement, and slow TiKV detection.

## Official Source Content

#### `PD_pending_peer_region_count`

* Alert rule:

    `(sum(pd_regions_status{type="pending-peer-region-count"}) by (instance) > 100) and (sum(etcd_server_is_leader) by (instance) > 0)`

* Description:

    There are too many Regions that have lagged Raft logs. It is normal that scheduling leads to a small number of pending peers, but if the number remains high, there might be an issue.

* Solution:

    * Watch the Region health panel and see whether `pending_peer_region_count` is continuously decreasing.
    * Check the network between TiKV servers, especially whether there is enough bandwidth.
#### `PD_leader_change`

* Alert rule:

    `count(changes(pd_tso_events{type="save"}[10m]) > 0) >= 2`

* Description:

    The PD leader is recently switched.

* Solution:

    * Exclude the human factors, such as restarting PD, manually transferring leader, and adjusting leader priority.
    * Check the network and system load status.
    * If the problematic PD instance cannot be recovered due to environmental factors, make it offline and replace it.
#### `TiKV_space_used_more_than_80%`

* Alert rule:

    `sum(pd_cluster_status{type="storage_size"}) / sum(pd_cluster_status{type="storage_capacity"}) * 100 > 80`

* Description:

    Over 80% of the cluster space is occupied.

* Solution:

    * Check whether it is needed to increase capacity.
    * Check whether there is any file that occupies a large amount of disk space, such as the log, snapshot, and core dump.
#### `PD_system_time_slow`

* Alert rule:

    `changes(pd_tso_events{type="system_time_slow"}[10m]) >= 1`

* Description:

    The system time rewind might happen.

* Solution:

    Check whether the system time is configured correctly.
#### `PD_no_store_for_making_replica`

* Alert rule:

    `increase(pd_checker_event_count{type="replica_checker", name="no_target_store"}[1m]) > 0`

* Description:

    There is no appropriate store for additional replicas.

* Solution:

    * Check whether there is enough space in the store.
    * Check whether there is any store for additional replicas according to the label configuration if it is configured.
#### `PD_cluster_slow_tikv_nums`

* Alert rule:

    `sum(pd_cluster_status{type="store_slow_count"}) by (instance) > 0) and (sum(etcd_server_is_leader) by (instance) > 0`

* Description:

    There is a slow TiKV node. `raftstore.inspect-interval` controls the detection of TiKV slow nodes. For more information, see [`raftstore.inspect-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#inspect-interval).

* Solution:

    * Watch the [**TiKV-Details** > **PD** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#pd) and view the Store Slow Score metric. Identify the node with a metric value exceeding 80, which is detected as a slow node.
    * Watch the [**TiKV-Details** > **Raft IO** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#raft-io) and see whether the latency increases. If the latency is high, it means a bottleneck might exist in the disk.
    * Set the [`raftstore.inspect-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#inspect-interval) configuration item to a larger value to increase the timeout limit of latency.
    * For further analysis of performance issues of the alerted TiKV node and tuning methods, see [Performance analysis and tuning](https://docs.pingcap.com/tidb/stable/performance-tuning-methods#storage-async-write-duration-store-duration-and-apply-duration).
