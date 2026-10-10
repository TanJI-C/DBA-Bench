# TiDB Cloud release notes for late July 2022

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2022.md`
- Source Title: `TiDB Cloud Release Notes in 2022`
- Source Heading Path: `TiDB Cloud Release Notes in 2022 > July 28, 2022 | TiDB Cloud Release Notes in 2022 > July 26, 2022 | TiDB Cloud Release Notes in 2022 > July 19, 2022 | TiDB Cloud Release Notes in 2022 > July 12, 2022`
- Source Line Ranges: `438-472`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dumpling`, `tikv`
- Topic Tags: `release-notes`, `security-settings`, `developer-tier`, `hibernation`, `resume`, `username-prefix`, `backup-restore`, `storage-limit`, `import-filters`, `console-navigation`, `node-size`, `connection-code`, `validation`, `billing-profile`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0634_d2f7e3e30a`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2022.md#july-28-2022`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `915f726e4667035355be151127a61c2a8631b241876d61ffcd3f5a3593e2edcc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2022#july-28-2022
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2022.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud release-note entries from July 2022 about Developer Tier hibernation and resume, user name prefix, backup and restore disablement, security settings, data import validation, TiKV node size options, or billing profile updates.
- Retrieval Keywords: July 28 2022, July 26 2022, July 19 2022, July 12 2022, Allow Access from Anywhere, Security Quick Start, Configure Cluster Security Settings, automatic hibernation, resuming, Developer Tier clusters, 24 hours of inactivity, Resume button, within 50 seconds, user name prefix, backup and restore feature, Dumpling, storage size 1 GiB, breadcrumbs, multiple filter rules, Traffic Filters page, Add Rules from Default Set, TiKV node size, 8 vCPU, 32 GiB, 8 vCPU, 64 GiB, Connect to TiDB, syntax highlighting, Data Import Task, Validate button, Amazon S3, data access issues, Billing Profile, Payment Method, tax registration number
- Follow-up Guidance: The source references related documentation for Configure Cluster Security Settings, user name prefix, Dumpling overview, Connect via standard connection, Data Import Task, and billing profile information.
- Classification Note: This is a TiDB Cloud release-notes chunk about cloud console and service behavior changes in late July 2022, with several items specific to Developer Tier clusters and data import workflows.

## Official Source Content

## July 28, 2022

* Add the **Allow Access from Anywhere** button to the **Security Quick Start** dialog, which allows your cluster to be accessible by any IP addresses. For more information, see [Configure Cluster Security Settings](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-security-settings).
## July 26, 2022

* Support automatic hibernation and resuming for new [Developer Tier clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless).

    A Developer Tier cluster will not be deleted after 7 days of inactivity so you can still use it at any time until the one-year free trial ends. After 24 hours of inactivity, the Developer Tier cluster will hibernate automatically. To resume the cluster, either send a new connection to the cluster or click the **Resume** button in the TiDB Cloud console. The cluster will be resumed within 50 seconds and back to service automatically.

* Add a user name prefix limitation for new [Developer Tier clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless).

    Whenever you use or set a database user name, you must include the prefix for your cluster in the user name. For more information, see [User name prefix](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#user-name-prefix).

* Disable the backup and restore feature for [Developer Tier clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless).

    The backup and restore feature (including both automatic backup and manual backup) is disabled for Developer Tier clusters. You can still use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) to export your data as a backup.

* Increase the storage size of a [Developer Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster from 500 MiB to 1 GiB.
* Add breadcrumbs to the TiDB Cloud console to improve the navigation experience.
* Support configuring multiple filter rules when you import data into TiDB Cloud.
* Remove the **Traffic Filters** page from **Project Settings**, and remove the **Add Rules from Default Set** button from the **Connect to TiDB** dialog.
## July 19, 2022

* Provide a new option for [TiKV node size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tikv-vcpu-and-ram): `8 vCPU, 32 GiB`. You can choose either `8 vCPU, 32 GiB` or `8 vCPU, 64 GiB` for an 8 vCPU TiKV node.
* Support syntax highlighting in sample code provided in the [**Connect to TiDB**](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection) dialog to improve code readability. You can easily identify the parameters that you need to replace in the sample code.
* Support automatically validating whether TiDB Cloud can access your source data after you confirm the import task on the [**Data Import Task**](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data) page.
* Change the theme color of the TiDB Cloud console to make it consistent with that of [PingCAP website](https://www.pingcap.com/).
## July 12, 2022

* Add the **Validate** button to the [**Data Import Task**](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data) page for Amazon S3, which helps you detect data access issues before the data import starts.
* Add **Billing Profile** under the [**Payment Method**](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#payment-method) tab. By providing your tax registration number in **Billing Profile**, certain taxes might be exempted from your invoice. For more information, see [Edit billing profile information](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#billing-profile).
