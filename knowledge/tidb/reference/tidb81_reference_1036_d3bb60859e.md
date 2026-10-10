# Query installable TiUP components

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-management.md`
- Source Title: `Manage TiUP Components with TiUP Commands`
- Source Heading Path: `Manage TiUP Components with TiUP Commands > Query the component list`
- Source Line Ranges: `22-50`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `tiup list`, `installed`, `verbose`, `hidden components`, `versions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1036_d3bb60859e`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-management.md#query-the-component-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `681f71b85cc08f6963024e1e7cb896ef2363b02ae7c9c73600f1ae98fb15d657`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management#query-the-component-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax and flags for querying installable or locally installed TiUP components and versions.
- Retrieval Keywords: Query the component list, tiup list, tiup list ${component}, --installed, --all, --verbose, hidden components, installed versions, supported platforms, tiup list --installed, tiup list tikv
- Follow-up Guidance: Examples show `tiup list --installed` for currently installed components and `tiup list tikv` for all installable TiKV versions from the server.
- Classification Note: This is reference content because it documents `tiup list` usage, flags, and example queries.

## Official Source Content

## Query the component list

You can use the `tiup list` command to query the component list. This usage of this command is as follows:

- `tiup list`: checks which components can be installed.
- `tiup list ${component}`: checks which versions of a specific component can be installed.

You can also use the following flags in the above commands:

- `--installed`: checks which components or which version of a specific component has been installed locally.
-`--all`: views all components, including the hidden ones
-`--verbose`: views all columns (including installed versions and supported platforms)

Example 1: View all currently installed components.

```shell
tiup list --installed
```

Example 2: Get a list of the TiKV component of all installable versions from the server.

```shell
tiup list tikv
```
