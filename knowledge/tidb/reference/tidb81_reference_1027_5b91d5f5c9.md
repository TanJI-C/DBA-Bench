# tiup dm prune command usage and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-prune.md`
- Source Title: `tiup dm prune`
- Source Heading Path: `tiup dm prune | tiup dm prune > Syntax | tiup dm prune > Option | tiup dm prune > Option > -h, --help | tiup dm prune > Output`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `metadata-cleanup`, `scale-in`, `etcd`, `command-syntax`, `help-option`, `command-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1027_5b91d5f5c9`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-prune.md#tiup-dm-prune`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `525b6c068742270c2505a391e0b27d675bd32aaf725b49e6d76eb7ba1141239f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-prune#tiup-dm-prune
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-prune.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP DM command that manually cleans up metadata in etcd left after scaling in a cluster, including its syntax, help flag, and output description.
- Retrieval Keywords: tiup dm prune, scale in the cluster, metadata in etcd is not cleaned up, clean up the metadata, tiup dm prune <cluster-name> [flags], -h, --help, Prints the help information, The log of the cleanup process, TiUP DM command list
- Follow-up Guidance: The source states that this metadata remains after you scale in the cluster and can be cleaned manually with the `tiup dm prune` command.
- Classification Note: This is reference content because it defines the `tiup dm prune` command purpose, command syntax, available option, and the described output.

## Official Source Content

# tiup dm prune

When you scale in the cluster(/tiup/tiup-component-dm-scale-in.md), a small amount of metadata in etcd is not cleaned up, which usually causes no problem. If you need to clean up the metadata, you can manually execute the `tiup dm prune` command.
## Syntax

```shell
tiup dm prune <cluster-name> [flags]
```
## Option
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The log of the cleanup process.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
