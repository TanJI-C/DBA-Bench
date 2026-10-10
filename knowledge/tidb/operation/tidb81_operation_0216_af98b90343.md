# Scale in TiDB, PD, or TiKV nodes with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/scale-tidb-using-tiup.md`
- Source Title: `Scale a TiDB Cluster Using TiUP`
- Source Heading Path: `Scale a TiDB Cluster Using TiUP > Scale in a TiDB/PD/TiKV cluster`
- Source Line Ranges: `276-370`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `scale-in`, `node-removal`, `cluster-display`, `reload`, `prometheus`, `topology`, `tombstone`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0216_af98b90343`
- Source ID: `tidb-docs-8.1:scale-tidb-using-tiup.md#scale-in-a-tidb-pd-tikv-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fd87b4bf042f0506e1bc668a0b32cee36b6f97fd7086ba489aa0b6d2fe1bd537`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-tidb-pd-tikv-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/scale-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP scale-in procedure for removing a TiDB, PD, or TiKV node and checking node IDs and Tombstone status.
- Retrieval Keywords: tiup cluster scale-in <cluster-name> --node 10.0.1.5:20160, tiup cluster display <cluster-name>, tiup cluster reload <cluster-name> --skip-restart, tiup cluster reload <cluster-name> -R prometheus, Tombstone, PD leader, remove a TiKV node, scale in a TiDB/PD/TiKV cluster
- Follow-up Guidance: The content notes that refreshing cluster configuration is only required after removing PD nodes, and for TiUP earlier than v1.15.0 it shows `tiup cluster reload <cluster-name> --skip-restart` and `tiup cluster reload <cluster-name> -R prometheus`.
- Classification Note: This is classified as an operation because it gives step-by-step TiUP commands to scale in cluster nodes and verify the result.

## Official Source Content

## Scale in a TiDB/PD/TiKV cluster

This section exemplifies how to remove a TiKV node from the `10.0.1.5` host.

> **Note:**
>
> - You can take similar steps to remove a TiDB or PD node.
> - Because the TiKV, TiFlash, and TiDB Binlog components are taken offline asynchronously and the stopping process takes a long time, TiUP takes them offline in different methods. For details, see [Particular handling of components' offline process](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-scale-in#particular-handling-of-components-offline-process).
> - The PD Client in TiKV caches the list of PD nodes. The current version of TiKV has a mechanism to automatically and regularly update PD nodes, which can help mitigate the issue of an expired list of PD nodes cached by TiKV. However, after scaling out PD, you should try to avoid directly removing all PD nodes at once that exist before the scaling. If necessary, before making all the previously existing PD nodes offline, make sure to switch the PD leader to a newly added PD node.

1. View the node ID information:

    ```shell
    tiup cluster display <cluster-name>
    ```

    ```
    Starting /root/.tiup/components/cluster/v1.12.3/cluster display <cluster-name>
    TiDB Cluster: <cluster-name>
    TiDB Version: v8.1.2
    ID              Role         Host        Ports                            Status  Data Dir                Deploy Dir
    --              ----         ----        -----                            ------  --------                ----------
    10.0.1.3:8300   cdc          10.0.1.3    8300                             Up      data/cdc-8300           deploy/cdc-8300
    10.0.1.4:8300   cdc          10.0.1.4    8300                             Up      data/cdc-8300           deploy/cdc-8300
    10.0.1.4:2379   pd           10.0.1.4    2379/2380                        Healthy data/pd-2379            deploy/pd-2379
    10.0.1.1:20160  tikv         10.0.1.1    20160/20180                      Up      data/tikv-20160         deploy/tikv-20160
    10.0.1.2:20160  tikv         10.0.1.2    20160/20180                      Up      data/tikv-20160         deploy/tikv-20160
    10.0.1.5:20160  tikv         10.0.1.5    20160/20180                      Up      data/tikv-20160         deploy/tikv-20160
    10.0.1.3:4000   tidb         10.0.1.3    4000/10080                       Up      -                       deploy/tidb-4000
    10.0.1.4:4000   tidb         10.0.1.4    4000/10080                       Up      -                       deploy/tidb-4000
    10.0.1.5:4000   tidb         10.0.1.5    4000/10080                       Up      -                       deploy/tidb-4000
    10.0.1.3:9000   tiflash      10.0.1.3    9000/8123/3930/20170/20292/8234  Up      data/tiflash-9000       deploy/tiflash-9000
    10.0.1.4:9000   tiflash      10.0.1.4    9000/8123/3930/20170/20292/8234  Up      data/tiflash-9000       deploy/tiflash-9000
    10.0.1.5:9090   prometheus   10.0.1.5    9090                             Up      data/prometheus-9090    deploy/prometheus-9090
    10.0.1.5:3000   grafana      10.0.1.5    3000                             Up      -                       deploy/grafana-3000
    10.0.1.5:9093   alertmanager 10.0.1.5    9093/9294                        Up      data/alertmanager-9093  deploy/alertmanager-9093
    ```

2. Run the scale-in command:

    ```shell
    tiup cluster scale-in <cluster-name> --node 10.0.1.5:20160
    ```

    The `--node` parameter is the ID of the node to be taken offline.

    If you see `Scaled cluster <cluster-name> in successfully`, the scale-in operation succeeds.

3. Refresh the cluster configuration.

    > **Note:**
    >
    > - Refreshing cluster configuration is only required after you remove PD nodes. If you only remove TiDB or TiKV nodes, skip this step.
    > - If you are using TiUP v1.15.0 or a later version, skip this step because TiUP does it. If you are using a TiUP version earlier than v1.15.0, perform the following sub-steps.

    1. Refresh the cluster configuration:

        ```shell
        tiup cluster reload <cluster-name> --skip-restart
        ```

    2. Refresh the Prometheus configuration and restart Prometheus:

        ```shell
        tiup cluster reload <cluster-name> -R prometheus
        ```

4. Check the cluster status:

    The scale-in process takes some time. You can run the following command to check the scale-in status:

    ```shell
    tiup cluster display <cluster-name>
    ```

    If the node to be scaled in becomes `Tombstone`, the scale-in operation succeeds.

    Access the monitoring platform at <http://10.0.1.5:3000> using your browser, and view the status of the cluster.

The current topology is as follows:

| Host IP   | Service   |
|:----|:----|
| 10.0.1.3   | TiDB + TiFlash + TiCDC  |
| 10.0.1.4   | TiDB + PD + TiFlash + TiCDC |
| 10.0.1.5   | TiDB + Monitor **(TiKV is deleted)**   |
| 10.0.1.1   | TiKV    |
| 10.0.1.2   | TiKV    |
