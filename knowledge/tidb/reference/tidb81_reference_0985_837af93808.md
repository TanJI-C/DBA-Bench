# tiup mirror clone syntax and options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-clone.md`
- Source Title: `tiup mirror clone`
- Source Heading Path: `tiup mirror clone | tiup mirror clone > Syntax | tiup mirror clone > Options | tiup mirror clone > Options > -f, --full | tiup mirror clone > Options > -a, --arch | tiup mirror clone > Options > -o, --os | tiup mirror clone > Options > --prefix | tiup mirror clone > Options > --{component}`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `mirror`, `clone`, `syntax`, `flags`, `version-selection`, `platform-filter`, `os-filter`, `signature-key`, `component-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0985_837af93808`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-clone.md#tiup-mirror-clone`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ca64cee94ea6f635704a1759b812cf17f384d86d2c57248a43573c89a4e432a2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-clone#tiup-mirror-clone
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-clone.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the syntax, flags, and component or version selection behavior of the `tiup mirror clone` command for creating a new mirror from an existing mirror.
- Retrieval Keywords: tiup mirror clone, tiup mirror clone <target-dir> [global version] [flags], --full, -f, --arch, -a, --os, -o, --prefix, --{component}, target-dir, global version, clone whole mirror, clone some components, different signature key, component version list, tiup list --all
- Follow-up Guidance: The content notes that you can run `tiup list --all` to view available component names for `--{component}`.
- Classification Note: This is reference content because it defines the command purpose, syntax, option names, defaults, and matching behavior for `tiup mirror clone`.

## Official Source Content

# tiup mirror clone

The command `tiup mirror clone` is used to clone an existing mirror or clone some of its components to create a new mirror. The new mirror has the same components as the old one, but uses a different signature key.
## Syntax

```shell
tiup mirror clone <target-dir> [global version] [flags]
```

- `<target-dir>` is used to set the local path to the cloned mirror. If the path does not exist, TiUP automatically creates one.
- If `[global version]` is specified, TiUP tries to clone all components of the specified version. If some components do not have the specified version, then TiUP clones its latest version.
## Options
### -f, --full

- Whether to clone the whole mirror. If this option is set, other options becomes ignored and TiUP completely clones all components of all versions from the targeted mirror.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### -a, --arch

- Only clones components that can run on the specified platform.
- Data type: `STRING`
- Default: "amd64,arm64"
### -o, --os

- Only clones components that can run on the specified operating system.
- Data type: `STRING`
- Default: "linux,darwin"
### --prefix

- Whether to only match the prefix of versions. By default, TiUP downloads a component version when it is strictly matched. If this option is set, TiUP also downloads component versions of which prefixes are matched.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --{component}

- Specifies the version list of the component to be cloned. Fill component names in `{component}`. You can run [`tiup list --all`](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-list) to view available component names.
- Data type: Strings
- Default: Null

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
