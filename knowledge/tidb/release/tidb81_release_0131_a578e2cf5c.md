# Tools and TiDB Ansible release note changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.8.md`
- Source Title: `TiDB 3.0.8 Release Notes`
- Source Heading Path: `TiDB 3.0.8 Release Notes > Tools | TiDB 3.0.8 Release Notes > TiDB Ansible`
- Source Line Ranges: `101-112`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `tidb-binlog`, `pump`, `ddl-binlog`, `ansible`, `rolling-update`, `configuration`, `grafana`, `monitoring`, `tispark`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0131_a578e2cf5c`
- Source ID: `tidb-docs-8.1:releases/release-3.0.8.md#tools`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a9f47c457927c46c28e8f778c12af368deaa5350cbcd28466492eb263ef60153`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.8#tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.8.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.8 release notes about TiDB Binlog Pump missing DDL committed binlog or TiDB Ansible changes to rolling update checks, configuration, TiSpark, and Grafana monitoring items.
- Retrieval Keywords: TiDB 3.0.8 Tools, TiDB Binlog, Pump does not receive the DDL committed binlog, binlog is ignored, TiDB Ansible 3.0.8, Revert the simplified configuration item, checking the TiDB version when performing a rolling update, Upgrade TiSpark to v2.1.8, PD role monitoring item wrongly displayed on Grafana, Thread Voluntary Context Switches, Thread Nonvoluntary Context Switches, TiKV Detail page on Grafana
- Follow-up Guidance: The source also includes TiDB Ansible changes for rolling update version checks, a reverted simplified configuration item, a TiSpark upgrade to v2.1.8, and Grafana monitoring fixes.
- Classification Note: This is a release-note chunk for shared tooling, specifically TiDB Binlog and TiDB Ansible updates, within self-managed TiDB 3.0.8.

## Official Source Content

## Tools

+ TiDB Binlog
    - Fix the issue that the binlog is ignored because Pump does not receive the DDL committed binlog [#853](https://github.com/pingcap/tidb-binlog/pull/853)
## TiDB Ansible

- Revert the simplified configuration item [#1053](https://github.com/pingcap/tidb-ansible/pull/1053)
- Optimize the logic for checking the TiDB version when performing a rolling update [#1056](https://github.com/pingcap/tidb-ansible/pull/1056)
- Upgrade TiSpark to v2.1.8 [#1061](https://github.com/pingcap/tidb-ansible/pull/1061)
- Fix the issue that the PD role monitoring item is wrongly displayed on Grafana [#1065](https://github.com/pingcap/tidb-ansible/pull/1065)
- Optimize `Thread Voluntary Context Switches` and `Thread Nonvoluntary Context Switches` monitoring items on the TiKV Detail page on Grafana [#1071](https://github.com/pingcap/tidb-ansible/pull/1071)
