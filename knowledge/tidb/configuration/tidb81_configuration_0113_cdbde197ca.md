# GC configuration variables, I/O limit, and version-specific behavior

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/garbage-collection-configuration.md`
- Source Title: `Garbage Collection Configuration`
- Source Heading Path: `Garbage Collection Configuration | Garbage Collection Configuration > GC I/O limit | Garbage Collection Configuration > Changes in TiDB 5.0 | Garbage Collection Configuration > Changes in TiDB 6.1.0 | Garbage Collection Configuration > Changes in TiDB 6.1.0 > GC in Compaction Filter`
- Source Line Ranges: `5-121`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `sql`, `shared`
- Topic Tags: `garbage-collection`, `system-variables`, `io-limit`, `distributed-gc`, `safe-point`, `active-transactions`, `compaction-filter`, `dynamic-configuration`, `version-changes`, `deprecation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0113_cdbde197ca`
- Source ID: `tidb-docs-8.1:garbage-collection-configuration.md#garbage-collection-configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d634da30ac7708aac4cde8695bb8d716fb939c55d85e8fb2b3fcd1c2ec7be1f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/garbage-collection-configuration#garbage-collection-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/garbage-collection-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB garbage collection configuration variables, TiKV GC I/O limiting, or version-specific GC behavior such as distributed GC, GC safe point blocking by active transactions, and GC in Compaction Filter.
- Retrieval Keywords: tidb_gc_enable, tidb_gc_run_interval, tidb_gc_life_time, tidb_gc_concurrency, tidb_gc_scan_lock_mode, tidb_gc_max_wait_time, GC I/O limit, gc.max-write-bytes-per-sec, tikv-ctl modify-tikv-config, mysql.tidb system table, CENTRAL garbage collection mode, DISTRIBUTED GC mode, GC safe point, active transactions block the GC safe point, GC in Compaction Filter, gc.enable-compaction-filter, show config where type = 'tikv' and name like '%enable-compaction-filter%', set config tikv gc.enable-compaction-filter = true, Resolve Locks, compaction process of RocksDB, next(), prev(), processed_keys, region-compact-min-redundant-rows, region-compact-redundant-rows-percent, gc.auto-compaction.redundant-rows-threshold, gc.auto-compaction.redundant-rows-percent-threshold
- Follow-up Guidance: The content also provides exact SQL and tikv-ctl examples for viewing or modifying gc.enable-compaction-filter and gc.max-write-bytes-per-sec, plus version-specific notes for TiDB 5.0, 6.1.0, 7.1.3 to 7.5.6, and 7.5.7 onward.
- Classification Note: This chunk is classified as configuration for TiKV in self-managed deployments because it centers on GC-related system variables and TiKV configuration items, including dynamic configuration commands and deployment-specific notes.

## Official Source Content

# Garbage Collection Configuration

You can configure garbage collection (GC) using the following system variables:

* [`tidb_gc_enable`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_enable-new-in-v50): controls whether to enable garbage collection for TiKV.
* [`tidb_gc_run_interval`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_run_interval-new-in-v50): specifies the GC interval.
* [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50): specifies the time limit during which data is retained for each GC.
* [`tidb_gc_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_concurrency-new-in-v50): specifies the number of threads in the [Resolve Locks](https://docs.pingcap.com/tidb/stable/garbage-collection-overview#resolve-locks) step of GC.
* [`tidb_gc_scan_lock_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_scan_lock_mode-new-in-v50): specifies the way of scanning locks in the Resolve Locks step of GC.
* [`tidb_gc_max_wait_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_max_wait_time-new-in-v610): specifies the maximum time that active transactions block the GC safe point.

For more information about how to modify the value of a system variable, see [System variables](https://docs.pingcap.com/tidb/stable/system-variables).
## GC I/O limit

> **Note:**
>
> This section is only applicable to TiDB Self-Managed. TiDB Cloud does not have a GC I/O limit by default.

TiKV supports the GC I/O limit. You can configure `gc.max-write-bytes-per-sec` to limit writes of a GC worker per second, and thus to reduce the impact on normal requests.

`0` indicates disabling this feature.

You can dynamically modify this configuration using tikv-ctl:

```bash
tikv-ctl --host=ip:port modify-tikv-config -n gc.max-write-bytes-per-sec -v 10MB
```
## Changes in TiDB 5.0

In previous releases of TiDB, garbage collection was configured via the `mysql.tidb` system table. While changes to this table continue to be supported, it is recommended to use the system variables provided. This helps ensure that any changes to configuration can be validated, and prevent unexpected behavior ([#20655](https://github.com/pingcap/tidb/issues/20655)).

The `CENTRAL` garbage collection mode is no longer supported. The `DISTRIBUTED` GC mode (which has been the default since TiDB 3.0) will automatically be used in its place. This mode is more efficient, since TiDB no longer needs to send requests to each TiKV region to trigger garbage collection.

For information on changes in previous releases, refer to earlier versions of this document using the _TIDB version selector_ in the left hand menu.
## Changes in TiDB 6.1.0

Before TiDB v6.1.0, the transaction in TiDB does not affect the GC safe point. Starting from v6.1.0, TiDB considers the startTS of the transaction when calculating the GC safe point, to resolve the problem that the data to be accessed has been cleared. If the transaction is too long, the safe point will be blocked for a long time, which affects the application performance.

In TiDB v6.1.0, the system variable [`tidb_gc_max_wait_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_max_wait_time-new-in-v610) is introduced to control the maximum time that active transactions block the GC safe point. After the value is exceeded, the GC safe point is forwarded forcefully.
### GC in Compaction Filter

