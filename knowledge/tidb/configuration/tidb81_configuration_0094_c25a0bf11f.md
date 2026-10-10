# Multi-replica DR overview, setup, replica placement, and monitoring

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-multi-replica.md`
- Source Title: `DR Solution Based on Multiple Replicas in a Single Cluster`
- Source Heading Path: `DR Solution Based on Multiple Replicas in a Single Cluster | DR Solution Based on Multiple Replicas in a Single Cluster > Introduction | DR Solution Based on Multiple Replicas in a Single Cluster > Set up a cluster and configure replicas | DR Solution Based on Multiple Replicas in a Single Cluster > Monitor the cluster`
- Source Line Ranges: `5-160`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `pd`, `tikv`, `tidb`, `dashboard`, `sql`
- Topic Tags: `disaster-recovery`, `multi-replica`, `placement-policy`, `topology`, `replica-configuration`, `leader-priority`, `cross-region`, `monitoring`, `grafana`, `dashboard`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0094_c25a0bf11f`
- Source ID: `tidb-docs-8.1:dr-multi-replica.md#dr-solution-based-on-multiple-replicas-in-a-single-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `36591dae44223fb81d92a49e6aa6f4fcd1ee4e3efe55e13bb4578171df5fcc4e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-multi-replica#dr-solution-based-on-multiple-replicas-in-a-single-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-multi-replica.md

## Retrieval Guidance

- Use When: Use this when looking for the official single-cluster multi-replica DR setup across three regions, including TiUP topology, replica placement, PD leader priority, placement policies, and monitoring entry points.
- Retrieval Keywords: DR Solution Based on Multiple Replicas in a Single Cluster, multi-replica DR, single cluster, three regions five replicas, tiup cluster deploy drtest, replication.location-labels, server.labels, Region1 Region2 Region3, max-replicas 5, label-property reject-leader Region Region3, leader_priority, CREATE PLACEMENT POLICY primary_rule_for_region1, CREATE PLACEMENT POLICY secondary_rule_for_region2, ALTER TABLE PLACEMENT POLICY, TIKV_STORE_STATUS, Grafana, TiDB Dashboard
- Follow-up Guidance: The source also includes a later section on performing a DR switchover, covering both planned and unplanned switchover procedures.
- Classification Note: Classified as configuration because the content focuses on topology file settings, PD and TiKV replica-related configuration, placement policy SQL, and monitoring references for a self-managed cluster.

## Official Source Content

# DR Solution Based on Multiple Replicas in a Single Cluster

This document describes the disaster recovery (DR) solution based on multiple replicas in a single cluster. The document is organized as follows:

- Solution introduction
- How to set up a cluster and configure replicas
- How to monitor the cluster
- How to perform a DR switchover
## Introduction

Important production systems usually require regional DR with zero RPO and minute-level RTO. A Raft-based distributed database, TiDB provides multiple replicas, which allows it to support regional DR with data consistency and high availability guaranteed. Considering the small network latency between available zones (AZs) in the same region, we can dispatch business traffic to two AZs on the same region simultaneously, and achieve load balance among AZs on the same region by properly locating the Region leader and the PD leader.

