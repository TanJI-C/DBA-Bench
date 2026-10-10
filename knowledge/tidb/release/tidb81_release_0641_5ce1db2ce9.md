# March-April 2023 TiDB Cloud release updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2023.md`
- Source Title: `TiDB Cloud Release Notes in 2023`
- Source Heading Path: `TiDB Cloud Release Notes in 2023 > April 11, 2023 | TiDB Cloud Release Notes in 2023 > April 4, 2023 | TiDB Cloud Release Notes in 2023 > March 29, 2023 | TiDB Cloud Release Notes in 2023 > March 28, 2023`
- Source Line Ranges: `645-749`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `ticdc`, `tidb`
- Topic Tags: `release-notes`, `monitoring`, `alerts`, `billing`, `changefeed`, `data-service`, `access-control`, `data-migration`, `slow-query`, `integrations`, `new-relic`, `prometheus`, `serverless`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0641_5ce1db2ce9`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2023.md#april-11-2023`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `449b99bb2c95e5c81949216e3a1ca08e5f46440645b0d70ef283fc53d574c168`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2023#april-11-2023
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2023.md

## Retrieval Guidance

- Use When: Use this chunk when searching for March-April 2023 TiDB Cloud release-note changes involving Dedicated Tier or Serverless monitoring, alerts, billing, changefeeds, Data Service access control, Data Migration regions, slow query UI, or cloud integrations such as New Relic and Prometheus.
- Retrieval Keywords: April 11 2023 TiDB Cloud, April 4 2023 TiDB Cloud, March 29 2023 TiDB Cloud, March 28 2023 TiDB Cloud, Dedicated Tier AWS Oregon us-west-2 connection migration scale out scale in, New Relic integration Dedicated Tier, Prometheus integration changefeed metrics, tidbcloud_changefeed_latency, tidbcloud_changefeed_replica_rows, Monitoring page node-level resource metrics Server category Metrics tab, Billing Summary by Project Summary by Service, built-in alerts removed false positives, At least one TiDB node in the cluster has run out of memory, One or more cluster nodes are offline, Alerts page Dedicated Tier active and closed alerts, Edit Rule feature, historical data for the last 7 days, Getting Started page interactive tutorials, Data Service beta fine-grained access control for Data Apps, Manage linked clusters, Manage API keys, ReadOnly, ReadAndWrite, changefeed 2 RCUs 4 RCUs 8 RCUs, Scale a changefeed, Sink to TiDB Cloud, Dedicated Tier to Serverless Tier same project same region, Data Migration GCP Singapore asia-southeast1, Data Migration GCP Oregon us-west1, Slow Query page Serverless Tier new native web infrastructure
- Follow-up Guidance: The source points to related pages for Integrate TiDB Cloud with New Relic, TiDB Cloud built-in alerts, Manage linked clusters, Manage API keys, Scale a changefeed, Sink to TiDB Cloud, and Migrate MySQL-compatible databases to TiDB Cloud using Data Migration.
- Classification Note: This is a TiDB Cloud release-notes chunk summarizing dated cloud feature and console updates across monitoring, alerts, billing, changefeed, Data Service, Data Migration, and slow query topics.

## Official Source Content

## April 11, 2023

**General changes**

