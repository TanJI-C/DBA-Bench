# Observability features: session identifiers in logs and Dashboard plan table view

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Feature details > Observability`
- Source Line Ranges: `234-247`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `dashboard`
- Topic Tags: `observability`, `logging`, `session-id`, `session-alias`, `slow-query`, `troubleshooting`, `execution-plan`, `dashboard`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0509_b9ab703d1c`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#observability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `05e50a0cd225930d0b573d55c1a2e0f74fae1d43dcf4e5917db7791c6aa0ead0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#observability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.4.0 observability updates related to correlating logs by session identity or viewing execution plans in Dashboard.
- Retrieval Keywords: CONNECTION_ID, session connection IDs, session aliases, tidb_session_alias, TiDB logs, slow query logs, slow logs from the coprocessor on TiKV, correlate logs, troubleshooting, diagnostic efficiency, TiDB Dashboard, execution plans, table view, Slow Query page, SQL Statement page
- Follow-up Guidance: The source links to documentation for Dashboard statement details and states that tidb_session_alias can add custom identifiers to related logs.
- Classification Note: This is an observability release-note chunk because it describes logging and Dashboard features that improve troubleshooting and diagnosis in TiDB 7.4.0.

## Official Source Content

### Observability

* Support adding session connection IDs and session aliases to logs [#46071](https://github.com/pingcap/tidb/issues/46071) @[lcwangchao](https://github.com/lcwangchao)

     When you troubleshoot a SQL execution problem, it is often necessary to correlate the contents of TiDB component logs to pinpoint the root cause. Starting from v7.4.0, TiDB can write session connection IDs (`CONNECTION_ID`) to session-related logs, including TiDB logs, slow query logs, and slow logs from the coprocessor on TiKV. You can correlate the contents of several types of logs based on session connection IDs to improve troubleshooting and diagnostic efficiency.

     In addition, by setting the session-level system variable [`tidb_session_alias`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_alias-new-in-v740), you can add custom identifiers to the logs mentioned above. With this ability to inject your application identification information into the logs, you can correlate the contents of the logs with the application, build the link from the application to the logs, and reduce the difficulty of diagnosis.

* TiDB Dashboard supports displaying execution plans in a table view [#1589](https://github.com/pingcap/tidb-dashboard/issues/1589) @[baurine](https://github.com/baurine)

    In v7.4.0, TiDB Dashboard supports displaying execution plans on the **Slow Query** and **SQL Statement** pages in a table view to improve the diagnosis experience.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-details).
