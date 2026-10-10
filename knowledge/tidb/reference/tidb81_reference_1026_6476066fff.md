# tiup dm list command usage, help option, and output fields

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-list.md`
- Source Title: `tiup dm list`
- Source Heading Path: `tiup dm list | tiup dm list > Syntax | tiup dm list > Options | tiup dm list > Options > -h, --help | tiup dm list > Output`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `command syntax`, `cluster listing`, `control machine`, `help option`, `output fields`, `cluster metadata`, `storage path`, `private key`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1026_6476066fff`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-list.md#tiup-dm-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc3640ed75014d213b0fcbe32d09fa577afcb89795925c0d038226faa0ebd370`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list#tiup-dm-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-list.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax, help flag, storage note, or output fields for listing DM clusters deployed on a control machine by the currently logged-in user.
- Retrieval Keywords: tiup dm list, tiup dm list [flags], -h, --help, DM cluster list, control machine, currently logged-in user, ~/.tiup/storage/dm/clusters/, Name, User, Version, Path, PrivateKey
- Follow-up Guidance: The output is a table with the fields Name, User, Version, Path, and PrivateKey.
- Classification Note: This is reference content because it defines the tiup dm list command syntax, the help option, and the exact output fields and storage path note.

## Official Source Content

# tiup dm list

`tiup-dm` supports deploying multiple clusters using the same control machine. You can use the `tiup dm list` command to check which clusters are deployed using the control machine by the currently logged-in user.

> **Note:**
>
> By default, the data of the deployed clusters is stored in the `~/.tiup/storage/dm/clusters/` directory. The currently logged-in user cannot view the clusters deployed by other users on the same control machine.
## Syntax

```shell
tiup dm list [flags]
```
## Options
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Output

A table consisting of the following fields:

- `Name`: the cluster name.
- `User`: the user who deployed the cluster.
- `Version`: the cluster version.
- `Path`: the path of the cluster deployment data on the control machine.
- `PrivateKey`: the path of the private key to the cluster.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
