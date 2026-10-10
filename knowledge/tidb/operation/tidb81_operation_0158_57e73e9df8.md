# TiUP configuration changes, hotfix patching, and cluster renaming

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/maintain-tidb-using-tiup.md`
- Source Title: `TiUP Common Operations`
- Source Heading Path: `TiUP Common Operations > Modify the configuration | TiUP Common Operations > Modify the configuration > Example | TiUP Common Operations > Replace with a hotfix package | TiUP Common Operations > Rename the cluster`
- Source Line Ranges: `79-198`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `pd`, `shared`
- Topic Tags: `edit-config`, `server-configs`, `node-config`, `reload`, `rolling-restart`, `hotfix`, `patch`, `rename`, `monitoring-restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0158_57e73e9df8`
- Source ID: `tidb-docs-8.1:maintain-tidb-using-tiup.md#modify-the-configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e521cfaf691ea300e64869769c3c8983e85a8a70a440f204c44d31b6a3b7f2df`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/maintain-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this when you need to edit component configuration, apply a hotfix package with patch, or rename a deployed cluster.
- Retrieval Keywords: tiup cluster edit-config ${cluster-name}, server_configs, tidb_servers, log.slow-threshold: 300, tiup cluster reload ${cluster-name} [-N <nodes>] [-R <roles>], tiup cluster patch --help, tiup cluster patch test-cluster /tmp/tidb-hotfix.tar.gz -R tidb, tiup cluster patch test-cluster /tmp/tidb-hotfix.tar.gz -N 172.16.4.5:4000, tiup cluster rename ${cluster-name} ${new-name}, Prometheus and Grafana
- Follow-up Guidance: After renaming a cluster, some old cluster-name panels on Grafana might remain and need to be deleted manually.
- Classification Note: This chunk covers TiUP configuration changes, rolling reloads, hotfix replacement with patch, and cluster renaming.

## Official Source Content

## Modify the configuration

When the cluster is in operation, if you need to modify the parameters of a component, run the `edit-config` command. The detailed steps are as follows:

1. Open the configuration file of the cluster in the editing mode:

    ```bash
    tiup cluster edit-config ${cluster-name}
    ```

2. Configure the parameters:

    - If the configuration is globally effective for a component, edit `server_configs`:

        ```
        server_configs:
          tidb:
            log.slow-threshold: 300
        ```

    - If the configuration takes effect on a specific node, edit the configuration in `config` of the node:

        ```
        tidb_servers:
        - host: 10.0.1.11
          port: 4000
          config:
              log.slow-threshold: 300
        ```

    For the parameter format, see the [TiUP parameter template](https://github.com/pingcap/tiup/blob/master/embed/examples/cluster/topology.example.yaml).

    **Use `.` to represent the hierarchy of the configuration items**.

    For more information on the configuration parameters of components, refer to [TiDB `config.toml.example`](https://github.com/pingcap/tidb/blob/release-8.1/pkg/config/config.toml.example), [TiKV `config.toml.example`](https://github.com/tikv/tikv/blob/release-8.1/etc/config-template.toml), and [PD `config.toml.example`](https://github.com/tikv/pd/blob/release-8.1/conf/config.toml).

3. Rolling update the configuration and restart the corresponding components by running the `reload` command:

    ```bash
    tiup cluster reload ${cluster-name} [-N <nodes>] [-R <roles>]
    ```
### Example

If you want to set the transaction size limit parameter (`txn-total-size-limit` in the [performance](https://github.com/pingcap/tidb/blob/release-8.1/pkg/config/config.toml.example) module) to `1G` in tidb-server, edit the configuration as follows:

```
server_configs:
  tidb:
    performance.txn-total-size-limit: 1073741824
```

Then, run the `tiup cluster reload ${cluster-name} -R tidb` command to rolling restart the TiDB component.
## Replace with a hotfix package

For normal upgrade, see [Upgrade TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup). But in some scenarios, such as debugging, you might need to replace the currently running component with a temporary package. To achieve this, use the `patch` command:

```bash
tiup cluster patch --help
```

```
Replace the remote package with a specified package and restart the service

Usage:
  cluster patch <cluster-name> <package-path> [flags]

Flags:
  -h, --help                   help for patch
  -N, --node strings           Specify the nodes
      --overwrite              Use this package in the future scale-out operations
  -R, --role strings           Specify the role
      --transfer-timeout int   Timeout in seconds when transferring PD and TiKV store leaders (default 600)

Global Flags:

      --native-ssh        Use the system's native SSH client
      --wait-timeout int  Timeout of waiting the operation
      --ssh-timeout int   Timeout in seconds to connect host via SSH, ignored for operations that don't need an SSH connection. (default 5)
  -y, --yes               Skip all confirmations and assumes 'yes'
```

If a TiDB hotfix package is in `/tmp/tidb-hotfix.tar.gz` and you want to replace all the TiDB packages in the cluster, run the following command:

```bash
tiup cluster patch test-cluster /tmp/tidb-hotfix.tar.gz -R tidb
```

You can also replace only one TiDB package in the cluster:

```bash
tiup cluster patch test-cluster /tmp/tidb-hotfix.tar.gz -N 172.16.4.5:4000
```
## Rename the cluster

After deploying and starting the cluster, you can rename the cluster using the `tiup cluster rename` command:

```bash
tiup cluster rename ${cluster-name} ${new-name}
```

> **Note:**
>
> + The operation of renaming a cluster restarts the monitoring system (Prometheus and Grafana).
> + After a cluster is renamed, some panels with the old cluster name might remain on Grafana. You need to delete them manually.
