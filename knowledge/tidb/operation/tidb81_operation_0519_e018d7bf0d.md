# Link TiUP component binaries

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-management.md`
- Source Title: `Manage TiUP Components with TiUP Commands`
- Source Heading Path: `Manage TiUP Components with TiUP Commands > Operate components > Link components`
- Source Line Ranges: `247-285`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `tiup link`, `tiup unlink`, `binary`, `executable directory`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0519_e018d7bf0d`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-management.md#link-components`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `09b6c1cfe8017f5e005e8273f5dedf4d51af46ea75323e3cf23018a06a904c06`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management#link-components
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need details about the experimental `tiup link` and `tiup unlink` commands and linked component executables in `$TIUP_HOME/bin/`.
- Retrieval Keywords: Link components, experimental, tiup link, tiup unlink, $TIUP_HOME/bin/, automatic update checking, environment variables, ctl cannot be used, tiup install cluster, tiup link cluster, tiup link cluster:v1.13.0, package cluster provides these executables: tiup-cluster, tiup-cluster, tiup unlink cluster, tiup update --self, tiup link tiup:v1.13.0
- Follow-up Guidance: The examples show linking the cluster component, switching it to version v1.13.0, unlinking it, and linking TiUP itself starting from v1.13.0.
- Classification Note: This is operation content because it explains how to link and unlink component binaries and what the linked executable name looks like.

## Official Source Content

### Link components

TiUP v1.13.0 adds the experimental `link` and `unlink` commands to link the binary of a component to the executable directory (`$TIUP_HOME/bin/`) and remove the link. This feature enables you to call a component without going through TiUP each time, while preserving the ability to switch between different versions. However, this method lacks the process of automatic update checking and setting certain environment variables and some components (such as ctl) cannot be used. Therefore, it is recommended to use it only when necessary.

Example 1: install and link the latest version of the cluster component

```shell
tiup install cluster
tiup link cluster
```

Example 2: switch the cluster component to version v1.13.0

```shell
tiup link cluster:v1.13.0
```

The following is the output of the `tiup link cluster` command:

```shell
package cluster provides these executables: tiup-cluster
```

This indicates that the binary name of the cluster component is `tiup-cluster`. After the link command is completed, you can use the cluster component by directly typing `tiup-cluster` into the command line.

Example 3: cancel the link of the cluster component

```shell
tiup unlink cluster
```

Example 4: manage the version of TiUP

Before v1.13.0, TiUP is installed in `~/.tiup/bin/` and different versions cannot coexist. Starting from v1.13.0, you can install and link TiUP like any other components.

```shell
tiup update --self # update tiup itself to a version that supports link
tiup link tiup:v1.13.0
```
