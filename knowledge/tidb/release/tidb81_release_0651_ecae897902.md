# TiDB Cloud 2025 release notes: Jan 21 to May 13 updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-release-notes.md`
- Source Title: `TiDB Cloud Release Notes in 2025`
- Source Heading Path: `TiDB Cloud Release Notes in 2025 > May 13, 2025 | TiDB Cloud Release Notes in 2025 > April 22, 2025 | TiDB Cloud Release Notes in 2025 > April 15, 2025 | TiDB Cloud Release Notes in 2025 > April 1, 2025 | TiDB Cloud Release Notes in 2025 > March 25, 2025 | TiDB Cloud Release Notes in 2025 > March 18, 2025 | TiDB Cloud Release Notes in 2025 > February 18, 2025 | TiDB Cloud Release Notes in 2025 > January 21, 2025`
- Source Line Ranges: `117-272`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `release-notes`, `serverless`, `dedicated`, `full-text-search`, `vector-search`, `node-groups`, `storage`, `maintenance-window`, `backup`, `data-import`, `data-export`, `firewall-rules`, `audit-logging`, `mfa`, `support-services`, `pricing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0651_ecae897902`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-release-notes.md#may-13-2025`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50ebe4f62289698b14d4b19da18d11a00a9cf8b7148091d2eadec33f547ad4ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-release-notes#may-13-2025
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-release-notes.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for TiDB Cloud release-note changes from January 21, 2025 to May 13, 2025 across Serverless or Dedicated features such as full-text search, TiDB Node Groups, storage, import/export, firewall rules, audit logging, MFA, maintenance window, backup, pricing, or support services.
- Retrieval Keywords: TiDB Cloud Release Notes in 2025, May 13, 2025, April 22, 2025, April 15, 2025, April 1, 2025, March 25, 2025, March 18, 2025, February 18, 2025, January 21, 2025, Full-text search (beta), TiDB Cloud Serverless, vector search, BM25, Full Text Search with SQL, Full Text Search with Python, TiFlash node storage, maintenance window, Backup Setting, Alibaba Cloud OSS, Export Data from TiDB Cloud Serverless, Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless, Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless, TiDB Node Groups, Manage TiDB Node Groups, Standard storage, Basic storage, Pricing, firewall rules for public endpoints, Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints, Database Audit Logging, Password Authentication, Connected Care, Connected Care Overview, Import Local Files to TiDB Cloud
- Follow-up Guidance: The content points to related documentation such as Full Text Search with SQL, Full Text Search with Python, Manage TiDB Node Groups, Configure maintenance window, backup and restore, import/export guides, firewall rules, Database Audit Logging, Password Authentication, Connected Care Overview, and Import Local Files to TiDB Cloud.
- Classification Note: This chunk is classified as a cloud release-note summary because the official content is organized by dated TiDB Cloud release entries covering general and console changes for Serverless and Dedicated.

## Official Source Content

## May 13, 2025

**General changes**

- Full-text search (beta) now available in [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) for AI applications.

    TiDB Cloud Serverless now supports full-text search (beta), enabling AI and Retrieval-Augmented Generation (RAG) applications to retrieve content by exact keywords. This complements vector search, which retrieves content by semantic similarity. Combining both methods significantly improves retrieval accuracy and answer quality in RAG workflows. Key features include:

    - Direct text search: query string columns directly without the need for embeddings.
    - Multilingual support: automatically detects and analyzes text in multiple languages, even within the same table, without requiring language specification.
    - Relevance-based ranking: results are ranked using the industry-standard BM25 algorithm for optimal relevance.
    - Native SQL compatibility: seamlessly use SQL features such as filtering, grouping, and joining with full-text search.

  To get started, see [Full Text Search with SQL](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-full-text-search-sql) or [Full Text Search with Python](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-full-text-search-python).

- Increase the maximum TiFlash node storage for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster:

    - For 8 vCPU TiFlash, from 2048 GiB to 4096 GiB
    - For 32 vCPU TiFlash, from 4096 GiB to 8192 GiB

  This enhancement increases the analytics data storage capacity of your TiDB Cloud Dedicated cluster, improves workload scaling efficiency, and accommodates growing data requirements.

    For more information, see [TiFlash node storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tiflash-node-storage).

- Enhance the maintenance window configuration experience by providing intuitive options to configure and reschedule maintenance tasks.

    For more information, see [Configure maintenance window](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-maintenance-window).

