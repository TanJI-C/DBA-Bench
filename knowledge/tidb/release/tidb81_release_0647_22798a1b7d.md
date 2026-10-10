# TiDB Cloud 2024 release notes: Jan-Jun platform, API, CLI, sizing, and recovery updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2024.md`
- Source Title: `TiDB Cloud Release Notes in 2024`
- Source Heading Path: `TiDB Cloud Release Notes in 2024 > June 18, 2024 | TiDB Cloud Release Notes in 2024 > June 4, 2024 | TiDB Cloud Release Notes in 2024 > May 28, 2024 | TiDB Cloud Release Notes in 2024 > May 21, 2024 | TiDB Cloud Release Notes in 2024 > May 14, 2024 | TiDB Cloud Release Notes in 2024 > April 16, 2024 | TiDB Cloud Release Notes in 2024 > April 9, 2024 | TiDB Cloud Release Notes in 2024 > April 2, 2024 | TiDB Cloud Release Notes in 2024 > March 5, 2024 | TiDB Cloud Release Notes in 2024 > February 21, 2024 | TiDB Cloud Release Notes in 2024 > February 20, 2024 | TiDB Cloud Release Notes in 2024 > January 23, 2024`
- Source Line Ranges: `275-431`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`, `dm`, `sql`, `shared`
- Topic Tags: `release-notes`, `serverless`, `dedicated`, `node-sizing`, `version-upgrade`, `recovery-group`, `disaster-recovery`, `billing`, `metering`, `tiflash`, `ttl`, `data-migration`, `api`, `data-service`, `cli`, `oauth`, `vpc-peering`, `time-zone`, `cost-explorer`, `monitoring`, `resource-metrics`, `usage-quota`, `google-cloud`, `aws`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0647_22798a1b7d`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2024.md#june-18-2024`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `47920e1efbbad6bdcd07e811998f4462b1289da1c75a18b95a1cf6fdf3646756`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2024#june-18-2024
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2024.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud release-note changes from January to June 2024 across Dedicated and Serverless, including node sizing, version upgrades, Recovery Group, TiFlash billing, Data Migration, Data Service API, CLI, VPC peering, monitoring, billing, and usage quota behavior.
- Retrieval Keywords: TiDB Cloud Release Notes in 2024, June 18 2024, June 4 2024, May 28 2024, May 21 2024, May 14 2024, April 16 2024, April 9 2024, April 2 2024, March 5 2024, February 21 2024, February 20 2024, January 23 2024, TiDB Cloud Dedicated, TiDB Cloud Serverless, Recovery Group, billing and metering beta, TiFlash, TTL, Data Migration, Google Cloud Taiwan asia-east1, TiDB node size, 16 vCPU, 64 GiB, 8 vCPU, 16 GiB, 8 vCPU, 32 GiB, 32 vCPU, 128 GiB, Data Service API, API v1beta1, Data App, Data Source, Endpoint, Data API Key, OpenAPI Specification 3.0, TiDB Cloud CLI 1.0.0-beta.1, ticloud serverless, OAuth, TiDB Bot, VPC peering, Time Zone, Cost Explorer, node-level resource metrics, limit label, usage quota, Free and Scalable service plans, regional CIDR size /19, up to 124 TiDB Cloud nodes, default TiDB version v7.5.2, v7.5.1, v7.1.3
- Follow-up Guidance: The source points to related documentation such as TiFlash node storage, recovery groups, Data Service API v1beta1, TiDB Cloud CLI reference, Cost Explorer, built-in monitoring metrics, usage quota, VPC peering, and cluster sizing pages.
- Classification Note: This chunk is classified as a cloud release-note summary because the official content lists dated TiDB Cloud platform, API, CLI, sizing, billing, monitoring, and version changes released in 2024.

## Official Source Content

## June 18, 2024

**General changes**

