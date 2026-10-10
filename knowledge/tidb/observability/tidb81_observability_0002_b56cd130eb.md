# PD component alert rules

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/alert-rules.md`
- Source Title: `TiDB Cluster Alert Rules`
- Source Heading Path: `TiDB Cluster Alert Rules > PD alert rules | TiDB Cluster Alert Rules > PD alert rules > Emergency-level alerts | TiDB Cluster Alert Rules > PD alert rules > Emergency-level alerts > `PD_cluster_down_store_nums` | TiDB Cluster Alert Rules > PD alert rules > Critical-level alerts | TiDB Cluster Alert Rules > PD alert rules > Critical-level alerts > `PD_etcd_write_disk_latency` | TiDB Cluster Alert Rules > PD alert rules > Critical-level alerts > `PD_miss_peer_region_count` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_cluster_lost_connect_store_nums` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_cluster_unhealthy_tikv_nums` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_cluster_low_space` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_etcd_network_peer_latency` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_tidb_handle_requests_duration` | TiDB Cluster Alert Rules > PD alert rules > Warning-level alerts > `PD_down_peer_region_nums``
- Source Line Ranges: `174-326`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tiflash`, `tidb`
- Topic Tags: `alert-rules`, `store-heartbeat`, `etcd-latency`, `replica-health`, `low-space`, `network-latency`, `tso`, `region-health`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0002_b56cd130eb`
- Source ID: `tidb-docs-8.1:alert-rules.md#pd-alert-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2207532718e94813c788d8d2c6965087b75127285ca162af5e892066cbadf894`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/alert-rules#pd-alert-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when the user is investigating PD alert rules, their Prometheus expressions, descriptions, or listed solutions for down stores, etcd disk latency, missing replicas, disconnected stores, unhealthy stores, low disk space, PD peer network latency, slow TSO handling, or down-peer Regions.
- Retrieval Keywords: PD alert rules, PD_cluster_down_store_nums, pd_cluster_status, store_down_count, PD_etcd_write_disk_latency, etcd_disk_wal_fsync_duration_seconds_bucket, PD_miss_peer_region_count, pd_regions_status, miss-peer-region-count, PD_cluster_lost_connect_store_nums, store_disconnected_count, max-down-time, PD_cluster_unhealthy_tikv_nums, store_unhealth_count, max-store-down-time, PD_cluster_low_space, store_low_space_count, PD_etcd_network_peer_latency, etcd_network_peer_round_trip_time_seconds_bucket, PD_tidb_handle_requests_duration, pd_client_request_handle_requests_duration_seconds_bucket, type="tso", PD_down_peer_region_nums, down-peer-region-count, down_peer_region_count, etcd_server_is_leader, TSO, pprof
- Follow-up Guidance: The source includes follow-up checks such as store state, Region health panels, server load, network status, and pprof CPU profile analysis for PD.
- Classification Note: This is observability content because it lists PD alert rules together with alert expressions, conditions, and monitoring and diagnosis guidance.

## Official Source Content

## PD alert rules

This section gives the alert rules for the PD component.
### Emergency-level alerts
#### `PD_cluster_down_store_nums`

* Alert rule:

    `(sum(pd_cluster_status{type="store_down_count"}) by (instance) > 0) and (sum(etcd_server_is_leader) by (instance) > 0)`

* Description:

    PD has not received a TiKV/TiFlash heartbeat for a long time (the default configuration is 30 minutes).

* Solution:

    * Check whether the TiKV/TiFlash process is normal, the network is isolated or the load is too high, and recover the service as much as possible.
    * If the TiKV/TiFlash instance cannot be recovered, you can make it offline.
### Critical-level alerts
#### `PD_etcd_write_disk_latency`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(etcd_disk_wal_fsync_duration_seconds_bucket[1m])) by (instance, job, le)) > 1`

* Description:

    If the latency of the fsync operation exceeds 1 second, it indicates that etcd writes data to disk at a lower speed than normal. It might lead to PD leader timeout or failure to store TSO on disk in time, which will shut down the service of the entire cluster.

* Solution:

    * Find the cause of slow writes. It might be other services that overload the system. You can check whether PD itself occupies a large amount of CPU or I/O resources.
    * Try to restart PD or manually transfer leader to another PD to recover the service.
    * If the problematic PD instance cannot be recovered due to environmental factors, make it offline and replace it.
