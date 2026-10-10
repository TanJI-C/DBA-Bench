# tiup dm edit-config command usage and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-edit-config.md`
- Source Title: `tiup dm edit-config`
- Source Heading Path: `tiup dm edit-config | tiup dm edit-config > Syntax | tiup dm edit-config > Option | tiup dm edit-config > Option > -h, --help | tiup dm edit-config > Output`
- Source Line Ranges: `5-36`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `command`, `configuration`, `topology-file`, `editor`, `reload`, `help`, `output`, `validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1023_209fbf77a1`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-edit-config.md#tiup-dm-edit-config`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1478f670fcbc31b2295670c4ba8c9c3d121aeb47122f7fda7e741b29ab1177e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-edit-config#tiup-dm-edit-config
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-edit-config.md

## Retrieval Guidance

- Use When: Use this when someone asks how to modify a deployed DM cluster service configuration with TiUP, which editor is used, what the command syntax is, or what output and validation behavior to expect when saving topology changes.
- Retrieval Keywords: tiup dm edit-config, tiup dm edit-config <cluster-name> [flags], $EDITOR, vi editor, topology file, tiup dm reload, -h, --help, no output, fields that cannot be modified, error is reported when you save the file, control machine
- Follow-up Guidance: The content also states that the configuration change is only made on the control machine after `tiup dm edit-config`, and `tiup dm reload` is needed to reload the configuration.
- Classification Note: This is reference content because it defines the `tiup dm edit-config` command usage, syntax, option, output behavior, and limits on modifying the topology file.

## Official Source Content

# tiup dm edit-config

If you need to modify the cluster service configuration after the cluster is deployed, you can use the `tiup dm edit-config` command that starts an editor for you to modify the [topology file](https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference). of the specified cluster. This editor is specified in the `$EDITOR` environment variable by default. If the `$EDITOR` environment variable does not exist, the `vi` editor is used.

> **Note:**
>
> + When you modify the configuration, you cannot add or delete machines. For how to add machines, see [Scale out a cluster](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-scale-out). For how to delete machines, see [Scale in a cluster](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-scale-in).
> + After you execute the `tiup dm edit-config` command, the configuration is modified only on the control machine. Then you need to execute the `tiup dm reload` command to reload the configuration.
## Syntax

```shell
tiup dm edit-config <cluster-name> [flags]
```

`<cluster-name>`: the cluster to operate on.
## Option
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

- Normally, no output.
- If you have mistakenly modified the fields that cannot be modified, when you save the file, an error is reported, reminding you to edit the file again. For the fields that cannot be modified, see [the topology file](https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference).

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
