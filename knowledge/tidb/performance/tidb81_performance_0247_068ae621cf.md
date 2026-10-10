# Speed up TiFlash replication

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/create-tiflash-replicas.md`
- Source Title: `Create TiFlash Replicas`
- Source Heading Path: `Create TiFlash Replicas > Speed up TiFlash replication`
- Source Line Ranges: `127-185`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tikv`, `pd`, `sql`, `tiup`
- Topic Tags: `replication-speed`, `snapshot-bandwidth`, `dynamic-config`, `pd-control`, `resource-usage`, `throttling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0247_068ae621cf`
- Source ID: `tidb-docs-8.1:tiflash/create-tiflash-replicas.md#speed-up-tiflash-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc29ac40e9038534097d74988bbc293bca8254cab1f1830f305c7a58ec2148cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas#speed-up-tiflash-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/create-tiflash-replicas.md

## Retrieval Guidance

- Use When: Use this when you need the documented self-managed procedure and exact commands to speed up TiFlash replication by changing snapshot bandwidth and PD store limits.
- Retrieval Keywords: Speed up TiFlash replication, SET CONFIG tikv `server.snap-io-max-bytes-per-sec` = '300MiB', SET CONFIG tiflash `raftstore-proxy.server.snap-io-max-bytes-per-sec` = '300MiB', Dynamic Config SQL statement, tiup ctl:v<CLUSTER_VERSION> pd -u http://<PD_ADDRESS>:2379 store limit all engine tiflash 60 add-peer, tiup ctl:v<CLUSTER_VERSION> pd -u http://<PD_ADDRESS>:2379 store limit all engine tiflash 90 add-peer, tiup ctl:v<CLUSTER_VERSION> pd -u http://<PD_ADDRESS>:2379 store limit all engine tiflash 30 add-peer, server.snap-io-max-bytes-per-sec, raftstore-proxy.server.snap-io-max-bytes-per-sec, store limit all engine tiflash, add-peer
- Follow-up Guidance: The source says this section is not applicable to TiDB Cloud and includes reverting the PD limit to 30 and both snapshot write speed limits to 100MiB after replication is complete.
- Classification Note: This is classified as a performance chunk because the content focuses on accelerating TiFlash replica creation speed and describes the resource-usage impact of tuning TiKV, TiFlash, and PD limits.

## Official Source Content

## Speed up TiFlash replication

> **Note:**
>
> This section is not applicable to TiDB Cloud.

Before TiFlash replicas are added, each TiKV instance performs a full table scan and sends the scanned data to TiFlash as a "snapshot" to create replicas. By default, TiFlash replicas are added slowly with fewer resources usage in order to minimize the impact on the online service. If there are spare CPU and disk IO resources in your TiKV and TiFlash nodes, you can accelerate TiFlash replication by performing the following steps.

1. Temporarily increase the snapshot write speed limit for each TiKV and TiFlash instance by using the [Dynamic Config SQL statement](https://docs.pingcap.com/tidb/stable/dynamic-config):

    ```sql
    -- The default value for both configurations are 100MiB, i.e. the maximum disk bandwidth used for writing snapshots is no more than 100MiB/s.
    SET CONFIG tikv `server.snap-io-max-bytes-per-sec` = '300MiB';
    SET CONFIG tiflash `raftstore-proxy.server.snap-io-max-bytes-per-sec` = '300MiB';
    ```

    After executing these SQL statements, the configuration changes take effect immediately without restarting the cluster. However, since the replication speed is still restricted by the PD limit globally, you cannot observe the acceleration for now.

2. Use [PD Control](https://docs.pingcap.com/tidb/stable/pd-control) to progressively ease the new replica speed limit.

    The default new replica speed limit is 30, which means, approximately 30 Regions add TiFlash replicas every minute. Executing the following command will adjust the limit to 60 for all TiFlash instances, which doubles the original speed:

    ```shell
    tiup ctl:v<CLUSTER_VERSION> pd -u http://<PD_ADDRESS>:2379 store limit all engine tiflash 60 add-peer
    ```

    > In the preceding command, you need to replace `v<CLUSTER_VERSION>` with the actual cluster version, such as `v8.1.2` and `<PD_ADDRESS>:2379` with the address of any PD node. For example:
    >
    > ```shell
    > tiup ctl:v8.1.2 pd -u http://192.168.1.4:2379 store limit all engine tiflash 60 add-peer
    > ```

    Within a few minutes, you will observe a significant increase in CPU and disk IO resource usage of the TiFlash nodes, and TiFlash should create replicas faster. At the same time, the TiKV nodes' CPU and disk IO resource usage increases as well.

    If the TiKV and TiFlash nodes still have spare resources at this point and the latency of your online service does not increase significantly, you can further ease the limit, for example, triple the original speed:

    ```shell
    tiup ctl:v<CLUSTER_VERSION> pd -u http://<PD_ADDRESS>:2379 store limit all engine tiflash 90 add-peer
    ```

3. After the TiFlash replication is complete, revert to the default configuration to reduce the impact on online services.

    Execute the following PD Control command to restore the default new replica speed limit:

    ```shell
    tiup ctl:v<CLUSTER_VERSION> pd -u http://<PD_ADDRESS>:2379 store limit all engine tiflash 30 add-peer
    ```

    Execute the following SQL statements to restore the default snapshot write speed limit:

    ```sql
    SET CONFIG tikv `server.snap-io-max-bytes-per-sec` = '100MiB';
    SET CONFIG tiflash `raftstore-proxy.server.snap-io-max-bytes-per-sec` = '100MiB';
    ```
