# AWS DMS migration overview, prerequisites, and limitations

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-aws-dms.md`
- Source Title: `Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS`
- Source Heading Path: `Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS | Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS > Prerequisites | Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS > Limitation`
- Source Line Ranges: `5-33`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `tidb`
- Topic Tags: `aws dms`, `migration`, `prerequisites`, `limitations`, `binlog`, `collation`, `network access`, `vpc peering`, `private endpoint`, `system databases`, `schema migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0096_d1f91f415f`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-aws-dms.md#migrate-from-mysql-compatible-databases-to-tidb-cloud-using-aws-dms`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `de816427bc4c307586ede594948e7973d71927ca849d57eeb20fc3170e5361ea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-aws-dms#migrate-from-mysql-compatible-databases-to-tidb-cloud-using-aws-dms
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-aws-dms.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving prerequisites, compatibility limits, and migration constraints for using AWS DMS to migrate MySQL-compatible databases to TiDB Cloud.
- Retrieval Keywords: AWS DMS, TiDB Cloud Dedicated cluster, Amazon RDS, Amazon Aurora, self-hosted MySQL, binlog_format, ROW, MIXED, parameter group, newset, utf8mb4_bin, utf8mb4_0900_ai_ci, Character Set and Collation, INFORMATION_SCHEMA, PERFORMANCE_SCHEMA, mysql, sys, test, filter out system databases, migration object %, IP access lists, VPC Peerings, Private Endpoint connections, dms.t3.large, OOM, awsdms_control, DROP TABLE, secondary indexes, foreign keys, user accounts, basic schema migration
- Follow-up Guidance: The source notes that AWS DMS automatically creates the `awsdms_control` database in the target database and does not support replicating `DROP TABLE` or automatically creating secondary indexes, foreign keys, or user accounts in TiDB Cloud.
- Classification Note: This chunk is classified as data_pipeline because it describes migration prerequisites, source and target compatibility requirements, and AWS DMS limitations for moving data into TiDB Cloud.

## Official Source Content

# Migrate from MySQL-Compatible Databases to TiDB Cloud Using AWS DMS

If you want to migrate heterogeneous databases, such as PostgreSQL, Oracle, and SQL Server to TiDB Cloud, it is recommended to use AWS Database Migration Service (AWS DMS).

AWS DMS is a cloud service that makes it easy to migrate relational databases, data warehouses, NoSQL databases, and other types of data stores. You can use AWS DMS to migrate your data into TiDB Cloud.

This document uses Amazon RDS as an example to show how to migrate data to TiDB Cloud using AWS DMS. The procedure also applies to migrating data from self-hosted MySQL databases or Amazon Aurora to TiDB Cloud.

In this example, the data source is Amazon RDS, and the data destination is a TiDB Cloud Dedicated cluster in TiDB Cloud. Both upstream and downstream databases are in the same region.
## Prerequisites

Before you start the migration, make sure you have read the following:

- If the source database is Amazon RDS or Amazon Aurora, you need to set the `binlog_format` parameter to `ROW`. If the database uses the default parameter group, the `binlog_format` parameter is `MIXED` by default and cannot be modified. In this case, you need to [create a new parameter group](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_GettingStarted.Prerequisites.html#CHAP_GettingStarted.Prerequisites.params), for example `newset`, and set its `binlog_format` to `ROW`. Then, [modify the default parameter group](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithDBInstanceParamGroups.html#USER_WorkingWithParamGroups.Modifying) to `newset`. Note that modifying the parameter group will restart the database.
- Check and ensure that the source database uses collations that are compatible with TiDB. The default collation for the utf8mb4 character set in TiDB is `utf8mb4_bin`. But in MySQL 8.0, the default collation is `utf8mb4_0900_ai_ci`. If the upstream MySQL uses the default collation, because TiDB is not compatible with `utf8mb4_0900_ai_ci`, AWS DMS cannot create the target tables in TiDB and cannot migrate the data. To resolve this problem, you need to modify the collation of the source database to `utf8mb4_bin` before the migration. For a complete list of TiDB supported character sets and collations, see [Character Set and Collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation).
- TiDB contains the following system databases by default: `INFORMATION_SCHEMA`, `PERFORMANCE_SCHEMA`, `mysql`, `sys`, and `test`. When you create an AWS DMS migration task, you need to filter out these system databases instead of using the default `%` to select the migration object. Otherwise, AWS DMS will try to migrate these system databases from the source database to the target TiDB, which will cause the task to fail. To avoid this issue, it is recommended to fill in the specific database and table names.
- Add the public and private network IP addresses of AWS DMS to the IP access lists of both source and target databases. Otherwise, the network connection might fail in some scenarios.
- Use [VPC Peerings](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#set-up-vpc-peering-on-aws) or [Private Endpoint connections](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections) to connect AWS DMS and the TiDB cluster.
- It is recommended to use the same region for AWS DMS and the TiDB cluster to get better data writing performance.
- It is recommended to use AWS DMS `dms.t3.large` (2 vCPUs and 8 GiB memory) or a higher instance class. Small instance classes will possibly cause out of memory (OOM) errors.
- AWS DMS will automatically create the `awsdms_control` database in the target database.
## Limitation

- AWS DMS does not support replicating `DROP TABLE`.
- AWS DMS supports basic schema migration, including the creation of tables and primary keys. However, AWS DMS does not automatically create secondary indexes, foreign keys, or user accounts in TiDB Cloud. You must manually create these objects in TiDB, including tables with secondary indexes, if needed. For more information, see [Migration planning for AWS Database Migration Service](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html#CHAP_SettingUp.MigrationPlanning).
