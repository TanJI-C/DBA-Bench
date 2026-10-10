# TiDB 7.3.0 release overview and feature details

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.3.0.md`
- Source Title: `TiDB 7.3.0 Release Notes`
- Source Heading Path: `TiDB 7.3.0 Release Notes | TiDB 7.3.0 Release Notes > Feature details | TiDB 7.3.0 Release Notes > Feature details > Performance | TiDB 7.3.0 Release Notes > Feature details > Reliability | TiDB 7.3.0 Release Notes > Feature details > SQL`
- Source Line Ranges: `5-115`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `lightning`, `sql`
- Topic Tags: `release-notes`, `feature-overview`, `performance`, `reliability`, `sql`, `optimizer-hints`, `runaway-queries`, `tiflash`, `mpp`, `runtime-filter`, `cte`, `partitioning`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0495_cf6cdf3b6d`
- Source ID: `tidb-docs-8.1:releases/release-7.3.0.md#tidb-7-3-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3818ad8326fe6bf205ca83ff5e06b7c537141cac688b63414a8d722ec2cf515`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.3.0#tidb-7-3-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.3.0 release-note content about major features and feature details such as TiDB Lightning conflict detection, QUERY WATCH runaway query management, new optimizer hints, SHOW ANALYZE STATUS, TiFlash replica selection, Runtime Filter, CTE execution in MPP, and default partitions for List or List COLUMNS partitioned tables.
- Retrieval Keywords: TiDB 7.3.0 Release Notes, 7.3.0, Partitioned Raft KV, TiDB Lightning, Physical Import Mode, conflict detection, replace, ignore, QUERY WATCH, runaway queries, SQL Digest, plan digest, NO_INDEX_JOIN(), NO_MERGE_JOIN(), NO_INDEX_MERGE_JOIN(), NO_HASH_JOIN(), NO_INDEX_HASH_JOIN(), SHOW ANALYZE STATUS, mysql.analyze_jobs, TiFlash, tiflash_replica_read, replica selection strategy, zone attributes, MPP, Runtime Filter, tidb_runtime_filter_mode, LOCAL, common table expressions, CTEs, tidb_opt_force_inline_cte, tidb_opt_enable_mpp_shared_cte_execution, List partitioned tables, List COLUMNS partitioned tables, default partition
- Follow-up Guidance: The content points to related documentation for QUERY WATCH parameters, optimizer hints, runtime filter, system variables, partitioned tables, and SHOW ANALYZE STATUS.
- Classification Note: This is a self-managed release-notes overview chunk covering shared TiDB 7.3.0 feature announcements and detailed enhancements across TiDB server, TiFlash, Lightning, SQL, performance, reliability, and observability.

## Official Source Content

# TiDB 7.3.0 Release Notes

Release date: August 14, 2023

TiDB version: 7.3.0

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.3/quick-start-with-tidb)

