# tiup status command syntax and output fields

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-status.md`
- Source Title: `tiup status`
- Source Heading Path: `tiup status | tiup status > Syntax | tiup status > Option | tiup status > Output | tiup status > Output > Component status`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tiflash`, `dashboard`
- Topic Tags: `command`, `status`, `syntax`, `output`, `process`, `component-state`, `tags`, `pd-scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0996_ab4aeb4e6a`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-status.md#tiup-status`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `55aa6eada86641d17d8a9435f11019f97c2cafe94767572c8e3f2669da819206`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-status#tiup-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-status.md

## Retrieval Guidance

- Use When: Use this chunk when you need the `tiup status` command syntax, the meaning of its output fields, or the component states shown for running components started with TiUP tags.
- Retrieval Keywords: tiup status, tiup status [flags], Name, Component, PID, Status, Created Time, Directory, Binary, Args, -T, --tag, Up, Down, Unreachable, Tombstone, Pending Offline, Unknown, Offline returned by PD API, Leaving in TiDB Dashboard, PD scheduling information
- Follow-up Guidance: The source notes that `Pending Offline` in TiUP, `Offline` returned by PD API, and `Leaving` in TiDB Dashboard indicate the same status.
- Classification Note: This is reference content because it defines the `tiup status` command syntax, states there are no options, and enumerates the output fields and component status meanings from the official command description.

## Official Source Content

# tiup status

The `tiup status` command is used to view the operation information of the components after you run the components using the `tiup [flags] <component> [args...]` command.

> **Note:**
>
> You can only check the information of the following components:
>
> - Components that are still in operation
> - Components that run through the tag specified by `tiup -T/--tag`
## Syntax

```shell
tiup status [flags]
```
## Option

None
## Output

A table consisting of the following fields:

- `Name`: The tag name specified by `-T/--tag`. If not specified, it is a random string.
- `Component`: The operating components.
- `PID`: The corresponding process ID of the operating components.
- `Status`: The status of the operating components.
- `Created Time`: The starting time of the components.
- `Directory`: The data directory of the components.
- `Binary`: The binary file path of the components.
- `Args`: The starting arguments of the operating components.
### Component status

A component can run in one of the following statuses:

- Up: The component is running normally.
- Down or Unreachable: The component is not running or a network problem exists on the corresponding host.
- Tombstone: The data on the component has been completely migrated out and the scaling-in is complete. This status exists only on TiKV or TiFlash.
- Pending Offline: The data on the component is being migrated out and the scaling-in is in process. This status exists only on TiKV or TiFlash.
- Unknown: The running status of the component is unknown.

> **Note:**
>
> `Pending Offline` in TiUP, `Offline` returned by PD API, and `Leaving` in TiDB Dashboard indicate the same status.

Component status derives from the PD scheduling information. For more details, see [Information collection](https://docs.pingcap.com/tidb/stable/tidb-scheduling#information-collection).

[<< Back to the previous page - TiUP Reference command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#command-list)
