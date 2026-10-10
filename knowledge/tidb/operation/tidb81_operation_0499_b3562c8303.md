# tiup cluster destroy command behavior, syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-destroy.md`
- Source Title: `tiup cluster destroy`
- Source Heading Path: `tiup cluster destroy | tiup cluster destroy > Syntax | tiup cluster destroy > Options | tiup cluster destroy > Options > --force | tiup cluster destroy > Options > --retain-node-data | tiup cluster destroy > Options > --retain-role-data | tiup cluster destroy > Options > -h, --help | tiup cluster destroy > Output`
- Source Line Ranges: `5-52`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `cluster-destroy`, `cluster-lifecycle`, `data-deletion`, `directory-cleanup`, `syntax`, `flags`, `force`, `retain-node-data`, `retain-role-data`, `help`, `execution-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0499_b3562c8303`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-destroy.md#tiup-cluster-destroy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8a0f75b5ef11498e9049373f66cad3a097bcaa3dd73ceb10658b3d62e2c456d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-destroy#tiup-cluster-destroy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-destroy.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks what `tiup cluster destroy` does, its syntax and flags, or how it handles cleanup of cluster data, deployment directories, log directories, and parent directories.
- Retrieval Keywords: tiup cluster destroy, tiup cluster destroy <cluster-name> [flags], --force, --retain-node-data, --retain-role-data, -h, --help, Stops the cluster, delete its log directory, deployment directory, and data directory, parent directory of the data directory, parent directory of the deployment directory, execution log of the tiup-cluster
- Follow-up Guidance: The source also states that `--force` can ignore SSH connection errors for down nodes, and that `--retain-node-data` and `--retain-role-data` can be specified multiple times.
- Classification Note: This is classified as an operation topic because the content defines the `tiup cluster destroy` command behavior, command syntax, options, and output for cluster lifecycle cleanup.

## Official Source Content

# tiup cluster destroy

After an application goes offline, if you want to release the machines occupied by the cluster for use by other applications, you need to clean up the data on the cluster and the deployed binary files. To destroy the cluster, the `tiup cluster destroy` command performs the following operations:

- Stops the cluster.
- For each service, delete its log directory, deployment directory, and data directory.
- If the parent directory of the data directory or deployment directory of each service is created by tiup-cluster, also delete the parent directory.
## Syntax

```shell
tiup cluster destroy <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to destroy.
## Options
### --force

- In some cases, some nodes in the cluster have been down, making it impossible to connect to the node through SSH for operation. At this time, you can use the `--force` option to ignore these errors.
- Data type: `Boolean`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --retain-node-data

- Specifies the nodes that need to retain data. If you need to specify more than one node, use this option multiple times: `--retain-node-data <node-A> --retain-node-data <node-B>`.
- Data type: `StringArray`
- Default: empty
### --retain-role-data

- Specifies the role that needs to retain data. If you need to specify more than one role, use this option multiple times: `--retain-role-data <role-A> --retain-role-data <role-B>`.
- Data type: `StringArray`
- Default: empty
### -h, --help

- Prints the help information.
- Data type: `Boolean`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Output

The execution log of the tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
