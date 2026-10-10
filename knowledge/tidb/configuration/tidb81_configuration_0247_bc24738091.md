# GTID prerequisites for source databases

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md`
- Source Title: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > For Amazon RDS and Amazon Aurora MySQL | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > For Google Cloud SQL for MySQL | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > For Azure Database for MySQL | Migrate Only Incremental Data from MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > For a self-hosted MySQL instance`
- Source Line Ranges: `37-122`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `prerequisites`, `gtid`, `rds`, `aurora`, `cloud-sql`, `azure-mysql`, `self-hosted-mysql`, `binlog-row-image`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0247_bc24738091`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md#prerequisites`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e13e5001e57da18e779ad247cbc62a60890fcc54a22256a40946b10cce04576`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration#prerequisites
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-incremental-data-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs prerequisite configuration details to use GTID as the incremental migration start position for Amazon RDS, Amazon Aurora MySQL, Google Cloud SQL for MySQL, Azure Database for MySQL, or a self-hosted MySQL instance.
- Retrieval Keywords: GTID prerequisites, SHOW VARIABLES LIKE 'gtid_mode', gtid_mode, enforce_gtid_consistency, Amazon RDS, Amazon Aurora MySQL, Google Cloud SQL for MySQL, Azure Database for MySQL, binlog_row_image, SHOW VARIABLES LIKE 'binlog_row_image', FULL, SET GLOBAL gtid_mode = ON, SET GLOBAL enforce_gtid_consistency = ON, RESET MASTER, self-hosted MySQL instance
- Follow-up Guidance: For a self-hosted MySQL instance, the document includes SQL statements to enable GTID mode, restart the MySQL server, and verify the setting with SHOW VARIABLES LIKE 'gtid_mode'.
- Classification Note: This is configuration content because it provides prerequisite parameter names, SQL checks, and platform-specific GTID setup details required before using a GTID start position.

## Official Source Content

## Prerequisites

> **Note**:
>
> This section only includes prerequisites about incremental data migration. It is recommended that you also read the [general prerequisites](https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#prerequisites).

If you want to use GTID to specify the start position, make sure that the GTID is enabled in the source database. The operations vary depending on the database type.
### For Amazon RDS and Amazon Aurora MySQL

For Amazon RDS and Amazon Aurora MySQL, you need to create a new modifiable parameter group (that is, not the default parameter group) and then modify the following parameters in the parameter group and restart the instance application.

- `gtid_mode`
- `enforce_gtid_consistency`

You can check if the GTID mode has been successfully enabled by executing the following SQL statement:

```sql
SHOW VARIABLES LIKE 'gtid_mode';
```

If the result is `ON` or `ON_PERMISSIVE`, the GTID mode is successfully enabled.

For more information, see [Parameters for GTID-based replication](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/mysql-replication-gtid.html#mysql-replication-gtid.parameters).
### For Google Cloud SQL for MySQL

The GTID mode is enabled for Google Cloud SQL for MySQL by default. You can check if the GTID mode has been successfully enabled by executing the following SQL statement:

```sql
SHOW VARIABLES LIKE 'gtid_mode';
```

If the result is `ON` or `ON_PERMISSIVE`, the GTID mode is successfully enabled.
### For Azure Database for MySQL

The GTID mode is enabled by default for Azure Database for MySQL (versions 5.7 and later). You can check if the GTID mode has been successfully enabled by executing the following SQL statement:

```sql
SHOW VARIABLES LIKE 'gtid_mode';
```

If the result is `ON` or `ON_PERMISSIVE`, the GTID mode is successfully enabled.

In addition, ensure that the `binlog_row_image` server parameter is set to `FULL`. You can check this by executing the following SQL statement:

```sql
SHOW VARIABLES LIKE 'binlog_row_image';
```

If the result is not `FULL`, you need to configure this parameter for your Azure Database for MySQL instance using the [Azure portal](https://portal.azure.com/) or [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/).
### For a self-hosted MySQL instance

> **Note**:
>
> The exact steps and commands might vary depending on the MySQL version and configuration. Make sure that you understand the impact of enabling GTID and that you have properly tested and verified it in a non-production environment before performing this action.

To enable the GTID mode for a self-hosted MySQL instance, follow these steps:

1. Connect to the MySQL server using a MySQL client with the appropriate privileges.

2. Execute the following SQL statements to enable the GTID mode:

    ```sql
    -- Enable the GTID mode
    SET GLOBAL gtid_mode = ON;

    -- Enable `enforce_gtid_consistency`
    SET GLOBAL enforce_gtid_consistency = ON;

    -- Reload the GTID configuration
    RESET MASTER;
    ```

3. Restart the MySQL server to ensure that the configuration changes take effect.

4. Check if the GTID mode has been successfully enabled by executing the following SQL statement:

    ```sql
    SHOW VARIABLES LIKE 'gtid_mode';
    ```

    If the result is `ON` or `ON_PERMISSIVE`, the GTID mode is successfully enabled.
