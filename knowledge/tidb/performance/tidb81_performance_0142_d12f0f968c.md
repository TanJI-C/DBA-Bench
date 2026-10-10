# Enable tidb_rc_read_check_ts to reduce TSO requests

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-practices.md`
- Source Title: `Performance Tuning Practices for OLTP Scenarios`
- Source Heading Path: `Performance Tuning Practices for OLTP Scenarios > Scenario 6: Enable the `tidb_rc_read_check_ts` variable to reduce TSO requests | Performance Tuning Practices for OLTP Scenarios > Scenario 6: Enable the `tidb_rc_read_check_ts` variable to reduce TSO requests > Application configuration | Performance Tuning Practices for OLTP Scenarios > Scenario 6: Enable the `tidb_rc_read_check_ts` variable to reduce TSO requests > Performance analysis | Performance Tuning Practices for OLTP Scenarios > Scenario 6: Enable the `tidb_rc_read_check_ts` variable to reduce TSO requests > Performance analysis > Dashboard`
- Source Line Ranges: `311-326`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `dashboard`
- Topic Tags: `rc-read`, `tso`, `global-variable`, `dashboard`, `cpu`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0142_d12f0f968c`
- Source ID: `tidb-docs-8.1:performance-tuning-practices.md#scenario-6-enable-the-tidb-rc-read-check-ts-variable-to-reduce-tso-requests`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `318bb09ae0f9794750ba5f2a55790f665718ca0d39e25efce9f13eb44457ac9b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-practices#scenario-6-enable-the-tidb-rc-read-check-ts-variable-to-reduce-tso-requests
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-practices.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the specific scenario where `tidb_rc_read_check_ts` is enabled to reduce TSO requests while keeping the same application configuration as Scenario 5.
- Retrieval Keywords: Scenario 6, tidb_rc_read_check_ts, set global tidb_rc_read_check_ts=on;, reduce TSO requests, Dashboard, ExecutePreparedStmt cpu = 22% cpu time = 8.4s, application configuration remains the same as Scenario 5
- Follow-up Guidance: The chunk states that after configuring `set global tidb_rc_read_check_ts=on;`, the TiDB CPU flame chart does not have any significant changes.
- Classification Note: This is classified as performance for TiDB because the content focuses on the performance-related global variable `tidb_rc_read_check_ts`, its effect on TSO requests, and CPU flame chart observations.

## Official Source Content

## Scenario 6: Enable the `tidb_rc_read_check_ts` variable to reduce TSO requests
### Application configuration

Compared with Scenario 5, the application configuration remains the same. The only difference is that the `set global tidb_rc_read_check_ts=on;` variable is configured to reduce TSO requests.
### Performance analysis
#### Dashboard

The flame chart of the TiDB CPU does not have any significant changes.

- ExecutePreparedStmt cpu = 22% cpu time = 8.4s

![flame-graph-for-rc-read](/media/performance/6.2.2.png)
