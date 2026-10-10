# Scale in TiFlash and TiCDC nodes

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/scale-tidb-using-tiup.md`
- Source Title: `Scale a TiDB Cluster Using TiUP`
- Source Heading Path: `Scale a TiDB Cluster Using TiUP > Scale in a TiFlash cluster | Scale a TiDB Cluster Using TiUP > Scale in a TiFlash cluster > 1. Adjust the number of replicas of the tables according to the number of remaining TiFlash nodes | Scale a TiDB Cluster Using TiUP > Scale in a TiFlash cluster > 2. Perform the scale-in operation | Scale a TiDB Cluster Using TiUP > Scale in a TiFlash cluster > 2. Perform the scale-in operation > Solution 1. Use TiUP to remove a TiFlash node | Scale a TiDB Cluster Using TiUP > Scale in a TiFlash cluster > 2. Perform the scale-in operation > Solution 2. Manually remove a TiFlash node | Scale a TiDB Cluster Using TiUP > Scale in a TiFlash cluster > 3. View the cluster status | Scale a TiDB Cluster Using TiUP > Scale in a TiCDC cluster`
- Source Line Ranges: `371-511`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tiflash`, `ticdc`, `pd`, `tidb`
- Topic Tags: `scale-in`, `tiflash-replica`, `placement-rules`, `pd-ctl`, `store-delete`, `prune`, `cluster-display`, `topology`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0217_e2c2647def`
- Source ID: `tidb-docs-8.1:scale-tidb-using-tiup.md#scale-in-a-tiflash-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6519d5fa7680b42f2fab15e8b730d80bf2214e80468b42c33e2085f77120cc59`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-tiflash-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/scale-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the scale-in steps for TiFlash or TiCDC nodes, including TiFlash replica checks, TiUP removal, manual pd-ctl removal, and topology cleanup.
- Retrieval Keywords: SELECT * FROM information_schema.tiflash_replica WHERE REPLICA_COUNT > 'tobe_left_nodes';, ALTER TABLE <db-name>.<table-name> SET tiflash replica 'new_replica_num';, tiup cluster scale-in <cluster-name> --node 10.0.1.4:9000, tiup cluster prune <cluster-name>, tiup ctl:v<CLUSTER_VERSION> pd -u http://<pd_ip>:<pd_port> store, tiup ctl:v<CLUSTER_VERSION> pd -u http://<pd_ip>:<pd_port> store delete <store_id>, state_name, Tombstone, scale in a TiFlash cluster, scale in a TiCDC cluster, tiup cluster scale-in <cluster-name> --node 10.0.1.4:8300
- Follow-up Guidance: For TiFlash, the content says to verify the removed node becomes `Tombstone` and then run `tiup cluster prune <cluster-name>`, and for TiCDC it shows checking status with `tiup cluster display <cluster-name>`.
- Classification Note: This is classified as an operation because it provides procedural scale-in workflows for TiFlash and TiCDC, including SQL checks, TiUP commands, pd-ctl commands, and status verification.

## Official Source Content

## Scale in a TiFlash cluster

This section exemplifies how to remove a TiFlash node from the `10.0.1.4` host.
### 1. Adjust the number of replicas of the tables according to the number of remaining TiFlash nodes

1. Query whether any table has TiFlash replicas more than the number of TiFlash nodes after scale-in. `tobe_left_nodes` means the number of TiFlash nodes after scale-in. If the query result is empty, you can start scaling in TiFlash. If the query result is not empty, you need to modify the number of TiFlash replicas of the related table(s).

    ```sql
    SELECT * FROM information_schema.tiflash_replica WHERE REPLICA_COUNT >  'tobe_left_nodes';
    ```

2. Execute the following statement for all tables with TiFlash replicas more than the number of TiFlash nodes after scale-in. `new_replica_num` must be less than or equal to `tobe_left_nodes`:

    ```sql
    ALTER TABLE <db-name>.<table-name> SET tiflash replica 'new_replica_num';
    ```

    After executing this statement, TiDB modifies or deletes PD [placement rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules) accordingly. Then, PD schedules data based on the updated placement rules.

