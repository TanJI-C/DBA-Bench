# Scale out and rolling upgrade a TiDB cluster with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP > Scale out a cluster | Deploy and Maintain an Online TiDB Cluster Using TiUP > Rolling upgrade | Deploy and Maintain an Online TiDB Cluster Using TiUP > Rolling upgrade > Operations for different nodes | Deploy and Maintain an Online TiDB Cluster Using TiUP > Rolling upgrade > Upgrade command`
- Source Line Ranges: `308-405`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `scale-out`, `rolling-upgrade`, `topology-file`, `leader-transfer`, `validation`, `cluster-maintenance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0491_785f3761d3`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster.md#scale-out-a-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5842d16fcfdefa16cce4e731374cdb1e167c2f1e35ea6f7de78537b22ac3375e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster#scale-out-a-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiUP cluster scale-out syntax with a topology file, or for rolling upgrade behavior, node-specific upgrade steps, and upgrade command flags.
- Retrieval Keywords: tiup cluster scale-out tidb-test scale.yaml, scale.yaml, topology file includes only the description of the new nodes, tiup cluster display tidb-test, Rolling upgrade, Operations for different nodes, cluster upgrade <cluster-name> <version> [flags], tiup cluster upgrade tidb-test v8.1.2, --force, --transfer-timeout, PD Leader, TiKV Region Leader, correctness validation, join
- Follow-up Guidance: The content says that before upgrade, TiUP cluster checks whether each component configuration file is rational, and if any unhealthy node is detected during PD upgrade, the tool stops and exits.
- Classification Note: This is classified as an operation topic because the content covers scale-out procedures, rolling upgrade mechanics for PD and TiKV, and the exact TiUP commands and flags used for cluster maintenance.

## Official Source Content

## Scale out a cluster

> **Note:**
>
> This section describes only the syntax of the scale-out command. For detailed steps of online scaling, refer to [Scale a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup).

The scale-out operation has an inner logic similar to that of deployment: the TiUP cluster component firstly ensures the SSH connection of the node, creates the required directories on the target node, then executes the deployment operation, and starts the node service.

When you scale out PD, the node is added to the cluster by `join`, and the configurations of services associated with PD are updated. When you scale out other services, the service is started directly and added to the cluster.

All services conduct correctness validation when they are scaled out. The validation results show whether the scaling-out is successful.

To add a TiKV node and a PD node in the `tidb-test` cluster, take the following steps:

1. Create a `scale.yaml` file, and add IPs of the new TiKV and PD nodes:

    > **Note:**
    >
    > You need to create a topology file, which includes only the description of the new nodes, not the existing nodes.

    ```yaml
    ---

    pd_servers:
      - host: 172.16.5.140

    tikv_servers:
      - host: 172.16.5.140
    ```

2. Perform the scale-out operation. TiUP cluster adds the corresponding nodes to the cluster according to the port, directory, and other information described in `scale.yaml`.

    ```shell
    tiup cluster scale-out tidb-test scale.yaml
    ```

    After the command is executed, you can check the status of the scaled-out cluster by running `tiup cluster display tidb-test`.
## Rolling upgrade

> **Note:**
>
> This section describes only the syntax of the upgrade command. For detailed steps of online upgrade, refer to [Upgrade TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup).

The rolling upgrade feature leverages the distributed capabilities of TiDB. The upgrade process is made as transparent as possible to the application, and does not affect the business.

Before the upgrade, TiUP cluster checks whether the configuration file of each component is rational. If so, the components are upgraded node by node; if not, TiUP reports an error and exits. The operations vary with different nodes.
### Operations for different nodes

- Upgrade the PD node

    - First, upgrade non-Leader nodes.
    - After all the non-Leader nodes are upgraded, upgrade the Leader node.
        - The upgrade tool sends a command to PD that migrates Leader to an already upgraded node.
        - After the Leader role is switched to another node, upgrade the previous Leader node.
    - During the upgrade, if any unhealthy node is detected, the tool stops this upgrade operation and exits. You need to manually analyze the cause, fix the issue and run the upgrade again.

- Upgrade the TiKV node

    - First, add a scheduling operation in PD that migrates the Region Leader of this TiKV node. This ensures that the upgrade process does not affect the business.
    - After the Leader is migrated, upgrade this TiKV node.
    - After the upgraded TiKV is started normally, remove the scheduling of the Leader.

- Upgrade other services

    - Stop the service normally and update the node.
### Upgrade command

The flags for the upgrade command is as follows:

```bash
Usage:
  cluster upgrade <cluster-name> <version> [flags]

Flags:
      --force                  Force upgrade won't transfer leader
  -h, --help                   help for upgrade
      --transfer-timeout int   Timeout in seconds when transferring PD and TiKV store leaders (default 600)

Global Flags:
      --ssh string          (Experimental) The executor type. Optional values are 'builtin', 'system', and 'none'.
      --wait-timeout int  Timeout of waiting the operation
      --ssh-timeout int   Timeout in seconds to connect host via SSH, ignored for operations that don't need an SSH connection. (default 5)
  -y, --yes               Skip all confirmations and assumes 'yes'
```

For example, the following command upgrades the cluster to v8.1.2:

```bash
tiup cluster upgrade tidb-test v8.1.2
```
