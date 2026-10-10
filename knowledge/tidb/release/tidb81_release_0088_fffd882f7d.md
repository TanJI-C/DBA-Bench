# Tools and TiDB Ansible 3.0 GA changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0-ga.md`
- Source Title: `TiDB 3.0 GA Release Notes`
- Source Heading Path: `TiDB 3.0 GA Release Notes > Tools | TiDB 3.0 GA Release Notes > TiDB Ansible`
- Source Line Ranges: `177-218`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `lightning`, `ecosystem`
- Topic Tags: `release-notes`, `lightning`, `binlog`, `sync-diff-inspector`, `monitoring`, `deployment`, `operations`, `rolling-updates`, `version-support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0088_fffd882f7d`
- Source ID: `tidb-docs-8.1:releases/release-3.0-ga.md#tools`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f20f8d86d8b5cfda4aebef9f4e293148826d503b18e84a188caba908c6a66c8b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0-ga#tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 3.0 GA release-note details about Tools or TiDB Ansible, especially Lightning, Binlog, sync-diff-inspector, monitoring dashboards, rolling updates, and supported operating systems.
- Retrieval Keywords: TiDB 3.0 GA Release Notes, Tools and TiDB Ansible 3.0 GA changes, TiDB Lightning, redirected replication of data tables, importing CSV files, SQL to KV pairs, batch import of single tables, separately importing data and indexes, row_id, default column value, TIKV-importer speed limit, TiDB Binlog, advertise-addr, Drainer, GetMvccByEncodeKey, Pump, Arbiter, Kafka, MySQL, Reparo, generated columns, syncer.sql-mode, syncer.ignore-table, sync-diff-inspector, checkpoint, only-use-checksum, TiDB statistics, split chunks for comparison, Prometheus V2.8.1, Pushgateway V0.7.0, Node_exporter V0.17.0, Alertmanager V0.17.0, Grafana V6.1.6, Ansible V2.7.11, TiKV summary monitoring dashboard, TiKV trouble_shooting monitoring dashboard, TiKV details monitoring dashboard, rolling updates, table-regions.py, Leader distribution by tables, latency related monitoring items by SQL categories, CentOS 7.0+, Red Hat 7.0+, maximum QPS
- Follow-up Guidance: The source also notes TiDB Ansible support for deployment and operations for TiDB Lightning, concurrent version-consistency checks during rolling updates, and several new TiKV monitoring dashboards.
- Classification Note: This is a self-managed release-notes chunk for shared tooling and TiDB Ansible changes in TiDB 3.0 GA, covering import tools, binlog replication, data verification, monitoring, deployment, and version support.

## Official Source Content

## Tools

+ TiDB Lightning
    - Support redirected replication of data tables
    - Support importing CSV files
    - Improve performance for conversion from SQL to KV pairs
    - Support batch import of single tables to improve performance
    - Support separately importing data and indexes for big tables to improve the performance of TiKV-importer
    - Support filling the missing column using the `row_id` or the default column value when column data is missing in the new file
    - Support setting a speed limit in `TIKV-importer` when uploading SST files to TiKV
+ TiDB Binlog
    - Add the `advertise-addr` configuration in Drainer to support the bridge mode in the container environment
    - Add the `GetMvccByEncodeKey` function in Pump to speed up querying the transaction status
    - Support compressing communication data among components to reduce network resource consumption
    - Add the Arbiter tool that supports reading binlog from Kafka and replicate the data into MySQL
    - Support filtering out files that don't require replication via Reparo
    - Support replicating generated columns
    - Add the `syncer.sql-mode` configuration item to support using different sql-modes to parse DDL queries
    - Add the `syncer.ignore-table` configuration item to support filtering tables not to be replicated
+ sync-diff-inspector
    - Support checkpoint to record verification status and continue the verification from last saved point after restarting
    - Add the `only-use-checksum` configuration item to check data consistency by calculating checksum
    - Support using TiDB statistics and multiple columns to split chunks for comparison to adapt to more scenarios
## TiDB Ansible

- Upgrade the following monitoring components to a stable version:
    - Prometheus from V2.2.1 to V2.8.1
    - Pushgateway from V0.4.0 to V0.7.0
    - Node_exporter from V0.15.2 to V0.17.0
    - Alertmanager from V0.14.0 to V0.17.0
    - Grafana from V4.6.3 to V6.1.6
    - Ansible from V2.5.14 to V2.7.11
- Add the TiKV summary monitoring dashboard to view cluster status conveniently
- Add the TiKV trouble_shooting monitoring dashboard to remove duplicate items and facilitate troubleshooting
- Add the TiKV details monitoring dashboard to facilitate debugging and troubleshooting
- Add concurrent check for version consistency during rolling updates to improve the update performance
- Support deployment and operations for TiDB Lightning
- Optimize the `table-regions.py` script to support displaying Leader distribution by tables
- Optimize TiDB monitoring and add latency related monitoring items by SQL categories
- Modify the operating system version limit to only support the CentOS 7.0+ and Red Hat 7.0+ operating systems
- Add the monitoring item to predict the maximum QPS of the cluster (hidden by default)