> **Note:**
>
> ["Region" in TiKV](https://docs.pingcap.com/tidb/stable/glossary#regionpeerraft-group) means a range of data while the term "region" means a physical location. The two terms are not interchangeable.
## Set up a cluster and configure replicas

This section illustrates how to create a TiDB cluster across three regions with five replicas using TiUP, and how to achieve DR by properly distributing data and PD nodes.

In this example, TiDB contains five replicas and three regions. Region 1 is the primary region, region 2 is the secondary region, and region 3 is used for voting. Similarly, the PD cluster also contains 5 replicas, which function basically the same as the TiDB cluster.

1. Create a topology file similar to the following:

    ```toml
    global:
      user: "root"
      ssh_port: 22
      deploy_dir: "/data/tidb_cluster/tidb-deploy"
      data_dir: "/data/tidb_cluster/tidb-data"

    server_configs:
      tikv:
        server.grpc-compression-type: gzip
      pd:
        replication.location-labels:  ["Region","AZ"] # PD schedules replicas according to the Region and AZ configuration of TiKV nodes.

    pd_servers:
      - host: tidb-dr-test1
        name: "pd-1"
      - host: tidb-dr-test2
        name: "pd-2"
      - host: tidb-dr-test3
        name: "pd-3"
      - host: tidb-dr-test4
        name: "pd-4"
      - host: tidb-dr-test5
        name: "pd-5"

    tidb_servers:
      - host: tidb-dr-test1
      - host: tidb-dr-test3

    tikv_servers:  # Label the Regions and AZs of each TiKV node through the labels option.
      - host: tidb-dr-test1
        config:
          server.labels: { Region: "Region1", AZ: "AZ1" }
      - host: tidb-dr-test2
        config:
          server.labels: { Region: "Region1", AZ: "AZ2" }
      - host: tidb-dr-test3
        config:
          server.labels: { Region: "Region2", AZ: "AZ3" }
      - host: tidb-dr-test4
        config:
          server.labels: { Region: "Region2", AZ: "AZ4" }
      - host: tidb-dr-test5
        config:
          server.labels: { Region: "Region3", AZ: "AZ5" }

          raftstore.raft-min-election-timeout-ticks: 50
          raftstore.raft-max-election-timeout-ticks: 60

    monitoring_servers:
      - host: tidb-dr-test2

    grafana_servers:
      - host: tidb-dr-test2

    alertmanager_servers:
      - host: tidb-dr-test2
    ```

    The preceding configurations use the following options to optimize toward cross-region DR:

    - `server.grpc-compression-type: gzip` to enable gRPC message compression in TiKV, thus reducing network traffic.
    - `raftstore.raft-min-election-timeout-ticks` and `raftstore.raft-max-election-timeout-ticks` to extend the time before region 3 participates in the election, thus preventing any replica in this region from being voted as the leader.

2. Create a cluster using the preceding configuration file:

    ```shell
    tiup cluster deploy drtest v6.4.0 ./topo.yaml
    tiup cluster start drtest --init
    tiup cluster display drtest
    ```

    Configure the number of replicas and the leader limit for the cluster:

    ```shell
    tiup ctl:v6.4.0 pd config set max-replicas 5
    tiup ctl:v6.4.0 pd config set label-property reject-leader Region Region3

    # The following step adds some test data to the cluster, which is optional.
    tiup bench tpcc  prepare -H 127.0.0.1 -P 4000 -D tpcc --warehouses 1
    ```

    Specify the priority of PD leader:

    ```shell
    tiup ctl:v6.4.0 pd member leader_priority  pd-1 4
    tiup ctl:v6.4.0 pd member leader_priority  pd-2 3
    tiup ctl:v6.4.0 pd member leader_priority  pd-3 2
    tiup ctl:v6.4.0 pd member leader_priority  pd-4 1
    tiup ctl:v6.4.0 pd member leader_priority  pd-5 0
    ```

    > **Note:**
    >
    > The greater the priority number, the higher the probability that this node becomes the leader.

3. Create placement rules and fix the primary replica of the test table to region 1:

    ```sql
    -- Create two placement rules: the first rule specifies that region 1 works as the primary region, and region 2 as the secondary region.
    -- The second placement rule specifies that when region 1 is down, region 2 will become the primary region.
    MySQL [(none)]> CREATE PLACEMENT POLICY primary_rule_for_region1 PRIMARY_REGION="Region1" REGIONS="Region1, Region2,Region3";
    MySQL [(none)]> CREATE PLACEMENT POLICY secondary_rule_for_region2 PRIMARY_REGION="Region2" REGIONS="Region1,Region2,Region3";

    -- Apply the rule primary_rule_for_region1 to the corresponding user tables.
    ALTER TABLE tpcc.warehouse PLACEMENT POLICY=primary_rule_for_region1;
    ALTER TABLE tpcc.district PLACEMENT POLICY=primary_rule_for_region1;

    -- Note: You can modify the database name, table name, and placement rule name as needed.

    -- Confirm whether the leaders have been transferred by executing the following query to check the number of leaders in each region.
    SELECT STORE_ID, address, leader_count, label FROM TIKV_STORE_STATUS ORDER BY store_id;
    ```

    The following SQL statement can generate a SQL script to configure the leader of all non-system schema tables to a specific region:

    ```sql
    SET @region_name=primary_rule_for_region1;
    SELECT CONCAT('ALTER TABLE ', table_schema, '.', table_name, ' PLACEMENT POLICY=', @region_name, ';') FROM information_schema.tables WHERE table_schema NOT IN ('METRICS_SCHEMA', 'PERFORMANCE_SCHEMA', 'INFORMATION_SCHEMA','mysql');
    ```
## Monitor the cluster

You can monitor the performance metrics of TiKV, TiDB, PD, and other components in the cluster by accessing Grafana or TiDB Dashboard. Based on the status of the components, you can determine whether to perform a DR switchover. For details, see the following documents:

- [Key Monitoring Metrics of TiDB](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard)
- [Key Monitoring Metrics of TiKV](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard)
- [Key Monitoring Metrics of PD](https://docs.pingcap.com/tidb/stable/grafana-pd-dashboard)
- [TiDB Dashboard Monitoring Page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-monitoring)
