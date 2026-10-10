# tiup dm destroy command reference

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-destroy.md`
- Source Title: `tiup dm destroy`
- Source Heading Path: `tiup dm destroy | tiup dm destroy > Syntax | tiup dm destroy > Option | tiup dm destroy > Option > -h, --help | tiup dm destroy > Output`
- Source Line Ranges: `5-34`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `cluster-destroy`, `cleanup`, `stop-cluster`, `delete-data`, `delete-deployment`, `delete-logs`, `syntax`, `flags`, `help`, `output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0507_00425d08b1`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-destroy.md#tiup-dm-destroy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1643e2d447b7c324105fe80fb22396a89a438478e26e221e44df51af32698b8c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-destroy#tiup-dm-destroy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-destroy.md

## Retrieval Guidance

- Use When: Use when you need the TiUP DM command reference for destroying a cluster and cleaning up its files and logs.
- Retrieval Keywords: tiup dm destroy, cluster-name, Stops the cluster, delete its log directory, deployment directory, data directory, parent directory, -h, --help, execution log of the tiup-dm
- Follow-up Guidance: The command output is the execution log of the tiup-dm.
- Classification Note: This chunk documents the `tiup dm destroy` operation, including its syntax, help option, and the cleanup steps it performs.

## Official Source Content

# tiup dm destroy

After an application goes offline, if you want to release the machines occupied by the cluster for use by other applications, you need to clean up the data on the cluster and the deployed binary files. To destroy the cluster, the `tiup dm destroy` command performs the following operations:

- Stops the cluster.
- For each service, delete its log directory, deployment directory, and data directory.
- If the parent directory of the data directory or deployment directory of each service is created by `tiup-dm`, also delete the parent directory.
## Syntax

```shell
tiup dm destroy <cluster-name> [flags]
```

`<cluster-name>`: the name of the cluster to be destroyed.
## Option
### -h, --help

- Prints the help information.
- Data type: `Boolean`
- Default: false
## Output

The execution log of the tiup-dm.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
