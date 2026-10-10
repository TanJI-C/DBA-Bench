# Registering Event Log on Windows

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > Registering Event Log on Windows`
- Source Line Ranges: `1973-2006`
- Chunk ID: `pg16_solution_0028_fdb4b6ebc8`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8bfbdf190e2efd632c92d5ae1858a6b37485fb42519e58ab75492dabb42505bc`

## Retrieval Guidance

- Use When: Windows 上需要让 PostgreSQL 日志写入 Event Viewer 并正确显示。
- Retrieval Keywords: Windows event log, regsvr32, pgevent.dll, event_source, log_destination eventlog
- Follow-up Guidance: 同时在 postgresql.conf 中将 log_destination 包含 eventlog。
- Classification Note: 说明 regsvr32 注册/注销 pgevent.dll 和 event_source 的动作。

## Official Source Content

## Registering Event Log on Windows

To register a Windows
event log library with the operating system,
issue this command:

```
regsvr32 `pgsql_library_directory`/pgevent.dll
```

This creates registry entries used by the event viewer, under the default
event source named `PostgreSQL`.

To specify a different event source name (see
[guc-event-source](#guc-event-source)), use the `/n`
and `/i` options:

```
regsvr32 /n /i:`event_source_name` `pgsql_library_directory`/pgevent.dll
```

To unregister the event log library from
the operating system, issue this command:

```
regsvr32 /u [/i:`event_source_name`] `pgsql_library_directory`/pgevent.dll
```

> **Note:**

> To enable event logging in the database server, modify
> [guc-log-destination](#guc-log-destination) to include
> `eventlog` in `postgresql.conf`.
>