3. Perform step 1 again and make sure that there is no table with TiFlash replicas more than the number of TiFlash nodes after scale-in.
### 2. Perform the scale-in operation

Perform the scale-in operation with one of the following solutions.
#### Solution 1. Use TiUP to remove a TiFlash node

1. Confirm the name of the node to be taken down:

    ```shell
    tiup cluster display <cluster-name>
    ```

2. Remove the TiFlash node (assume that the node name is `10.0.1.4:9000` from Step 1):

    ```shell
    tiup cluster scale-in <cluster-name> --node 10.0.1.4:9000
    ```

3. View the status of the removed TiFlash node:

    ```shell
    tiup cluster display <cluster-name>
    ```

4. After the status of the removed TiFlash node becomes `Tombstone`, delete the information of the removed node from the TiUP topology (TiUP will automatically clean up the related data files of the `Tombstone` node):

    ```shell
    tiup cluster prune <cluster-name>
    ```
#### Solution 2. Manually remove a TiFlash node

In special cases (such as when a node needs to be forcibly taken down), or if the TiUP scale-in operation fails, you can manually remove a TiFlash node with the following steps.

1. Use the store command of pd-ctl to view the store ID corresponding to this TiFlash node.

    * Enter the store command in [pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control) (the binary file is under `resources/bin` in the tidb-ansible directory).

    * If you use TiUP deployment, replace `pd-ctl` with `tiup ctl:v<CLUSTER_VERSION> pd`:

    ```shell
    tiup ctl:v<CLUSTER_VERSION> pd -u http://<pd_ip>:<pd_port> store
    ```

    > **Note:**
    >
    > If multiple PD instances exist in the cluster, you only need to specify the IP address:port of an active PD instance in the above command.

2. Remove the TiFlash node in pd-ctl:

    * Enter `store delete <store_id>` in pd-ctl (`<store_id>` is the store ID of the TiFlash node found in the previous step.

    * If you use TiUP deployment, replace `pd-ctl` with `tiup ctl:v<CLUSTER_VERSION> pd`:

        ```shell
        tiup ctl:v<CLUSTER_VERSION> pd -u http://<pd_ip>:<pd_port> store delete <store_id>
        ```

    > **Note:**
    >
    > If multiple PD instances exist in the cluster, you only need to specify the IP address:port of an active PD instance in the above command.

3. Wait for the store of the TiFlash node to disappear or for the `state_name` to become `Tombstone` before you stop the TiFlash process.

4. Delete the information of the removed node from the TiUP topology (TiUP will automatically clean up the related data files of the `Tombstone` node):

    ```shell
    tiup cluster prune <cluster-name>
    ```
### 3. View the cluster status

```shell
tiup cluster display <cluster-name>
```

Access the monitoring platform at <http://10.0.1.5:3000> using your browser, and view the status of the cluster and the new nodes.

After the scaling, the cluster topology is as follows:

| Host IP   | Service   |
|:----|:----|
| 10.0.1.3   | TiDB + TiFlash + TiCDC  |
| 10.0.1.4   | TiDB + PD + TiCDC **(TiFlash is deleted)**  |
| 10.0.1.5   | TiDB+ Monitor  |
| 10.0.1.1   | TiKV    |
| 10.0.1.2   | TiKV    |
## Scale in a TiCDC cluster

 This section exemplifies how to remove the TiCDC node from the `10.0.1.4` host.

1. Take the node offline:

    ```shell
    tiup cluster scale-in <cluster-name> --node 10.0.1.4:8300
    ```

2. View the cluster status:

    ```shell
    tiup cluster display <cluster-name>
    ```

    Access the monitoring platform at <http://10.0.1.5:3000> using your browser, and view the status of the cluster.

The current topology is as follows:

| Host IP   | Service   |
|:----|:----|
| 10.0.1.3   | TiDB + TiFlash + TiCDC  |
| 10.0.1.4   | TiDB + PD + **(TiCDC is deleted）**  |
| 10.0.1.5   | TiDB + Monitor  |
| 10.0.1.1   | TiKV    |
| 10.0.1.2   | TiKV    |
