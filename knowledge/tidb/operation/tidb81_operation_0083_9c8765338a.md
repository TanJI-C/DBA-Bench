# Pre-migration compatibility and deployment planning

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-best-practices.md`
- Source Title: `TiDB Data Migration (DM) Best Practices`
- Source Heading Path: `TiDB Data Migration (DM) Best Practices > Before data migration > Other restrictions and impact > Data types in upstream and downstream | TiDB Data Migration (DM) Best Practices > Before data migration > Other restrictions and impact > Character sets and collations | TiDB Data Migration (DM) Best Practices > Before data migration > Best practices for deployment | TiDB Data Migration (DM) Best Practices > Before data migration > Best practices for deployment > Deploy DM-master and DM-worker | TiDB Data Migration (DM) Best Practices > Before data migration > Best practices for deployment > Plan the migration tasks | TiDB Data Migration (DM) Best Practices > Before data migration > Best practices for deployment > Choose and configure the upstream data source`
- Source Line Ranges: `107-165`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `data-types`, `character-sets`, `collations`, `deployment-planning`, `high-availability`, `task-splitting`, `full-migration`, `gtid`, `backup-source`, `read-locks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0083_9c8765338a`
- Source ID: `tidb-docs-8.1:dm/dm-best-practices.md#data-types-in-upstream-and-downstream`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7d3ff17a0fdae66a367d4f263307a5637ad11fecce06742212006f9d2830d73a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-best-practices#data-types-in-upstream-and-downstream
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when planning DM migration compatibility, deployment size, task splitting, or upstream full-backup behavior before migrating data to TiDB.
- Retrieval Keywords: SPATIAL, Data Types, new_collations_enabled_on_first_bootstrap, utf8_general_ci, utf8mb4_general_ci, utf8_unicode_ci, utf8mb4_unicode_ci, gbk_chinese_ci, gbk_bin, utf8mb4, GBK, DM-master, DM-worker, high availability, split the migration task, final consistency, real-time consistency, FLUSH TABLES WITH READ LOCK, enable-gtid: true, consistency, mydumpers.global.extra-args: "--consistency none", backup database, Amazon Aurora, AWS MySQL RDS, RDS snapshots
- Follow-up Guidance: The source also points to switching the upstream MySQL data source through Switch DM-worker Connection between Upstream MySQL Instances and to Aurora snapshot migration guidance.
- Classification Note: This is classified as operation content because it covers pre-migration restrictions, deployment planning, migration task design, and upstream backup considerations for DM.

## Official Source Content

#### Data types in upstream and downstream

