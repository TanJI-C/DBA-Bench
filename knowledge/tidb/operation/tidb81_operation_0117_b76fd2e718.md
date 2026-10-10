# DM cluster changes: scale, upgrade, and reload configuration

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/maintain-dm-using-tiup.md`
- Source Title: `Maintain a DM Cluster Using TiUP`
- Source Heading Path: `Maintain a DM Cluster Using TiUP > Scale in a cluster | Maintain a DM Cluster Using TiUP > Scale out a cluster | Maintain a DM Cluster Using TiUP > Rolling upgrade | Maintain a DM Cluster Using TiUP > Rolling upgrade > Upgrade command | Maintain a DM Cluster Using TiUP > Update configuration`
- Source Line Ranges: `120-224`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `scale-in`, `scale-out`, `topology-file`, `rolling-upgrade`, `version-upgrade`, `downgrade-preparation`, `secret-key`, `config-edit`, `reload`, `restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0117_b76fd2e718`
- Source ID: `tidb-docs-8.1:dm/maintain-dm-using-tiup.md#scale-in-a-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ead556f5bd76f4f71e8c1359acfdfc5e43d912397b3a52e7593d97a2fcfefdbf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#scale-in-a-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/maintain-dm-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiUP DM procedures and commands for scale-in, scale-out, rolling upgrade, editing cluster configuration, and reloading configuration.
- Retrieval Keywords: tiup dm scale-in <cluster-name> -N <node-id>, tiup dm scale-in prod-cluster -N 172.16.5.140:8262, tiup dm scale-out prod-cluster scale.yaml, scale.yaml, worker_servers, tiup dm display prod-cluster, tiup dm upgrade prod-cluster ${version}, tiup dm edit-config prod-cluster, tiup dm reload prod-cluster, config export, config import, customized secret key, relay worker, start-relay
- Follow-up Guidance: It explains that scale-in removes specified nodes and deletes remaining data files, scale-out uses a topology file containing only new nodes, and `reload` sends the configuration to target machines and restarts the cluster to make the configuration take effect.
- Classification Note: This is classified as operation content because it covers lifecycle changes to a DM cluster, including scaling, upgrading, and applying configuration changes.

## Official Source Content

## Scale in a cluster

Scaling in a cluster means making some node(s) offline. This operation removes the specified node(s) from the cluster and deletes the remaining data files.

When you scale in a cluster, DM operations on DM-master and DM-worker components are performed in the following order:

1. Stop component processes.
2. Call the API for DM-master to delete the `member`.
3. Clean up the data files related to the node.

The basic usage of the scale-in command:

```bash
tiup dm scale-in <cluster-name> -N <node-id>
```

To use this command, you need to specify at least two arguments: the cluster name and the node ID. The node ID can be obtained by using the `tiup dm display` command in the previous section.

For example, to scale in the DM-worker node on `172.16.5.140` (similar to scaling in DM-master), run the following command:

```bash
tiup dm scale-in prod-cluster -N 172.16.5.140:8262
```
## Scale out a cluster

The scale-out operation has an inner logic similar to that of deployment: the TiUP DM component first ensures the SSH connection of the node, creates the required directories on the target node, then executes the deployment operation, and starts the node service.

For example, to scale out a DM-worker node in the `prod-cluster` cluster, take the following steps (scaling out DM-master has similar steps):

1. Create a `scale.yaml` file and add information of the new worker node:

    > **Note:**
    >
    > You need to create a topology file, which includes only the description of the new nodes, not the existing nodes.
    > For more configuration items (such as the deployment directory), refer to this [TiUP configuration parameter example](https://github.com/pingcap/tiup/blob/master/embed/examples/dm/topology.example.yaml).

    ```yaml
    ---

    worker_servers:
      - host: 172.16.5.140

    ```

2. Perform the scale-out operation. TiUP DM adds the corresponding nodes to the cluster according to the port, directory, and other information described in `scale.yaml`.

    ```shell
    tiup dm scale-out prod-cluster scale.yaml
    ```

    After the command is executed, you can check the status of the scaled-out cluster by running `tiup dm display prod-cluster`.
## Rolling upgrade

> **Note:**
>
> Since v2.0.5, dmctl support [Export and Import Data Sources and Task Configuration of Clusters](https://docs.pingcap.com/tidb/stable/dm/dm-export-import-config).
>
> Before upgrading, you can use `config export` to export the configuration files of clusters. After upgrading, if you need to downgrade to an earlier version, you can first redeploy the earlier cluster and then use `config import` to import the previous configuration files.
>
> For clusters earlier than v2.0.5, you can use dmctl (>= v2.0.5 and < v8.0.0) to export and import the data source and task configuration files.
>
> For clusters later than v2.0.2, currently, it is not supported to automatically import the configuration related to relay worker. You can use `start-relay` command to manually [start relay log](https://docs.pingcap.com/tidb/stable/dm/relay-log#enable-and-disable-relay-log).

The rolling upgrade process is made as transparent as possible to the application, and does not affect the business. The operations vary with different nodes.
### Upgrade command

You can run the `tiup dm upgrade` command to upgrade a DM cluster. For example, the following command upgrades the cluster to `${version}`. Modify `${version}` to your needed version before running this command:

> **Note:**
>
> Starting from v8.0.0, DM removes the fixed secret key for encryption and decryption and enables you to customize a secret key for encryption and decryption. If encrypted passwords are used in [data source configurations](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file) and [migration task configurations](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) before the upgrade, you need to refer to the upgrade steps in [Customize a Secret Key for DM Encryption and Decryption](https://docs.pingcap.com/tidb/stable/dm/dm-customized-secret-key) for additional operations.

```bash
tiup dm upgrade prod-cluster ${version}
```
## Update configuration

If you want to dynamically update the component configurations, the TiUP DM component saves a current configuration for each cluster. To edit this configuration, execute the `tiup dm edit-config <cluster-name>` command. For example:

```bash
tiup dm edit-config prod-cluster
```

TiUP DM opens the configuration file in the vi editor. If you want to use other editors, use the `EDITOR` environment variable to customize the editor, such as `export EDITOR=nano`. After editing the file, save the changes. To apply the new configuration to the cluster, execute the following command:

```bash
tiup dm reload prod-cluster
```

The command sends the configuration to the target machine and restarts the cluster to make the configuration take effect.
