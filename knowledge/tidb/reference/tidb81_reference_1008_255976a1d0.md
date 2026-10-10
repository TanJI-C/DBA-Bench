# tiup cluster list command syntax options and output fields

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-list.md`
- Source Title: `tiup cluster list`
- Source Heading Path: `tiup cluster list | tiup cluster list > Syntax | tiup cluster list > Options | tiup cluster list > Options > -h, --help | tiup cluster list > Outputs`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `cluster-listing`, `command-syntax`, `help-option`, `output-fields`, `control-machine`, `deployment-metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1008_255976a1d0`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-list.md#tiup-cluster-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `564c1f52edbe15ea71bbe60380e4a62691a440fd1d70b7aa3014cfa1d7290361`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-list#tiup-cluster-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-list.md

## Retrieval Guidance

- Use When: Use this when looking for the `tiup cluster list` command syntax, help flag, or the meaning of the cluster listing output fields on a control machine.
- Retrieval Keywords: tiup cluster list, tiup cluster list [flags], -h, --help, Name, User, Version, Path, PrivateKey, ~/.tiup/storage/cluster/clusters/, control machine, currently logged-in user, clusters deployed by other users
- Follow-up Guidance: The content notes that deployed cluster data is stored in `~/.tiup/storage/cluster/clusters/` by default, so the currently logged-in user on the same control machine cannot view clusters deployed by other users.
- Classification Note: This is reference content because it defines the command syntax, the `-h, --help` option, and the exact output fields returned by `tiup cluster list`.

## Official Source Content

# tiup cluster list

tiup-cluster supports deploying multiple clusters using the same control machine. The `tiup cluster list` command outputs all clusters deployed by the currently logged-in user using this control machine.

> **Note:**
>
> The deployed cluster data is stored in the `~/.tiup/storage/cluster/clusters/` directory by default, so on the same control machine, the currently logged-in user cannot view the clusters deployed by other users.
## Syntax

```shell
tiup cluster list [flags]
```
## Options
### -h, --help

- Prints help information.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Outputs

Outputs the table with the following fields:

- Name: the cluster name
- User: the deployment user
- Version: the cluster version
- Path: the path of the cluster deployment data on the control machine
- PrivateKey: the path of the private key that is used to connect the cluster

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
