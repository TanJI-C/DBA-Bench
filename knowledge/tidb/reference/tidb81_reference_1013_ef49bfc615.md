# TiUP cluster scale-out command syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-scale-out.md`
- Source Title: `tiup cluster scale-out`
- Source Heading Path: `tiup cluster scale-out | tiup cluster scale-out > Syntax | tiup cluster scale-out > Options | tiup cluster scale-out > Options > -u, --user | tiup cluster scale-out > Options > -i, --identity_file | tiup cluster scale-out > Options > -p, --password | tiup cluster scale-out > Options > --no-labels | tiup cluster scale-out > Options > --skip-create-user | tiup cluster scale-out > Options > -h, --help | tiup cluster scale-out > Output`
- Source Line Ranges: `5-66`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`
- Topic Tags: `scale-out`, `syntax`, `topology-file`, `ssh`, `deployment`, `pd-join`, `user-authentication`, `identity-file`, `password-authentication`, `label-check`, `topology-labels`, `user-creation`, `help`, `command-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1013_ef49bfc615`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-scale-out.md#tiup-cluster-scale-out`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5b8204fcdff46396d237875fc6f53bccdec844292def4830a7161822a4234941`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-scale-out#tiup-cluster-scale-out
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-scale-out.md

## Retrieval Guidance

- Use When: Use this content when looking for the `tiup cluster scale-out` command syntax, flags, SSH authentication options, topology file scope, or the special behavior when scaling out PD nodes.
- Retrieval Keywords: tiup cluster scale-out, tiup cluster scale-out <cluster-name> <topology.yaml> [flags], topology.yaml, cluster list, -u --user, -i --identity_file, -p --password, --no-labels, --skip-create-user, -h --help, PD join operation, The log of scaling out
- Follow-up Guidance: The content points to `cluster list` for checking the cluster name and to Schedule Replicas by Topology Labels for label configuration.
- Classification Note: This is reference content because it defines the command purpose, syntax, options, defaults, and output for `tiup cluster scale-out`.

## Official Source Content

# tiup cluster scale-out

The `tiup cluster scale-out` command is used for scaling out the cluster. The internal logic of scaling out the cluster is similar to the cluster deployment. The tiup-cluster component first establishes an SSH connection to the new node, creates the necessary directories on the target node, then performs the deployment and starts the service.

When PD is scaled out, new PD nodes are added to the cluster by the join operation, and the configuration of the services associated with PD is updated; other services are directly started and added to the cluster.
## Syntax

```shell
tiup cluster scale-out <cluster-name> <topology.yaml> [flags]
```

`<cluster-name>`: the name of the cluster to operate on. If you forget the cluster name, you can check it with the [`cluster list`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list) command.

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
### --no-labels

- This option is used to skip the label check.
- When two or more TiKV nodes are deployed on the same physical machine, a risk exists: PD does not know the cluster topology, so it might schedule multiple replicas of a Region to different TiKV nodes on one physical machine, which makes this physical machine a single point of failure. To avoid this risk, you can use labels to tell PD not to schedule the same Region to the same machine. See [Schedule Replicas by Topology Labels](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels) for label configuration.
- For the test environment, this risk might not matter, and you can use `--no-labels` to skip the check.
- Data type: `BOOLEAN`
- Default: false
### --skip-create-user

- During the cluster deployment, tiup-cluster checks whether the specified user name in the topology file exists or not. If not, it creates one. To skip this check, you can use the `--skip-create-user` option.
- Data type: `BOOLEAN`
- Default: false
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The log of scaling out.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
