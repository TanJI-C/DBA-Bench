# TiDB Cloud release notes for September to October 2022

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2022.md`
- Source Title: `TiDB Cloud Release Notes in 2022`
- Source Heading Path: `TiDB Cloud Release Notes in 2022 > October 28, 2022 | TiDB Cloud Release Notes in 2022 > October 25, 2022 | TiDB Cloud Release Notes in 2022 > October 19, 2022 | TiDB Cloud Release Notes in 2022 > October 18, 2022 | TiDB Cloud Release Notes in 2022 > October 11, 2022 | TiDB Cloud Release Notes in 2022 > September 27, 2022 | TiDB Cloud Release Notes in 2022 > September 20, 2022 | TiDB Cloud Release Notes in 2022 > September 15, 2022 | TiDB Cloud Release Notes in 2022 > September 14, 2022 | TiDB Cloud Release Notes in 2022 > September 13, 2022`
- Source Line Ranges: `168-322`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`, `tikv`, `tiflash`, `ecosystem`, `shared`
- Topic Tags: `release-notes`, `serverless`, `dedicated-tier`, `developer-tier`, `system-variables`, `tls`, `billing`, `organizations`, `slow-query`, `data-import`, `api`, `vercel`, `terraform`, `regions`, `playground`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0632_17db67072a`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2022.md#october-28-2022`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2667b68c3fa0ff4f82f5f722a6e3bc8b930c2e430c2fe3911e78dea9fd0e69d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2022#october-28-2022
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2022.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for TiDB Cloud release changes from September to October 2022 covering Serverless Tier, Dedicated Tier, system variables, TLS, billing, organizations, Slow Query, data import, API, Vercel, Terraform, regions, or Playground.
- Retrieval Keywords: TiDB Cloud release notes 2022 September October, October 28 2022 Serverless Tier Developer Tier upgraded, Serverless Tier enforces TLS connection, October 25 2022 SET GLOBAL SESSION system variables beta, SET GLOBAL tidb_committer_concurrency = 127, require_secure_transport, tidb_committer_concurrency, tidb_enable_batch_dml, tidb_enable_prepared_plan_cache, tidb_max_tiflash_threads, tidb_mem_oom_action, tidb_mem_quota_query, tidb_prepared_plan_cache_size, tidb_query_log_max_len, default TiDB version new Dedicated Tier clusters v6.1.2, TiDB Cloud Vercel Integration, TiDB Cloud Starter Template, minimum storage size TiKV TiFlash 200 GiB, Contract tab Billing page, TiDB Cloud Terraform Provider, default TiDB version new Developer Tier clusters v6.3.0, billing details Usage Details CSV, joining multiple organizations by invitation, Slow Query page SQL diagnosis, cost quota-based invoice, new web UI for data import, TiDB Cloud API beta available to all users, Dedicated Tier clusters via TLS, download the TiDB cluster CA, Playground for Developer Tier clusters, GitHub events dataset, N. Virginia us-east4
- Follow-up Guidance: The chunk points to related documentation such as the TiDB Cloud quickstart, secure connections, system variables, Vercel integration, billing, Terraform provider, API overview, standard connection, and organization management pages.
- Classification Note: This is a release-notes chunk for TiDB Cloud because it lists dated product, console, API, integration, billing, and documentation changes across multiple September and October 2022 entries.

## Official Source Content

## October 28, 2022

**General changes**

* Developer Tier is upgraded to [Serverless Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). Serverless Tier, a fully-managed, auto-scaling deployment of TiDB, is now available. It is still in beta and free to use.

    * A Serverless Tier cluster still contains fully functional HTAP ability as Dedicated Tier clusters.
    * Serverless Tier offers you faster cluster creation time and instantaneous cold start time. Compared with Developer Tier, the creation time reduces from minutes to seconds.
    * You do not need to worry about deployment topology. Serverless Tier will adjust automatically according to your requests.
    * Serverless Tier [enforces TLS connection to clusters for the sake of security](https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters).
    * Existing Developer Tier clusters will be automatically migrated to Serverless Tier in the coming months. Your ability to use your cluster should not be affected, and you will not be charged for the use of your Serverless Tier cluster in beta.

  Get started [here](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart).
## October 25, 2022

**General changes**

