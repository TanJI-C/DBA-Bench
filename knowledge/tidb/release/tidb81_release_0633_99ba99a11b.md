# TiDB Cloud release notes for September to early August 2022

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2022.md`
- Source Title: `TiDB Cloud Release Notes in 2022`
- Source Heading Path: `TiDB Cloud Release Notes in 2022 > September 9, 2022 | TiDB Cloud Release Notes in 2022 > September 6, 2022 | TiDB Cloud Release Notes in 2022 > August 30, 2022 | TiDB Cloud Release Notes in 2022 > August 24, 2022 | TiDB Cloud Release Notes in 2022 > August 23, 2022 | TiDB Cloud Release Notes in 2022 > August 16, 2022 | TiDB Cloud Release Notes in 2022 > August 9, 2022 | TiDB Cloud Release Notes in 2022 > August 2, 2022`
- Source Line Ranges: `323-437`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `sql`, `tidb`, `tiflash`, `tikv`
- Topic Tags: `release-notes`, `datadog`, `monitoring`, `api`, `beta`, `privatelink`, `network-access`, `pause-resume`, `cluster-version`, `developer-tier`, `dedicated-tier`, `node-size`, `credits`, `regions`, `data-import`, `support-plans`, `console-ui`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0633_99ba99a11b`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2022.md#september-9-2022`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a627418f192dc3148d5c2900e3a447fa77819b325b0b3dbd34d7f842eb8bce3e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2022#september-9-2022
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2022.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud release-note entries from August to September 2022 about Datadog metrics, TiDB Cloud API beta changes, AWS PrivateLink, pause or resume, node sizes, credits, regions, data import, support plans, or console UI updates.
- Retrieval Keywords: September 9 2022, September 6 2022, August 30 2022, August 24 2022, August 23 2022, August 16 2022, August 9 2022, August 2 2022, Datadog, metrics available to Datadog, Dedicated Tier, Developer Tier, TiDB Cloud API, beta, storage_size_gib, Modify a Dedicated Tier cluster, AWS PrivateLink-powered endpoint connection, Private Endpoint, VPC Peering, pause or resume your Dedicated Tier cluster, Node Compute Cost, v6.1.1, v6.2.0, 2 vCPU, 8 GiB (Beta), 4 vCPU, 16 GiB, Credits, Billing page, GCP region Osaka, Monitoring page, Diagnosis tab, Custom Pattern, Import CSV Files, Import Apache Parquet Files, TiDB Cloud Support Plans, Connect button, Import data button
- Follow-up Guidance: The source points to related documentation such as monitor-datadog integration, TiDB Cloud API documentation, Set Up Private Endpoint Connections, pause or resume your Dedicated Tier cluster, built-in monitoring, import CSV or Parquet files, and TiDB Cloud Support.
- Classification Note: This is a TiDB Cloud release-notes chunk covering cloud general changes, console changes, and API changes across Dedicated Tier and Developer Tier in August and early September 2022.

## Official Source Content

## September 9, 2022

**General changes**

