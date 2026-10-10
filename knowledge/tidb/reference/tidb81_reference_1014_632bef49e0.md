# tiup cluster start syntax options and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-start.md`
- Source Title: `tiup cluster start`
- Source Heading Path: `tiup cluster start | tiup cluster start > Syntax | tiup cluster start > Options | tiup cluster start > Options > --init | tiup cluster start > Options > -N, --node | tiup cluster start > Options > -R, --role | tiup cluster start > Options > -h, --help | tiup cluster start > Output`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`
- Topic Tags: `cluster-start`, `syntax`, `flags`, `safe-start`, `node-selection`, `role-selection`, `help`, `output`, `root-password`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1014_632bef49e0`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-start.md#tiup-cluster-start`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `212a3736d0f489d5b04393d32c7651324a1008d79ea513986e9bb793c0559fc1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-start#tiup-cluster-start
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-start.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, flags, node or role selection behavior, safe start behavior, or output of the `tiup cluster start` command for a specified cluster.
- Retrieval Keywords: tiup cluster start <cluster-name> [flags], tiup cluster start, --init, safe start, TiDB root user password, -N, --node, node IDs, tiup cluster display, cluster status table, -R, --role, roles of nodes, -h, --help, log of starting the service, tiup cluster list
- Follow-up Guidance: If the cluster name, node IDs, or node roles are needed, the content points to `tiup cluster list` and `tiup cluster display`, and if the generated root password is forgotten, it points to `Forget the root password`.
- Classification Note: This is reference content because it defines the command purpose, syntax, options, option interactions, and output for `tiup cluster start`.

## Official Source Content

# tiup cluster start

The `tiup cluster start` command is used to start all services or some services of the specified cluster.
## Syntax

```shell
tiup cluster start <cluster-name> [flags]
```

`<cluster-name>` is the name of the cluster to operate on. If you forget the cluster name, you can check it using the [`tiup cluster list`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list) command.
## Options
### --init

Starts the cluster in a safe way. It is recommended to use this option when the cluster is started for the first time. This method generates the password of the TiDB root user at startup and returns the password in the command line interface.

> **Note:**
>
> - After safe start of a TiDB cluster, you cannot log in to the database using the root user without a password. Therefore, you need to record the password returned by the command line for future logins.
> - The password is generated only once. If you do not record or forget the password, refer to [Forget the `root` password](https://docs.pingcap.com/tidb/stable/user-account-management#forget-the-root-password) to change the password.
### -N, --node

- Specifies the nodes to be started. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the [cluster status table](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) returned by the `tiup cluster display` command.
- Data type: `STRINGS`
- If this option is not specified in the command, all nodes are started by default.

> **Note:**
>
> If the `-R, --role` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are started.
### -R, --role

- Specifies the roles of nodes to be started. The value of this option is a comma-separated list of the roles of the nodes. You can get the roles of the nodes from the second column of the [cluster status table](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-display) returned by the `tiup cluster display` command.
- Data type: `STRINGS`
- If this option is not specified in the command, all roles are started by default.

> **Note:**
>
> If the `-N, --node` option is specified at the same time, only the service nodes that match both the specifications of `-N, --node` and `-R, --role` are started.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Output

The log of starting the service.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