7.3.0 introduces the following major features. In addition to that, 7.3.0 also includes a series of enhancements (described in the [Feature details](#feature-details) section) to query stability in TiDB server and TiFlash. These enhancements are more miscellaneous in nature and not user-facing so they are not included in the following table.

<table>
<thead>
  <tr>
    <th>Category</th>
    <th>Feature</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Scalability and Performance</td>
    <td>TiDB Lightning supports <a href="https://docs.pingcap.com/tidb/v7.3/partitioned-raft-kv">Partitioned Raft KV</a> (experimental)</td>
    <td>TiDB Lightning now supports the new Partitioned Raft KV architecture, as part of the near-term GA of the architecture.
    </td>
  </tr>
  <tr>
    <td rowspan="2">Reliability and Availability</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.3/tidb-lightning-physical-import-mode-usage#conflict-detection">Add automatic conflict detection and resolution on data imports</a></td>
    <td>The TiDB Lightning Physical Import Mode supports a new version of conflict detection, which implements the semantics of replacing (<code>replace</code>) or ignoring (<code>ignore</code>) conflict data when encountering conflicts. It automatically handles conflict data for you while improving the performance of conflict resolution.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.3/tidb-resource-control#query-watch-parameters">Manual management of runaway queries </a>(experimental)</td>
    <td>Queries might take longer than you expect. With the new watch list of resource groups, you can now manage queries more effectively and either deprioritize or kill them. Allowing operators to mark target queries by exact SQL text, SQL digest, or plan digest and deal with the queries at a resource group level, this feature gives you much more control over the potential impact of unexpected large queries on a cluster.</td>
  </tr>
  <tr>
    <td>SQL</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.3/optimizer-hints">Enhance operator control over query stability by adding more optimizer hints to the query planner</a></td>
    <td>Added hints: <code>NO_INDEX_JOIN()</code>, <code>NO_MERGE_JOIN()</code>, <code>NO_INDEX_MERGE_JOIN()</code>, <code>NO_HASH_JOIN()</code>, <code>NO_INDEX_HASH_JOIN()</code>
    </td>
  </tr>
  <tr>
    <td>DB Operations and Observability</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.3/sql-statement-show-analyze-status">Show the progress of statistics collection tasks</a></td>
    <td>Support viewing the progress of <code>ANALYZE</code> tasks using the <code>SHOW ANALYZE STATUS</code> statement or through the <code>mysql.analyze_jobs</code> system table.</td>
  </tr>
</tbody>
</table>
## Feature details
### Performance

* TiFlash supports the replica selection strategy [#44106](https://github.com/pingcap/tidb/issues/44106) @[XuHuaiyu](https://github.com/XuHuaiyu)

    Before v7.3.0, TiFlash uses replicas from all its nodes for data scanning and MPP calculations to maximize performance. Starting from v7.3.0, TiFlash introduces the replica selection strategy and lets you configure it using the [`tiflash_replica_read`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_replica_read-new-in-v730) system variable. This strategy supports selecting specific replicas based on the [zone attributes](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels#optional-configure-labels-for-tidb) of nodes and scheduling specific nodes for data scanning and MPP calculations.

    For a cluster that is deployed in multiple data centers and each data center has complete TiFlash data replicas, you can configure this strategy to only select TiFlash replicas from the current data center. This means data scanning and MPP calculations are performed only on TiFlash nodes in the current data center, which avoids excessive network data transmission across data centers.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_replica_read-new-in-v730).

* TiFlash supports Runtime Filter within nodes [#40220](https://github.com/pingcap/tidb/issues/40220) @[elsa0520](https://github.com/elsa0520)

    Runtime Filter is a **dynamic predicate** generated during the query planning phase. In the process of table joining, these dynamic predicates can effectively filter out rows that do not meet the join conditions, reducing scan time and network overhead, and improving the efficiency of table joining. Starting from v7.3.0, TiFlash supports Runtime Filter within nodes, improving the overall performance of analytical queries. In some TPC-DS workloads, the performance can be improved by 10% to 50%.

    This feature is disabled by default in v7.3.0. To enable this feature, set the system variable [`tidb_runtime_filter_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_runtime_filter_mode-new-in-v720) to `LOCAL`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/runtime-filter).

* TiFlash supports executing common table expressions (CTEs) (experimental) [#43333](https://github.com/pingcap/tidb/issues/43333) @[winoros](https://github.com/winoros)

    Before v7.3.0, the MPP engine of TiFlash cannot execute queries that contain CTEs by default. To achieve the best execution performance within the MPP framework, you need to use the system variable [`tidb_opt_force_inline_cte`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_force_inline_cte-new-in-v630) to enforce inlining CTE.

    Starting from v7.3.0, TiFlash's MPP engine supports executing queries with CTEs without inlining them, allowing for optimal query execution within the MPP framework. In TPC-DS benchmark tests, compared with inlining CTEs, this feature has shown a 20% improvement in overall query execution speed for queries containing CTE.

    This feature is experimental and is disabled by default. It is controlled by the system variable [`tidb_opt_enable_mpp_shared_cte_execution`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_mpp_shared_cte_execution-new-in-v720).
### Reliability

* Add new optimizer hints [#45520](https://github.com/pingcap/tidb/issues/45520) @[qw4990](https://github.com/qw4990)

    In v7.3.0, TiDB introduces several new optimizer hints to control the join methods between tables, including:

    - [`NO_MERGE_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_merge_joint1_name--tl_name-) selects join methods other than merge join.
    - [`NO_INDEX_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_joint1_name--tl_name-) selects join methods other than index nested loop join.
    - [`NO_INDEX_MERGE_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_merge_joint1_name--tl_name-) selects join methods other than index nested loop merge join.
    - [`NO_HASH_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_hash_joint1_name--tl_name-) selects join methods other than hash join.
    - [`NO_INDEX_HASH_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_hash_joint1_name--tl_name-) selects join methods other than [index nested loop hash join](https://docs.pingcap.com/tidb/stable/optimizer-hints#inl_hash_join).

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/optimizer-hints).

* Manually mark queries that use resources more than expected (experimental) [#43691](https://github.com/pingcap/tidb/issues/43691) @[Connor1996](https://github.com/Connor1996) @[CabinfeverB](https://github.com/CabinfeverB)

    In v7.2.0, TiDB automatically manages queries that use resources more than expected (Runaway Query) by automatically downgrading or canceling runaway queries. In actual practice, rules alone cannot cover all cases. Therefore, TiDB v7.3.0 introduces the ability to manually mark runaway queries. With the new command [`QUERY WATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-query-watch), you can mark runaway queries based on SQL text, SQL Digest, or execution plan, and the marked runaway queries can be downgraded or cancelled.

    This feature provides an effective intervention method for sudden performance issues in the database. For performance issues caused by queries, before identifying the root cause, this feature can quickly alleviate its impact on overall performance, thereby improving system service quality.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-resource-control#query-watch-parameters).
### SQL

* List and List COLUMNS partitioned tables support default partitions [#20679](https://github.com/pingcap/tidb/issues/20679) @[mjonss](https://github.com/mjonss) @[bb7133](https://github.com/bb7133)

    Before v7.3.0, when you use the `INSERT` statement to insert data into a List or List COLUMNS partitioned table, the data needs to meet the specified partitioning conditions of the table. If the data to be inserted does not meet any of these conditions, either the execution of the statement will fail or the non-compliant data will be ignored.

   Starting from v7.3.0, List and List COLUMNS partitioned tables support default partitions. After a default partition is created, if the data to be inserted does not meet any partitioning condition, it will be written to the default partition. This feature improves the usability of List and List COLUMNS partitioning, avoiding the execution failure of the `INSERT` statement or data being ignored due to data that does not meet partitioning conditions.

    Note that this feature is a TiDB extension to MySQL syntax. For a partitioned table with a default partition, the data in the table cannot be directly replicated to MySQL.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-table#list-partitioning).
