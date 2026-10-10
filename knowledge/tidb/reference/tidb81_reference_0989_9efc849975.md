# tiup mirror merge syntax, prerequisites, and outputs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-merge.md`
- Source Title: `tiup mirror merge`
- Source Heading Path: `tiup mirror merge | tiup mirror merge > Syntax | tiup mirror merge > Option | tiup mirror merge > Outputs`
- Source Line Ranges: `5-33`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `mirror`, `merge`, `syntax`, `prerequisites`, `owner-keys`, `private-keys`, `output`, `error-handling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0989_9efc849975`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-merge.md#tiup-mirror-merge`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c204221cef37d43fa7bf66cd314c4b2dcb75660f6db198d97bd6bfa9678e3a48`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-merge#tiup-mirror-merge
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-merge.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the syntax, prerequisites, and output behavior of the `tiup mirror merge` command for merging one or more mirrors into the current mirror.
- Retrieval Keywords: tiup mirror merge, tiup mirror merge <mirror-dir-1> [mirror-dir-N] [flags], merge one or more mirrors to the current mirror, owner IDs of all components of the target mirror exist in the current mirror, ${TIUP_HOME}/keys, private keys corresponding to owner IDs, tiup mirror set, Error: missing owner keys for owner %s on component %s, no output if executed successfully
- Follow-up Guidance: The source also points to `tiup mirror set` for switching the current mirror to the mirror that is currently authorized to modify.
- Classification Note: This is reference content because it specifies command purpose, required conditions, exact syntax, options, and exact outputs for `tiup mirror merge`.

## Official Source Content

# tiup mirror merge

The `tiup mirror merge` command is used to merge one or more mirrors to the current mirror.

To execute this command, the following conditions must be met:

- The owner IDs of all components of the target mirror exist in the current mirror.
- The `${TIUP_HOME}/keys` directory of the user who executes this command contains all the private keys corresponding to the above owner IDs in the current mirror (you can use the command [`tiup mirror set`](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-set) to switch the current mirror to the mirror that is currently authorized to modify).
## Syntax

```shell
tiup mirror merge <mirror-dir-1> [mirror-dir-N] [flags]
```

- `<mirror-dir-1>`: the first mirror to be merged into the current mirror
- `[mirror-dir-N]`: the Nth mirror to be merged into the current mirror
## Option

None
## Outputs

- If the command is executed successfully, there is no output.
- If the current mirror does not have a component owner of the target mirror, or if `${TIUP_HOME}/keys` does not have the owner's private key, TiUP reports the `Error: missing owner keys for owner %s on component %s` error.

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
