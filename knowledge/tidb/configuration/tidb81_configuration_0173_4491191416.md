# Topology YAML, labels, and tuning for three-AZ two-region deployment

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/three-data-centers-in-two-cities-deployment.md`
- Source Title: `Three Availability Zones in Two Regions Deployment`
- Source Heading Path: `Three Availability Zones in Two Regions Deployment > Configuration | Three Availability Zones in Two Regions Deployment > Configuration > Example | Three Availability Zones in Two Regions Deployment > Configuration > Labels design | Three Availability Zones in Two Regions Deployment > Configuration > Optimize parameter configuration`
- Source Line Ranges: `60-209`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `topology-yaml`, `labels`, `location-labels`, `replica-policy`, `grpc-compression`, `election-timeout`, `scheduling`, `leader-priority`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0173_4491191416`
- Source ID: `tidb-docs-8.1:three-data-centers-in-two-cities-deployment.md#configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `29eaa78c722b73b89a26374858b95dfe659153d3bd8dba1e76911a60974c1a6a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/three-data-centers-in-two-cities-deployment#configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/three-data-centers-in-two-cities-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the official topology.yaml example, label configuration, or parameter tuning details for a three availability zones in two regions deployment.
- Retrieval Keywords: tiup topology.yaml, replication.location-labels, server.labels, az replication zone rack host, server.grpc-compression-type gzip, raftstore.raft-min-election-timeout-ticks, raftstore.raft-max-election-timeout-ticks, config set max-replicas 5, config set label-property reject-leader dc 3, member leader_priority, pd scheduling policy, placement rules, TiKV labels design, Optimize parameter configuration
- Follow-up Guidance: The source also provides the note that starting from TiDB v5.2, label-property is not supported by default and placement rules should be used to set the replica policy.
- Classification Note: This is classified as configuration because the content provides concrete YAML settings, TiKV and PD label definitions, and specific scheduling and leader priority commands.

## Official Source Content

## Configuration
### Example

See the following `tiup topology.yaml` yaml file for example:

```yaml
# # Global variables are applied to all deployments and used as the default value of
# # the deployments if a specific deployment value is missing.
global:
  user: "tidb"
  ssh_port: 22
  deploy_dir: "/data/tidb_cluster/tidb-deploy"
  data_dir: "/data/tidb_cluster/tidb-data"

server_configs:
  tikv:
    server.grpc-compression-type: gzip
  pd:
    replication.location-labels: ["az","replication zone","rack","host"]

pd_servers:
  - host: 10.63.10.10
    name: "pd-10"
  - host: 10.63.10.11
    name: "pd-11"
  - host: 10.63.10.12
    name: "pd-12"
  - host: 10.63.10.13
    name: "pd-13"
  - host: 10.63.10.14
    name: "pd-14"

tidb_servers:
  - host: 10.63.10.10
  - host: 10.63.10.11
  - host: 10.63.10.12
  - host: 10.63.10.13
  - host: 10.63.10.14

tikv_servers:
  - host: 10.63.10.30
    config:
      server.labels: { az: "1", replication zone: "1", rack: "1", host: "30" }
  - host: 10.63.10.31
    config:
      server.labels: { az: "1", replication zone: "2", rack: "2", host: "31" }
  - host: 10.63.10.32
    config:
      server.labels: { az: "2", replication zone: "3", rack: "3", host: "32" }
  - host: 10.63.10.33
    config:
      server.labels: { az: "2", replication zone: "4", rack: "4", host: "33" }
  - host: 10.63.10.34
    config:
      server.labels: { az: "3", replication zone: "5", rack: "5", host: "34" }
      raftstore.raft-min-election-timeout-ticks: 50
      raftstore.raft-max-election-timeout-ticks: 60

monitoring_servers:
  - host: 10.63.10.60

grafana_servers:
  - host: 10.63.10.60

alertmanager_servers:
  - host: 10.63.10.60
```
### Labels design

