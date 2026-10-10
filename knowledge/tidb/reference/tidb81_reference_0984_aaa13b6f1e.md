# tiup list syntax options and outputs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-list.md`
- Source Title: `tiup list`
- Source Heading Path: `tiup list | tiup list > Syntax | tiup list > Options | tiup list > Options > --all | tiup list > Options > --installed | tiup list > Options > --verbose | tiup list > Outputs`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `command-line`, `component-listing`, `mirror`, `syntax`, `flags`, `installed-components`, `verbose-output`, `version-listing`, `command-output`, `error-message`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0984_aaa13b6f1e`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-list.md#tiup-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `337351927a5c50d97adbd8b99f9140261da0544eca4fb25603bc496190be8514`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-list#tiup-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-list.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about the syntax, flags, outputs, or error behavior of the `tiup list` command for listing mirror components or component versions.
- Retrieval Keywords: tiup list, tiup list [component] [flags], --all, --installed, --verbose, available components of a mirror, installed component versions, list all versions of the specified component, Name Installed Owner Description, Version Installed Release Platforms, failed to fetch component: unknown component
- Follow-up Guidance: If `[component]` is set, the source also states that TiUP lists all versions of the specified component and reports `failed to fetch component: unknown component` when the component does not exist.
- Classification Note: This is reference content because it defines `tiup list` syntax, option semantics, output fields, and the exact error text from the official command documentation.

## Official Source Content

# tiup list

The command `tiup list` is used to get the list of available components of a mirror.
## Syntax

```shell
tiup list [component] [flags]
```

`[component]` is an optional parameter used to specify a certain component. If `[component]` is set, TiUP lists all versions of the specified component; if not, TiUP lists all components.
## Options
### --all

- Displays all components. By default, TiUP does not show hidden components.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --installed

- Only displays components and versions that have been installed.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --verbose

- Displays installed component versions in the components list.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Outputs

- If `[component]` is not set:
    - If `--verbose` is specified: TiUP outputs a component information list consisting of `Name` (component name), `Installed` (installed versions), `Owner` (component owner), and `Description` (component description).
    - If `--verbose` is not specified: TiUP outputs a component information list consisting of `Name` (component name), `Owner` (component owner), and `Description` (component description).
- If `[component]` is set:
    - If the specified component exists: TiUP outputs a version information list of the specified component, consisting of `Version` (version number), `Installed` (installation status), `Release` (release date), and `Platforms` (supported platforms).
    - If the specified component does not exist: TiUP reports the error `failed to fetch component: unknown component`.

[<< Back to the previous page - TiUP Reference command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#command-list)