Based on the `DISTRIBUTED` GC mode, the mechanism of GC in Compaction Filter uses the compaction process of RocksDB, instead of a separate GC worker thread, to run GC. This new GC mechanism helps to avoid extra disk read caused by GC. Also, after clearing the obsolete data, it avoids a large number of left tombstone marks which degrade the sequential scan performance.

> **Note:**
>
> The following examples of modifying TiKV configurations are only applicable to TiDB Self-Managed. For TiDB Cloud, the mechanism of GC in Compaction Filter is enabled by default.

The following example shows how to enable the mechanism in the TiKV configuration file:

```toml
[gc]
enable-compaction-filter = true
```

You can also enable this GC mechanism by modifying the configuration dynamically. See the following example:

```sql
show config where type = 'tikv' and name like '%enable-compaction-filter%';
```

```sql
+------+-------------------+-----------------------------+-------+
| Type | Instance          | Name                        | Value |
+------+-------------------+-----------------------------+-------+
| tikv | 172.16.5.37:20163 | gc.enable-compaction-filter | false |
| tikv | 172.16.5.36:20163 | gc.enable-compaction-filter | false |
| tikv | 172.16.5.35:20163 | gc.enable-compaction-filter | false |
+------+-------------------+-----------------------------+-------+
```

```sql
set config tikv gc.enable-compaction-filter = true;
show config where type = 'tikv' and name like '%enable-compaction-filter%';
```

```sql
+------+-------------------+-----------------------------+-------+
| Type | Instance          | Name                        | Value |
+------+-------------------+-----------------------------+-------+
| tikv | 172.16.5.37:20163 | gc.enable-compaction-filter | true  |
| tikv | 172.16.5.36:20163 | gc.enable-compaction-filter | true  |
| tikv | 172.16.5.35:20163 | gc.enable-compaction-filter | true  |
+------+-------------------+-----------------------------+-------+
```

> **Note:**
>
> When using the Compaction Filter mechanism, GC progress might be delayed, which can affect TiKV scan performance. If your workload contains a large number of coprocessor requests and you observe in the [**TiKV-Details > Coprocessor Detail**](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#coprocessor-detail) panel that the `next()` or `prev()` call count in **Total Ops Details** significantly exceeds three times the `processed_keys` calls, you can take the following actions:
> 
> - For TiDB versions before v7.1.3, it is recommended to disable Compaction Filter to speed up GC.
> - For TiDB versions from v7.1.3 to v7.5.6, TiDB automatically triggers compaction based on the number of redundant versions in each Region [`region-compact-min-redundant-rows`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-min-redundant-rows-new-in-v710) and the percentage of redundant versions [`region-compact-redundant-rows-percent`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-redundant-rows-percent-new-in-v710) to improve Compaction Filter GC performance. In this case, adjust these configuration items instead of disabling Compaction Filter.
> - Starting from v7.5.7, [`region-compact-min-redundant-rows`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-min-redundant-rows-new-in-v710) and [`region-compact-redundant-rows-percent`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-compact-redundant-rows-percent-new-in-v710) are deprecated. TiDB now automatically triggers compaction based on [`gc.auto-compaction.redundant-rows-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#redundant-rows-threshold-new-in-v757) and [`gc.auto-compaction.redundant-rows-percent-threshold`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#redundant-rows-percent-threshold-new-in-v757). In this case, adjust these configuration items instead of disabling Compaction Filter.