* Provide [more metrics](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-datadog-integration#metrics-available-to-datadog) of Dedicated Tier clusters in Datadog to help you better understand the cluster performance status.

    If you have [integrated TiDB Cloud with Datadog](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-datadog-integration), you can view these metrics in your Datadog dashboards directly.
## September 6, 2022

**General changes**

* Upgrade the default TiDB version of new [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v6.1.0](https://docs.pingcap.com/tidb/stable/release-6.1.0) to [v6.1.1](https://docs.pingcap.com/tidb/stable/release-6.1.1).

**Console changes**

* Now you can [apply for a PoC](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-poc) from the entry in the upper-right corner of the TiDB Cloud console.

**API changes**

* Support increasing the storage of a TiKV or TiFlash node through the [TiDB Cloud API](https://docs.pingcap.com/tidb/stable/tidb-cloud/api-overview). You can use the `storage_size_gib` field of the API endpoint to do the scaling.

    Currently, TiDB Cloud API is still in beta and only available upon request.

    For details, see [Modify a Dedicated Tier cluster](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/UpdateCluster).
## August 30, 2022

**General changes**

* Support AWS PrivateLink-powered endpoint connection as a new network access management option for TiDB Cloud [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    The endpoint connection is secure and private, and does not expose your data to the public internet. In addition, the endpoint connection supports CIDR overlap and is easier for network management.

    For more information, see [Set Up Private Endpoint Connections](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections).

**Console changes**

* Provide sample connection strings of MySQL, MyCLI, JDBC, Python, Go, and Node.js in the **VPC Peering** tab and **Private Endpoint** tab of the [Connect](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster) dialog for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    You can easily connect to your Dedicated Tier cluster by simply copying and pasting the connection codes to your apps.
## August 24, 2022

**General changes**

* Support pausing or resuming a Dedicated Tier cluster.

    You can [pause or resume your Dedicated Tier cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/pause-or-resume-tidb-cluster) in TiDB Cloud. When a cluster is paused, Node Compute Cost will not be charged.
## August 23, 2022

**General changes**

* Upgrade the default TiDB version of new [Developer Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters from [v6.1.0](https://docs.pingcap.com/tidb/stable/release-6.1.0) to [v6.2.0](https://docs-archive.pingcap.com/tidb/v6.2/release-6.2.0).

**API changes**

* Introduce TiDB Cloud API as beta.

    Through this API, you can manage TiDB Cloud resources such as clusters automatically and efficiently. For more information, see [TiDB Cloud API Documentation](https://docs.pingcap.com/tidbcloud/api/v1beta).

    Currently, TiDB Cloud API is still in beta and only available upon request. You can apply for API access by submitting a request:

    * Click **Help** in the lower-right corner of [TiDB Cloud console](https://tidbcloud.com/project/clusters).
    * In the dialog, fill in "Apply for TiDB Cloud API" in the **Description** field and click **Send**.
## August 16, 2022

* Add `2 vCPU, 8 GiB (Beta)` node size of TiDB and TiKV as beta.

    * For each `2 vCPU, 8 GiB (Beta)` TiKV node, the storage size is between 200 GiB and 500 GiB.

    * Suggested usage scenarios:

        * Low-workload production environments for SMB
        * PoC and staging environments
        * Development environments

* Introduce [Credits](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#credits) (previously named as trail points) for PoC users.

    You can now view information about your organization's credits on the **Credits** tab of the **Billing** page, the credits can be used to pay for TiDB Cloud fees. You can <a href="mailto:tidbcloud-support@pingcap.com">contact us</a> to get credits.
## August 9, 2022

* Add the support of the GCP region `Osaka` for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster creation.
## August 2, 2022

* The `4 vCPU, 16 GiB` node size of TiDB and TiKV is now in General Availability (GA).

    * For each `4 vCPU, 16 GiB` TiKV node, the storage size is between 200 GiB and 2 TiB.
    * Suggested usage scenarios:

        * Low workload production environments for SMB
        * PoC and staging environments
        * Development environments

* Add a [Monitoring page](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring) to the **Diagnosis** tab for [Dedicated Tier clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).

    The Monitoring page provides a system-level entry for overall performance diagnosis. According to the top-down performance analysis methodology, the Monitoring page organizes TiDB performance metrics based on database time breakdown and displays these metrics in different colors. By checking these colors, you can identify performance bottlenecks of the entire system at the first glance, which significantly reduces performance diagnosis time and simplifies performance analysis and diagnosis.

* Add a switch to enable or disable **Custom Pattern** on the **Data Import** page for CSV and Parquet source files.

    The **Custom Pattern** feature is disabled by default. You can enable it when you are going to import CSV or Parquet files whose filenames match a certain pattern to a single target table.

    For more information, see [Import CSV Files](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files) and [Import Apache Parquet Files](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files).

* Add TiDB Cloud Support Plans (Basic, Standard, Enterprise, and Premium) to meet different support needs of customers' organizations. For more information, see [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

* Optimize the UI of the [Clusters](https://tidbcloud.com/project/clusters) page and the cluster details page:

    * Add **Connect** and **Import data** buttons to the **Clusters** page.
    * Move **Connect** and **Import data** buttons to the upper-right corner on the cluster details page.
