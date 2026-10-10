# tiup cluster deploy syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-deploy.md`
- Source Title: `tiup cluster deploy`
- Source Heading Path: `tiup cluster deploy | tiup cluster deploy > Syntax | tiup cluster deploy > Options | tiup cluster deploy > Options > -u, --user | tiup cluster deploy > Options > -i, --identity_file | tiup cluster deploy > Options > -p, --password | tiup cluster deploy > Options > --ignore-config-check | tiup cluster deploy > Options > --no-labels | tiup cluster deploy > Options > --skip-create-user | tiup cluster deploy > Options > -h, --help | tiup cluster deploy > Output`
- Source Line Ranges: `5-70`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `cluster-deployment`, `command-syntax`, `topology-file`, `ssh-user`, `identity-file`, `password-auth`, `config-check`, `label-check`, `user-creation`, `help`, `deployment-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0498_21b0c2f7ff`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-deploy.md#tiup-cluster-deploy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8073a4997e999cad9a78efabd5930547fac8b626534821733c3f944465e63a21`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-deploy#tiup-cluster-deploy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-deploy.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, flags, connection options, validation skips, or output of the `tiup cluster deploy` command for deploying a new cluster.
- Retrieval Keywords: tiup cluster deploy, tiup cluster deploy <cluster-name> <version> <topology.yaml> [flags], topology.yaml, -u --user, -i --identity_file, -p --password, --ignore-config-check, --no-labels, --skip-create-user, -h --help, deployment log, <binary> --config-check <config-file>, ~/.ssh/id_rsa
- Follow-up Guidance: The source also points to the topology file reference and the TiUP Cluster command list back link.
- Classification Note: This is classified as an operation chunk because the content defines the `tiup cluster deploy` command syntax, options, required arguments, and resulting deployment log output.

## Official Source Content

# tiup cluster deploy

The `tiup cluster deploy` command is used to deploy a new cluster.
## Syntax

```shell
tiup cluster deploy <cluster-name> <version> <topology.yaml> [flags]
```

- `<cluster-name>`: the name of the new cluster, which cannot be the same as the existing cluster names.
- `<version>`: the version number of the TiDB cluster to deploy, such as `v8.1.2`.
- `<topology.yaml>`: the prepared [topology file](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference).
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

- Specifies the password used to connect to the target machine. Do not use this option with `-i/--identity_file` at the same time.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --ignore-config-check

- This option is used to skip the configuration check. After the binary files of components are deployed, the configurations of TiDB, TiKV, and PD components are checked using `<binary> --config-check <config-file>`. `<binary>` is the path of the deployed binary file. `<config-file>` is the configuration file generated based on the user configuration.
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
- Default: false
### --no-labels

- This option is used to skip the label check.
- When two or more TiKV nodes are deployed on the same physical machine, a risk exists: PD cannot learn the cluster topology, so PD might schedule multiple replicas of a Region to different TiKV nodes on one physical machine, which makes this physical machine a single point. To avoid this risk, you can use labels to tell PD not to schedule the same Region to the same machine. See [Schedule Replicas by Topology Labels](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels) for label configuration.
- For the test environment, this risk might matter and you can use `--no-labels` to skip the check.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --skip-create-user

- During the cluster deployment, tiup-cluster checks whether the specified user name in the topology file exists or not. If not, it creates one. To skip this check, you can use the `--skip-create-user` option.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### -h, --help

- Prints help information.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Output

The deployment log.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
