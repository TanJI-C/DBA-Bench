# Check TiUP component status

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-management.md`
- Source Title: `Manage TiUP Components with TiUP Commands`
- Source Heading Path: `Manage TiUP Components with TiUP Commands > Operate components > Query the operating status of a component`
- Source Line Ranges: `148-168`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `tiup status`, `instance`, `pid`, `running`, `terminated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0123_9c9d010b79`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-management.md#query-the-operating-status-of-a-component`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `09470db78f0430529d9d7d8a85bef830b6af262927e0aff75ae29a2e096d2a3a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management#query-the-operating-status-of-a-component
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need to inspect TiUP component instance status and understand the columns returned by `tiup status`.
- Retrieval Keywords: Query the operating status of a component, tiup status, Name, Component, PID, Status, RUNNING, TERM, Created Time, Directory, Binary, Args, --tag, --binpath
- Follow-up Guidance: The output lists one instance per line with status, process ID, working directory, binary, and arguments.
- Classification Note: This is observability content because it focuses on checking instance operating status and interpreting status output.

## Official Source Content

### Query the operating status of a component

You can use the `tiup status` command to check the operating status of a component:

```shell
tiup status
```

By executing this command, you will get a list of instances, one instance per line. The list contains the following columns:

- `Name`: The tag name of the instance.
- `Component`: The component name of the instance.
- `PID`: The process ID of the operating instance.
- `Status`: The instance status. `RUNNING` means that the instance is operating. `TERM` means that the instance is terminated.
- `Created Time`: The starting time of the instance.
- `Directory`: The working directory of the instance, which can be specified using `--tag`.
- `Binary`: The executable program of the instance, which can be specified using `--binpath`.
- `Args`: The arguments of the operating instance.