In the deployment of three AZs in two regions, the label design requires taking availability and disaster recovery into account. It is recommended that you define the four levels (`az`, `replication zone`, `rack`, and `host`) based on the physical structure of the deployment.

![Label logical definition](/media/three-data-centers-in-two-cities-deployment-03.png)

In the PD configuration, add level information of TiKV labels:

```yaml
server_configs:
  pd:
    replication.location-labels: ["az","replication zone","rack","host"]
```

The configuration of `tikv_servers` is based on the label information of the real physical deployment location of TiKV, which makes it easier for PD to perform global management and scheduling.

```yaml
tikv_servers:
  - host: 10.63.10.30
    config:
      server.labels: { az: "1", replication zone: "1", rack: "1", host: "30" }
  - host: 10.63.10.31
    config:
      server.labels: { az: "1", replication zone: "2", rack: "2", host: "31" }
  - host: 10.63.10.32
    config:
      server.labels: { az: "2", replication zone: "3", rack: "3", host: "32" }
  - host: 10.63.10.33
    config:
      server.labels: { az: "2", replication zone: "4", rack: "4", host: "33" }
  - host: 10.63.10.34
    config:
      server.labels: { az: "3", replication zone: "5", rack: "5", host: "34" }
```
### Optimize parameter configuration

In the deployment of three AZs in two regions, to optimize performance, you need to not only configure regular parameters, but also adjust component parameters.

- Enable gRPC message compression in TiKV. Because data of the cluster is transmitted in the network, you can enable the gRPC message compression to lower the network traffic.

    ```yaml
    server.grpc-compression-type: gzip
    ```

- Optimize the network configuration of the TiKV node in another region (San Francisco). Modify the following TiKV parameters for AZ3 in San Francisco and try to prevent the replica in this TiKV node from participating in the Raft election.

    ```yaml
    raftstore.raft-min-election-timeout-ticks: 50
    raftstore.raft-max-election-timeout-ticks: 60
    ```

> **Note:**
>
> Using `raftstore.raft-min-election-timeout-ticks` and `raftstore.raft-max-election-timeout-ticks` to configure larger election timeout ticks for a TiKV node can significantly decrease the likelihood of Regions on that node becoming Leaders. However, in a disaster scenario where some TiKV nodes are offline and the remaining active TiKV nodes lag behind in Raft logs, only Regions on this TiKV node with large election timeout ticks can become Leaders. Because Regions on this TiKV node must wait for at least the duration set by `raftstore.raft-min-election-timeout-ticks` before initiating an election, it is recommended to avoid setting these values excessively large to prevent potential impact on the cluster availability in such scenarios.

- Configure scheduling. After the cluster is enabled, use the `tiup ctl:v{CLUSTER_VERSION} pd` tool to modify the scheduling policy. Modify the number of TiKV Raft replicas. Configure this number as planned. In this example, the number of replicas is five.

    ```bash
    config set max-replicas 5
    ```

- Forbid scheduling the Raft leader to AZ3. Scheduling the Raft leader to another region (AZ3) causes unnecessary network overhead between AZ1/AZ2 in Seattle and AZ3 in San Francisco. The network bandwidth and latency also affect the performance of the TiDB cluster.

    ```bash
    config set label-property reject-leader dc 3
    ```

   > **Note:**
   >
   > Starting from TiDB v5.2, the `label-property` configuration is not supported by default. To set the replica policy, use the [placement rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules).

- Configure the priority of PD. To avoid the situation where the PD leader is in another region (AZ3), you can increase the priority of local PD (in Seattle) and decrease the priority of PD in another region (San Francisco). The larger the number, the higher the priority.

    ```bash
    member leader_priority PD-10 5
    member leader_priority PD-11 5
    member leader_priority PD-12 5
    member leader_priority PD-13 5
    member leader_priority PD-14 1
    ```
