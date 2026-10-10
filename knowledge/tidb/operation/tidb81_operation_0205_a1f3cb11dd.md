# TiUP deployment and upgrade improvements

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > Deployment and maintenance > Optimize the logic of cluster deployment operations, to help DBAs deploy a set of standard TiDB production cluster faster | What's New in TiDB 5.0 > Deployment and maintenance > Improve upgrade stability | What's New in TiDB 5.0 > Deployment and maintenance > Optimize the upgrade time | What's New in TiDB 5.0 > Deployment and maintenance > Support the breakpoint feature | What's New in TiDB 5.0 > Deployment and maintenance > Enhance the functionalities of maintenance and operations`
- Source Line Ranges: `416-462`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `tikv`, `dm`, `shared`
- Topic Tags: `deployment`, `upgrade`, `rolling-upgrade`, `offline-upgrade`, `topology-check`, `environment-check`, `breakpoint-retry`, `cluster-maintenance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0205_a1f3cb11dd`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#optimize-the-logic-of-cluster-deployment-operations-to-help-dbas-deploy-a-set-of-standard-tidb-production-cluster-faster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d7b72b6ba76b541d7693646da7ea19fb33f61fc8e2e43ed0cc026dba8d006605`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#optimize-the-logic-of-cluster-deployment-operations-to-help-dbas-deploy-a-set-of-standard-tidb-production-cluster-faster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiUP v1.4.0 deployment, upgrade, breakpoint retry, topology check, or maintenance improvements for TiDB and DM clusters.
- Retrieval Keywords: TiUP Cluster, tiup-cluster, check topo.yaml, check topo.yaml --apply, template, edit-config, remote_config, external_alertmanagers, PD online rolling upgrades, PD follower, PD Leader, tiup cluster upgrade --offline, Region Leader relocation, check subcommand, replay subcommand, display --version, downtime TiDB and DM clusters
- Follow-up Guidance: The source points to the production deployment using TiUP document and the telemetry-independent release notes describe the related subcommands and parameters to retrieve.
- Classification Note: This is classified as operation for the self-managed tiup component because the content covers cluster deployment, rolling upgrade behavior, offline upgrade, breakpoint recovery, and maintenance commands.

## Official Source Content

### Optimize the logic of cluster deployment operations, to help DBAs deploy a set of standard TiDB production cluster faster

[User Document](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup)

In previous TiDB versions, DBAs using TiUP to deploy TiDB clusters find that the environment initialization is complicated, the checksum configuration is excessive, and the cluster topology file is difficult to edit. All of these issues lead to low deployment efficiency for DBAs. In TiDB v5.0, the TiDB deployment efficiency using TiUP is improved for DBAs through the following items:

+ TiUP Cluster supports the `check topo.yaml` command to perform a more comprehensive one-click environment check and provide repair recommendations.
+ TiUP Cluster supports the `check topo.yaml --apply` command to automatically repair environmental problems found during the environment check.
+ TiUP Cluster supports the `template` command to get the cluster topology template file for DBAs to edit and support modifying the global node parameters.
+ TiUP supports editing the `remote_config` parameter using the `edit-config` command to configure remote Prometheus.
+ TiUP supports editing the `external_alertmanagers` parameter to configure different AlertManagers using the `edit-config` command.
+ When editing the topology file using the `edit-config` subcommand in tiup-cluster, you can modify the data types of the configuration item values.
### Improve upgrade stability

Before TiUP v1.4.0, during the upgrade of a TiDB cluster using tiup-cluster, the SQL responses of the cluster jitter for a long period of time, and during PD online rolling upgrades, the QPS of the cluster jitter between 10s to 30s.

TiUP v1.4.0 adjusts the logic and makes the following optimizations:

+ During the upgrade of PD nodes, TiUP automatically checks the status of the restarted PD node, and then rolls to upgrade the next PD node after confirming that the status is ready.
+ TiUP identifies the PD role automatically, first upgrades the PD nodes of the follower role, and finally upgrades the PD Leader node.
### Optimize the upgrade time

Before TiUP v1.4.0, when DBAs upgrade TiDB clusters using tiup-cluster, for clusters with a large number of nodes, the total upgrade time is long and cannot meet the upgrade time window requirement for certain users.

Starting from v1.4.0, TiUP optimizes the following items:

+ Supports fast offline upgrades using the `tiup cluster upgrade --offline` subcommand.
+ Speeds up the Region Leader relocation for users using rolling upgrades during upgrades by default, so that reduces the time of rolling TiKV upgrades.
+ Checks the status of the Region monitor using the `check` subcommand before running a rolling upgrade. Ensure that the cluster is in a normal state before the upgrade, thus reducing the probability of upgrade failures.
### Support the breakpoint feature

Before TiUP v1.4.0, when DBAs upgrade TiDB clusters using tiup-cluster, if the execution of a command is interrupted, all the upgrade operations have to be performed again from the beginning.

TiUP v1.4.0 supports retrying failed operations from breakpoints using the tiup-cluster `replay` subcommand, to avoid re-executing all operations after an upgrade interruption.
### Enhance the functionalities of maintenance and operations

TiUP v1.4.0 further enhances the functionalities for operating and maintaining TiDB clusters.

+ Supports the upgrade or patch operation on the downtime TiDB and DM clusters to adapt to more usage scenarios.
+ Adds the `--version` parameter to the `display` subcommand of tiup-cluster to get the cluster version.
+ When only Prometheus is included in the node being scaled out, the operation of updating the monitoring configuration is not performed, to avoid scale-out failure due to the absence of the Prometheus node.
+ Adds user input to the error message when the results of the input TiUP commands are incorrect, so that you can locate the cause of the problem more quickly.
