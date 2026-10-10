# TiDB Cloud release notes for January to February 2023

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2023.md`
- Source Title: `TiDB Cloud Release Notes in 2023`
- Source Heading Path: `TiDB Cloud Release Notes in 2023 > February 2, 2023 | TiDB Cloud Release Notes in 2023 > January 18, 2023 | TiDB Cloud Release Notes in 2023 > January 17, 2023 | TiDB Cloud Release Notes in 2023 > January 10, 2023 | TiDB Cloud Release Notes in 2023 > January 5, 2023 | TiDB Cloud Release Notes in 2023 > January 4, 2023`
- Source Line Ranges: `913-1003`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`, `tikv`, `tiflash`, `ticdc`, `dashboard`
- Topic Tags: `release-notes`, `cli`, `signup`, `serverless`, `dedicated`, `regions`, `data-import`, `chat2query`, `support`, `scaling`, `monitoring`, `prometheus`, `grafana`, `version-upgrade`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0643_c740d8778c`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2023.md#february-2-2023`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2a30bdb49d91a29322bafa199eacf199b0a319ad1b8169728178dc40d9d3e4a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2023#february-2-2023
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2023.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud release-note details from January to February 2023 about CLI availability, sign-up options, Serverless and Dedicated changes, regions, import, Chat2Query, support entry points, scaling, monitoring, Prometheus, or Grafana.
- Retrieval Keywords: TiDB Cloud release notes January 2023 February 2023, ticloud, TiDB Cloud CLI client, setup-tidbcloud-cli, TiDB Cloud CLI Quick Start, TiDB Cloud CLI Reference, signing up with a Microsoft account, Dedicated Tier v6.5.0, Serverless Tier free cluster, Seoul (ap-northeast-2), Data Migration, changefeed, backup and restore, import local CSV files, drag and drop, Explore your data by Chat2Query, Get Support, Chat2Query (beta), SQL Editor (beta), generate SQL queries using AI, Node Size(vCPU + RAM), Monitoring page, Diagnosis tab, metrics retention period, Prometheus integration, Grafana dashboard JSON, Serverless Tier v6.4.0, cold start issue, Clusters page, Connect, Import
- Follow-up Guidance: The source points to related documents including TiDB Cloud CLI Quick Start, TiDB Cloud CLI Reference, Import local files to TiDB Cloud, built-in Monitoring, Prometheus and Grafana integration, and the TiDB Cloud API (beta) UpdateCluster operation.
- Classification Note: This chunk is classified as a cloud release note because it records dated TiDB Cloud updates across console, CLI, cluster versions, regions, import, monitoring, and scaling features.

## Official Source Content

## February 2, 2023

**CLI changes**

- Introduce the TiDB Cloud CLI client [`ticloud`](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference).

    Using `ticloud`, you can easily manage your TiDB Cloud resources from a terminal or other automatic workflows with a few lines of commands. Especially for GitHub Actions, we have provided [`setup-tidbcloud-cli`](https://github.com/marketplace/actions/set-up-tidbcloud-cli) for you to easily set up `ticloud`.

    For more information, see [TiDB Cloud CLI Quick Start](https://docs.pingcap.com/tidb/stable/tidb-cloud/get-started-with-cli) and [TiDB Cloud CLI Reference](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference).
## January 18, 2023

**General changes**

* Support [signing up](https://tidbcloud.com/free-trial) TiDB Cloud with a Microsoft account.
## January 17, 2023

**General changes**

- Upgrade the default TiDB version of new [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v6.1.3](https://docs.pingcap.com/tidb/stable/release-6.1.3) to [v6.5.0](https://docs.pingcap.com/tidb/stable/release-6.5.0).

- For new sign-up users, TiDB Cloud will automatically create a free [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster so that you can quickly start a data exploration journey with TiDB Cloud.

- Support a new AWS region for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters: `Seoul (ap-northeast-2)`.

    The following features are enabled for this region:

    - [Migrate MySQL-compatible databases to TiDB Cloud using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration)
    - [Stream data from TiDB Cloud to other data services using changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview)
    - [Back up and restore TiDB cluster data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore)
## January 10, 2023

**General changes**

- Optimize the feature of importing data from local CSV files to TiDB to improve the user experience for [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    - To upload a CSV file, now you can simply drag and drop it to the upload area on the **Import** page.
    - When creating an import task, if your target database or table does not exist, you can enter a name to let TiDB Cloud create it for you automatically. For the target table to be created, you can specify a primary key or select multiple fields to form a composite primary key.
    - After the import is completed, you can explore your data with [AI-powered Chat2Query](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query) by clicking **Explore your data by Chat2Query** or clicking the target table name in the task list.

  For more information, see [Import local files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files).

**Console changes**

- Add the **Get Support** option for each cluster to simplify the process of requesting support for a specific cluster.

    You can request support for a cluster in either of the following ways:

    - On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click **...** in the row of your cluster and select **Get Support**.
    - On your cluster overview page, click **...** in the upper-right corner and select **Get Support**.
## January 5, 2023

**Console changes**

- Rename SQL Editor (beta) to Chat2Query (beta) for [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters and support generating SQL queries using AI.

  In Chat2Query, you can either let AI generate SQL queries automatically or write SQL queries manually, and run SQL queries against databases without a terminal.

  To access Chat2Query, go to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click your cluster name, and then click **Chat2Query** in the left navigation pane.
## January 4, 2023

**General changes**

- Support scaling up TiDB, TiKV, and TiFlash nodes by increasing the **Node Size(vCPU + RAM)** for TiDB Cloud Dedicated clusters hosted on AWS and created after December 31, 2022.

    You can increase the node size [using the TiDB Cloud console](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster#change-vcpu-and-ram) or [using the TiDB Cloud API (beta)](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster).

- Extend the metrics retention period on the [**Monitoring**](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring) page to two days.

    Now you have access to metrics data of the last two days, giving you more flexibility and visibility into your cluster performance and trends.

    This improvement comes at no additional cost and can be accessed on the **Diagnosis** tab of the [**Monitoring**](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring) page for your cluster. This will help you identify and troubleshoot performance issues and monitor the overall health of your cluster more effectively.

- Support customizing Grafana dashboard JSON for Prometheus integration.

    If you have [integrated TiDB Cloud with Prometheus](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-prometheus-and-grafana-integration), you can now import a pre-built Grafana dashboard to monitor TiDB Cloud clusters and customize the dashboard to your needs. This feature enables easy and fast monitoring of your TiDB Cloud clusters and helps you identify any performance issues quickly.

    For more information, see [Use Grafana GUI dashboards to visualize the metrics](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-prometheus-and-grafana-integration#step-3-use-grafana-gui-dashboards-to-visualize-the-metrics).

- Upgrade the default TiDB version of all [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters from [v6.3.0](https://docs.pingcap.com/tidb/v6.3/release-6.3.0) to [v6.4.0](https://docs.pingcap.com/tidb/v6.4/release-6.4.0). The cold start issue after upgrading the default TiDB version of Serverless Tier clusters to v6.4.0 has been resolved.

**Console changes**

- Simplify the display of the [**Clusters**](https://tidbcloud.com/project/clusters) page and the cluster overview page.

    - You can click the cluster name on the [**Clusters**](https://tidbcloud.com/project/clusters) page to enter the cluster overview page and start operating the cluster.
    - Remove the **Connection** and **Import** panes from the cluster overview page. You can click **Connect** in the upper-right corner to get the connection information and click **Import** in the left navigation pane to import data.
