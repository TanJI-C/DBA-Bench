# Prepare new cluster with GC, full backup restore, and upgrade

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-upgrade-migration-guide.md`
- Source Title: `Migrate and Upgrade a TiDB Cluster`
- Source Heading Path: `Migrate and Upgrade a TiDB Cluster > Step 2: Prepare the new cluster | Migrate and Upgrade a TiDB Cluster > Step 2: Prepare the new cluster > 1. Adjust the GC lifetime of the old cluster | Migrate and Upgrade a TiDB Cluster > Step 2: Prepare the new cluster > 2. Migrate full data to the new cluster | Migrate and Upgrade a TiDB Cluster > Step 2: Prepare the new cluster > 3. Upgrade the new cluster to the target version`
- Source Line Ranges: `45-116`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tidb`, `tikv`, `tiup`, `shared`
- Topic Tags: `gc-lifetime`, `full-backup`, `full-restore`, `tso`, `offline-upgrade`, `system-tables`, `configuration-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0467_416c58c86d`
- Source ID: `tidb-docs-8.1:tidb-upgrade-migration-guide.md#step-2-prepare-the-new-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `907768db71b97e18737c9bb793f9c10fa01a9b2809c6995fa607d49de3eb0064`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-upgrade-migration-guide#step-2-prepare-the-new-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-upgrade-migration-guide.md

## Retrieval Guidance

- Use When: Use this chunk when preparing a new cluster for migration by adjusting GC retention, running BR full backup and restore, recording backup TSO, and performing an offline upgrade.
- Retrieval Keywords: Step 2: Prepare the new cluster, adjust the GC lifetime of the old cluster, tidb_gc_life_time, SHOW VARIABLES LIKE '%tidb_gc_life_time%', SET GLOBAL tidb_gc_life_time=60h, unrecoverable `failed` state, MVCC, Migrate full data to the new cluster, BR version used for backup and restore must match the major version of the old cluster, new_collations_enabled_on_first_bootstrap, BR restore will fail, --with-sys-table, tiup br:${cluster_version} backup full, validate decode --field="end-version", record the TSO, tiup cluster deploy, tiup br:${cluster_version} restore full, offline upgrade, tiup cluster stop, tiup cluster upgrade <new_cluster_name> <v_target_version> --offline, tiup cluster start, replicate essential configurations, system variables
- Follow-up Guidance: The source next uses the recorded backup TSO to create a TiCDC Changefeed and establish forward incremental replication from the old cluster to the new cluster.
- Classification Note: This is classified as an operation chunk because it gives procedural preparation steps for backup, restore, upgrade, and configuration continuity of the new cluster.

## Official Source Content

## Step 2: Prepare the new cluster
### 1. Adjust the GC lifetime of the old cluster

To ensure data replication stability, adjust the system variable [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) to a value that covers the total duration of the following operations and intervals: BR backup, BR restore, cluster upgrade, and TiCDC Changefeed replication setup. Otherwise, the replication task might enter an unrecoverable `failed` state, requiring a restart of the entire migration and upgrade process from a new full backup.

The following example sets `tidb_gc_life_time` to `60h`:

```sql
-- Check the current GC lifetime setting.
SHOW VARIABLES LIKE '%tidb_gc_life_time%';
-- Set GC lifetime.
SET GLOBAL tidb_gc_life_time=60h;
```

> **Note:**
>
> Increasing `tidb_gc_life_time` increases storage usage for [MVCC](https://docs.pingcap.com/tidb/stable/glossary#multi-version-concurrency-control-mvcc) data and might affect query performance. For more information, see [GC Overview](https://docs.pingcap.com/tidb/stable/garbage-collection-overview). Adjust the GC duration based on estimated operation time while considering storage and performance impacts.
### 2. Migrate full data to the new cluster

When migrating full data to the new cluster, note the following:

- **Version compatibility**: the BR version used for backup and restore must match the major version of the old cluster.
- **Performance impact**: BR backup consumes system resources. To minimize business impact, perform backups during off-peak hours.
- **Time estimation**: under optimal hardware conditions (no disk I/O or network bandwidth bottlenecks), estimated times are:

    - Backup speed: backing up 1 TiB of data per TiKV node with 8 threads takes approximately 1 hour.
    - Restore speed: restoring 1 TiB of data per TiKV node takes approximately 20 minutes.

- **Configuration consistency**: ensure that the [`new_collations_enabled_on_first_bootstrap`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap) configuration is identical between the old and new clusters. Otherwise, BR restore will fail.
- **System table restore**: Use the `--with-sys-table` option during BR restore to recover system table data.

To migrate full data to the new cluster, take the following steps:

1. Perform a full backup on the old cluster:

    ```shell
    tiup br:${cluster_version} backup full --pd ${pd_host}:${pd_port} -s ${backup_location}
    ```

2. Record the TSO of the old cluster for later TiCDC Changefeed creation:

    ```shell
    tiup br:${cluster_version} validate decode --field="end-version" \
    --storage "s3://xxx?access-key=${access-key}&secret-access-key=${secret-access-key}" | tail -n1
    ```

3. Deploy the new cluster:

    ```shell
    tiup cluster deploy ${new_cluster_name} ${cluster_version} tidb-cluster.yaml
    ```

4. Restore the full backup to the new cluster:

    ```shell
    tiup br:${cluster_version} restore full --pd ${pd_host}:${pd_port} -s ${backup_location} --with-sys-table
    ```
### 3. Upgrade the new cluster to the target version

To save time, you can perform an offline upgrade using the following commands. For more upgrade methods, see [Upgrade TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup).

```shell
tiup cluster stop <new_cluster_name>      # Stop the cluster
tiup cluster upgrade <new_cluster_name> <v_target_version> --offline  # Perform offline upgrade
tiup cluster start <new_cluster_name>     # Start the cluster
```

To maintain business continuity, you need to replicate essential configurations from the old cluster to the new cluster, such as configuration items and system variables.
