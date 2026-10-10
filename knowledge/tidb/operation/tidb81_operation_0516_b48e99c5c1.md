# Run TiUP components

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-management.md`
- Source Title: `Manage TiUP Components with TiUP Commands`
- Source Heading Path: `Manage TiUP Components with TiUP Commands > Operate components`
- Source Line Ranges: `115-147`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `tiup component`, `tag`, `working directory`, `start`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0516_b48e99c5c1`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-management.md#operate-components`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e55e0d7f51e6cae4bd9a00a8f486443797dd3b6b35d2b69adcd5b36c3014bee2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management#operate-components
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need to start a TiUP component, specify a version, or control the instance working directory with `--tag`.
- Retrieval Keywords: Operate components, tiup [flags] <component>[:version] [args...], --tag, latest stable version (installed), working directory, automatically deleted, reuse the working directory, tiup tidb:v8.1.2, tiup --tag=experiment tikv
- Follow-up Guidance: It explains that the tag name determines the working directory name, and specifying the same `--tag` lets you reuse the previous working directory.
- Classification Note: This is operation content because it explains how to run components and how tags affect instance directories.

## Official Source Content

## Operate components

After the installation is complete, you can use the `tiup <component>` command to start the corresponding component:

```shell
tiup [flags] <component>[:version] [args...]

Flags:
  -T, --tag string                     Specifies the tag for the component instance.
```

To use this command, you need to specify the component name and the optional version. If no version is specified, the latest stable version (installed) of this component is used.

Before the component is started, TiUP creates a directory for it, and then puts this component into the directory for operation. The component generates all the data in this directory, and the name of this directory is the tag name specified when the component operates. If no tag is specified, a tag name is randomly generated. This working directory will be *automatically deleted* when the instance is terminated.

If you want to start the same component multiple times and reuse the previous working directory, you can use `--tag` to specify the same name when the component is started. After the tag is specified, the working directory will *not be automatically deleted* when the instance is terminated, which makes it convenient to reuse the working directory.

Example 1: Operate TiDB v8.1.2.

```shell
tiup tidb:v8.1.2
```

Example 2: Specify the tag with which TiKV operates.

```shell
tiup --tag=experiment tikv
```
