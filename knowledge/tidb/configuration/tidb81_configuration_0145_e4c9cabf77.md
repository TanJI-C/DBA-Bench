# Configure topology labels for TiKV, TiFlash, and TiDB

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/schedule-replicas-by-topology-labels.md`
- Source Title: `Schedule Replicas by Topology Labels`
- Source Heading Path: `Schedule Replicas by Topology Labels | Schedule Replicas by Topology Labels > Configure `labels` for TiKV, TiFlash, and TiDB | Schedule Replicas by Topology Labels > Configure `labels` for TiKV, TiFlash, and TiDB > Configure a cluster using TiUP (recommended) | Schedule Replicas by Topology Labels > Configure `labels` for TiKV, TiFlash, and TiDB > Configure a cluster using command lines or configuration files | Schedule Replicas by Topology Labels > Configure `labels` for TiKV, TiFlash, and TiDB > Configure a cluster using command lines or configuration files > Configure `labels` for TiKV and TiFlash | Schedule Replicas by Topology Labels > Configure `labels` for TiKV, TiFlash, and TiDB > Configure a cluster using command lines or configuration files > (Optional) Configure `labels` for TiDB`
- Source Line Ranges: `5-216`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`, `tiup`
- Topic Tags: `topology-labels`, `labels`, `tiup`, `deployment`, `follower-read`, `same-zone-reads`, `node-topology`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0145_e4c9cabf77`
- Source ID: `tidb-docs-8.1:schedule-replicas-by-topology-labels.md#schedule-replicas-by-topology-labels`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2ae28a9b84ddc503d9ef79eaff3dbab5efcd4430db6725a298ab193018c53a92`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels#schedule-replicas-by-topology-labels
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/schedule-replicas-by-topology-labels.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to configure topology `labels` for TiKV, TiFlash, and optionally TiDB in a self-managed cluster, including TiUP topology examples and command-line or configuration-file syntax.
- Retrieval Keywords: labels, server.labels, replication.location-labels, TiUP topology file, tidb_servers, tikv_servers, tiflash_servers, learner_config, tiflash-learner.toml, tikv-server --labels, [labels], Follower read, same region, zone, dc, rack, host
- Follow-up Guidance: If same-region reads with Follower read are relevant, this content notes that TiDB currently depends on the `zone` label and that `zone` must also be included when configuring PD `location-labels`.
- Classification Note: The classification is configuration because the content provides deployment and config-file settings for `labels` on TiKV, TiFlash, and TiDB, mainly in self-managed clusters using TiUP or direct configuration files.

## Official Source Content

# Schedule Replicas by Topology Labels

> **Note:**
>
> TiDB v5.3.0 introduces [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql). This offers a more convenient way to configure the placement of tables and partitions. Placement Rules in SQL might replace placement configuration with PD in future releases.

To improve the high availability and disaster recovery capability of TiDB clusters, it is recommended that TiKV nodes are physically scattered as much as possible. For example, TiKV nodes can be distributed on different racks or even in different data centers. According to the topology information of TiKV, the PD scheduler automatically performs scheduling at the background to isolate each replica of a Region as much as possible, which maximizes the capability of disaster recovery.

To make this mechanism effective, you need to properly configure TiKV and PD so that the topology information of the cluster, especially the TiKV location information, is reported to PD during deployment. Before you begin, see [Deploy TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) first.
## Configure `labels` for TiKV, TiFlash, and TiDB

You can configure `labels` for TiKV, TiFlash, and TiDB based on the cluster topology.
### Configure a cluster using TiUP (recommended)

When using TiUP to deploy a cluster, you can configure the TiKV location in the [initialization configuration file](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-3-initialize-cluster-topology-file). TiUP will generate the corresponding configuration files for TiDB, TiKV, PD, and TiFlash during deployment.

In the following example, a two-layer topology of `zone/host` is defined. The TiDB nodes, TiKV nodes, and TiFlash nodes of the cluster are distributed among three zones, z1, z2, and z3.

- In each zone, there are two hosts that have TiDB instances deployed, and each host has a separate TiDB instance deployed.
- In each zone, there are two hosts that have TiKV instances deployed. In z1, each host has two TiKV instances deployed. In z2 and z3, each host has a separate TiKV instance deployed.
- In each zone, there are two hosts that have TiFlash instances deployed, and each host has a separate TiFlash instance deployed.

In the following example, `tidb-host-machine-n` represents the IP address of the `n`th TiDB node, `tikv-host-machine-n` represents the IP address of the `n`th TiKV node, and `tiflash-host-machine-n` represents the IP address of the `n`th TiFlash node.

