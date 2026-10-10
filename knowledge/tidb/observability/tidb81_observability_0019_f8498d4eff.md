# TiDB Dashboard daily check indicators

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/daily-check.md`
- Source Title: `Daily Check`
- Source Heading Path: `Daily Check | Daily Check > Key indicators of TiDB Dashboard | Daily Check > Key indicators of TiDB Dashboard > Instance panel | Daily Check > Key indicators of TiDB Dashboard > Host panel | Daily Check > Key indicators of TiDB Dashboard > SQL analysis panel | Daily Check > Key indicators of TiDB Dashboard > Region panel | Daily Check > Key indicators of TiDB Dashboard > KV Request Duration | Daily Check > Key indicators of TiDB Dashboard > PD TSO Wait Duration | Daily Check > Key indicators of TiDB Dashboard > Overview panel | Daily Check > Key indicators of TiDB Dashboard > Exceptions | Daily Check > Key indicators of TiDB Dashboard > GC status`
- Source Line Ranges: `5-84`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `tikv`, `sql`, `tiflash`
- Topic Tags: `daily-check`, `dashboard`, `monitoring`, `instance-status`, `host-resources`, `slow-sql`, `regions`, `kv-latency`, `tso-wait`, `overview`, `exceptions`, `gc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0019_f8498d4eff`
- Source ID: `tidb-docs-8.1:daily-check.md#daily-check`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85397e614939165e65078776024883acffed7770466723da6471432cd7b59de3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/daily-check#daily-check
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/daily-check.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Dashboard daily check indicators and what each panel or metric in Dashboard is used to observe in a TiDB cluster.
- Retrieval Keywords: TiDB Dashboard daily check indicators, Key indicators of TiDB Dashboard, Instance panel, Host panel, SQL analysis panel, Region panel, KV Request Duration, PD TSO Wait Duration, Overview panel, Exceptions, GC status, http://${pd-ip}:${pd_port}/dashboard, Up Time, Version, Deployment Directory, Git Hash, down-peer-region-count, empty-region-count, extra-peer-region-count, learner-peer-region-count, miss-peer-region-count, offline-peer-region-count, oversized-region-count, pending-peer-region-count, undersized-region-count, Region Merge, TRUNCATE TABLE, DROP TABLE, region-max-size, region-max-keys, max-merge-region-size, max-merge-region-keys, slow SQL statement, syntax error, primary key conflicts, last GC happens
- Follow-up Guidance: The content also names possible reasons for long PD TSO wait duration, including high network latency from TiDB to PD, high load for the TiDB server, and high load for the PD server.
- Classification Note: This chunk is classified as observability for the Dashboard component because it describes TiDB Dashboard panels and monitoring indicators for instance status, host resources, SQL, Regions, latency, exceptions, and GC.

## Official Source Content

# Daily Check

As a distributed database, TiDB is more complicated than the stand-alone database in terms of the mechanism, and monitoring items. To help operate and maintain TiDB in a more convenient way, this document introduces some key performance indicators.
## Key indicators of TiDB Dashboard

Starting from v4.0, TiDB provides a new operation and maintenance management tool, [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro). This tool is integrated into the PD component. You can access TiDB Dashboard at the default address `http://${pd-ip}:${pd_port}/dashboard`.

TiDB Dashboard simplifies the operation and maintenance of the TiDB database. You can view the running status of the entire TiDB cluster through one interface. The following are descriptions of some performance indicators.
### Instance panel

![Instance panel](/media/instance-status-panel.png)

+ **Status**: This indicator is used to check whether the status is normal. For an online node, this can be ignored.
+ **Up Time**: The key indicator. If you find that the `Up Time` is changed, you need to locate the reason why the component is restarted.
+ **Version**, **Deployment Directory**, **Git Hash**: These indicators need to be checked to avoid inconsistent or even incorrect version/deployment directory.
### Host panel

![Host panel](/media/host-panel.png)

You can view the usage of CPU, memory, and disk. When the usage of any resource exceeds 80%, it is recommended to scale out the capacity accordingly.
### SQL analysis panel

![SQL analysis panel](/media/sql-analysis-panel.png)

You can locate the slow SQL statement executed in the cluster. Then you can optimize the specific SQL statement.
### Region panel

![Region panel](/media/region-panel.png)

+ `down-peer-region-count`: The number of Regions with an unresponsive peer reported by the Raft leader.
+ `empty-region-count`: The number of empty Regions, with a size of smaller than 1 MiB. These Regions are generated by executing the `TRUNCATE TABLE`/`DROP TABLE` statement. If this number is large, you can consider enabling `Region Merge` to merge Regions across tables.
+ `extra-peer-region-count`: The number of Regions with extra replicas. These Regions are generated during the scheduling process.
+ `learner-peer-region-count`: The number of Regions with the learner peer. The sources of learner peers can be various, for example, the learner peers in TiFlash, and the learner peers included in the configured Placement Rules.
+ `miss-peer-region-count`: The number of Regions without enough replicas. This value is not always greater than `0`.
+ `offline-peer-region-count`: The number of Regions during the peer offline process.
+ `oversized-region-count`: The number of Regions with a size larger than `region-max-size` or `region-max-keys`.
+ `pending-peer-region-count`: The number of Regions with outdated Raft logs. It is normal that a few pending peers are generated in the scheduling process. However, it is not normal if this value is large for a period of time (longer than 30 minutes).
+ `undersized-region-count`: The number of Regions with a size smaller than `max-merge-region-size` or `max-merge-region-keys`.

Generally, it is normal for these metrics to show small and non-zero values.
### KV Request Duration

![TiKV request duration](/media/kv-duration-panel.png)

The KV request duration 99 in TiKV. If you find nodes with a long duration, check whether there are hot spots, or whether there are nodes with poor performance.
### PD TSO Wait Duration

![TiDB TSO Wait Duration](/media/pd-duration-panel.png)

The time it takes for TiDB to obtain TSO from PD. The following are reasons for the long wait duration:

+ High network latency from TiDB to PD. You can manually execute the ping command to test the network latency.
+ High load for the TiDB server.
+ High load for the PD server.
### Overview panel

![Overview panel](/media/overview-panel.png)

You can view the load, memory available, network traffic, and I/O utilities. When a bottleneck is found, it is recommended to scale out the capacity, or to optimize the cluster topology, SQL, and cluster parameters.
### Exceptions

![Exceptions](/media/failed-query-panel.png)

You can view the errors triggered by the execution of SQL statements on each TiDB instance. These include syntax error and primary key conflicts.
### GC status

![GC status](/media/garbage-collation-panel.png)

You can check whether the GC (Garbage Collection) status is normal by viewing the time when the last GC happens. If the GC is abnormal, it might lead to excessive historical data, thereby decreasing the access efficiency.
