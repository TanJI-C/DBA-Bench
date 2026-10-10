# TiUP Cluster syntax, global options, and command list

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster.md`
- Source Title: `TiUP Cluster`
- Source Heading Path: `TiUP Cluster | TiUP Cluster > Syntax | TiUP Cluster > Options | TiUP Cluster > Options > --ssh | TiUP Cluster > Options > --ssh-timeout | TiUP Cluster > Options > --wait-timeout | TiUP Cluster > Options > -y, --yes | TiUP Cluster > Options > -v, --version | TiUP Cluster > Options > -h, --help | TiUP Cluster > Command list`
- Source Line Ranges: `5-90`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `syntax`, `global-options`, `ssh`, `timeout`, `confirmation`, `version`, `help`, `command-list`, `cluster-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1018_cef8ab6de3`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster.md#tiup-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7d343f3c1dca24e65b4f9d2d5489af1880ba6c9260cba1d75257ae05ebd3f1ae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#tiup-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the overall tiup cluster command syntax, global flags, SSH-related options, timeout behavior, confirmation and help/version flags, or the list of supported cluster management commands.
- Retrieval Keywords: tiup cluster [command] [flags], TiUP Cluster, --ssh, builtin, system, none, --ssh-timeout, --wait-timeout, -y, --yes, -v, --version, -h, --help, import, template, check, deploy, list, display, start, stop, restart, scale-in, scale-out, upgrade, prune, edit-config, reload, patch, rename, clean, destroy, audit, replay, enable, disable, meta backup, meta restore, help, cluster management component of TiUP
- Follow-up Guidance: The source also provides the command list for TiUP Cluster, including commands such as deploy, start, stop, scale-out, upgrade, edit-config, reload, destroy, audit, and meta backup.
- Classification Note: This chunk is classified as reference content because it defines the tiup cluster syntax, documents command-line options with defaults and supported values, and enumerates the supported commands.

## Official Source Content

# TiUP Cluster

TiUP Cluster is a cluster management component of TiUP written in Golang. You can use the TiUP Cluster component to perform daily operations and maintenance, including deploying, starting, shutting down, destroying, elastic scaling, upgrading TiDB clusters, and managing TiDB cluster parameters.
## Syntax

```shell
tiup cluster [command] [flags]
```

`[command]` is the name of the command. For the supported commands, refer to the [command list](#command-list) below.
## Options
### --ssh

- Specifies the SSH client to connect to the remote end (the machine where the TiDB service is deployed) for the command execution.
- Data type: `STRING`
- Supported values:

    - `builtin`: uses the easyssh client built in tiup-cluster as the SSH client.
    - `system`: uses the default SSH client of the current operating system.
    - `none`: The SSH client is not used. The deployment is only for the current machine.

- If this option is not specified in the command, `builtin` is used as the default value.
### --ssh-timeout

- Specifies the SSH connection timeout in seconds.
- Data type: `UINT`
- If this option is not specified in the command, the default timeout is `5` seconds.
### --wait-timeout

- Specifies the maximum waiting time (in seconds) for each step in the operation process. The operation process consists of many steps, such as specifying systemctl to start or stop services, and waiting for ports to be online or offline. Each step may take several seconds. If the execution time of a step exceeds the specified timeout, the step exits with an error.
- Data type: `UINT`
- If this option is not specified in the command, the maximum waiting time for each step is `120` seconds.
### -y, --yes

- Skips the secondary confirmation of all risky operations. Using this option is not recommended, unless you are using a script to call TiUP.
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
### -v, --version

- Prints the current version of TiUP Cluster.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
### -h, --help

- Prints the help information of the related commands.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Command list

- [import](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-import): imports a cluster deployed by Ansible
- [template](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-template): outputs the topology template
- [check](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-check): checks a cluster before and after the deployment
- [deploy](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-deploy): deploys a cluster based on a specified topology
- [list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list): queries the list of deployed clusters
- [display](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display): displays the status of a specified cluster
- [start](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-start): starts a specified cluster
- [stop](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-stop): stops a specified cluster
- [restart](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-restart): restarts a specified cluster
- [scale-in](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-scale-in): scales in a specified cluster
- [scale-out](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-scale-out): scales out a specified cluster
- [upgrade](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-upgrade): upgrades a specified cluster
- [prune](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-prune): cleans up the instances in the Tombstone status for a specified cluster
- [edit-config](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-edit-config): modifies the configuration of a specified cluster
- [reload](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-reload): reloads the configuration of a specified cluster
- [patch](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-patch): replaces a service in a deployed cluster
- [rename](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-rename): renames a cluster
- [clean](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-clean): deletes data from the specified cluster
- [destroy](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-destroy): destroys a specified cluster
- [audit](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-audit): queries the operation audit log of a specified cluster
- [replay](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-replay): retries the specified command
- [enable](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-enable): enables the auto-enabling of the cluster service after a machine is restarted
- [disable](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-disable): disables the auto-enabling of the cluster service after a machine is restarted
- [meta backup](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-meta-backup): backs up the TiUP meta file required for the operation and maintenance of a specified cluster
- [meta restore](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-meta-restore): restores the TiUP meta file of a specified cluster
- [help](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-help): prints the help information

[<< Back to the previous page - TiUP Reference component list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#component-list)
