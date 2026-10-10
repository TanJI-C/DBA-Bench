# tiup install command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-install.md`
- Source Title: `tiup install`
- Source Heading Path: `tiup install | tiup install > Syntax | tiup install > Option | tiup install > Output`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `component installation`, `syntax`, `version selection`, `command output`, `error messages`, `mirror repository`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0983_d6cde44f92`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-install.md#tiup-install`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d65268379624f15fde81e287fc20f07e97370bd6c9d7f3328692d3a53a9be6ea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-install#tiup-install
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-install.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP command syntax, version selection behavior, download behavior, or exact install-time error messages for installing components from the mirror repository.
- Retrieval Keywords: tiup install, tiup install <component1>[:version] [component2...N] [flags], component installation, mirror repository, latest stable version, local TiUP data directory, The component "%s" not found, version %s not supported by component %s, download information, multiple components, multiple versions of the same component
- Follow-up Guidance: The source also states that when TiUP needs to run a component that does not exist in the mirror repository, it tries to download the component first and then runs it automatically.
- Classification Note: This is a reference chunk because it defines the purpose, syntax, options, normal output, and exact error messages of the `tiup install` command.

## Official Source Content

# tiup install

The `tiup install` command is used for component installation. It downloads the component package of a specified version from the mirror repository and decompresses it in the local TiUP data directory for later use. In addition, when TiUP needs to run a component that does not exist in the mirror repository, it tries to download the component first and then runs it automatically. If the component does not exist in the repository, an error is reported.
## Syntax

```shell
tiup install <component1>[:version] [component2...N] [flags]
```

`<component1>` and `<component2>` represent component names, and `[version]` represents an optional version number. If `version` is not added, the latest stable version of the specified component is installed. `[component2...N]` means that you can specify multiple components or multiple versions of the same component at the same time.
## Option

None
## Output

- Normally outputs the download information of the component.
- If the component does not exist, the `The component "%s" not found` error is reported.
- If the version does not exist, the `version %s not supported by component %s` error is reported.

[<< Back to the previous page - TiUP Reference command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#command-list)
