# Set available zones for TiFlash replicas

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/create-tiflash-replicas.md`
- Source Title: `Create TiFlash Replicas`
- Source Heading Path: `Create TiFlash Replicas > Set available zones`
- Source Line Ranges: `186-279`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `pd`, `tidb`
- Topic Tags: `availability-zones`, `replica-placement`, `topology-labels`, `server-labels`, `high-availability`, `replication-progress`, `sql`, `scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0351_66fbe82e5d`
- Source ID: `tidb-docs-8.1:tiflash/create-tiflash-replicas.md#set-available-zones`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `223fac5683f43b1e935664e25efdbd0bfce35e13c19c777cf8b3a1bd789340df`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas#set-available-zones
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/create-tiflash-replicas.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to distribute TiFlash replicas across availability zones by labeling TiFlash nodes and verifying Region distribution on TiFlash stores.
- Retrieval Keywords: Set available zones, TiFlash replicas, available zones, server.labels, learner_config, flash.proxy.labels, ALTER TABLE table_name SET TIFLASH REPLICA count, ALTER TABLE t SET TIFLASH REPLICA 2, PD schedules the replicas, topology labels, information_schema.tikv_region_status, information_schema.tikv_region_peers, information_schema.tikv_store_status, JSON_EXTRACT(s.label, '$[0].value') = 'tiflash', partitioned table, non-partitioned table, LOCATION LABELS, tiflash_replica_read
- Follow-up Guidance: The source also points to scheduling replicas by topology labels, multi-data-center deployment references, and the `tiflash_replica_read` system variable for replica selection strategy across zones.
- Classification Note: This is classified as self-managed TiFlash configuration because the content describes setting `server.labels` in `learner_config`, using `ALTER TABLE ... SET TIFLASH REPLICA`, and explicitly notes that the section is not applicable to TiDB Cloud.

## Official Source Content

## Set available zones

> **Note:**
>
> This section is not applicable to TiDB Cloud.

When configuring replicas, if you need to distribute TiFlash replicas to multiple data centers for disaster recovery, you can configure available zones by following the steps below:

1. Specify labels for TiFlash nodes in the cluster configuration file.

    ```
    tiflash_servers:
      - host: 172.16.5.81
          logger.level: "info"
        learner_config:
          server.labels:
            zone: "z1"
      - host: 172.16.5.82
        config:
          logger.level: "info"
        learner_config:
          server.labels:
            zone: "z1"
      - host: 172.16.5.85
        config:
          logger.level: "info"
        learner_config:
          server.labels:
            zone: "z2"
    ```

    Note that the `flash.proxy.labels` configuration in earlier versions cannot handle special characters in the available zone name correctly. It is recommended to use the `server.labels` in `learner_config` to configure the name of an available zone.

2. After starting a cluster, specify the number of TiFlash replicas for high availability. The syntax is as follows:

    ```sql
    ALTER TABLE table_name SET TIFLASH REPLICA count;
    ```

    For example:

    ```sql
    ALTER TABLE t SET TIFLASH REPLICA 2;
    ```

3. PD schedules the replicas of the table `t` to different availability zones based on the `server.labels` in the TiFlash node's `learner_config` and the number (`count`) of the table's replicas, ensuring availability. For more information, see [Schedule Replicas by Topology Labels](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels/). You can use the following SQL statement to verify the distribution of a table's Regions across TiFlash nodes:

    ```sql
    -- Non-partitioned table
    SELECT table_id, p.store_id, address, COUNT(p.region_id) 
    FROM
      information_schema.tikv_region_status r,
      information_schema.tikv_region_peers p,
      information_schema.tikv_store_status s
    WHERE
      r.db_name = 'test' 
      AND r.table_name = 'table_to_check'
      AND r.region_id = p.region_id 
      AND p.store_id = s.store_id
      AND JSON_EXTRACT(s.label, '$[0].value') = 'tiflash'
    GROUP BY table_id, p.store_id, address;

    -- Partitioned table
    SELECT table_id, r.partition_name, p.store_id, address, COUNT(p.region_id)
    FROM
      information_schema.tikv_region_status r,
      information_schema.tikv_region_peers p,
      information_schema.tikv_store_status s
    WHERE 
      r.db_name = 'test' 
      AND r.table_name = 'table_to_check' 
      AND r.partition_name LIKE 'p202312%'
      AND r.region_id = p.region_id 
      AND p.store_id = s.store_id
      AND JSON_EXTRACT(s.label, '$[0].value') = 'tiflash'
    GROUP BY table_id, r.partition_name, p.store_id, address
    ORDER BY table_id, r.partition_name, p.store_id;
    ```

For more information about scheduling replicas by using labels, see [Schedule Replicas by Topology Labels](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels), [Multiple Data Centers in One City Deployment](https://docs.pingcap.com/tidb/stable/multi-data-centers-in-one-city-deployment), and [Three Data Centers in Two Cities Deployment](https://docs.pingcap.com/tidb/stable/three-data-centers-in-two-cities-deployment).

TiFlash supports configuring the replica selection strategy for different zones. For more information, see [`tiflash_replica_read`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_replica_read-new-in-v730).

> **Note:**
>
> In the syntax `ALTER TABLE table_name SET TIFLASH REPLICA count LOCATION LABELS location_labels;`, if you specify multiple labels for `location_labels`, TiDB cannot parse them correctly to set placement rules. Therefore, do not use `LOCATION LABELS` to configure TiFlash replicas.