```
server_configs:
  pd:
    replication.location-labels: ["zone", "host"]
tidb_servers:
# z1
  - host: tidb-host-machine-1
    config:
      labels:
        zone: z1
        host: tidb-host-machine-1
  - host: tidb-host-machine-2
    config:
      labels:
        zone: z1
        host: tidb-host-machine-2
# z2
  - host: tidb-host-machine-3
    config:
      labels:
        zone: z2
        host: tidb-host-machine-3
  - host: tikv-host-machine-4
    config:
      labels:
        zone: z2
        host: tidb-host-machine-4
# z3
  - host: tidb-host-machine-5
    config:
      labels:
        zone: z3
        host: tidb-host-machine-5
  - host: tidb-host-machine-6
    config:
      labels:
        zone: z3
        host: tidb-host-machine-6
tikv_servers:
# z1
  # machine-1 on z1
  - host: tikv-host-machine-1
    port: 20160
    config:
      server.labels:
        zone: z1
        host: tikv-host-machine-1
  - host: tikv-host-machine-1
    port: 20161
    config:
      server.labels:
        zone: z1
        host: tikv-host-machine-1
  # machine-2 on z1
  - host: tikv-host-machine-2
    port: 20160
    config:
      server.labels:
        zone: z1
        host: tikv-host-machine-2
  - host: tikv-host-machine-2
    port: 20161
    config:
      server.labels:
        zone: z1
        host: tikv-host-machine-2
# z2
  - host: tikv-host-machine-3
    config:
      server.labels:
        zone: z2
        host: tikv-host-machine-3
  - host: tikv-host-machine-4
    config:
      server.labels:
        zone: z2
        host: tikv-host-machine-4
# z3
  - host: tikv-host-machine-5
    config:
      server.labels:
        zone: z3
        host: tikv-host-machine-5
  - host: tikv-host-machine-6
    config:
      server.labels:
        zone: z3
        host: tikv-host-machine-6

tiflash_servers:
# z1
  - host: tiflash-host-machine-1
    learner_config:
      server.labels:
        zone: z1
        host: tiflash-host-machine-1
  - host: tiflash-host-machine-2
    learner_config:
      server.labels:
        zone: z1
        host: tiflash-host-machine-2
# z2
  - host: tiflash-host-machine-3
    learner_config:
      server.labels:
        zone: z2
        host: tiflash-host-machine-3
  - host: tiflash-host-machine-4
    learner_config:
      server.labels:
        zone: z2
        host: tiflash-host-machine-4
# z3
  - host: tiflash-host-machine-5
    learner_config:
      server.labels:
        zone: z3
        host: tiflash-host-machine-5
  - host: tiflash-host-machine-6
    learner_config:
      server.labels:
        zone: z3
        host: tiflash-host-machine-6
```

For details, see [Geo-distributed Deployment topology](https://docs.pingcap.com/tidb/stable/geo-distributed-deployment-topology).

> **Note:**
>
> If you have not configured `replication.location-labels` in the configuration file, when you deploy a cluster using this topology file, an error might occur. It is recommended that you confirm `replication.location-labels` is configured in the configuration file before deploying a cluster.
### Configure a cluster using command lines or configuration files
#### Configure `labels` for TiKV and TiFlash

You can use the command-line flag or set the TiKV or TiFlash configuration file to bind some attributes in the form of key-value pairs. These attributes are called `labels`. After TiKV and TiFlash are started, they report their `labels` to PD so users can identify the location of TiKV and TiFlash nodes.

Assume that the topology has four layers: zone > data center (dc) > rack > host, and you can use these labels (zone, dc, rack, host) to set location of the TiKV and TiFlash. To set labels for TiKV and TiFlash, you can use one of the following methods:

+ Use the command-line flag to start a TiKV instance:

    ```shell
    tikv-server --labels zone=<zone>,dc=<dc>,rack=<rack>,host=<host>
    ```

+ Configure in the TiKV configuration file:

    ```toml
    [server]
    [server.labels]
    zone = "<zone>"
    dc = "<dc>"
    rack = "<rack>"
    host = "<host>"
    ```

To set labels for TiFlash, you can use the `tiflash-learner.toml` file, which is the configuration file of tiflash-proxy:

```toml
[server]
[server.labels]
zone = "<zone>"
dc = "<dc>"
rack = "<rack>"
host = "<host>"
```
#### (Optional) Configure `labels` for TiDB

When [Follower read](https://docs.pingcap.com/tidb/stable/follower-read) is enabled, if you want TiDB to prefer to read data from the same region, you need to configure `labels` for TiDB nodes.

You can set `labels` for TiDB using the configuration file:

```toml
[labels]
zone = "<zone>"
dc = "<dc>"
rack = "<rack>"
host = "<host>"
```

> **Note:**
>
> Currently, TiDB depends on the `zone` label to match and select replicas that are in the same region. To use this feature, you need to include `zone` when [configuring `location-labels` for PD](#configure-location-labels-for-pd), and configure `zone` when configuring `labels` for TiDB, TiKV, and TiFlash. For more details, see [Configure `labels` for TiKV and TiFlash](#configure-labels-for-tikv-and-tiflash).
