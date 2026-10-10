# DM replication migration workflow from MariaDB to TiDB

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-mariadb.md`
- Source Title: `Migrate Data from MariaDB to TiDB`
- Source Heading Path: `Migrate Data from MariaDB to TiDB > Replicate data with DM | Migrate Data from MariaDB to TiDB > Replicate data with DM > Step 1. Prepare | Migrate Data from MariaDB to TiDB > Replicate data with DM > Step 2. Replicate data | Migrate Data from MariaDB to TiDB > Replicate data with DM > Step 3. Migrate user accounts and permissions | Migrate Data from MariaDB to TiDB > Replicate data with DM > Step 4. Test your data | Migrate Data from MariaDB to TiDB > Replicate data with DM > Step 5. Switch over | Migrate Data from MariaDB to TiDB > Replicate data with DM > Step 6. Clean up`
- Source Line Ranges: `281-332`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `operator`, `tidb`
- Topic Tags: `replication`, `binlog`, `precheck`, `switchover`, `cleanup`, `user-migration`, `validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0034_393f6a8649`
- Source ID: `tidb-docs-8.1:migrate-from-mariadb.md#replicate-data-with-dm`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c88ea22842db4cd7b14fbf0c04da2999802375b7ed0ff37916970ede70aee121`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-mariadb#replicate-data-with-dm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-mariadb.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the end-to-end DM workflow for migrating data from MariaDB to TiDB, including preparation, replication, switchover, and cleanup details.
- Retrieval Keywords: DM, Data Migration, MariaDB to TiDB, TiUP cluster, TiDB Operator, dmctl, binlogs, binlog_format, ROW, binlog_annotate_row_events=OFF, log_bin_compress=OFF, SUPER, BINLOG MONITOR, REPLICATION MASTER ADMIN, ignore-checking-items, replication_privilege, Migration Task Precheck, Quick Start Guide for TiDB Data Migration, query-status <taskname>, synced: true, subTaskStatus, replication delay, switch over, stop and remove the DM cluster
- Follow-up Guidance: The source also points to exporting users and grants, testing replicated data with read-only queries, checking replication delay with `query-status <taskname>`, and cleaning up the MariaDB server and DM cluster after verification.
- Classification Note: This is classified as a self-managed DM data pipeline workflow because the content describes deploying DM with TiUP or TiDB Operator and using `dmctl` to replicate data from MariaDB to TiDB.

## Official Source Content

## Replicate data with DM

This method assumes you would set up replication, stop your application and wait for the replication to catch up, and then re-configure your application to use TiDB.

To use DM, you need to deploy a set of DM services either with a [TiUP cluster](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup) or with [TiDB Operator](https://docs.pingcap.com/tidb/stable/tidb-operator-overview). After that, use `dmctl` to configure the DM services.

> **Note:**
>
> It is strongly recommended to first do this on a test or development instance of your application before doing it in production. This is both to check for possible compatibility issues as to get insight into how much time the migration will take.
### Step 1. Prepare

Make sure that binlogs are enabled on MariaDB and that the `binlog_format` is set to `ROW`. It is also recommended to set `binlog_annotate_row_events=OFF` and `log_bin_compress=OFF`.

You also need an account with the `SUPER` permission or with the `BINLOG MONITOR` and `REPLICATION MASTER ADMIN` permissions. This account also needs read permission for the schemas you are going to migrate.

If you are not using an account with the `SUPER` permission, then you might have to add the following to the DM configuration, because TiDB does not yet know how to check for MariaDB specific permissions.

```yaml
ignore-checking-items: ["replication_privilege"]
```

Before you use DM to migrate data from upstream to downstream, a precheck helps detect errors in the upstream database configurations and ensures that the migration goes smoothly. For more information, see [Migration Task Precheck](https://docs.pingcap.com/tidb/stable/dm/dm-precheck)
### Step 2. Replicate data

Follow the [Quick Start Guide for TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/quick-start-with-dm) to replicate your data from MariaDB to TiDB.

Note that it is not required to first copy the initial data as you would do with MariaDB to MariaDB replication, DM will do this for you.
### Step 3. Migrate user accounts and permissions

See [Export users and grants](#export-users-and-grants) for how to migrate your users and permissions.
### Step 4. Test your data

Once your data is replicated, you can run read-only queries on it to validate it. For more information, see [Test your application](#test-your-application).
### Step 5. Switch over

To switch over to TiDB, you need to do the following:

1. Stop your application.
2. Monitor the replication delay, which should go to 0 seconds.
3. Change the configuration of your application so that it connects to TiDB and start it again.

To check for replication delay, run [`query-status <taskname>`](https://docs.pingcap.com/tidb/stable/dm/dm-query-status#detailed-query-result) via `dmctl` and check for `"synced: true"` in the `subTaskStatus`.
### Step 6. Clean up

Once you have verified that the migration is successful, you can make a final backup of the data in MariaDB and stop the server. It also means you can stop and remove the DM cluster.
