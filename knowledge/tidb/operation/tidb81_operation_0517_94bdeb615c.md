# Clean TiUP component instances

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-management.md`
- Source Title: `Manage TiUP Components with TiUP Commands`
- Source Heading Path: `Manage TiUP Components with TiUP Commands > Operate components > Clean component instance`
- Source Line Ranges: `169-200`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `tiup clean`, `tag`, `delete working directory`, `kill process`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0517_94bdeb615c`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-management.md#clean-component-instance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d23c636b0395df2667df5f126bc33b9a97c4cebfd38f4af4592f6d1fe1a2cb58`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management#clean-component-instance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need the command syntax for cleaning TiUP component instances, deleting working directories, or cleaning all instances.
- Retrieval Keywords: Clean component instance, tiup clean [tag] [flags], tiup clean, --all, delete the working directory, kill process, instance tag, tiup clean experiment, tiup clean --all
- Follow-up Guidance: It states that if the instance is still operating before cleaning, the related process is killed first.
- Classification Note: This is operation content because it describes how to clean component instances and remove their working directories.

## Official Source Content

### Clean component instance

You can use the `tiup clean` command to clean up component instances and delete the working directory. If the instance is still operating before the cleaning, the related process is killed first. The command usage is as follows:

```bash
tiup clean [tag] [flags]
```

The following flag is supported:

- `--all`: Cleans up all instance information.

In the above command, `tag` is the instance tag to be cleaned. If `--all` is used, no tag is passed.

Example 1: Clean up the component instance with the `experiment` tag name.

```shell
tiup clean experiment
```

Example 2: Clean up all component instances.

```shell
tiup clean --all
```
