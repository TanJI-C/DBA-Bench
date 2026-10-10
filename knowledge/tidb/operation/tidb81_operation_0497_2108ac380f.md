# tiup cluster clean command syntax, options, warning, and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-clean.md`
- Source Title: `tiup cluster clean`
- Source Heading Path: `tiup cluster clean | tiup cluster clean > Syntax | tiup cluster clean > Options | tiup cluster clean > Options > --all | tiup cluster clean > Options > --data | tiup cluster clean > Options > --log | tiup cluster clean > Options > --ignore-node | tiup cluster clean > Options > --ignore-role | tiup cluster clean > Options > -h, --help | tiup cluster clean > Output`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `cluster-cleanup`, `data-deletion`, `log-cleanup`, `command-syntax`, `command-options`, `ignore-node`, `ignore-role`, `help-output`, `test-environment`, `cluster-reset`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0497_2108ac380f`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-clean.md#tiup-cluster-clean`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cea0052d8d5a41f9d1e308e03da07a18937fc13ddb0b3a167077c711b0a1bbef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-clean#tiup-cluster-clean
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-clean.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how `tiup cluster clean <cluster-name> [flags]` resets a cluster, what it deletes, and which flags control cleaning data, logs, or exclusions.
- Retrieval Keywords: tiup cluster clean, tiup cluster clean <cluster-name> [flags], --all, --data, --log, --ignore-node, --ignore-role, -h, --help, cluster is stopped and then cluster data is deleted, clean cluster, deleting all data, clean up logs, execution logs of tiup-cluster
- Follow-up Guidance: The content states that after running the command, the cluster is stopped and cluster data is deleted, and after restarting the cluster manually, you will get a clean cluster.
- Classification Note: This is classified as an operation topic because the official content defines the `tiup cluster clean` command syntax, flags, warning, and output for cluster cleanup.

## Official Source Content

# tiup cluster clean

In the test environment, sometimes you might need to reset the cluster back to the state as it has been just deployed, which means deleting all data. You can do that easily using the `tiup cluster clean` command. After running it, the cluster is stopped and then cluster data is deleted. After restarting the cluster manually, you will get a clean cluster.

> **Warning:**
>
> This command will first stop the cluster even if you choose only to clean up logs. Therefore, do not use it in a production environment.
## Syntax

```shell
tiup cluster clean <cluster-name> [flags]
```

`<cluster-name>` is the cluster to clean.
## Options
### --all

- Cleans data and the log at the same time. It is equivalent to specifying `--data` and `--log` at the same time.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
- If it is not specified, you must specify at lease one of the following options:
    - --data: Cleans data
    - --log: Cleans the log
### --data

- Cleans data. If neither of it nor `--all` is specified, data will not be cleaned.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --log

- Cleans the log. If neither of it nor `--all` is specified, the log will not be cleaned.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --ignore-node

- Specifies the node that does not need cleaning. To specify multiple nodes, you can use this option multiple times. For example, `--ignore-node <node-A> --ignore-node <node-B>`.
- Data type: `StringArray`
- Default: empty
### --ignore-role

- Specifies the role that does not need cleaning. To specify multiple roles, you can use this option multiple times. For example, `--ignore-role <role-A> --ignore-role <role-B>`.
- Data type: `StringArray`
- Default: empty
### -h, --help

- Prints help information.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Output

The execution logs of tiup-cluster.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
