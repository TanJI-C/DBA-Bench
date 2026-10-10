# PD, TiDB Binlog tools, and TiDB Ansible release updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.18.md`
- Source Title: `TiDB 2.1.18 Release Notes`
- Source Heading Path: `TiDB 2.1.18 Release Notes > PD | TiDB 2.1.18 Release Notes > Tools | TiDB 2.1.18 Release Notes > TiDB Ansible`
- Source Line Ranges: `59-76`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `ecosystem`, `tidb`
- Topic Tags: `release-notes`, `pd-ctl`, `tidb-binlog`, `drainer`, `pump`, `ansible`, `monitoring`, `alerting`, `deployment-checks`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0067_6c9b8eb53e`
- Source ID: `tidb-docs-8.1:releases/release-2.1.18.md#pd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0bd714a142c6a8f11d7d22d2e37e149dee92a4a274dbf37a17f9215ef29c80d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.18#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.18.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 2.1.18 release updates for PD, TiDB Binlog, Drainer, Pump, pd-ctl, or TiDB Ansible monitoring and deployment checks.
- Retrieval Keywords: TiDB 2.1.18 Release Notes, PD, pd-ctl --help, TiDB Binlog, Drainer, Pump, ALTER DATABASE causes Drainer to exit abnormally, querying the transaction status information for Commit binlog, replication efficiency, Drainer start_ts greater than Pump largest commit_ts, TiDB Ansible, queue size, query histogram, TiDB alerting rules, Check the configuration file before the deployment and upgrade, monitor index speed in TiDB, Grafana v4.6.3, TiDB Binlog monitoring dashboard
- Follow-up Guidance: The chunk also includes TiDB Ansible additions for TiDB Binlog monitoring items, updated alerting rules, configuration-file checks before deployment and upgrade, and Grafana dashboard compatibility.
- Classification Note: This is a release-notes chunk for shared components because it summarizes TiDB 2.1.18 updates across PD, TiDB Binlog tools, and TiDB Ansible rather than a single component.

## Official Source Content

## PD

- Improve the `--help` command output of pd-ctl [#1772](https://github.com/pingcap/pd/pull/1772)
## Tools

+ TiDB Binlog
    - Fix the issue that `ALTER DATABASE` related DDL operations cause Drainer to exit abnormally [#770](https://github.com/pingcap/tidb-binlog/pull/770)
    - Support querying the transaction status information for Commit binlog to improve replication efficiency [#761](https://github.com/pingcap/tidb-binlog/pull/761)
    - Fix the issue that a Pump panic might occur when Drainer's `start_ts` is greater than Pump's largest `commit_ts` [#759](https://github.com/pingcap/tidb-binlog/pull/759)
## TiDB Ansible

- Add two monitoring items "queue size" and "query histogram" for TiDB Binlog [#952](https://github.com/pingcap/tidb-ansible/pull/952)
- Update TiDB alerting rules [#961](https://github.com/pingcap/tidb-ansible/pull/961)
- Check the configuration file before the deployment and upgrade [#973](https://github.com/pingcap/tidb-ansible/pull/973)
- Add a new metric to monitor index speed in TiDB [#987](https://github.com/pingcap/tidb-ansible/pull/987)
- Update TiDB Binlog monitoring dashboard to make it compatible with Grafana v4.6.3 [#993](https://github.com/pingcap/tidb-ansible/pull/993)
