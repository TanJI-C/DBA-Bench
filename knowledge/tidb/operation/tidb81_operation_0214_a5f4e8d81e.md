# TiUP scale out for TiDB PD and TiKV clusters

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/scale-tidb-using-tiup.md`
- Source Title: `Scale a TiDB Cluster Using TiUP`
- Source Heading Path: `Scale a TiDB Cluster Using TiUP | Scale a TiDB Cluster Using TiUP > Scale out a TiDB/PD/TiKV cluster`
- Source Line Ranges: `5-167`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `scale-out`, `topology`, `precheck`, `configuration`, `reload`, `monitoring`, `cluster-status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0214_a5f4e8d81e`
- Source ID: `tidb-docs-8.1:scale-tidb-using-tiup.md#scale-a-tidb-cluster-using-tiup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fb12ed730a34fece62282b1caec16e9e0413d07f06dffff97b80efb526cb2288`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-a-tidb-cluster-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/scale-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP procedure and topology examples for scaling out TiDB, PD, or TiKV nodes in a self-managed TiDB cluster, including precheck, inherited configuration, reload, and status verification.
- Retrieval Keywords: tiup cluster list, tiup cluster edit-config <cluster-name>, scale-out.yml, tidb_servers, tikv_servers, pd_servers, tiup cluster check <cluster-name> scale-out.yml --cluster --user root, tiup cluster check <cluster-name> scale-out.yml --cluster --apply --user root, tiup cluster scale-out <cluster-name> scale-out.yml, Scaled cluster <cluster-name> out successfully, tiup cluster reload <cluster-name> --skip-restart, tiup cluster reload <cluster-name> -R prometheus, tiup cluster display <cluster-name>, global configuration inherited, server_configs inherited, PD scheduling parameters
- Follow-up Guidance: If PD nodes are added, the content includes refreshing cluster configuration with `tiup cluster reload <cluster-name> --skip-restart` and refreshing Prometheus with `tiup cluster reload <cluster-name> -R prometheus`, then checking status with `tiup cluster display <cluster-name>`.
- Classification Note: This chunk is classified as an operation topic because it provides step-by-step TiUP scale-out commands, topology configuration examples, precheck commands, and post-scale verification for TiDB, PD, and TiKV.

## Official Source Content

# Scale a TiDB Cluster Using TiUP

The capacity of a TiDB cluster can be increased or decreased without interrupting the online services.

This document describes how to scale the TiDB, TiKV, PD, TiCDC, or TiFlash cluster using TiUP. If you have not installed TiUP, refer to the steps in [Step 2. Deploy TiUP on the control machine](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-2-deploy-tiup-on-the-control-machine).

To view the current cluster name list, run `tiup cluster list`.

For example, if the original topology of the cluster is as follows:

| Host IP | Service |
|:---|:----|
| 10.0.1.3 | TiDB + TiFlash |
| 10.0.1.4 | TiDB + PD |
| 10.0.1.5 | TiKV + Monitor |
| 10.0.1.1 | TiKV |
| 10.0.1.2 | TiKV |
## Scale out a TiDB/PD/TiKV cluster

This section exemplifies how to add a TiDB node to the `10.0.1.5` host.

> **Note:**
>
> You can take similar steps to add a PD node. Before you add a TiKV node, it is recommended that you adjust the PD scheduling parameters in advance according to the cluster load.

1. Configure the scale-out topology:

    > **Note:**
    >
    > * The port and directory information is not required by default.
    > * If multiple instances are deployed on a single machine, you need to allocate different ports and directories for them. If the ports or directories have conflicts, you will receive a notification during deployment or scaling.
    > * Since TiUP v1.0.0, the scale-out configuration inherits the global configuration of the original cluster.

    Add the scale-out topology configuration in the `scale-out.yml` file:

    ```shell
    vi scale-out.yml
    ```

    ```ini
    tidb_servers:
    - host: 10.0.1.5
      ssh_port: 22
      port: 4000
      status_port: 10080
      deploy_dir: /tidb-deploy/tidb-4000
      log_dir: /tidb-deploy/tidb-4000/log
    ```

    Here is a TiKV configuration file template:

    ```ini
    tikv_servers:
    - host: 10.0.1.5
      ssh_port: 22
      port: 20160
      status_port: 20180
      deploy_dir: /tidb-deploy/tikv-20160
      data_dir: /tidb-data/tikv-20160
      log_dir: /tidb-deploy/tikv-20160/log
    ```

    Here is a PD configuration file template:

    ```ini
    pd_servers:
    - host: 10.0.1.5
      ssh_port: 22
      name: pd-1
      client_port: 2379
      peer_port: 2380
      deploy_dir: /tidb-deploy/pd-2379
      data_dir: /tidb-data/pd-2379
      log_dir: /tidb-deploy/pd-2379/log
    ```

    To view the configuration of the current cluster, run `tiup cluster edit-config <cluster-name>`. Because the parameter configuration of `global` and `server_configs` is inherited by `scale-out.yml` and thus also takes effect in `scale-out.yml`.

2. Run the scale-out command:

    Before you run the `scale-out` command, use the `check` and `check --apply` commands to detect and automatically repair potential risks in the cluster:

    1. Check for potential risks:

        ```shell
        tiup cluster check <cluster-name> scale-out.yml --cluster --user root [-p] [-i /home/root/.ssh/gcp_rsa]
        ```

    2. Enable automatic repair:

        ```shell
        tiup cluster check <cluster-name> scale-out.yml --cluster --apply --user root [-p] [-i /home/root/.ssh/gcp_rsa]
        ```

    3. Run the `scale-out` command:

        ```shell
        tiup cluster scale-out <cluster-name> scale-out.yml [-p] [-i /home/root/.ssh/gcp_rsa]
        ```

    In the preceding commands:

    - `scale-out.yml` is the scale-out configuration file.
    - `--user root` indicates logging in to the target machine as the `root` user to complete the cluster scale out. The `root` user is expected to have `ssh` and `sudo` privileges to the target machine. Alternatively, you can use other users with `ssh` and `sudo` privileges to complete the deployment.
    - `[-i]` and `[-p]` are optional. If you have configured login to the target machine without password, these parameters are not required. If not, choose one of the two parameters. `[-i]` is the private key of the root user (or other users specified by `--user`) that has access to the target machine. `[-p]` is used to input the user password interactively.

    If you see `Scaled cluster <cluster-name> out successfully`, the scale-out operation succeeds.

3. Refresh the cluster configuration.

    > **Note:**
    >
    > - Refreshing cluster configuration is only required after you add PD nodes. If you only add TiDB or TiKV nodes, skip this step.
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

    ```shell
    tiup cluster display <cluster-name>
    ```

    Access the monitoring platform at <http://10.0.1.5:3000> using your browser to monitor the status of the cluster and the new node.

After the scale-out, the cluster topology is as follows:

| Host IP   | Service   |
|:----|:----|
| 10.0.1.3   | TiDB + TiFlash   |
| 10.0.1.4   | TiDB + PD   |
| 10.0.1.5   | **TiDB** + TiKV + Monitor   |
| 10.0.1.1   | TiKV    |
| 10.0.1.2   | TiKV    |
