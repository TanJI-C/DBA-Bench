# TiDB Cloud release notes for 2021

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2021.md`
- Source Title: `TiDB Cloud Release Notes in 2021`
- Source Heading Path: `TiDB Cloud Release Notes in 2021 | TiDB Cloud Release Notes in 2021 > December 28, 2021 | TiDB Cloud Release Notes in 2021 > November 30, 2021 | TiDB Cloud Release Notes in 2021 > November 8, 2021 | TiDB Cloud Release Notes in 2021 > October 21, 2021 | TiDB Cloud Release Notes in 2021 > October 11, 2021 | TiDB Cloud Release Notes in 2021 > September 16, 2021 | TiDB Cloud Release Notes in 2021 > September 2, 2021 | TiDB Cloud Release Notes in 2021 > August 19, 2021 | TiDB Cloud Release Notes in 2021 > August 5, 2021 | TiDB Cloud Release Notes in 2021 > July 22, 2021 | TiDB Cloud Release Notes in 2021 > July 6, 2021 | TiDB Cloud Release Notes in 2021 > June 25, 2021 | TiDB Cloud Release Notes in 2021 > June 24, 2021 | TiDB Cloud Release Notes in 2021 > June 16, 2021 | TiDB Cloud Release Notes in 2021 > June 14, 2021 | TiDB Cloud Release Notes in 2021 > May 10, 2021`
- Source Line Ranges: `5-128`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `release-notes`, `feature-announcements`, `bug-fixes`, `version-upgrades`, `developer-tier`, `import`, `billing`, `organization-management`, `backup-restore`, `signup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0630_c42a2156ae`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2021.md#tidb-cloud-release-notes-in-2021`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd03bf49f23d1d73dafa024105e3de08f580a2a4f960cacf95a79a49ac1f0b19`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2021#tidb-cloud-release-notes-in-2021
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2021.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB Cloud 2021 release-note details about feature announcements, upgrades, bug fixes, billing, signup, import, backup and restore, or Developer Tier changes by date.
- Retrieval Keywords: TiDB Cloud Release Notes in 2021, December 28 2021 import Apache Parquet files from Amazon S3 or GCS into TiDB Cloud, importing more than 1000 files to TiDB Cloud, import data to existing tables that already have data, November 30 2021 TiDB v5.3.0 Developer Tier, adding VPC CIDR for your TiDB cloud project, Improve the monitoring ability for Developer Tier, auto backup time the same as the creation time of a Developer Tier cluster, TiKV crash issue due to full disk in Developer Tier, vulnerability of HTML injection, November 8 2021 Developer Tier one-year free trial, One TiDB shared node, One TiKV shared node, 500 MiB of OLTP storage, One TiFlash shared node, 500 MiB of OLAP storage, October 21 2021 importing or migrating from Amazon S3 or GCS to TiDB Cloud, October 11 2021 viewing and exporting billing details of TiDB Cloud, billing details cost of each service and each project, September 16 2021 upgrade the default TiDB version from 5.2.0 to 5.2.1, September 2 2021 upgrade the default TiDB version from 5.0.2 to 5.2.0, August 5 2021 organization role management, multiple projects within an organization, network and authority isolation, July 22 2021 adding credit cards, cluster recovered from backup cannot be charged normally, July 6 2021 upgrade the default TiDB version from 4.0.11 to 5.0.2, June 24 2021 parse errors of the parquet files when importing the Aurora snapshot, Estimated Hours not being updated, June 14 2021 mounting EBS error when importing the Aurora snapshot, May 10 2021 Public Preview, 48-Hour Free Trial, 2-Week PoC Free Trial, Preview On-Demand, Email verification and anti-robot reCAPTCHA, Data backup and restore features are available for PoC and on-demand trial options, Points calculator and points usage dashboard
- Follow-up Guidance: The page organizes changes by release date from May 10, 2021 through December 28, 2021 and points to linked TiDB Cloud or TiDB release-note pages for some items.
- Classification Note: This is a cloud release-notes summary page covering TiDB Cloud announcements, fixes, and version upgrades in 2021 across cloud, TiDB, TiKV, and TiFlash related topics.

## Official Source Content

# TiDB Cloud Release Notes in 2021

This page lists the release notes of [TiDB Cloud](https://www.pingcap.com/tidb-cloud/) in 2021.
## December 28, 2021

New feature:

* Support [importing Apache Parquet files from Amazon S3 or GCS into TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files)

Bug fixes:

* Fix the import error that occurs when importing more than 1000 files to TiDB Cloud
* Fix the issue that TiDB Cloud allows to import data to existing tables that already have data
## November 30, 2021

General change:

* Upgrade TiDB Cloud to [TiDB v5.3.0](https://docs.pingcap.com/tidb/stable/release-5.3.0) for Developer Tier

New feature:

* Support [adding VPC CIDR for your TiDB cloud project](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections)

Improvements:

* Improve the monitoring ability for Developer Tier
* Support setting the auto backup time the same as the creation time of a Developer Tier cluster

Bug fixes:

* Fix the TiKV crash issue due to full disk in Developer Tier
* Fix the vulnerability of HTML injection
## November 8, 2021

* Launch [Developer Tier](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless), which offers you a one-year free trial of TiDB Cloud

    Each Developer Tier cluster is a full-featured TiDB cluster and comes with the following:

    * One TiDB shared node
    * One TiKV shared node (with 500 MiB of OLTP storage)
    * One TiFlash shared node (with 500 MiB of OLAP storage)

  Get started [here](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart).
## October 21, 2021

* Open user registration to personal email accounts
* Support [importing or migrating from Amazon S3 or GCS to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files)
## October 11, 2021

* Support [viewing and exporting billing details of TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#billing-details), including the cost of each service and each project
* Fix several issues of TiDB Cloud internal features
## September 16, 2021

* Upgrade the default TiDB version from 5.2.0 to 5.2.1 for newly deployed clusters. See [5.2.1](https://docs.pingcap.com/tidb/stable/release-5.2.1) release notes for detailed changes in 5.2.1.
## September 2, 2021

* Upgrade the default TiDB version from 5.0.2 to 5.2.0 for newly deployed clusters. See [5.2.0](https://docs.pingcap.com/tidb/stable/release-5.2.0) and [5.1.0](https://docs.pingcap.com/tidb/stable/release-5.1.0) release notes for details of TiDB 5.1.0 and 5.2.0 features.
* Fix several issues of TiDB Cloud internal features.
## August 19, 2021

* Fix several issues of TiDB Cloud internal features. This release does not bring any user behavior changes.
## August 5, 2021

* Support organization role management. Organization owners can configure permissions of organization members as needed.
* Support the isolation of multiple projects within an organization. Organization owners can create and manage projects as needed, and the members and instances between projects support network and authority isolation.
* Optimize the bill to show the billing of each item in the current month and previous month.
## July 22, 2021

* Optimize the user experience of adding credit cards
* Strengthen the security management of credit cards
* Fix the issue that the cluster recovered from backup cannot be charged normally
## July 6, 2021

* Upgrade the default TiDB version from 4.0.11 to 5.0.2 for newly deployed clusters. The upgrade brings significant performance and functionality improvements. See [here](https://docs.pingcap.com/tidb/stable/release-5.0.0) for details.
## June 25, 2021

* Fix the **Select Region** not working issue on the [TiDB Cloud Pricing](https://www.pingcap.com/pricing/) page
## June 24, 2021

* Fix the parse errors of the parquet files when importing the Aurora snapshot into a TiDB instance
* Fix the Estimated Hours not being updated issue when PoC users create a cluster and change the cluster configuration
## June 16, 2021

* **China** is added to the **Country/Region** drop-down list when you sign up for an account
## June 14, 2021

* Fix the mounting EBS error when importing the Aurora snapshot into a TiDB instance
## May 10, 2021

General

* TiDB Cloud is now in Public Preview. You can [sign up](https://tidbcloud.com/signup) and select one of the trial options:

    * 48-Hour Free Trial
    * 2-Week PoC Free Trial
    * Preview On-Demand

Management Console

* Email verification and anti-robot reCAPTCHA have been added to the sign up process
* [TiDB Cloud Service Agreement](https://pingcap.com/legal/tidb-cloud-services-agreement) and [PingCAP Privacy Policy](https://pingcap.com/legal/privacy-policy/) have been updated
* You can apply for a [PoC](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-poc) by filling out an application form in the console
* You can import sample data into TiDB Cloud cluster through UI
* Clusters with the same name are not allowed to avoid confusion
* You can give feedback by clicking **Give Feedback** in the **Support** menu
* Data backup and restore features are available for PoC and on-demand trial options
* Points calculator and points usage dashboard have been added for Free Trial and PoC. Data storage and transfer costs are waived for all trial options
