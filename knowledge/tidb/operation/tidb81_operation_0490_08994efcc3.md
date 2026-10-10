# Scale in a TiDB cluster with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP > Scale in a cluster`
- Source Line Ranges: `235-307`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tiflash`, `tidb`
- Topic Tags: `scale-in`, `node-offline`, `cluster-maintenance`, `topology`, `data-cleanup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0490_08994efcc3`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster.md#scale-in-a-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `786e0432feebac47bb21f7bcff4471cede9b4dd89f2ad2d4d988e6a555494e1a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster#scale-in-a-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP cluster scale-in syntax, how a node is marked Offline, and how TiKV, TiFlash, TiDB Binlog, PD, and other components are handled during node removal.
- Retrieval Keywords: tiup cluster scale-in <cluster-name> -N <node-id>, tiup cluster display, scale in a cluster, Offline, TiKV, TiFlash, TiDB Binlog, PD, remove the node from the cluster topology, clean up the data files related to the node, 172.16.5.140:20160, prod-cluster
- Follow-up Guidance: The content notes that after PD schedules the data on the node to other TiKV nodes, this node will be deleted automatically.
- Classification Note: This is classified as an operation topic because the content explains the scale-in command behavior, required flags, component-specific offline handling, and example cluster maintenance output.

## Official Source Content

## Scale in a cluster

> **Note:**
>
> This section describes only the syntax of the scale-in command. For detailed steps of online scaling, refer to [Scale a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup).

Scaling in a cluster means making some node(s) offline. This operation removes the specific node(s) from the cluster and deletes the remaining files.

Because the offline process of the TiKV, TiFlash, and TiDB Binlog components is asynchronous (which requires removing the node through API), and the process takes a long time (which requires continuous observation on whether the node is successfully taken offline), special treatment is given to the TiKV, TiFlash, and TiDB Binlog components.

- For TiKV, TiFlash, and Binlog:

    - TiUP cluster takes the node offline through API and directly exits without waiting for the process to be completed.
    - Afterwards, when a command related to the cluster operation is executed, TiUP cluster examines whether there is a TiKV, TiFlash, or Binlog node that has been taken offline. If not, TiUP cluster continues with the specified operation; If there is, TiUP cluster takes the following steps:

        1. Stop the service of the node that has been taken offline.
        2. Clean up the data files related to the node.
        3. Remove the node from the cluster topology.

- For other components:

    - When taking the PD component down, TiUP cluster quickly deletes the specified node from the cluster through API, stops the service of the specified PD node, and deletes the related data files.
    - When taking other components down, TiUP cluster directly stops the node service and deletes the related data files.

The basic usage of the scale-in command:

```bash
tiup cluster scale-in <cluster-name> -N <node-id>
```

To use this command, you need to specify at least two flags: the cluster name and the node ID. The node ID can be obtained by using the `tiup cluster display` command in the previous section.

For example, to make the TiKV node on `172.16.5.140` offline, run the following command:

```bash
tiup cluster scale-in prod-cluster -N 172.16.5.140:20160
```

By running `tiup cluster display`, you can see that the TiKV node is marked `Offline`:

```bash
tiup cluster display prod-cluster
```

```
Starting /root/.tiup/components/cluster/v1.12.3/cluster display prod-cluster
TiDB Cluster: prod-cluster
TiDB Version: v8.1.2
ID                  Role        Host          Ports                            OS/Arch       Status   Data Dir              Deploy Dir
--                  ----        ----          -----                            -------       ------   --------              ----------
172.16.5.134:3000   grafana     172.16.5.134  3000                             linux/x86_64  Up       -                     deploy/grafana-3000
172.16.5.134:2379   pd          172.16.5.134  2379/2380                        linux/x86_64  Up|L     data/pd-2379          deploy/pd-2379
172.16.5.139:2379   pd          172.16.5.139  2379/2380                        linux/x86_64  Up|UI    data/pd-2379          deploy/pd-2379
172.16.5.140:2379   pd          172.16.5.140  2379/2380                        linux/x86_64  Up       data/pd-2379          deploy/pd-2379
172.16.5.134:9090   prometheus  172.16.5.134  9090                             linux/x86_64  Up       data/prometheus-9090  deploy/prometheus-9090
172.16.5.134:4000   tidb        172.16.5.134  4000/10080                       linux/x86_64  Up       -                     deploy/tidb-4000
172.16.5.139:4000   tidb        172.16.5.139  4000/10080                       linux/x86_64  Up       -                     deploy/tidb-4000
172.16.5.140:4000   tidb        172.16.5.140  4000/10080                       linux/x86_64  Up       -                     deploy/tidb-4000
172.16.5.141:9000   tiflash     172.16.5.141  9000/8123/3930/20170/20292/8234  linux/x86_64  Up       data/tiflash-9000     deploy/tiflash-9000
172.16.5.142:9000   tiflash     172.16.5.142  9000/8123/3930/20170/20292/8234  linux/x86_64  Up       data/tiflash-9000     deploy/tiflash-9000
172.16.5.143:9000   tiflash     172.16.5.143  9000/8123/3930/20170/20292/8234  linux/x86_64  Up       data/tiflash-9000     deploy/tiflash-9000
172.16.5.134:20160  tikv        172.16.5.134  20160/20180                      linux/x86_64  Up       data/tikv-20160       deploy/tikv-20160
172.16.5.139:20160  tikv        172.16.5.139  20160/20180                      linux/x86_64  Up       data/tikv-20160       deploy/tikv-20160
172.16.5.140:20160  tikv        172.16.5.140  20160/20180                      linux/x86_64  Offline  data/tikv-20160       deploy/tikv-20160
172.16.5.144:6000   tiproxy     172.16.5.144  6000/3080                        linux/x86_64  Up       -                     deploy/tiproxy-6000
```

After PD schedules the data on the node to other TiKV nodes, this node will be deleted automatically.
