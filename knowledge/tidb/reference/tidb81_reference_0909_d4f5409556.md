# Architecture, HA, migration, backup, HTAP, and security FAQs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-faq.md`
- Source Title: `TiDB Cloud FAQs`
- Source Heading Path: `TiDB Cloud FAQs > Architecture FAQs | TiDB Cloud FAQs > Architecture FAQs > There are different components in my TiDB cluster. What are TiDB, TiKV, and TiFlash nodes? | TiDB Cloud FAQs > Architecture FAQs > How does TiDB replicate data between the TiKV nodes? | TiDB Cloud FAQs > High availability FAQ | TiDB Cloud FAQs > High availability FAQ > How does TiDB Cloud ensure high availability? | TiDB Cloud FAQs > Migration FAQ | TiDB Cloud FAQs > Migration FAQ > Is there an easy migration path from another RDBMS to TiDB Cloud? | TiDB Cloud FAQs > Backup and restore FAQ | TiDB Cloud FAQs > Backup and restore FAQ > Does TiDB Cloud support incremental backups? | TiDB Cloud FAQs > HTAP FAQs | TiDB Cloud FAQs > HTAP FAQs > How do I make use of TiDB Cloud's HTAP capabilities? | TiDB Cloud FAQs > HTAP FAQs > Can I import my data directly to TiFlash? | TiDB Cloud FAQs > HTAP FAQs > Can I export TiFlash data in the CSV format? | TiDB Cloud FAQs > Security FAQs | TiDB Cloud FAQs > Security FAQs > Is TiDB Cloud secure? | TiDB Cloud FAQs > Security FAQs > How does TiDB Cloud encrypt my business data? | TiDB Cloud FAQs > Security FAQs > What versions of TLS does TiDB Cloud support? | TiDB Cloud FAQs > Security FAQs > Can I run TiDB Cloud in my VPC?`
- Source Line Ranges: `73-153`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`, `pd`, `sql`
- Topic Tags: `architecture`, `replication`, `raft`, `high-availability`, `migration`, `pitr`, `htap`, `tiflash`, `encryption`, `tls`, `vpc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0909_d4f5409556`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-faq.md#architecture-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1127ed958ded4e67aaf4ed8298c5a67d03e88467e2e4e7927bd3202dcc700902`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-faq#architecture-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering TiDB Cloud FAQ questions about cluster components and replication, high availability, MySQL-compatible migration, backup and PITR, HTAP and TiFlash behavior, encryption and TLS, or whether TiDB Cloud runs in a user's VPC.
- Retrieval Keywords: TiDB, TiKV, TiFlash, PD, Placement Driver, SQL computing layer, transactional store, analytical storage, real-time OLAP workloads, Region, Raft consensus algorithm, Raft Group, Raft log, high availability, automatic failover, Availability Zones, SOC 2 Type 1 compliance, migrate MySQL-compatible databases, Data Migration, incremental backups, PITR, Point-in-time Recovery, Dedicated cluster, Serverless cluster, HTAP, Hybrid Transactional Analytical Processing, OLTP, OLAP, import data directly to TiFlash, Create TiFlash Replicas, export TiFlash data in the CSV format, all data at rest is encrypted, Transport Layer Security (TLS), storage volume encryption, component-level TLS, TLS 1.2, TLS 1.3, TiDB Cloud VPC, DBaaS
- Follow-up Guidance: For more information, the content points to Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration, Use PITR in a TiDB Cloud Dedicated cluster, Use PITR in a TiDB Cloud Serverless cluster, Create TiFlash Replicas, and TiDB Cloud Support.
- Classification Note: This chunk is reference content because it consolidates official FAQ answers about architecture, replication, availability, migration, backup behavior, HTAP capabilities, and security properties in TiDB Cloud.

## Official Source Content

## Architecture FAQs
### There are different components in my TiDB cluster. What are TiDB, TiKV, and TiFlash nodes?

TiDB is the SQL computing layer that aggregates data from queries returned from TiKV or TiFlash stores. TiDB is horizontally scalable; increasing the number of TiDB nodes will increase the number of concurrent queries the cluster can handle.

TiKV is the transactional store used to store OLTP data. All the data in TiKV is automatically maintained in multiple replicas (three replicas by default), so TiKV has native high availability and supports automatic failover. TiKV is horizontally scalable; increasing the number of transactional stores will increase OLTP throughput.

TiFlash is the analytical storage that replicates data from the transactional store (TiKV) in real-time and supports real-time OLAP workloads. Unlike TiKV, TiFlash stores data in columns to accelerate analytical processing. TiFlash is also horizontally scalable; increasing TiFlash nodes will increase OLAP storage and computing capacity.