#### `PD_miss_peer_region_count`

* Alert rule:

    `(sum(pd_regions_status{type="miss-peer-region-count"}) by (instance) > 100) and (sum(etcd_server_is_leader) by (instance) > 0)`

* Description:

    The number of Region replicas is smaller than the value of `max-replicas`.

* Solution:

    * Find the cause of the issue by checking whether there is any TiKV machine that is down or being made offline.
    * Watch the Region health panel and see whether `miss-peer-region-count` is continuously decreasing.
### Warning-level alerts
#### `PD_cluster_lost_connect_store_nums`

* Alert rule:

    `(sum(pd_cluster_status{type="store_disconnected_count"}) by (instance) > 0) and (sum(etcd_server_is_leader) by (instance) > 0)`

* Description:

    PD does not receive a TiKV/TiFlash heartbeat within 20 seconds. Normally a TiKV/TiFlash heartbeat comes in every 10 seconds.

* Solution:

    * Check whether the TiKV/TiFlash instance is being restarted.
    * Check whether the TiKV/TiFlash process is normal, the network is isolated, and the load is too high, and recover the service as much as possible.
    * If you confirm that the TiKV/TiFlash instance cannot be recovered, you can make it offline.
    * If you confirm that the TiKV/TiFlash instance can be recovered, but not in the short term, you can consider increasing the value of `max-down-time`. It will prevent the TiKV/TiFlash instance from being considered as irrecoverable and the data from being removed from the TiKV/TiFlash.
#### `PD_cluster_unhealthy_tikv_nums`

* Alert rule:

    `(sum(pd_cluster_status{type="store_unhealth_count"}) by (instance) > 0) and (sum(etcd_server_is_leader) by (instance) > 0)`

* Description:

    Indicates that there are unhealthy stores. If the situation persists for some time (configured by [`max-store-down-time`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-store-down-time), defaults to `30m`), the store is likely to change to `Offline` state, which triggers the [`PD_cluster_down_store_nums`](#pd_cluster_down_store_nums) alert.

* Solution:

    Check the state of the TiKV stores.
#### `PD_cluster_low_space`

* Alert rule:

    `(sum(pd_cluster_status{type="store_low_space_count"}) by (instance) > 0) and (sum(etcd_server_is_leader) by (instance) > 0)`

* Description:

    Indicates that there is no sufficient space on the TiKV/TiFlash node.

* Solution:

    * Check whether the space in the cluster is generally insufficient. If so, increase its capacity.
    * Check whether there is any issue with Region balance scheduling. If so, it will lead to uneven data distribution.
    * Check whether there is any file that occupies a large amount of disk space, such as the log, snapshot, and core dump.
    * Lower the Region weight of the node to reduce the data volume.
    * When it is not possible to release the space, consider proactively making the node offline. This prevents insufficient disk space that leads to downtime.
#### `PD_etcd_network_peer_latency`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(etcd_network_peer_round_trip_time_seconds_bucket[1m])) by (To, instance, job, le)) > 1`

* Description:

    The network latency between PD nodes is high. It might lead to the leader timeout and TSO disk storage timeout, which impacts the service of the cluster.

* Solution:

    * Check the network and system load status.
    * If the problematic PD instance cannot be recovered due to environmental factors, make it offline and replace it.
#### `PD_tidb_handle_requests_duration`

* Alert rule:

    `histogram_quantile(0.99, sum(rate(pd_client_request_handle_requests_duration_seconds_bucket{type="tso"}[1m])) by (instance, job, le)) > 0.1`

* Description:

    It takes a longer time for PD to handle the TSO request. It is often caused by a high load.

* Solution:

    * Check the load status of the server.
    * Use pprof to analyze the CPU profile of PD.
    * Manually switch the PD leader.
    * If the problematic PD instance cannot be recovered due to environmental factors, make it offline and replace it.
#### `PD_down_peer_region_nums`

* Alert rule:

    `(sum(pd_regions_status{type="down-peer-region-count"}) by (instance)  > 0) and (sum(etcd_server_is_leader) by (instance) > 0)`

* Description:

    The number of Regions with an unresponsive peer reported by the Raft leader.

* Solution:

    * Check whether there is any TiKV that is down, or that was just restarted, or that is busy.
    * Watch the Region health panel and see whether `down_peer_region_count` is continuously decreasing.
    * Check the network between TiKV servers.
