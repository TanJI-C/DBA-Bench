# Offline dump and restore migration with Dumpling and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-mariadb.md`
- Source Title: `Migrate Data from MariaDB to TiDB`
- Source Heading Path: `Migrate Data from MariaDB to TiDB > Dump data with Dumpling and restore data with TiDB Lightning`
- Source Line Ranges: `255-280`
- Source Scope: `self_managed`
- Primary Component: `dumpling`
- Related Components: `lightning`, `tiup`, `tidb`
- Topic Tags: `offline-migration`, `dump`, `restore`, `downtime`, `user-migration`, `application-cutover`, `cleanup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0033_6859ed157f`
- Source ID: `tidb-docs-8.1:migrate-from-mariadb.md#dump-data-with-dumpling-and-restore-data-with-tidb-lightning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `39601abb17c8136a45236e329192f02788d52f97b415408f95c68fe6168bb8cf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-mariadb#dump-data-with-dumpling-and-restore-data-with-tidb-lightning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-mariadb.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented offline MariaDB-to-TiDB migration flow using Dumpling to export data and TiDB Lightning to restore it with application downtime.
- Retrieval Keywords: Dump data with Dumpling and restore data with TiDB Lightning, offline migration, take your application offline, tiup dumpling, tiup tidb-lightning, Get Started with TiDB Lightning, tiup dumpling --port 3306 --host 127.0.0.1 --user root --password secret -F 256MB -o /data/backup, migrate user accounts and permissions, Export users and grants, reconfigure your application, final backup of the data in MariaDB, remove tools such as TiUP Dumpling and TiDB Lightning
- Follow-up Guidance: The source says to migrate user accounts and permissions by using the Export users and grants section and to reconfigure the application to connect to the TiDB server after restoration.
- Classification Note: This is data pipeline content because it gives a step-by-step dump-and-restore migration procedure using Dumpling and TiDB Lightning, including operational sequencing and example commands.

## Official Source Content

## Dump data with Dumpling and restore data with TiDB Lightning

This method assumes that you take your application offline, migrate the data, and then re-configure your application to use the migrated data.

> **Note:**
>
> It is strongly recommended to first do this on a test or development instance of your application before doing it in production. This is both to check for possible compatibility issues as to get insight into how much time the migration will take.

Perform the following steps to migrate data from MariaDB to TiDB:

1. Stop your application. Take your application offline. This ensures there are no modifications made to the data in MariaDB during or after the migration.

2. Dump data in MariaDB with the [`tiup dumpling`](https://docs.pingcap.com/tidb/stable/dumpling-overview#use-dumpling-to-export-data) command.

    ```shell
    tiup dumpling --port 3306 --host 127.0.0.1 --user root --password secret -F 256MB  -o /data/backup
    ```

3. Restore the data by using the `tiup tidb-lightning` command. For more information about how to configure TiDB Lightning and how to run it, see [Get Started with TiDB Lightning](https://docs.pingcap.com/tidb/stable/get-started-with-tidb-lightning).

4. Migrate user accounts and permissions. For more information about how to migrate your users and permissions, see [Export users and grants](#export-users-and-grants).

5. Reconfigure your application. You need to change the application configuration so that it can connect to the TiDB server.

6. Clean up. Once you have verified that the migration is successful you can make a final backup of the data in MariaDB and stop the server. This also means you can remove tools such as TiUP, Dumpling, and TiDB Lightning.