- Support dynamically changing and persisting a subset of TiDB system variables (beta).

    You can use the standard SQL statement to set a new value for a supported system variable.

    ```sql
    SET [GLOBAL|SESSION] <variable>
    ```

    For example:

    ```sql
    SET GLOBAL tidb_committer_concurrency = 127;
    ```

    If a variable is set at the `GLOBAL` level, the variable will be applied to the cluster and persistent (keep effective even after you restart or reload the server). A variable at the `SESSION` level is not persistent and is only effective in the current session.

    **This feature is still in beta**, and only a limited number of variables are supported. It is not recommended to modify other [system variables](https://docs.pingcap.com/tidb/stable/system-variables) due to uncertainty of the side effects. See the following list for all supported variables based on TiDB v6.1:

    - [`require_secure_transport`](https://docs.pingcap.com/tidb/stable/system-variables#require_secure_transport-new-in-v610)
    - [`tidb_committer_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_committer_concurrency-new-in-v610)
    - [`tidb_enable_batch_dml`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_batch_dml)
    - [`tidb_enable_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_prepared_plan_cache-new-in-v610)
    - [`tidb_max_tiflash_threads`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_tiflash_threads-new-in-v610)
    - [`tidb_mem_oom_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_oom_action-new-in-v610)
    - [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query)
    - [`tidb_prepared_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prepared_plan_cache_size-new-in-v610)
    - [`tidb_query_log_max_len`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_query_log_max_len)

- Upgrade the default TiDB version of new [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v6.1.1](https://docs.pingcap.com/tidb/stable/release-6.1.1) to [v6.1.2](https://docs.pingcap.com/tidb/stable/release-6.1.2).
## October 19, 2022

**Integration changes**

* Publish [TiDB Cloud Vercel Integration](https://vercel.com/integrations/tidb-cloud) in [Vercel Integration Marketplace](https://vercel.com/integrations#databases).

    [Vercel](https://vercel.com) is the platform for frontend developers, providing the speed and reliability innovators need to create at the moment of inspiration. Using TiDB Cloud Vercel Integration, you can easily connect your Vercel projects to TiDB Cloud clusters. For details, see the document [Integrate TiDB Cloud with Vercel](https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel).

* Publish [TiDB Cloud Starter Template](https://vercel.com/templates/next.js/tidb-cloud-starter) in [Vercel template list](https://vercel.com/templates).

    You can use this template as a start to try out Vercel and TiDB Cloud. Before using this template, you need to [import data into your TiDB Cloud cluster](https://github.com/pingcap/tidb-prisma-vercel-demo#2-import-table-structures-and-data) first.
## October 18, 2022

**General changes**

* For Dedicated Tier clusters, the minimum storage size of a TiKV or TiFlash node is changed from 500 GiB to 200 GiB. This will be more cost-effective for users whose workloads are in small data volumes.

    For more details, see [TiKV node storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tikv-node-storage-size) and [TiFlash node storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tiflash-node-storage).

* Introduce online contracts to customize TiDB Cloud subscriptions and meet compliance requirements.

    A [**Contract** tab](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#contract) is added to the **Billing** page of the TiDB Cloud console. If you have agreed with our sales on a contract and received an email to process the contract online, you can go to the **Contract** tab to review and accept the contract. To learn more about contracts, feel free to [contact our sales](https://www.pingcap.com/contact-us/).

**Documentation changes**

* Add [documentation](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-tidbcloud-provider-overview) for [TiDB Cloud Terraform Provider](https://registry.terraform.io/providers/tidbcloud/tidbcloud).

    TiDB Cloud Terraform Provider is a plugin that allows you to use [Terraform](https://www.terraform.io/) to manage TiDB Cloud resources, such as clusters, backups, and restores. If you are looking for a simple way to automate resource provisioning and your infrastructure workflow, you can try out TiDB Cloud Terraform Provider according to the [documentation](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-tidbcloud-provider-overview).
## October 11, 2022

**General changes**

* Upgrade the default TiDB version of new [Developer Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters from [v6.2.0](https://docs-archive.pingcap.com/tidb/v6.2/release-6.2.0) to [v6.3.0](https://docs-archive.pingcap.com/tidb/v6.3/release-6.3.0).

**Console changes**

* Optimize billing information on the [billing details page](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#billing-details):

    * Provide more fine-grained billing information at the node level in the **Summary By Service** section.
    * Add a **Usage Details** section. You can also download usage details as a CSV file.
## September 27, 2022

**General changes**

* Support joining multiple organizations by invitation.

    In the TiDB Cloud console, you can view all organizations you have joined and switch between them. For details, see [Switch between organizations](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#view-and-switch-between-organizations).

* Add the [Slow Query](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#slow-query) page for SQL diagnosis.

    On the Slow Query page, you can search and view all slow queries in your TiDB cluster, and explore the bottlenecks of each slow query by viewing its [execution plan](https://docs.pingcap.com/tidbcloud/explain-overview), SQL execution information, and other details.

* When you reset the password for your account, TiDB Cloud will check your new password input against your last four passwords, and remind you to avoid using any of them. Any of the four used passwords will not be permitted.

    For details, see [Password Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-password-authentication).
## September 20, 2022

**General changes**

* Introduce the [cost quota-based invoice](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#invoices) for self-service users.

    TiDB Cloud will generate an invoice once your cost reaches a quota. To raise the quota or to receive invoices per month, contact [our sales](https://www.pingcap.com/contact-us/).

* Exempt the storage operation fee from the Data Backup Cost. See [TiDB Cloud Pricing Details](https://www.pingcap.com/tidb-cloud-pricing-details/) for the latest pricing information.

**Console changes**

* Provide a new web UI for data import. The new UI provides better user experience and makes data import more efficient.

    Using the new UI, you can preview the data to be imported, view the import process, and manage all import tasks easily.

**API changes**

* The TiDB Cloud API (beta) is now available to all users.

    You can start using the API by creating an API key in the TiDB Cloud console. For more information, refer to [API documentation](https://docs.pingcap.com/tidb/stable/tidb-cloud/api-overview).
## September 15, 2022

**General changes**

* Support connecting to TiDB Cloud [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters via TLS.

    For Dedicated Tier clusters, the **Standard Connection** tab in the [Connect](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection) dialog now provides a link to download the TiDB cluster CA and also provides the connection string and sample code for TLS connection. You can [connect to your Dedicated Tier cluster via TLS](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection) using third-party MySQL clients, MyCLI, and multiple connection methods for your applications, such as JDBC, Python, Go, and Node.js. This feature ensures the security of data transmission from your applications to TiDB clusters.
## September 14, 2022

**Console changes**

* Optimize the UI of the [Clusters](https://tidbcloud.com/project/clusters) page and the cluster overview page for better user experience.

    In the new design, the entrances of upgrade to Dedicated Tier, cluster connection, and data import are highlighted.

* Introduce Playground for [Developer Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    Playground contains a pre-loaded dataset of GitHub events, which allows you to get started with TiDB Cloud by running queries instantly, without importing your data or connecting to a client.
## September 13, 2022

**General changes**

* Support a new Google Cloud region for [Dedicated Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters: `N. Virginia (us-east4)`.
