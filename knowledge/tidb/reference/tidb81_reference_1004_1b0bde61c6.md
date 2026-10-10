# tiup cluster display syntax options and output status

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-display.md`
- Source Title: `tiup cluster display`
- Source Heading Path: `tiup cluster display | tiup cluster display > Syntax | tiup cluster display > Options | tiup cluster display > Options > --dashboard | tiup cluster display > Options > -N, --node | tiup cluster display > Options > -R, --role | tiup cluster display > Options > --process | tiup cluster display > Options > --uptime | tiup cluster display > Options > --status-timeout | tiup cluster display > Options > -h, --help | tiup cluster display > Outputs | tiup cluster display > Outputs > Node service status`
- Source Line Ranges: `5-104`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dashboard`, `pd`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `cluster display`, `syntax`, `command options`, `node filtering`, `role filtering`, `dashboard output`, `process usage`, `uptime`, `status timeout`, `service status`, `pd scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1004_1b0bde61c6`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-display.md#tiup-cluster-display`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e85e4bc0239d0026568ca866f188e7cc63785055f44176709ba7a427ff1ef4a5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display#tiup-cluster-display
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-display.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the syntax, flags, displayed fields, or node service status meanings for the `tiup cluster display` command in a TiUP-managed cluster.
- Retrieval Keywords: tiup cluster display <cluster-name> [flags], tiup cluster display, --dashboard, -N, --node, -R, --role, --process, --uptime, --status-timeout, cluster display output fields, Node service status, Up, Down or Unreachable, Tombstone, Pending Offline, Unknown, PD scheduling information, Dashboard address, ID IP:PORT, Offline returned by PD API, Leaving in TiDB Dashboard
- Follow-up Guidance: The content notes that `Pending Offline` in TiUP, `Offline` returned by PD API, and `Leaving` in TiDB Dashboard indicate the same status, and that node service status derives from PD scheduling information.
- Classification Note: This is reference content because it defines the `tiup cluster display` command syntax, command options, output fields, and the official meanings of each node service status.

## Official Source Content

# tiup cluster display

If you want to see the operation status of each component in the cluster, it is obviously inefficient to log in to each machine one by one. Therefore, tiup-cluster provides the `tiup cluster display` command to efficiently complete this task.
## Syntax

```shell
tiup cluster display <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to operate on. If you forget the cluster name, you can check it with the [cluster list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list) command.
## Options
### --dashboard

- By default, all node information of the entire cluster is displayed. With the `--dashboard` option, only dashboard information is displayed.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### -N, --node

- Specifies the node to display. If this option is not specified, all nodes are displayed. The value of this option is a comma-separated list of node IDs. If you are not sure about the ID of a node, you can skip this option in the command to show the IDs and status of all nodes in the output.
- Data type: `STRINGS`
- If this option is not specified in the command, all nodes are checked by default.

> **Note:**
>
> If the `-R, --role` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are checked.
### -R, --role

- Specifies the role to display. If it is not specified, all roles are displayed. The value of this option is a comma-separated list of node roles. If you are not sure about the role deployed on a node, you can skip this option in the command to show the roles and status of all nodes in the output.
- Data type: `STRINGS`
- If this option is not specified in the command, all roles are displayed by default.

> **Note:**
>
> If the `-N, --node` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are displayed.
### --process

- Displays the CPU and memory usage information of the node when this option is enabled. This option is disabled by default.
- Data type: `BOOLEAN`
- Default value: `false`
- To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --uptime

- Displays the `uptime` information of the node when this option is enabled. This option is disabled by default.
- Data type: `BOOLEAN`
- Default value: `false`
- To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --status-timeout

- Specifies the timeout period for obtaining the node status information.
- Data type: `INT`
- Default value: `10`, in the unit of second.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Outputs

- The cluster name
- The cluster version
- SSH Client Type
- Dashboard address
- The table with the following fields:
    - ID: the node ID, composed of `IP:PORT`
    - Role: the service role deployed on this node (such as TiDB, TiKV)
    - Host: the IP of the machine corresponding to the node
    - Ports: the port number occupied by the service
    - OS/Arch: the operating system and the machine architecture of this node
    - Status: the current status of the node service
    - Data Dir: the data directory of the service. `-` means no data directory.
    - Deploy Dir: the deployment directory of the service
### Node service status

A node service can run in one of the following statuses:

- Up: The node service is running normally.
- Down or Unreachable: The node service is not running or a network problem exists on the corresponding host.
- Tombstone: The data on the node service has been completely migrated out and the scaling-in is complete. This status exists only on TiKV or TiFlash.
- Pending Offline: The data on the node service is being migrated out and the scaling-in is in process. This status exists only on TiKV or TiFlash.
- Unknown: The running status of the node service is unknown.

> **Note:**
>
> `Pending Offline` in TiUP, `Offline` returned by PD API, and `Leaving` in TiDB Dashboard indicate the same status.

Node service status derives from the PD scheduling information. For more details, see [Information collection](https://docs.pingcap.com/tidb/stable/tidb-scheduling#information-collection).

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
