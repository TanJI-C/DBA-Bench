# TiDB Ansible fixes and dashboard updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.2.md`
- Source Title: `TiDB 3.0.2 Release Notes`
- Source Heading Path: `TiDB 3.0.2 Release Notes > TiDB Ansible`
- Source Line Ranges: `128-144`
- Source Scope: `self_managed`
- Primary Component: `operator`
- Related Components: `dashboard`, `pd`, `tikv`, `tidb`, `shared`, `ecosystem`
- Topic Tags: `monitoring`, `dashboard`, `ansible`, `binlog`, `configuration`, `alerting`, `leader transfer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0116_c04d5bbed6`
- Source ID: `tidb-docs-8.1:releases/release-3.0.2.md#tidb-ansible`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6bdb00dd7b3e0168c76d8aad02a33ad081b1902be46d7f351a12d87f338bee3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.2#tidb-ansible
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.2 TiDB Ansible release-note items about dashboard and monitoring fixes, generated configuration issues, Binlog and Kafka-related changes, or PD leader transfer during rolling updates.
- Retrieval Keywords: TiDB Ansible, TiDB 3.0.2 Release Notes, Disk Performance monitor treats seconds as milliseconds, log4j configuration file in Spark, Prometheus configuration file wrong format, Binlog enabled, Kafka, ZooKeeper, pessimistic-txn, generated TiDB configuration file, TiDB Dashboard, TiDB Summary Dashboard, Allocator Stats, TiKV Dashboard, Node Exporter alerting expression, TiSpark jar package v2.1.2, Ansible Task, local reader requests monitoring item, TiKV Memory monitoring item, Overview Dashboard, Remove the Binlog support in the Kafka mode, PD fails to transfer the Leader, rolling_update.yml
- Follow-up Guidance: The content also lists related dashboard updates such as monitoring item descriptions, TiDB Summary Dashboard, and expression updates for local reader requests and TiKV Memory.
- Classification Note: This is a self-managed release-notes chunk for the TiDB Ansible component because the official content enumerates fixes and updates to ansible-managed monitoring, configuration generation, Binlog support, and rolling update behavior.

## Official Source Content

## TiDB Ansible

- Fix the unit error that the Disk Performance monitor treats seconds as milliseconds [#840](https://github.com/pingcap/tidb-ansible/pull/840)
- Add the `log4j` configuration file in Spark [#841](https://github.com/pingcap/tidb-ansible/pull/841)
- Fix the issue that the Prometheus configuration file is generated in the wrong format when Binlog is enabled and Kafka or ZooKeeper is configured [#844](https://github.com/pingcap/tidb-ansible/pull/844)
- Fix the issue that the `pessimistic-txn` configuration parameter is left out in the generated TiDB configuration file [#850](https://github.com/pingcap/tidb-ansible/pull/850)
- Add and optimize metrics on the TiDB Dashboard [#853](https://github.com/pingcap/tidb-ansible/pull/853)
- Add descriptions for each monitoring item on the TiDB Dashboard [#854](https://github.com/pingcap/tidb-ansible/pull/854)
- Add the TiDB Summary Dashboard to better view the cluster status and troubleshoot issues [#855](https://github.com/pingcap/tidb-ansible/pull/855)
- Update the Allocator Stats monitoring item on the TiKV Dashboard [#857](https://github.com/pingcap/tidb-ansible/pull/857)
- Fix the unit error in the Node Exporter's alerting expression [#860](https://github.com/pingcap/tidb-ansible/pull/860)
- Upgrade the TiSpark jar package to v2.1.2 [#862](https://github.com/pingcap/tidb-ansible/pull/862)
- Update the descriptions of the Ansible Task feature [#867](https://github.com/pingcap/tidb-ansible/pull/867)
- Update the expression of the local reader requests monitoring item on the TiDB Dashboard [#874](https://github.com/pingcap/tidb-ansible/pull/874)
- Update the expression of the TiKV Memory monitoring item on the Overview Dashboard, and fix the issue of wrongly displayed monitoring [#879](https://github.com/pingcap/tidb-ansible/pull/879)
- Remove the Binlog support in the Kafka mode [#878](https://github.com/pingcap/tidb-ansible/pull/878)
- Fix the issue that PD fails to transfer the Leader when executing the `rolling_update.yml` operation [#887](https://github.com/pingcap/tidb-ansible/pull/887)
