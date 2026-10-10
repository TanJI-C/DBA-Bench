# TiUP DM overview, syntax, global options, and command list

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm.md`
- Source Title: `TiUP DM`
- Source Heading Path: `TiUP DM | TiUP DM > Syntax | TiUP DM > Options | TiUP DM > Options > --ssh | TiUP DM > Options > --ssh-timeout | TiUP DM > Options > --wait-timeout | TiUP DM > Options > -y, --yes | TiUP DM > Options > -v, --version | TiUP DM > Options > -h, --help | TiUP DM > Command list`
- Source Line Ranges: `5-86`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `cli`, `syntax`, `global-options`, `ssh`, `timeouts`, `confirmation`, `version`, `help`, `command-list`, `cluster-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1034_386e0fb9c9`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm.md#tiup-dm`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9773e3b11a68aa64114b11f7ae2be4716c1616ab83bf7539b57e056dd3144e1f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#tiup-dm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP DM CLI syntax, global options such as SSH and timeout flags, or the list of supported DM cluster management commands.
- Retrieval Keywords: TiUP DM, tiup dm [command] [flags], --ssh, builtin, system, none, --ssh-timeout, --wait-timeout, -y, --yes, -v, --version, -h, --help, import, template, deploy, list, display, start, stop, restart, scale-in, scale-out, upgrade, prune, edit-config, reload, patch, destroy, audit, replay, enable, disable, help, DM clusters, operation audit log, Tombstone status
- Follow-up Guidance: The source also points to subcommand pages for import, deploy, display, start, stop, scale-in, scale-out, upgrade, prune, edit-config, reload, patch, destroy, audit, replay, enable, disable, and help.
- Classification Note: This is reference content because it defines the TiUP DM command syntax, documents global flags and defaults, and enumerates the supported command list for managing DM clusters.

## Official Source Content

# TiUP DM

Similar to [TiUP Cluster](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster) which is used to manage TiDB clusters, TiUP DM is used to manage DM clusters. You can use the TiUP DM component to perform daily operations and maintenance tasks of DM clusters, including deploying, starting, stopping, destroying, elastic scaling, upgrading DM clusters, and managing the configuration parameters of DM clusters.
## Syntax

```shell
tiup dm [command] [flags]
```

`[command]` is used to pass the name of the command. See the [Command list](#command-list) for supported commands.
## Options
### --ssh

- Specifies the SSH client to connect to the remote end (the machine where the TiDB service is deployed) for the command execution.
- Data type: `STRING`
- Support values:

    - `builtin`: Uses the built-in easyssh client of tiup-cluster as the SSH client.
    - `system`: Uses the default SSH client of the current operating system.
    - `none`: No SSH client is used. The deployment is only for the current machine.

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

- Skips the secondary confirmation of all risky operations. It is not recommended to use this option unless you use a script to call TiUP.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
### -v, --version

- Prints the current version of TiUP DM.
- Data type:`BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
### -h, --help

- Prints help information about the specified command.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Command list

- [import](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-import): Imports a DM v1.0 cluster deployed by DM-Ansible.
- [template](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-template): Outputs the topology template.
- [deploy](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-deploy): Deploys a cluster based on a specified topology.
- [list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list): Queries the list of deployed clusters.
- [display](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display): Displays the status of a specified cluster.
- [start](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-start): Starts a specified cluster.
- [stop](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-stop): Stops a specified cluster.
- [restart](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-restart): Restarts a specified cluster.
- [scale-in](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-scale-in): Scales in a specified cluster.
- [scale-out](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-scale-out): Scales out a specified cluster.
- [upgrade](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-upgrade): Upgrades a specified cluster.
- [prune](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-prune): Cleans up instances in the Tombstone status for a specified cluster.
- [edit-config](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-edit-config): Modifies the configuration of a specified cluster.
- [reload](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-reload): Reloads the configuration of a specified cluster.
- [patch](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-patch): Replaces a specified service in a deployed cluster.
- [destroy](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-destroy): Destroys a specified cluster.
- [audit](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-audit): Queries the operation audit log of a specified cluster.
- [replay](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-replay): Replays the specified commands
- [enable](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-enable): Enables the auto-enabling of the cluster service after a machine is restarted.
- [disable](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-disable): Disables the auto-enabling of the cluster service after a machine is restarted.
- [help](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-help): Prints help information.

[<< Back to the previous page - TiUP Reference component list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#component-list)
