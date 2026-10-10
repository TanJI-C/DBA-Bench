# Overview, architecture, and prerequisites for Oracle to TiDB Cloud migration with AWS DMS

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-oracle-using-aws-dms.md`
- Source Title: `Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS`
- Source Heading Path: `Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Why use AWS DMS? | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Deployment architecture | Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS > Prerequisites`
- Source Line Ranges: `5-44`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `aws-dms`, `oracle`, `migration`, `architecture`, `prerequisites`, `serverless`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0081_06c35a4046`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-oracle-using-aws-dms.md#migrate-from-amazon-rds-for-oracle-to-tidb-cloud-using-aws-dms`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d8c94f84b3508d5684ad41ba4f40dafe0fb7b01c3b6c042fb151a18022abccae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-oracle-using-aws-dms#migrate-from-amazon-rds-for-oracle-to-tidb-cloud-using-aws-dms
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-oracle-using-aws-dms.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the high-level overview, deployment architecture, reasons to use AWS DMS, or prerequisites for migrating from Amazon RDS for Oracle to TiDB Cloud Serverless.
- Retrieval Keywords: Amazon RDS for Oracle, TiDB Cloud Serverless, AWS Database Migration Service, AWS DMS, Why use AWS DMS, Deployment architecture, Prerequisites, AWS DMS Prerequisites, AWS Cloud Account, TiDB Cloud Account, DBeaver, heterogeneous databases
- Follow-up Guidance: The next part explains the step-by-step procedure to set up the source Amazon RDS for Oracle, the target TiDB Cloud Serverless cluster, and the AWS DMS full load migration.
- Classification Note: This chunk is classified as architecture because it describes the migration scenario, high-level steps, and prerequisite components rather than detailed execution.

## Official Source Content

# Migrate from Amazon RDS for Oracle to TiDB Cloud Using AWS DMS

This document describes a step-by-step example of how to migrate data from Amazon RDS for Oracle to [TiDB Cloud Serverless](https://tidbcloud.com/clusters/create-cluster) using AWS Database Migration Service (AWS DMS).

If you are interested in learning more about TiDB Cloud and AWS DMS, see the following:

- [TiDB Cloud](https://docs.pingcap.com/tidbcloud/)
- [TiDB Developer Guide](https://docs.pingcap.com/tidbcloud/dev-guide-overview)
- [AWS DMS Documentation](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_GettingStarted.html)
## Why use AWS DMS?

AWS DMS is a cloud service that makes it possible to migrate relational databases, data warehouses, NoSQL databases, and other types of data stores.

If you want to migrate data from heterogeneous databases, such as PostgreSQL, Oracle, and SQL Server to TiDB Cloud, it is recommended to use AWS DMS.
## Deployment architecture

At a high level, follow the following steps:

1. Set up the source Amazon RDS for Oracle.
2. Set up the target [TiDB Cloud Serverless](https://tidbcloud.com/project/clusters/create-cluster).
3. Set up data migration (full load) using AWS DMS.

The following diagram illustrates the high-level architecture.

![Architecture](/media/tidb-cloud/aws-dms-from-oracle-to-tidb-0.png)
## Prerequisites

Read the following prerequisites before you get started:

- [AWS DMS Prerequisites](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-aws-dms#prerequisites)
- [AWS Cloud Account](https://aws.amazon.com)
- [TiDB Cloud Account](https://tidbcloud.com)
- [DBeaver](https://dbeaver.io/)

Next, you will learn how to use AWS DMS to migrate data from Amazon RDS for Oracle into TiDB Cloud.