- Increase the maximum node storage of 16 vCPU TiFlash and 32 vCPU TiFlash for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from 2048 GiB to 4096 GiB.

    This enhancement increases the analytics data storage capacity of your TiDB Cloud Dedicated cluster, improves workload scaling efficiency, and accommodates growing data requirements.

    For more information, see [TiFlash node storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tiflash-node-storage).

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v7.5.1](https://docs.pingcap.com/tidb/v7.5/release-7.5.1) to [v7.5.2](https://docs.pingcap.com/tidb/v7.5/release-7.5.2).
## June 4, 2024

**General changes**

- Introduce the Recovery Group feature (beta) for disaster recovery of [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters deployed on AWS.

    This feature enables you to replicate your databases between TiDB Cloud Dedicated clusters, ensuring rapid recovery in the event of a regional disaster. If you are in the `Project Owner` role, you can enable this feature by creating a new recovery group and assigning databases to the group. By replicating databases with recovery groups, you can improve disaster readiness, meet stricter availability SLAs, and achieve more aggressive Recovery Point Objectives (RPO) and Recovery Time Objectives (RTO).

    For more information, see [Get started with recovery groups](https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-get-started).

- Introduce billing and metering (beta) for the [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) columnar storage [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview).

    Until June 30, 2024, columnar storage in TiDB Cloud Serverless clusters remains free with a 100% discount. After this date, each TiDB Cloud Serverless cluster will include a free quota of 5 GiB for columnar storage. Usage beyond the free quota will be charged.

    For more information, see [TiDB Cloud Serverless pricing details](https://www.pingcap.com/tidb-serverless-pricing-details/#storage).

- [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) supports [Time to live (TTL)](https://docs.pingcap.com/tidb/stable/time-to-live).
## May 28, 2024

**General changes**

- Google Cloud `Taiwan (asia-east1)` region supports the [Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration) feature.

    The [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted in the Google Cloud `Taiwan (asia-east1)` region now support the Data Migration (DM) feature. If your upstream data is stored in or near this region, you can now take advantage of faster and more reliable data migration from Google Cloud to TiDB Cloud.

- Provide a new [TiDB node size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tidb-vcpu-and-ram) for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS and Google Cloud: `16 vCPU, 64 GiB`

**API changes**

- Introduce TiDB Cloud Data Service API for managing the following resources automatically and efficiently:

    * **Data App**: a collection of endpoints that you can use to access data for a specific application.
    * **Data Source**: clusters linked to Data Apps for data manipulation and retrieval.
    * **Endpoint**: a web API that you can customize to execute SQL statements.
    * **Data API Key**: used for secure endpoint access.
    * **OpenAPI Specification**: Data Service supports generating the OpenAPI Specification 3.0 for each Data App, which enables you to interact with your endpoints in a standardized format.

  These TiDB Cloud Data Service API endpoints are released in TiDB Cloud API v1beta1, which is the latest API version of TiDB Cloud.

    For more information, see [API documentation (v1beta1)](https://docs.pingcap.com/tidbcloud/api/v1beta1/dataservice).
## May 21, 2024

**General changes**

- Provide a new [TiDB node size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tidb-vcpu-and-ram) for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on Google Cloud: `8 vCPU, 16 GiB`
## May 14, 2024

**General changes**

- Expand the selection of time zones in the [**Time Zone**](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#set-the-time-zone-for-your-organization) section to better accommodate customers from diverse regions.

- Support [creating a VPC peering](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) when your VPC is in a different region from the VPC of TiDB Cloud.

- [Data Service (beta)](https://tidbcloud.com/project/data-service) supports path parameters alongside query parameters.

    This feature enhances resource identification with structured URLs and improves user experience, search engine optimization (SEO), and client integration, offering developers more flexibility and better alignment with industry standards.

    For more information, see [Basic properties](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#basic-properties).
## April 16, 2024

**CLI changes**

- Introduce [TiDB Cloud CLI 1.0.0-beta.1](https://github.com/tidbcloud/tidbcloud-cli), built upon the new [TiDB Cloud API](https://docs.pingcap.com/tidb/stable/tidb-cloud/api-overview). The new CLI brings the following new features:

    - [Export data from TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export)
    - [Import data from local storage into TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-import-start)
    - [Authenticate via OAuth](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auth-login)
    - [Ask questions via TiDB Bot](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-ai)

  Before upgrading your TiDB Cloud CLI, note that this new CLI is incompatible with previous versions. For example, `ticloud cluster` in CLI commands is now updated to `ticloud serverless`. For more information, see [TiDB Cloud CLI reference](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference).
## April 9, 2024

**General changes**

- Provide a new [TiDB node size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tidb-vcpu-and-ram) for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS: `8 vCPU, 32 GiB`.
## April 2, 2024

**General changes**

- Introduce two service plans for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters: **Free** and **Scalable**.

    To meet different user requirements, TiDB Cloud Serverless offers the free and scalable service plans. Whether you are just getting started or scaling to meet the increasing application demands, these plans provide the flexibility and capabilities you need.

    For more information, see [Cluster plans](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#cluster-plans).

- Modify the throttling behavior for TiDB Cloud Serverless clusters upon reaching their usage quota. Now, once a cluster reaches its usage quota, it immediately denies any new connection attempts, thereby ensuring uninterrupted service for existing operations.

    For more information, see [Usage quota](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-limitations#usage-quota).
## March 5, 2024

**General changes**

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v7.5.0](https://docs.pingcap.com/tidb/v7.5/release-7.5.0) to [v7.5.1](https://docs.pingcap.com/tidb/v7.5/release-7.5.1).

**Console changes**

- Introduce the **Cost Explorer** tab on the [**Billing**](https://tidbcloud.com/org-settings/billing/payments) page, which provides an intuitive interface for analyzing and customizing cost reports for your organization over time.

    To use this feature, navigate to the **Billing** page of your organization and click the **Cost Explorer** tab.

    For more information, see [Cost Explorer](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#cost-explorer).

- [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) displays a **limit** label for [node-level resource metrics](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#server).

    The **limit** label shows the maximum usage of resources such as CPU, memory, and storage for each component in a cluster. This enhancement simplifies the process of monitoring the resource usage rate of your cluster.

    To access these metric limits, navigate to the **Monitoring** page of your cluster, and then check the **Server** category under the **Metrics** tab.

    For more information, see [Metrics for TiDB Cloud Dedicated clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring#server).
## February 21, 2024

**General changes**

- Upgrade the TiDB version of [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters from [v6.6.0](https://docs.pingcap.com/tidb/v6.6/release-6.6.0) to [v7.1.3](https://docs.pingcap.com/tidb/v7.1/release-7.1.3).
## February 20, 2024

**General changes**

- Support creating more TiDB Cloud nodes on Google Cloud.

    - By [configuring a regional CIDR size](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#prerequisite-set-a-cidr-for-a-region) of `/19` for Google Cloud, you can now create up to 124 TiDB Cloud nodes within any region of a project.
    - If you want to create more than 124 nodes in any region of a project, you can contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for assistance in customizing an IP range size ranging from `/16` to `/18`.
## January 23, 2024

**General changes**

- Add 32 vCPU as a node size option for TiDB, TiKV, and TiFlash.

    For each `32 vCPU, 128 GiB` TiKV node, the node storage ranges from 200 GiB to 6144 GiB.

    It is recommended to use such nodes in the following scenarios:

    - High-workload production environments
    - Extremely high performance
