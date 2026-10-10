# Deployment, maintenance, and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > New features > Deployment and maintenance | TiDB 6.0.0 Release Notes > Compatibility changes`
- Source Line Ranges: `240-287`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`, `ecosystem`
- Topic Tags: `deployment`, `maintenance`, `collation`, `leader-balancing`, `statistics`, `diagnostics`, `enterprise-management`, `monitoring`, `compatibility`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0287_75e2a0d017`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#deployment-and-maintenance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ed65b9818b7053a10fa405ee38c41d0f429b7dec3eee282d337854428e46e542`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#deployment-and-maintenance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.0.0 release-note changes for deployment, maintenance, monitoring customization, diagnostics, enterprise management, or compatibility notes.
- Retrieval Keywords: TiDB 6.0.0 deployment and maintenance, new_collations_enabled_on_first_bootstrap, enable new collation rules by default, leader balancing after restarting TiKV nodes, scheduler-config balance-leader-scheduler, cancel automatic update of statistics, PingCAP Clinic Technical Preview, TiDB Enterprise Manager TiEM, TiEM self-hosted public cloud environments, TiUP topology.yaml monitoring components, Prometheus Grafana Alertmanager customize configurations, Compatibility changes upgrade intermediate versions release notes
- Follow-up Guidance: The content notes that when upgrading from an earlier version to v6.0.0, you can check the Release Notes of corresponding intermediate versions for all compatibility change notes.
- Classification Note: This chunk is classified as release content because it summarizes new deployment and maintenance capabilities together with compatibility-change guidance in the TiDB 6.0.0 release notes.

## Official Source Content

### Deployment and maintenance

- Enable new collation rules by default

    Since v4.0, TiDB has supported new collation rules that behave the same way as MySQL in the case-insensitive, accent-insensitive, and padding rules. The new collation rules are controlled by the `new_collations_enabled_on_first_bootstrap` parameter, which was disabled by default. Since v6.0, TiDB enables the new collation rules by default. Note that this configuration takes effect only upon TiDB cluster initialization.

    [User documentation](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap)

- ​​Accelerate leader balancing after restarting TiKV nodes

    After a restart of TiKV nodes, the unevenly scattered leaders must be redistributed for load balance. In large-scale clusters, leader balancing time is positively correlated with the number of Regions. For example, the leader balancing of 100K Regions can take 20-30 minutes, which is prone to performance issues and stability risks due to uneven load. TiDB v6.0.0 provides a parameter to control the balancing concurrency and enlarges the default value to 4 times of the original, which greatly shortens the leader rebalancing time and accelerates the business recovery after a restart of the TiKV nodes.

    [User documentation](https://docs.pingcap.com/tidb/stable/pd-control#scheduler-config-balance-leader-scheduler), [#4610](https://github.com/tikv/pd/issues/4610)

- Support canceling the automatic update of statistics

    Statistics are one of the most important basic data that affect SQL performance. To ensure the completeness and timeliness of statistics, TiDB automatically updates object statistics periodically in the background. However, automatic statistics updates may result in resource contention, affecting SQL performance. To address this issue, you can manually cancel the automatic update of statistics since v6.0.

    [User documentation](https://docs.pingcap.com/tidb/stable/statistics#automatic-update)

- PingCAP Clinic diagnostic service (Technical Preview version)

    PingCAP Clinic is a diagnostic service for TiDB clusters. This service helps troubleshoot cluster issues remotely and provides a quick check of cluster status locally. With PingCAP Clinic, you can ensure the stable operation of your TiDB cluster during its full life cycle, predict potential issues, reduce the probability of issues, and quickly troubleshoot cluster issues.

    When contacting PingCAP technical support for remote assistance to troubleshoot cluster issues, you can use the PingCAP Clinic service to collect and upload diagnostic data, thereby improving the troubleshooting efficiency.

    [User documentation](https://docs.pingcap.com/tidb/stable/clinic/clinic-introduction)

- An enterprise-level database management platform, TiDB Enterprise Manager

    TiDB Enterprise Manager (TiEM) is an enterprise-level database management platform based on the TiDB database, which aims to help users manage TiDB clusters in self-hosted or public cloud environments.

    TiEM not only provides full lifecycle visual management for TiDB clusters, but also provides one-stop services: parameter management, version upgrades, cluster clone, active-standby cluster switching, data import and export, data replication, and data backup and restore services. TiEM can improve the efficiency of DevOps on TiDB and reduce the DevOps cost for enterprises.

    Currently, TiEM is provided in the [TiDB Enterprise](https://www.pingcap.com/tidb-enterprise/) edition only. To get TiEM, contact us via the [TiDB Enterprise](https://www.pingcap.com/tidb-enterprise/) page.

- Support customizing configurations of the monitoring components

    When you deploy a TiDB cluster using TiUP, TiUP automatically deploys monitoring components such as Prometheus, Grafana, and Alertmanager, and automatically adds new nodes into the monitoring scope after scale-out. You can customize the configurations of the monitoring components by adding configuration items to the `topology.yaml` file.

    [User document](https://docs.pingcap.com/tidb/stable/tiup/customized-montior-in-tiup-environment)
## Compatibility changes

> **Note:**
>
> When upgrading from an earlier TiDB version to v6.0.0, if you want to know the compatibility change notes of all intermediate versions, you can check the [Release Notes](https://docs.pingcap.com/tidb/stable/releases/release-notes) of the corresponding version.
