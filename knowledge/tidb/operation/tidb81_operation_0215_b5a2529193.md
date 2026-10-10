# TiUP scale out for TiFlash and TiCDC nodes

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/scale-tidb-using-tiup.md`
- Source Title: `Scale a TiDB Cluster Using TiUP`
- Source Heading Path: `Scale a TiDB Cluster Using TiUP > Scale out a TiFlash cluster | Scale a TiDB Cluster Using TiUP > Scale out a TiCDC cluster`
- Source Line Ranges: `168-275`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tiflash`, `ticdc`, `pd`, `tidb`
- Topic Tags: `scale-out`, `tiflash`, `ticdc`, `placement-rules`, `configuration`, `cluster-status`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0215_b5a2529193`
- Source ID: `tidb-docs-8.1:scale-tidb-using-tiup.md#scale-out-a-tiflash-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0c549ce28b130f0723b004da7512d0cf5820bc80664a4a521e669f7eb1fea942`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-out-a-tiflash-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/scale-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP scale-out steps for adding TiFlash or TiCDC nodes, including the required `scale-out.yml` fields, placement-rules note for TiFlash, and cluster status checks.
- Retrieval Keywords: Scale out a TiFlash cluster, Scale out a TiCDC cluster, tiflash_servers, cdc_servers, gc-ttl, data_dir: /tidb-data/cdc-8300, tiup ctl:v<CLUSTER_VERSION> pd -u http://<pd_ip>:<pd_port> config set enable-placement-rules true, enable-placement-rules true, pd-ctl, Currently, you can only add IP addresses but not domain names, tiup cluster scale-out <cluster-name> scale-out.yml, tiup cluster display <cluster-name>, mutual trust, -p option, -i option
- Follow-up Guidance: After scaling out TiFlash or TiCDC, the content says to run `tiup cluster display <cluster-name>` and check the monitoring platform to view the status of the cluster and the new node or nodes.
- Classification Note: This chunk is classified as an operation topic because it documents the concrete TiUP scale-out procedures and configuration snippets for TiFlash and TiCDC nodes, plus the TiFlash placement-rules prerequisite note.

## Official Source Content

## Scale out a TiFlash cluster

This section exemplifies how to add a TiFlash node to the `10.0.1.4` host.

> **Note:**
>
> When adding a TiFlash node to an existing TiDB cluster, note the following:
>
> - Confirm that the current TiDB version supports using TiFlash. Otherwise, upgrade your TiDB cluster to v5.0 or later versions.
> - Run the `tiup ctl:v<CLUSTER_VERSION> pd -u http://<pd_ip>:<pd_port> config set enable-placement-rules true` command to enable the Placement Rules feature. Or run the corresponding command in [pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control).

1. Add the node information to the `scale-out.yml` file:

    Create the `scale-out.yml` file to add the TiFlash node information.

    ```ini
    tiflash_servers:
    - host: 10.0.1.4
    ```

    Currently, you can only add IP addresses but not domain names.

2. Run the scale-out command:

    ```shell
    tiup cluster scale-out <cluster-name> scale-out.yml
    ```

    > **Note:**
    >
    > The preceding command is based on the assumption that the mutual trust has been configured for the user to run the command and the new machine. If the mutual trust cannot be configured, use the `-p` option to enter the password of the new machine, or use the `-i` option to specify the private key file.

3. View the cluster status:

    ```shell
    tiup cluster display <cluster-name>
    ```

    Access the monitoring platform at <http://10.0.1.5:3000> using your browser, and view the status of the cluster and the new node.

After the scale-out, the cluster topology is as follows:

| Host IP   | Service   |
|:----|:----|
| 10.0.1.3   | TiDB + TiFlash   |
| 10.0.1.4   | TiDB + PD + **TiFlash**    |
| 10.0.1.5   | TiDB+ TiKV + Monitor   |
| 10.0.1.1   | TiKV    |
| 10.0.1.2   | TiKV    |
## Scale out a TiCDC cluster

This section exemplifies how to add two TiCDC nodes to the `10.0.1.3` and `10.0.1.4` hosts.

1. Add the node information to the `scale-out.yml` file:

    Create the `scale-out.yml` file to add the TiCDC node information.

    ```ini
    cdc_servers:
      - host: 10.0.1.3
        gc-ttl: 86400
        data_dir: /tidb-data/cdc-8300
      - host: 10.0.1.4
        gc-ttl: 86400
        data_dir: /tidb-data/cdc-8300
    ```

2. Run the scale-out command:

    ```shell
    tiup cluster scale-out <cluster-name> scale-out.yml
    ```

    > **Note:**
    >
    > The preceding command is based on the assumption that the mutual trust has been configured for the user to run the command and the new machine. If the mutual trust cannot be configured, use the `-p` option to enter the password of the new machine, or use the `-i` option to specify the private key file.

3. View the cluster status:

    ```shell
    tiup cluster display <cluster-name>
    ```

    Access the monitoring platform at <http://10.0.1.5:3000> using your browser, and view the status of the cluster and the new nodes.

After the scale-out, the cluster topology is as follows:

| Host IP   | Service   |
|:----|:----|
| 10.0.1.3   | TiDB + TiFlash + **TiCDC**  |
| 10.0.1.4   | TiDB + PD + TiFlash + **TiCDC**  |
| 10.0.1.5   | TiDB+ TiKV + Monitor   |
| 10.0.1.1   | TiKV    |
| 10.0.1.2   | TiKV    |