TiDB supports most MySQL data types. However, some special types are not supported yet (such as `SPATIAL`). For the compatibility of data types, see [Data Types](https://docs.pingcap.com/tidb/stable/data-type-overview).
#### Character sets and collations

Since TiDB v6.0.0, the new framework for collations is used by default. In earlier versions, if you want TiDB to support utf8_general_ci, utf8mb4_general_ci, utf8_unicode_ci, utf8mb4_unicode_ci, gbk_chinese_ci and gbk_bin, you need to explicitly declare it when creating the cluster by setting the value of `new_collations_enabled_on_first_bootstrap` to `true`. For more information, see [New framework for collations](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations).

The default character set in TiDB is utf8mb4. It is recommended that you use utf8mb4 for the upstream and downstream databases and applications. If the upstream database has explicitly specified a character set or collation, you need to check whether TiDB supports it.

Since TiDB v6.0.0, GBK is supported. For more information, see the following documents:

- [Character Set and Collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation)
- [GBK compatibility](https://docs.pingcap.com/tidb/stable/character-set-gbk#mysql-compatibility)
### Best practices for deployment
#### Deploy DM-master and DM-worker

DM consists of DM-master and DM-worker nodes.

- DM-master manages the metadata of migration tasks and schedules DM-worker nodes. It is the core of the whole DM platform. Therefore, you can deploy DM-master as clusters to ensure high availability of the DM platform.

- DM-worker executes upstream and downstream migration tasks. A DM-worker node is stateless. You can deploy at most 1000 DM-worker nodes. When using DM, it is recommended that you reserve some idle DM-workers to ensure high availability.
#### Plan the migration tasks

When migrating and merging MySQL shards, you can split a migration task according to the types of shards in the upstream. For example, if `usertable_1~50` and `Logtable_1~50` are two types of shards, you can create two migration tasks. It can simplify the migration task template and effectively control the impact of interruption in data migration.

For migration of large datasets, you can refer to the following suggestions to split the migration task:

- If you need to migrate multiple databases in the upstream, you can split the migration task according to the number of databases.

- Split the task according to the write pressure in the upstream, that is, split the tables with frequent DML operations in the upstream to a separate migration task. Use another migration task to migrate the tables without frequent DML operations. This method can speed up the migration progress, especially when there are a large number of logs written to a table in the upstream. But if this table that contains a large number of logs does not affect the whole business, this method still works well.

Note that splitting the migration task can only guarantee the final consistency of data. Real-time consistency may deviate significantly due to various reasons.

The following table describes the recommended deployment plans for DM-master and DM-worker in different scenarios.

| Scenario | DM-master deployment | DM-worker deployment |
| :--- | :--- | :--- |
| <li>Small dataset (less than 1 TiB)</li><li>One-time data migration</li> | Deploy 1 DM-master node | Deploy 1~N DM-worker nodes according to the number of upstream data sources. Generally, 1 DM-worker node is recommended. |
| <li>Large dataset (more than 1 TiB) and migrating and merging MySQL shards</li><li>One-time data migration</li> | It is recommended to deploy 3 DM-master nodes to ensure the availability of the DM cluster during long-time data migration. | Deploy DM-worker nodes according to the number of data sources or migration tasks. Besides working DM-worker nodes, it is recommended to deploy 1~3 idle DM-worker nodes. |
| Long-term data replication | It is necessary to deploy 3 DM-master nodes. If you deploy DM-master nodes on the cloud, try to deploy them in different availability zones (AZ). | Deploy DM-worker nodes according to the number of data sources or migration tasks. It is necessary to deploy 1.5~2 times the number of DM-worker nodes that are actually needed. |
#### Choose and configure the upstream data source

DM backs up the full data of the entire database when performing full data migration, and uses the parallel logical backup method. During backing up MySQL, it adds a global read lock [`FLUSH TABLES WITH READ LOCK`](https://dev.mysql.com/doc/refman/8.0/en/flush.html#flush-tables-with-read-lock). DML and DDL operations of the upstream database will be blocked for a short time. Therefore, it is strongly recommended to use a backup database in upstream to perform the full data backup, and enable the GTID function of the data source (`enable-gtid: true`). In this way, you can avoid the impact from the upstream, and switch to the master node in the upstream to reduce the latency during the incremental migration. For the instructions of switching the upstream MySQL data source, see [Switch DM-worker Connection between Upstream MySQL Instances](https://docs.pingcap.com/tidb/stable/dm/usage-scenario-master-slave-switch#switch-dm-worker-connection-via-virtual-ip).

Note the following:

- You can only perform full data backup on the master node of the upstream database.

    In this scenario, you can set the `consistency` parameter to `none` in the configuration file, `mydumpers.global.extra-args: "--consistency none"`, to avoid adding a global read lock to the master node. But this might affect the data consistency of the full backup, which may lead to inconsistent data between the upstream and downstream.

- Use backup snapshots to perform full data migration (only applicable to the migration of MySQL RDS and Aurora RDS on AWS)

    If the database to be migrated is AWS MySQL RDS or Aurora RDS, you can use RDS snapshots to directly migrate the backup data in Amazon S3 to TiDB to ensure data consistency. For more information, see [Migrate Data from Amazon Aurora to TiDB](https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb).
