# tiup cluster prune command syntax, help option, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-prune.md`
- Source Title: `tiup cluster prune`
- Source Heading Path: `tiup cluster prune | tiup cluster prune > Syntax | tiup cluster prune > Option | tiup cluster prune > Option > -h, --help | tiup cluster prune > Output`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `scale-in`, `cleanup`, `command-syntax`, `help-option`, `command-output`, `data-scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1009_336c2de2a4`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-prune.md#tiup-cluster-prune`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `204d0fd5a232b362906d40c5403fc385b52da2b01c68cf413d6290229e006289`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-prune#tiup-cluster-prune
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-prune.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, help flag, or output of the `tiup cluster prune` command used after scaling in and waiting for data scheduling to complete.
- Retrieval Keywords: tiup cluster prune, tiup cluster prune <cluster-name> [flags], scale in the cluster, data scheduling to complete, manually execute the tiup cluster prune command, -h, --help, Prints the help information, The log of the cleanup process
- Follow-up Guidance: The content states that some components are not immediately stopped or deleted during scaling in, so cleanup is done after data scheduling completes by running `tiup cluster prune`.
- Classification Note: This is reference content because it defines the `tiup cluster prune` command purpose, command syntax, `-h, --help` option, and output description.

## Official Source Content

# tiup cluster prune

When [scaling in the cluster](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-scale-in), for some components, TiUP does not immediately stop their services or delete their data. You need to wait for the data scheduling to complete and then manually execute the `tiup cluster prune` command to clean up.
## Syntax

```shell
tiup cluster prune <cluster-name> [flags]
```
## Option
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: false
## Output

The log of the cleanup process.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
