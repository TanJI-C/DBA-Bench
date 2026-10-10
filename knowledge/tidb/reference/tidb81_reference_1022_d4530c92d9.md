# tiup dm display syntax options and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-display.md`
- Source Title: `tiup dm display`
- Source Heading Path: `tiup dm display | tiup dm display > Syntax | tiup dm display > Options | tiup dm display > Options > -N, --node | tiup dm display > Options > -R, --role | tiup dm display > Options > -h, --help | tiup dm display > Output`
- Source Line Ranges: `5-61`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `cluster status`, `command syntax`, `node filtering`, `role filtering`, `help option`, `command output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1022_d4530c92d9`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-display.md#tiup-dm-display`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bc6eb2a09c5935b4e5a095e62841a27a99fbc00f2dd599b33161590a558158e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display#tiup-dm-display
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-display.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax, filter options, or output fields of the `tiup dm display <cluster-name> [flags]` command for checking DM cluster component status.
- Retrieval Keywords: tiup dm display, tiup dm display <cluster-name> [flags], -N, --node, -R, --role, -h, --help, DM cluster status, node filtering, role filtering, ID Role Host Ports OS/Arch Status Data Dir Deploy Dir, tiup dm list
- Follow-up Guidance: If the cluster name is unknown, the content says you can check it using the `tiup dm list` command.
- Classification Note: This is reference content because it defines the command syntax, option semantics, and the exact output fields for `tiup dm display`.

## Official Source Content

# tiup dm display

If you want to check the operational status of each component in a DM cluster, it is inefficient to log in to each machine one by one. Therefore, tiup-dm provides the `tiup dm display` command to do this job efficiently.
## Syntax

```shell
tiup dm display <cluster-name> [flags]
```

`<cluster-name>` is the name of the cluster to be operated. If you forget the cluster name, you can check it using the [`tiup dm list`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list) command.
## Options
### -N, --node

- Specifies the IDs of the nodes to query, splitting by commas for multiple nodes. If you are not sure about the ID of a node, you can skip this option in the command to show the IDs and status of all nodes in the output.
- Data type: `STRING`
- This option is enabled by default with `[]` (which means all nodes) passed in.

> **Note:**
> 
> If `-R, --role` is also specified, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are queried.
### -R, --role

- Specifies the roles to query, splitting by commas for multiple roles. If you are not sure about the role deployed on a node, you can skip this option in the command to show the roles and status of all nodes in the output.
- Data type: `STRING`
- This option is enabled by default with `[]` (which means all roles) passed in.

> **Note:**
> 
> If `-N, --node` is also specified, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are queried.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Output

- Cluster name
- Cluster version
- SSH client type
- A table containing the following fields:
    - `ID`: the node ID, consisting of IP:PORT.
    - `Role`: the service role deployed on the node (for example, TiDB or TiKV).
    - `Host`: the IP address of the machine corresponding to the node.
    - `Ports`: the port number used by the service.
    - `OS/Arch`: the operating system and machine architecture of the node.
    - `Status`: the current status of the services on the node.
    - `Data Dir`: the data directory of the service. `-` means that there is no data directory.
    - `Deploy Dir`: the deployment directory of the service.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
