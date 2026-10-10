# Create cluster, adapt schema and SQL, and import data

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-poc.md`
- Source Title: `Perform a Proof of Concept (PoC) with TiDB Cloud`
- Source Heading Path: `Perform a Proof of Concept (PoC) with TiDB Cloud > Step 3. Sign up and create a TiDB Cloud Dedicated cluster for the PoC | Perform a Proof of Concept (PoC) with TiDB Cloud > Step 4. Adapt your schemas and SQL | Perform a Proof of Concept (PoC) with TiDB Cloud > Step 5. Import data`
- Source Line Ranges: `59-137`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`, `dm`, `lightning`, `sql`
- Topic Tags: `poc`, `cluster-creation`, `credits`, `capacity-planning`, `scaling`, `backup`, `timezone`, `schema-adaptation`, `sql-compatibility`, `hotspot-avoidance`, `data-import`, `migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0420_3a1c3405c9`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-poc.md#step-3-sign-up-and-create-a-tidb-cloud-dedicated-cluster-for-the-poc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5876d1311f00a82d9ed3e56f6369acaa71df40b94bda097718c19aa2c118c272`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-poc#step-3-sign-up-and-create-a-tidb-cloud-dedicated-cluster-for-the-poc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-poc.md

## Retrieval Guidance

- Use When: Use this chunk when you need official PoC guidance for creating a TiDB Cloud Dedicated cluster, planning capacity, adapting schemas and SQL for compatibility, and choosing data import methods.
- Retrieval Keywords: Step 3. Sign up and create a TiDB Cloud Dedicated cluster for the PoC, Apply for PoC, Contact Sales, TiDB Cloud Dedicated, Create a TiDB Cloud Dedicated Cluster, payment methods, PoC credits, Size Your TiDB, Scale Your TiDB Cluster, Connect to Your TiDB Cloud Dedicated Cluster, Create Time, UTC, Set the Local Time Zone, full database backup on a daily basis, Step 4. Adapt your schemas and SQL, TiDB Cloud Serverless cluster, MySQL 8.0, TiDB compatibility with MySQL, features that are different from MySQL, TiDB's Keywords and Reserved Words, TiDB Limitations, hotspot issues, Right-Hand-Side Index Growth, SHARD_ROW_ID_BITS, AUTO_RANDOM, Step 5. Import data, Data Migration, Import Local Files to TiDB Cloud, Import sample data, Import CSV Files from Cloud Storage, Import Apache Parquet Files, Import page does not generate additional billing fees
- Follow-up Guidance: The source also points to related documents for sizing, scaling, connecting to the cluster, backup settings, MySQL compatibility, and multiple data import paths including Data Migration, local files, SQL sample data, CSV, and Apache Parquet.
- Classification Note: This chunk is classified as an operation topic because the official content covers procedural PoC tasks for cluster creation, configuration awareness, schema and SQL adaptation, and data import in TiDB Cloud.

## Official Source Content

## Step 3. Sign up and create a TiDB Cloud Dedicated cluster for the PoC

To create a [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster for the PoC, take the following steps:

1. Fill in the PoC application form by doing one of the following:

    - On the PingCAP website, go to the [Apply for PoC](https://pingcap.com/apply-for-poc/) page to fill in the application form.
    - In the [TiDB Cloud console](https://tidbcloud.com/), click **?** in the lower-right corner, click **Contact Sales**, and then select **Apply for PoC** to fill in the application form.

    Once you submit the form, the TiDB Cloud Support team will review your application, contact you, and transfer credits to your account once the application is approved. You can also contact a PingCAP support engineer to assist with your PoC procedures to ensure the PoC runs as smoothly as possible.

2. Refer to [Create a TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster) to create a TiDB Cloud Dedicated cluster for the PoC.

   > **Note:**
   >
   > Before creating a TiDB Cloud Dedicated cluster, you must add one of the following payment methods:
   >  - Add a credit card by following the on-screen instructions on the cluster creation page.
   >  - Contact the TiDB Cloud Support team to pay by wire transfer.
   >  - Sign up for TiDB Cloud through a cloud marketplace (AWS, Azure, or Google Cloud) to pay using your cloud provider account.
   >
   > Your PoC credits will automatically be used to offset eligible expenses incurred during the PoC period.

Capacity planning is recommended for cluster sizing before you create a cluster. You can start with estimated numbers of TiDB, TiKV, or TiFlash nodes, and scale out the cluster later to meet performance requirements. You can find more details in the following documents or consult our support team.

- For more information about estimation practice, see [Size Your TiDB](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster).
- For configurations of the TiDB Cloud Dedicated cluster, see [Create a TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster). Configure the cluster size for TiDB, TiKV, and TiFlash (optional) respectively.
- For how to plan and optimize your PoC credits consumption effectively, see [FAQ](#faq) in this document.
- For more information about scaling, see [Scale Your TiDB Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster).

Once a dedicated PoC cluster is created, you are ready to load data and perform a series of tests. For how to connect to a TiDB cluster, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster).

For a newly created cluster, note the following configurations:

- The default time zone (the **Create Time** column on the Dashboard) is UTC. You can change it to your local time zone by following [Set the Local Time Zone](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#set-the-time-zone-for-your-organization).
- The default backup setting on a new cluster is full database backup on a daily basis. You can specify a preferred backup time or back up data manually. For the default backup time and more details, see [Back up and Restore TiDB Cluster Data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-auto-backup).
## Step 4. Adapt your schemas and SQL

Next, you can load your database schemas to the TiDB cluster, including tables and indexes.

Because the amount of PoC credits is limited, to maximize the value of credits, it is recommended that you create a [TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) for compatibility tests and preliminary analysis on TiDB Cloud.

TiDB Cloud is highly compatible with MySQL 8.0. You can directly import your data into TiDB if it is MySQL-compatible or can be adapted to be compatible with MySQL.

For more information about compatibilities, see the following documents:

- [TiDB compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility).
- [TiDB features that are different from MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility#features-that-are-different-from-mysql).
- [TiDB's Keywords and Reserved Words](https://docs.pingcap.com/tidb/stable/keywords).
- [TiDB Limitations](https://docs.pingcap.com/tidb/stable/tidb-limitations).

Here are some best practices:

- Check whether there are inefficiencies in schema setup.
- Remove unnecessary indexes.
- Plan the partitioning policy for effective partitioning.
- Avoid [hotspot issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#identify-hotspot-issues) caused by Right-Hand-Side Index Growth, for example, indexes on the timestamp.
- Avoid [hotspot issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#identify-hotspot-issues) by using [SHARD_ROW_ID_BITS](https://docs.pingcap.com/tidb/stable/shard-row-id-bits) and [AUTO_RANDOM](https://docs.pingcap.com/tidb/stable/auto-random).

For SQL statements, you might need to adapt them depending on the level of your data source's compatibility with TiDB.

If you have any questions, contact [PingCAP](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for consultation.
## Step 5. Import data

You can import a small dataset to quickly test feasibility, or a large dataset to test the throughput of TiDB data migration tools. Although TiDB provides sample data, it is strongly recommended to perform a test with real workloads from your business.

You can import data in various formats to TiDB Cloud:

- [Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration)
- [Import Local Files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-import-local-files)
- [Import sample data in the SQL file format](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data)
- [Import CSV Files from Cloud Storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files)
- [Import Apache Parquet Files](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files)

> **Note:**
>
> Data import on the **Import** page does not generate additional billing fees.
