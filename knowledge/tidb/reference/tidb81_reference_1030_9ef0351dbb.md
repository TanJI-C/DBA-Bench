# tiup dm scale-out syntax options and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-scale-out.md`
- Source Title: `tiup dm scale-out`
- Source Heading Path: `tiup dm scale-out | tiup dm scale-out > Syntax | tiup dm scale-out > Options | tiup dm scale-out > Options > -u, --user | tiup dm scale-out > Options > -i, --identity_file | tiup dm scale-out > Options > -p, --password | tiup dm scale-out > Options > -h, --help | tiup dm scale-out > Output`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `scale-out`, `command-syntax`, `topology-file`, `ssh`, `user`, `identity-file`, `password`, `help`, `output`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1030_9ef0351dbb`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-scale-out.md#tiup-dm-scale-out`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84fc04c8791421e5861a0b2e44430318f53b7288f5b4b8ed3f34ac5d39575313`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-scale-out#tiup-dm-scale-out
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-scale-out.md

## Retrieval Guidance

- Use When: Use this when looking for the syntax, flags, and output of the `tiup dm scale-out` command for adding new nodes to a DM cluster.
- Retrieval Keywords: tiup dm scale-out, tiup dm scale-out <cluster-name> <topology.yaml> [flags], cluster-name, topology.yaml, topology file, new nodes, -u, --user, -i, --identity_file, -p, --password, -h, --help, ~/.ssh/id_rsa, SSH connection, scaling out log, tiup dm list
- Follow-up Guidance: If the cluster name is unknown, the content says it can be checked with the `cluster list` command, and the topology file should contain only the new nodes to be added to the current cluster.
- Classification Note: This is reference content because it defines the command purpose, exact syntax, option meanings and defaults, and the command output.

## Official Source Content

# tiup dm scale-out

The `tiup dm scale-out` command is used for scaling out the cluster. The internal logic of scaling out the cluster is similar to the cluster deployment. The `tiup-dm` components first establish an SSH connection to the new node, create the necessary directories on the target node, then perform the deployment and start the service.
## Syntax

```shell
tiup dm scale-out <cluster-name> <topology.yaml> [flags]
```

`<cluster-name>`: the name of the cluster to operate on. If you forget the cluster name, you can check it with the [cluster list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list) command.

`<topology.yaml>`: the prepared [topology file](https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference). This topology file should only contain the new nodes that are to be added to the current cluster.
## Options
### -u, --user

- Specifies the user name used to connect to the target machine. This user must have the secret-free sudo root permission on the target machine.
- Data type: `STRING`
- Default: the current user who executes the command.
### -i, --identity_file

- Specifies the key file used to connect to the target machine.
- Data type: `STRING`
- If this option is not specified in the command, the `~/.ssh/id_rsa` file is used to connect to the target machine by default.
### -p, --password

- Specifies the password used to connect to the target machine. Do not use this option and `-i/--identity_file` at the same time.
- Data type: `BOOLEAN`
- Default: false
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The log of scaling out.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