PD, the Placement Driver is "the brain" of the entire TiDB cluster, as it stores the metadata of the cluster. It sends data scheduling commands to specific TiKV nodes according to the data distribution state reported by TiKV nodes in real-time. On TiDB Cloud, PD of each cluster is managed by PingCAP and you can not see or maintain it.
### How does TiDB replicate data between the TiKV nodes?

TiKV divides the key-value space into key ranges, and each key range is treated as a "Region". In TiKV, data is distributed among all nodes in a cluster and uses the Region as the basic unit. PD is responsible for spreading (scheduling) Regions as evenly as possible across all nodes in a cluster.

TiDB uses the Raft consensus algorithm to replicate data by Regions. Multiple replicas of a Region stored in different nodes form a Raft Group.

Each data change is recorded as a Raft log. Through Raft log replication, data is safely and reliably replicated to multiple nodes of the Raft Group.
## High availability FAQ
### How does TiDB Cloud ensure high availability?

TiDB uses the Raft consensus algorithm to ensure that data is highly available and safely replicated throughout storage in Raft Groups. Data is redundantly copied between TiKV nodes and placed in different Availability Zones to protect against machine or data center failure. With automatic failover, TiDB ensures that your service is always on.

As a Software as a Service (SaaS) provider, we take data security seriously. We have established strict information security policies and procedures required by the [Service Organization Control (SOC) 2 Type 1 compliance](https://www.pingcap.com/press-release/pingcap-successfully-completes-soc-2-type-1-examination-for-tidb-cloud/). This ensures that your data is secure, available, and confidential.
## Migration FAQ
### Is there an easy migration path from another RDBMS to TiDB Cloud?

TiDB is highly compatible with MySQL. You can migrate data from any MySQL-compatible databases to TiDB smoothly, whether the data is from a self-hosted MySQL instance or RDS service provided by the public cloud. For more information, see [Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration).
## Backup and restore FAQ
### Does TiDB Cloud support incremental backups?

No. If you need to restore data to any point in time within the cluster's backup retention, you can use PITR (Point-in-time Recovery). For more information, see [Use PITR in a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-auto-backup) or [Use PITR in a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless#restore).
## HTAP FAQs
### How do I make use of TiDB Cloud's HTAP capabilities?

Traditionally, there are two types of databases: Online Transactional Processing (OLTP) databases and Online Analytical Processing (OLAP) databases. OLTP and OLAP requests are often processed in different and isolated databases. With this traditional architecture, migrating data from an OLTP database to a data warehouse or data lake for OLAP is a long and error-prone process.

As a Hybrid Transactional Analytical Processing (HTAP) database, TiDB Cloud helps you simplify your system architecture, reduce maintenance complexity, and support real-time analytics on transactional data by automatically replicating data reliably between the OLTP (TiKV) store and OLAP (TiFlash) store. Typical HTAP use cases are user personalization, AI recommendation, fraud detection, business intelligence, and real-time reporting.

For further HTAP scenarios, refer to [How We Build an HTAP Database That Simplifies Your Data Platform](https://pingcap.com/blog/how-we-build-an-htap-database-that-simplifies-your-data-platform).
### Can I import my data directly to TiFlash?

No. When you import data to TiDB Cloud, the data is imported to TiKV. After the import is complete, you can use SQL statements to specify which tables to be replicated to TiFlash. Then, TiDB will create the replicas of the specified tables in TiFlash accordingly. For more information, see [Create TiFlash Replicas](https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas).
### Can I export TiFlash data in the CSV format?

No. TiFlash data cannot be exported.
## Security FAQs
### Is TiDB Cloud secure?

In TiDB Cloud, all data at rest is encrypted, and all network traffic is encrypted using Transport Layer Security (TLS).

- Encryption of data at rest is automated using encrypted storage volumes.
- Encryption of data in transit between your client and your cluster is automated using TiDB Cloud web server TLS and TiDB cluster TLS.
### How does TiDB Cloud encrypt my business data?

TiDB Cloud uses storage volume encryption by default for your business data at rest, including your database data and backup data. TiDB Cloud requires TLS encryption for data in transit, and also requires component-level TLS encryption for data in your database cluster between TiDB, PD, TiKV, and TiFlash.

To get more specific information about business data encryption in TiDB Cloud, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
### What versions of TLS does TiDB Cloud support?

TiDB Cloud supports TLS 1.2 or TLS 1.3.
### Can I run TiDB Cloud in my VPC?

No. TiDB Cloud is Database-as-a-Service (DBaaS) and runs only in the TiDB Cloud VPC. As a cloud computing managed service, TiDB Cloud provides access to a database without requiring the setup of physical hardware and the installation of software.