- Extend the discount period for TiKV [Standard](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#standard-storage) and [Performance](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#performance-and-plus-storage) storage types. The promotion now ends on June 5, 2025. After this date, pricing will return to the standard rate.

**Console changes**

- Refine the **Backup Setting** page layout to improve the backup configuration experience in [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters.

    For more information, see [Back Up and Restore TiDB Cloud Dedicated Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore).
## April 22, 2025

**General changes**

- Data export to Alibaba Cloud OSS is now supported. 

    [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters now support exporting data to [Alibaba Cloud Object Storage Service (OSS)](https://www.alibabacloud.com/en/product/object-storage-service) using an [AccessKey pair](https://www.alibabacloud.com/help/en/ram/user-guide/create-an-accesskey-pair).

    For more information, see [Export Data from TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export#alibaba-cloud-oss).
## April 15, 2025

**General changes**

- Support importing data from [Alibaba Cloud Object Storage Service (OSS)](https://www.alibabacloud.com/en/product/object-storage-service) into [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    This feature simplifies data migration to TiDB Cloud Serverless. You can use an AccessKey pair to authenticate.

    For more information, see the following documentation:

    - [Import CSV Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files-serverless)
    - [Import Apache Parquet Files from Amazon S3, GCS, Azure Blob Storage, or Alibaba Cloud OSS into TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files-serverless)
## April 1, 2025

**General changes**

- The [TiDB Node Groups](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-overview) feature is now generally available (GA) for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS and Google Cloud.

    This feature enables **fine-grained computing resource isolation** within a single cluster, helping you optimize performance and resource allocation for multi-tenant or multi-workload scenarios.

    **Key benefits:**

    - **Resource isolation**:

        - Group TiDB nodes into logically isolated units, ensuring workloads in one group do not affect other groups.
        - Prevent resource contention between applications or business units.

    - **Simplified management**:

        - Manage all node groups within a single cluster, reducing operational overhead.
        - Scale groups independently based on demand.

  For more information about the benefits, see [the technical blog](https://www.pingcap.com/blog/tidb-cloud-node-groups-scaling-workloads-predictable-performance/). To get started, see [Manage TiDB Node Groups](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-management).

- Introduce the [Standard storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#standard-storage) type for TiKV nodes in [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS.

    The Standard storage type is ideal for most workloads, providing a balance between performance and cost efficiency.

    **Key benefits:**

    - **Improved performance**: Reserves sufficient disk resources for Raft logs, reducing I/O contention between Raft and data storage, thereby improving both the read and write performance of TiKV.
    - **Enhanced stability**: Isolates critical Raft operations from data workloads, ensuring more predictable performance.
    - **Cost efficiency**: Delivers higher performance at a competitive price compared with the previous storage type.

    **Availability:**

    The Standard storage type is automatically applied to new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters created on or after April 1, 2025, hosted on AWS, with supported versions (versions >= 7.5.5, 8.1.2, or 8.5.0). Existing clusters still use the previous [Basic storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#basic-storage) type, and no migration is needed.

    The price of the Standard storage differs from that of the Basic storage. For more information, see [Pricing](https://www.pingcap.com/tidb-dedicated-pricing-details/).
## March 25, 2025

**Console changes**

- Support firewall rules for public endpoints in [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    You can now configure firewall rules for TiDB Cloud Serverless clusters to control access via public endpoints. Specify allowed IP addresses or ranges directly in the [TiDB Cloud console](https://tidbcloud.com/) to enhance security.

    For more information, see [Configure TiDB Cloud Serverless Firewall Rules for Public Endpoints](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-serverless-firewall-rules-for-public-endpoints).
## March 18, 2025

**General changes**

- Support creating TiDB node groups for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters deployed on Google Cloud to enhance resource management flexibility.

    For more information, see [Overview of TiDB Node Group](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-node-group-overview).

- Support storing database audit log files in TiDB Cloud for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters deployed on AWS.

    You can download these audit log files directly from TiDB Cloud. Note that this feature is only available upon request.

    For more information, see [Database Audit Logging](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing).

- Enhance TiDB Cloud account security by improving the management of multi-factor authentication (MFA). This feature applies to password-based logins for TiDB Cloud.

    For more information, see [Password Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-password-authentication).
## February 18, 2025

**Console changes**

- Introduce Connected Care, the new support services for TiDB Cloud.

    The Connected Care services are designed to strengthen your connection with TiDB Cloud through modern communication tools, proactive support, and advanced AI capabilities, delivering a seamless and customer-centric experience.

    The Connected Care services introduce the following features:

    - **Clinic service**: Advanced monitoring and diagnostics to optimize performance.
    - **AI chat in IM**: Get immediate AI assistance through an instant message (IM) tool.
    - **IM subscription for alerts and ticket updates**: Stay informed with alerts and ticket progress via IM.
    - **IM interaction for support tickets**: Create and interact with support tickets through an IM tool.

  For more information, see [Connected Care Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-overview).

- Support importing data from GCS and Azure Blob Storage into [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    TiDB Cloud Serverless now supports importing data from Google Cloud Storage (GCS) and Azure Blob Storage. You can use a Google Cloud service account key or an Azure shared access signature (SAS) token to authenticate. This feature simplifies data migration to TiDB Cloud Serverless.

    For more information, see [Import CSV Files from Amazon S3, GCS, or Azure Blob Storage into TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files-serverless) and [Import Apache Parquet Files from Amazon S3, GCS, or Azure Blob Storage into TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files-serverless).
## January 21, 2025

**Console changes**

- Support importing a single local CSV file of up to 250 MiB per task to [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters, increased from the previous limit of 50 MiB.

    For more information, see [Import Local Files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files).
