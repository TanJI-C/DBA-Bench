# tiup dm patch syntax, preparation, options, and prerequisites

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-patch.md`
- Source Title: `Apply Hotfix to DM Clusters Online`
- Source Heading Path: `Apply Hotfix to DM Clusters Online | Apply Hotfix to DM Clusters Online > Syntax | Apply Hotfix to DM Clusters Online > Syntax > Preparation | Apply Hotfix to DM Clusters Online > Options | Apply Hotfix to DM Clusters Online > Options > --overwrite | Apply Hotfix to DM Clusters Online > Options > -N, --node | Apply Hotfix to DM Clusters Online > Options > -R, --role | Apply Hotfix to DM Clusters Online > Options > --offline | Apply Hotfix to DM Clusters Online > Options > -h, --help | Apply Hotfix to DM Clusters Online > Example | Apply Hotfix to DM Clusters Online > Example > Preparations`
- Source Line Ranges: `5-102`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `hotfix`, `patching`, `syntax`, `preparation`, `options`, `node-selection`, `role-selection`, `offline`, `help`, `version-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0509_7a1961d8a3`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-patch.md#apply-hotfix-to-dm-clusters-online`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3819f68e86087af188f374a26e12bda577218db8a4204ae08e4b94d84a62cf00`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-patch#apply-hotfix-to-dm-clusters-online
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-patch.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the `tiup dm patch <cluster-name> <package-path> [flags]` command syntax, hotfix package preparation steps, or the meanings of options such as `--overwrite`, `-N, --node`, `-R, --role`, `--offline`, and `-h, --help` for DM clusters.
- Retrieval Keywords: tiup dm patch, tiup dm patch <cluster-name> <package-path> [flags], Apply Hotfix to DM Clusters Online, --overwrite, -N, --node, -R, --role, --offline, -h, --help, tiup dm display, cluster status table, dm-master, dm-worker, component-hotfix-os-arch.tar.gz, Release Version: v5.3.0
- Follow-up Guidance: The example section says to prepare `dm-linux-amd64.tar.gz` and confirm the current DM software version with `/home/tidb/dm/deploy/dm-master-8261/bin/dm-master/dm-master -V`.
- Classification Note: This is classified as an operation chunk because the official content describes how `tiup dm patch` replaces binaries on running DM cluster services and explains the required flags and preparation.

## Official Source Content

# Apply Hotfix to DM Clusters Online

If you need to dynamically replace the binaries of a service while the cluster is running (that is, to keep the cluster available during the replacement), you can use the `tiup dm patch` command. The command does the following:

- Uploads the binary package for replacement to the target machine.
- Takes the related nodes offline using the API.
- Stops the target service.
- Unpacks the binary package and replaces the service.
- Starts the target service.
## Syntax

```shell
tiup dm patch <cluster-name> <package-path> [flags]
```

- `<cluster-name>`: The name of the cluster to be operated
- `<package-path>`: The path to the binary package used for replacement
### Preparation

You need to pack the binary package required for this command in advance according to the following steps:

- Determine the name `${component}` of the component to be replaced (dm-master, dm-worker ...), the `${version}` of the component (v2.0.0, v2.0.1 ...), and the operating system `${os}` and platform `${arch}` on which the component runs.
- Download the current component package using the command `wget https://tiup-mirrors.pingcap.com/${component}-${version}-${os}-${arch}.tar.gz -O /tmp/${component}-${version}-${os}-${arch}.tar.gz`.
- Run `mkdir -p /tmp/package && cd /tmp/package` to create a temporary directory to pack files.
- Run `tar xf /tmp/${component}-${version}-${os}-${arch}.tar.gz` to unpack the original binary package.
- Run `find .` to view the file structure in the temporary package directory.
- Copy the binary files or configuration files to the corresponding locations in the temporary directory.
- Run `tar czf /tmp/${component}-hotfix-${os}-${arch}.tar.gz *` to pack the files in the temporary directory.
- Finally, you can use `/tmp/${component}-hotfix-${os}-${arch}.tar.gz` as the value of `<package-path>` in the `tiup dm patch` command.
## Options
### --overwrite

- After you patch a certain component (such as dm-worker), when the tiup-dm scales out the component, tiup-dm uses the original component version by default. To use the version that you patch when the cluster scales out in the future, you need to specify the option `--overwrite` in the command.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
### -N, --node

- Specifies the nodes to be replaced. The value of this option is a comma-separated list of node IDs. You can get the node IDs from the first column of the cluster status table returned by the `[tiup dm display](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display)` command.
- Data type: `STRING`
- If this option is not specified, TiUP selects all nodes to replace by default.

> **Note:**
>
> If the option `-R, --role` is specified at the same time, TiUP then replaces service nodes that match both the requirements of `-N, --node` and `-R, --role`.
### -R, --role

- Specifies the roles to be replaced. The value of this option is a comma-separated list of the roles of the nodes. You can get the roles of the nodes from the second column of the cluster status table returned by the `[tiup dm display](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-display)` command.
- Data type: `STRING`
- If this option is not specified, TiUP selects all roles to replace by default.

> **Note:**
>
> If the option `-N, --node` is specified at the same time, TiUP then replaces service nodes that match both the requirements of `-N, --node` and `-R, --role`.
### --offline

- Declares that the current cluster is offline. When this option is specified, TiUP DM only replaces the binary files of the cluster components in place without restarting the service.
### -h, --help

- Prints help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Example

The following example shows how to apply `v5.3.0-hotfix` to the `v5.3.0` cluster deployed using TiUP. The operations might vary if you deploy the cluster using other methods.

> **Note:**
>
> Hotfix is used only for emergency fixes. Its daily maintenance is complicated. It is recommended that you upgrade the DM cluster to an official version as soon as it is released.
### Preparations

Before applying a hotfix, prepare the hotfix package `dm-linux-amd64.tar.gz` and confirm the current DM software version:

```shell
/home/tidb/dm/deploy/dm-master-8261/bin/dm-master/dm-master -V
```

Output:

```
Release Version: v5.3.0

Git Commit Hash: 20626babf21fc381d4364646c40dd84598533d66
Git Branch: heads/refs/tags/v5.3.0
UTC Build Time: 2021-11-29 08:29:49
Go Version: go version go1.16.4 linux/amd64
```
