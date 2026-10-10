# Geo-distributed deployment topology and key TiKV/PD parameters

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/geo-distributed-deployment-topology.md`
- Source Title: `Geo-distributed Deployment topology`
- Source Heading Path: `Geo-Distributed Deployment Topology | Geo-Distributed Deployment Topology > Topology information | Geo-Distributed Deployment Topology > Topology information > Topology templates | Geo-Distributed Deployment Topology > Topology information > Key parameters | Geo-Distributed Deployment Topology > Topology information > Key parameters > TiKV parameters | Geo-Distributed Deployment Topology > Topology information > Key parameters > PD parameters`
- Source Line Ranges: `5-103`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`, `tiup`
- Topic Tags: `geo-distributed`, `topology`, `deployment`, `templates`, `labels`, `replication`, `leader-election`, `placement-rules`, `high-availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0041_2bb50c8371`
- Source ID: `tidb-docs-8.1:geo-distributed-deployment-topology.md#geo-distributed-deployment-topology`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `61f502bb10ba74ebd36555d6f306e4a29aeec29ade609eed5d2b25a78dc255fe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/geo-distributed-deployment-topology#geo-distributed-deployment-topology
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/geo-distributed-deployment-topology.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the example geo-distributed deployment topology across three data centers in two cities and the key TiKV and PD parameters for labels, replica placement, election timeout ticks, and leader election policy.
- Retrieval Keywords: Geo-Distributed Deployment Topology, three data centers in two cities, sha, bja, bjb, geo-redundancy-deployment.yaml, Topology Configuration File for Deploying TiDB Using TiUP, server.grpc-compression-type: gzip, server.labels, zone, dc, rack, host, raftstore.raft-min-election-timeout-ticks, raftstore.raft-max-election-timeout-ticks, replication.location-labels, replication.max-replicas: 5, label-property, reject-leader, placement rules, Schedule Replicas by Topology Labels, remote TiKV Raft replica being elected as Leader
- Follow-up Guidance: The source also points to the geo-distributed topology template, the TiUP topology reference, placement rules, and Schedule Replicas by Topology Labels for further information.
- Classification Note: This is classified as architecture because the content describes a geo-distributed cluster topology example and the topology-related TiKV and PD configuration parameters that govern replica scheduling, labels, and leader election behavior.

## Official Source Content

# Geo-Distributed Deployment Topology

This document takes the typical architecture of three data centers (DC) in two cities as an example, and introduces the geo-distributed deployment architecture and the key configuration. The cities used in this example are Shanghai (referred to as `sha`) and Beijing (referred to as `bja` and `bjb`).
## Topology information

| Instance | Count | Physical machine configuration | BJ IP | SH IP | Configuration |
| :-- | :-- | :-- | :-- | :-- | :-- |
| TiDB | 5 | 16 VCore 32GB * 1 | 10.0.1.1 <br/> 10.0.1.2 <br/> 10.0.1.3 <br/> 10.0.1.4 | 10.0.1.5 | Default port <br/> Global directory configuration |
| PD | 5 | 4 VCore 8GB * 1 | 10.0.1.6 <br/> 10.0.1.7 <br/> 10.0.1.8 <br/> 10.0.1.9 | 10.0.1.10 | Default port <br/> Global directory configuration |
| TiKV | 5 | 16 VCore 32GB 4TB (nvme ssd) * 1 | 10.0.1.11 <br/> 10.0.1.12 <br/> 10.0.1.13 <br/> 10.0.1.14 | 10.0.1.15 | Default port <br/> Global directory configuration |
| Monitoring & Grafana | 1 | 4 VCore 8GB * 1 500GB (ssd) | 10.0.1.16 | | Default port <br/> Global directory configuration |

> **Note:**
>
> The IP addresses of the instances are given as examples only. In your actual deployment, replace the IP addresses with your actual IP addresses.
### Topology templates

- [The geo-distributed topology template](https://github.com/pingcap/docs/blob/master/config-templates/geo-redundancy-deployment.yaml)

For detailed descriptions of the configuration items in the above TiDB cluster topology file, see [Topology Configuration File for Deploying TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference).
### Key parameters

This section describes the key parameter configuration of the TiDB geo-distributed deployment.
#### TiKV parameters

- The gRPC compression format (`none` by default):

    To increase the transmission speed of gRPC packages between geo-distributed target nodes, set this parameter to `gzip`.

    ```yaml
    server.grpc-compression-type: gzip
    ```

- The label configuration:

    Since TiKV is deployed across different data centers, if the physical machines go down, the Raft Group might lose three of the default five replicas, which causes the cluster unavailability. To address this issue, you can configure the labels to enable the smart scheduling of PD, which ensures that the Raft Group does not allow three replicas to be located in TiKV instances on the same machine in the same cabinet of the same data center.

- The TiKV configuration:

    The same host-level label information is configured for the same physical machine.

    ```yaml
    config:
      server.labels:
        zone: bj
        dc: bja
        rack: rack1
        host: host2
    ```

- To prevent remote TiKV nodes from launching unnecessary Raft elections, it is required to increase the minimum and maximum number of ticks that the remote TiKV nodes need to launch an election. The two parameters are set to `0` by default.

    ```yaml
    raftstore.raft-min-election-timeout-ticks: 50
    raftstore.raft-max-election-timeout-ticks: 60
    ```

> **Note:** 
>
> Using `raftstore.raft-min-election-timeout-ticks` and `raftstore.raft-max-election-timeout-ticks` to configure larger election timeout ticks for a TiKV node can significantly decrease the likelihood of Regions on that node becoming Leaders. However, in a disaster scenario where some TiKV nodes are offline and the remaining active TiKV nodes lag behind in Raft logs, only Regions on this TiKV node with large election timeout ticks can become Leaders. Because Regions on this TiKV node must wait for at least the duration set by `raftstore.raft-min-election-timeout-ticks` before initiating an election, it is recommended to avoid setting these values excessively large to prevent potential impact on the cluster availability in such scenarios.
#### PD parameters

- The PD metadata information records the topology of the TiKV cluster. PD schedules the Raft Group replicas on the following four dimensions:

    ```yaml
    replication.location-labels: ["zone","dc","rack","host"]
    ```

- To ensure high availability of the cluster, adjust the number of Raft Group replicas to be `5`:

    ```yaml
    replication.max-replicas: 5
    ```

- Forbid the remote TiKV Raft replica being elected as Leader:

    ```yaml
    label-property:
          reject-leader:
            - key: "dc"
              value: "sha"
    ```

   > **Note:**
   >
   > Since TiDB 5.2, the `label-property` configuration is not supported by default. To set the replica policy, use the [placement rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules).
   
For the further information about labels and the number of Raft Group replicas, see [Schedule Replicas by Topology Labels](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels).

> **Note:**
>
> - You do not need to manually create the `tidb` user in the configuration file. The TiUP cluster component automatically creates the `tidb` user on the target machines. You can customize the user, or keep the user consistent with the control machine.
> - If you configure the deployment directory as a relative path, the cluster will be deployed in the home directory of the user.
