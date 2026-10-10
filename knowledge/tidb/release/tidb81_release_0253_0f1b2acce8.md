# Compatibility changes in temporary tables, privileges, DM, and Prometheus

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.0.md`
- Source Title: `TiDB 5.3 Release Notes`
- Source Heading Path: `TiDB 5.3 Release Notes > Compatibility changes > Others`
- Source Line Ranges: `59-80`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `dm`, `ticdc`, `tidb`, `tiup`
- Topic Tags: `compatibility`, `temporary-tables`, `downgrade`, `warnings`, `privileges`, `auto-analyze`, `plugins`, `prometheus`, `dm`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0253_0f1b2acce8`
- Source ID: `tidb-docs-8.1:releases/release-5.3.0.md#others`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d7101ec1b498133594490b4669c351f4c597d1d6a2d74a13179270ac8c3cdd5f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.0#others
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 5.3.0 compatibility changes involving temporary tables, illegal system variable warnings, privilege enforcement, auto-analyze timing, plugin storage, DM versioning, or the Prometheus default version change.
- Retrieval Keywords: global temporary tables, local temporary tables, downgraded to a version earlier than v5.3.0, TiCDC and BR support global temporary tables, table definition error occurs, data error is reported when you create a global temporary table, Warning 1292 Truncated incorrect, SHOW VIEW, SHOW CREATE VIEW, sql_auto_is_null, tidb_enable_noop_functions, GRANT ALL ON performance_schema.*, tidb_auto_analyze_start_time, tidb_auto_analyze_end_time, /data/deploy/plugin, DM follows TiDB in version numbers, upgrade from v2.0.x to v5.3.0, Prometheus v2.27.1, alert time representation, Unix timestamp to UTC
- Follow-up Guidance: The source also points to the temporary tables compatibility documents for compatibility with MySQL temporary tables and compatibility restrictions with other TiDB features.
- Classification Note: This is classified as a release compatibility section because it lists behavior changes, permission changes, default changes, and upgrade or downgrade effects introduced in TiDB 5.3.0.

## Official Source Content

### Others

- Temporary tables:

    - If you have created local temporary tables in a TiDB cluster earlier than v5.3.0, these tables are actually ordinary tables, and handled as ordinary tables after the cluster is upgraded to v5.3.0 or a later version. If you have created global temporary tables in a TiDB cluster of v5.3.0 or a later version, when the cluster is downgraded to a version earlier than v5.3.0, these tables are handled as ordinary tables and cause a data error.
    - Since v5.3.0, TiCDC and BR support [global temporary tables](https://docs.pingcap.com/tidb/stable/temporary-tables#global-temporary-tables). If you use TiCDC and BR of a version earlier than v5.3.0 to replicate global temporary tables to the downstream, a table definition error occurs.
    - The following clusters are expected to be v5.3.0 or later; otherwise, data error is reported when you create a global temporary table:

        - the cluster to be imported using TiDB migration tools
        - the cluster restored using TiDB migration tools
        - the downstream cluster in a replication task using TiDB migration tools
    - For the compatibility information of temporary tables, refer to [Compatibility with MySQL temporary tables](https://docs.pingcap.com/tidb/stable/temporary-tables#compatibility-with-mysql-temporary-tables) and [Compatibility restrictions with other TiDB features](https://docs.pingcap.com/tidb/stable/temporary-tables#compatibility-restrictions-with-other-tidb-features).

- For releases earlier than v5.3.0, TiDB reports an error when a system variable is set to an illegal value. For v5.3.0 and later releases, TiDB returns success with a warning such as "|Warning | 1292 | Truncated incorrect xxx: 'xx'" when a system variable is set to an illegal value.
- Fix the issue that the `SHOW VIEW` permission is not required to execute `SHOW CREATE VIEW`. Now you are expected to have the `SHOW VIEW` permission to execute the `SHOW CREATE VIEW` statement.
- The system variable `sql_auto_is_null` is added to the noop functions. When `tidb_enable_noop_functions = 0/OFF`, modifying this variable value causes an error.
- The `GRANT ALL ON performance_schema.*` syntax is no longer permitted. If you execute this statement in TiDB, an error occurs.
- Fix the issue that auto-analyze is unexpectedly triggered outside the specified time period when new indexes are added before v5.3.0. In v5.3.0, after you set the time period through the `tidb_auto_analyze_start_time` and `tidb_auto_analyze_end_time` variables, auto-analyze is triggered only during this time period.
- The default storage directory for plugins is changed from `""` to `/data/deploy/plugin`.
- The DM code is migrated to [the folder "dm" in TiCDC code repository](https://github.com/pingcap/tiflow/tree/release-5.3/dm). Now DM follows TiDB in version numbers. Next to v2.0.x, the new DM version is v5.3.0, and you can upgrade from v2.0.x to v5.3.0 without any risk.
- The default deployed version of Prometheus is upgraded from v2.8.1 to [v2.27.1](https://github.com/prometheus/prometheus/releases/tag/v2.27.1), which is released in May 2021. This version provides more features and fixes a security issue. Compared with Prometheus v2.8.1, alert time representation in v2.27.1 is changed from Unix timestamp to UTC. For details, refer to [Prometheus commit](https://github.com/prometheus/prometheus/commit/7646cbca328278585be15fa615e22f2a50b47d06) for more details.