- Improve the load balance of TiDB and reduce connection drops when you scale TiDB nodes of [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS.

    - Support automatically migrating existing connections to new TiDB nodes when you scale out TiDB nodes.
    - Support automatically migrating existing connections to available TiDB nodes when you scale in TiDB nodes.

  Currently, this feature is only provided for Dedicated Tier clusters that are hosted on the AWS `Oregon (us-west-2)` region.

- Support the [New Relic](https://newrelic.com/) integration for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    With the New Relic integration, you can configure TiDB Cloud to send metric data of your TiDB clusters to [New Relic](https://newrelic.com/). Then, you can monitor and analyze both your application performance and your TiDB database performance on [New Relic](https://newrelic.com/). This feature can help you quickly identify and troubleshoot potential issues and reduce the resolution time.

    For integration steps and available metrics, see [Integrate TiDB Cloud with New Relic](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-new-relic-integration).

- Add the following [changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview) metrics to the Prometheus integration for Dedicated Tier clusters.

    - `tidbcloud_changefeed_latency`
    - `tidbcloud_changefeed_replica_rows`

    If you have [integrated TiDB Cloud with Prometheus](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-prometheus-and-grafana-integration), you can monitor the performance and health of changefeeds in real time using these metrics. Additionally, you can easily create alerts to monitor the metrics using Prometheus.

**Console changes**

- Update the [Monitoring](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#view-the-metrics-page) page for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters to use [node-level resource metrics](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#server).

    With node-level resource metrics, you can see a more accurate representation of resource consumption to better understand the actual usage of purchased services.

    To access these metrics, navigate to the [Monitoring](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#view-the-metrics-page) page of your cluster, and then check the **Server** category under the **Metrics** tab.

- Optimize the [Billing](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#billing-details) page by reorganizing the billing items in **Summary by Project** and **Summary by Service**, which makes the billing information clearer.
## April 4, 2023

**General changes**

- Remove the following two alerts from [TiDB Cloud built-in alerts](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting#tidb-cloud-built-in-alert-conditions) to prevent false positives. This is because temporary offline or out-of-memory (OOM) issues on one of the nodes do not significantly affect the overall health of a cluster.

    - At least one TiDB node in the cluster has run out of memory.
    - One or more cluster nodes are offline.

**Console changes**

- Introduce the [Alerts](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting) page for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters, which lists both active and closed alerts for each Dedicated Tier cluster.

    The **Alerts** page provides the following:

    - An intuitive and user-friendly user interface. You can view alerts for your clusters on this page even if you have not subscribed to the alert notification emails.
    - Advanced filtering options to help you quickly find and sort alerts based on their severity, status, and other attributes. It also allows you to view the historical data for the last 7 days, which eases the alert history tracking.
    - The **Edit Rule** feature. You can customize alert rule settings to meet your cluster's specific needs.

  For more information, see [TiDB Cloud built-in alerts](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting).

- Consolidate the help-related information and actions of TiDB Cloud into a single place.

    Now, you can get all the [TiDB Cloud help information](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) and contact support by clicking **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com/).

- Introduce the [Getting Started](https://tidbcloud.com/getting-started) page to help you learn about TiDB Cloud.

    The **Getting Started** page provides you with interactive tutorials, essential guides, and useful links. By following interactive tutorials, you can easily explore TiDB Cloud features and HTAP capabilities with pre-built industry-specific datasets (Steam Game Dataset and S&P 500 Dataset).

    To access the **Getting Started** page, click <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 14.9998L9 11.9998M12 14.9998C13.3968 14.4685 14.7369 13.7985 16 12.9998M12 14.9998V19.9998C12 19.9998 15.03 19.4498 16 17.9998C17.08 16.3798 16 12.9998 16 12.9998M9 11.9998C9.53214 10.6192 10.2022 9.29582 11 8.04976C12.1652 6.18675 13.7876 4.65281 15.713 3.59385C17.6384 2.53489 19.8027 1.98613 22 1.99976C22 4.71976 21.22 9.49976 16 12.9998M9 11.9998H4C4 11.9998 4.55 8.96976 6 7.99976C7.62 6.91976 11 7.99976 11 7.99976M4.5 16.4998C3 17.7598 2.5 21.4998 2.5 21.4998C2.5 21.4998 6.24 20.9998 7.5 19.4998C8.21 18.6598 8.2 17.3698 7.41 16.5898C7.02131 16.2188 6.50929 16.0044 5.97223 15.9878C5.43516 15.9712 4.91088 16.1535 4.5 16.4998Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg> **Getting Started** in the left navigation bar of the [TiDB Cloud console](https://tidbcloud.com/). On this page, you can click **Query Sample Dataset** to open the interactive tutorials or click other links to explore TiDB Cloud. Alternatively, you can click **?** in the lower-right corner and click **Interactive Tutorials**.
## March 29, 2023

**General changes**

- [Data Service (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview) supports more fine-grained access control for Data Apps.

    On the Data App details page, now you can link clusters to your Data App and specify the role for each API key. The role controls whether the API key can read or write data to the linked clusters and can be set to `ReadOnly` or `ReadAndWrite`. This feature provides cluster-level and permission-level access control for Data Apps, giving you more flexibility to control the access scope according to your business needs.

    For more information, see [Manage linked clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#manage-linked-data-sources) and [Manage API keys](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key).
## March 28, 2023

**General changes**

- Add 2 RCUs, 4 RCUs, and 8 RCUs specifications for [changefeeds](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview), and support choosing your desired specification when you [create a changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview#create-a-changefeed).

    Using these new specifications, the data replication costs can be reduced by up to 87.5% compared to scenarios where 16 RCUs were previously required.

- Support scaling up or down specifications for [changefeeds](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview) created after March 28, 2023.

    You can improve replication performance by choosing a higher specification or reduce replication costs by choosing a lower specification.

    For more information, see [Scale a changefeed](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview#scale-a-changefeed).

- Support replicating incremental data in real-time from a [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster in AWS to a [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster in the same project and same region.

    For more information, see [Sink to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-tidb-cloud).

- Support two new GCP regions for the [Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration) feature of [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters: `Singapore (asia-southeast1)` and `Oregon (us-west1)`.

    With these new regions, you have more options for migrating your data to TiDB Cloud. If your upstream data is stored in or near these regions, you can now take advantage of faster and more reliable data migration from GCP to TiDB Cloud.

    For more information, see [Migrate MySQL-compatible databases to TiDB Cloud using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration).

**Console changes**

- Release a new native web infrastructure for the [Slow Query](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#slow-query) page of [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    With this new infrastructure, you can easily navigate through the [Slow Query](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#slow-query) page and access the necessary information in a more intuitive and efficient manner. The new infrastructure also resolves many problems on UX, making the SQL diagnosis process more user-friendly.
