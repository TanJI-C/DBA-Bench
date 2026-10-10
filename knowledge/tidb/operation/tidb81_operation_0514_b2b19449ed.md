# Install TiUP components

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-management.md`
- Source Title: `Manage TiUP Components with TiUP Commands`
- Source Heading Path: `Manage TiUP Components with TiUP Commands > Install components`
- Source Line Ranges: `51-81`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `tiup install`, `latest stable`, `nightly`, `versions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0514_b2b19449ed`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-management.md#install-components`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `262a10f7fa05ac9926c58bf0d01741ab4175be97a74cd6b8a431e421c91ee2e2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management#install-components
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need the command forms for installing the latest stable or a specified version of a TiUP component.
- Retrieval Keywords: Install components, tiup install <component>, tiup install <component>:[version], latest stable version, specified version, tiup install tidb, tiup install tidb:nightly, tiup install tikv:v8.1.2
- Follow-up Guidance: Examples include installing the latest stable TiDB, the nightly TiDB version, and TiKV v8.1.2.
- Classification Note: This is operation content because it gives concrete `tiup install` commands for installing components.

## Official Source Content

## Install components

You can use the `tiup install` command to query the component list. This usage of this command is as follows:

- `tiup install <component>`: installs the latest stable version of a specified component.
- `tiup install <component>:[version]`: installs the specified version of a specified component.

Example 1: Use TiUP to install the latest stable version of TiDB.

```shell
tiup install tidb
```

Example 2: Use TiUP to install the nightly version of TiDB.

```shell
tiup install tidb:nightly
```

Example 3: Use TiUP to install TiKV v8.1.2.

```shell
tiup install tikv:v8.1.2
```
