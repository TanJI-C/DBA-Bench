# Migration prerequisites, binlog setup, and connectivity planning

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-data-migration.md`
- Source Title: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Make sure your data source and version are supported | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Enable binary logs in the source MySQL-compatible database for replication | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Enable binary logs in the source MySQL-compatible database for replication > Check current values and configure the source MySQL instance | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Ensure network connectivity`
- Source Line Ranges: `52-168`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`, `shared`
- Topic Tags: `prerequisites`, `supported-versions`, `binlog`, `mysql-configuration`, `network-connectivity`, `tls`, `private-endpoint`, `vpc-peering`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0243_4673011ff6`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-data-migration.md#prerequisites`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5e7af70de0649c441641fc98d300f916bca566c8cbabbab0f3cf360875156256`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#prerequisites
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when you need prerequisites for creating a TiDB Cloud Data Migration job, including supported MySQL source versions, required binlog settings, the SHOW VARIABLES check, and available network connectivity methods.
- Retrieval Keywords: Prerequisites, supported data sources and versions, Self-managed MySQL 8.0 5.7 5.6, Amazon Aurora MySQL 8.0 5.7 5.6, Amazon RDS MySQL 8.0 5.7, Azure Database for MySQL - Flexible Server 8.0 5.7, Google Cloud SQL for MySQL 8.0 5.7 5.6, log_bin, binlog_format, binlog_row_image, binlog_expire_logs_seconds, SHOW VARIABLES WHERE Variable_name IN, server_id, expire_logs_days, ROW, FULL, 604800, 86400, DM service, public endpoints or IP addresses, private links or private endpoints, VPC peering
- Follow-up Guidance: The content includes platform-specific configuration paths for self-managed MySQL, AWS RDS or Aurora MySQL, Azure Database for MySQL - Flexible Server, and Google Cloud SQL for MySQL, plus guidance to choose among public endpoints, private endpoints, or VPC peering.
- Classification Note: This is configuration content because it defines prerequisite source settings, SQL verification commands, supported versions, and network connectivity setup choices for Data Migration.

## Official Source Content

## Prerequisites

Before migrating, check whether your data source is supported, enable binary logging in your MySQL-compatible database, ensure network connectivity, and grant required privileges for both the source database and the target TiDB Cloud cluster database.
### Make sure your data source and version are supported

Data Migration supports the following data sources and versions:

| Data source | Supported versions |
|:------------|:-------------------|
| Self-managed MySQL (on-premises or public cloud) | 8.0, 5.7, 5.6 |
| Amazon Aurora MySQL | 8.0, 5.7, 5.6 |
| Amazon RDS MySQL | 8.0, 5.7 |
| Azure Database for MySQL - Flexible Server | 8.0, 5.7 |
| Google Cloud SQL for MySQL | 8.0, 5.7, 5.6 |
### Enable binary logs in the source MySQL-compatible database for replication

To continuously replicate incremental changes from the source MySQL-compatible database to the TiDB Cloud target cluster using DM, you need the following configurations to enable binary logs in the source database:

| Configuration | Required value | Why |
|:--------------|:---------------|:----|
| `log_bin` | `ON` | Enables binary logging, which DM uses to replicate changes to TiDB |
| `binlog_format` | `ROW` | Captures all data changes accurately (other formats miss edge cases) |
| `binlog_row_image` | `FULL` | Includes all column values in events for safe conflict resolution |
| `binlog_expire_logs_seconds` | ≥ `86400` (1 day), `604800` (7 days, recommended) | Ensures DM can access consecutive logs during migration |
#### Check current values and configure the source MySQL instance

To check the current configurations, connect to the source MySQL instance and execute the following statement:

```sql
SHOW VARIABLES WHERE Variable_name IN
('log_bin','server_id','binlog_format','binlog_row_image',
'binlog_expire_logs_seconds','expire_logs_days');
```

If necessary, change the source MySQL instance configurations to match the required values.

<details>
<summary> Configure a self‑managed MySQL instance </summary>

1. Open `/etc/my.cnf` and add the following:

    ```
    [mysqld]
    log_bin = mysql-bin
    binlog_format = ROW
    binlog_row_image = FULL
    binlog_expire_logs_seconds = 604800   # 7 days retention
    ```

2. Restart the MySQL service to apply the changes:

    ```
    sudo systemctl restart mysqld
    ```

3. Run the `SHOW VARIABLES` statement again to verify that the settings take effect.

For detailed instructions, see [MySQL Server System Variables](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html) and [The Binary Log](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html) in MySQL documentation.

</details>

<details>
<summary> Configure AWS RDS or Aurora MySQL </summary>

1. In the AWS Management Console, open the [Amazon RDS console](https://console.aws.amazon.com/rds/), click **Parameter groups** in the left navigation pane, and then create or edit a custom parameter group.
2. Set the four parameters above to the required values.
3. Attach the parameter group to your instance or cluster, and then reboot to apply the changes.
4. After the reboot, connect to the instance and run the `SHOW VARIABLES` statement to verify the configuration.

For detailed instructions, see [Working with DB Parameter Groups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.html) and [Configuring MySQL Binary Logging](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.MySQL.BinaryFormat.html) in AWS documentation.

</details>

<details>
<summary> Configure Azure Database for MySQL - Flexible Server </summary>

1. In the [Azure portal](https://portal.azure.com/), search for and select **Azure Database for MySQL servers**, click your instance name, and then click **Setting** > **Server parameters** in the left navigation pane.

2. Search for each parameter and update its value.

    Most changes take effect without a restart. If a restart is required, you will get a prompt from the portal.

3. Run the `SHOW VARIABLES` statement to verify the configuration.

For detailed instructions, see [Configure server parameters in Azure Database for MySQL - Flexible Server using the Azure portal](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/how-to-configure-server-parameters-portal) in the Microsoft Azure documentation.

</details>

<details>
<summary> Configure Google Cloud SQL for MySQL </summary>

1. In the [Google Cloud console](https://console.cloud.google.com/project/_/sql/instances), select the project that contains your instance, click your instance name, and then click **Edit**.
2. Add or modify the required flags (`log_bin`, `binlog_format`, `binlog_row_image`, `binlog_expire_logs_seconds`).
3. Click **Save**. If a restart is required, you will get a prompt from the console.
4. After the restart, run the `SHOW VARIABLES` statement to confirm the changes.

For detailed instructions, see [Configure database flags](https://cloud.google.com/sql/docs/mysql/flags) and [Use point-in-time recovery](https://cloud.google.com/sql/docs/mysql/backup-recovery/pitr) in Google Cloud documentation.

</details>
### Ensure network connectivity

Before creating a migration job, you need to plan and set up proper network connectivity between your source MySQL instance, the TiDB Cloud Data Migration (DM) service, and your target TiDB Cloud cluster.

The available connection methods are as follows:

| Connection method | Availability | Recommended for |
|:---------------------|:-------------|:----------------|
| Public endpoints or IP addresses | All cloud providers supported by TiDB Cloud | Quick proof-of-concept migrations, testing, or when private connectivity is unavailable |
| Private links or private endpoints | AWS and Azure only | Production workloads without exposing data to the public internet |
| VPC peering | AWS and Google Cloud only | Production workloads that need low-latency, intra-region connections and have non-overlapping VPC/VNet CIDRs |

Choose a connection method that best fits your cloud provider, network topology, and security requirements, and then follow the setup instructions for that method.
