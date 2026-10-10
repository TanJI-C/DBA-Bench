# Release overview and new SQL and observability features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes | TiDB 6.1.0 Release Notes > New Features | TiDB 6.1.0 Release Notes > New Features > SQL | TiDB 6.1.0 Release Notes > New Features > Observability`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `dashboard`
- Topic Tags: `release-notes`, `new-features`, `sql`, `observability`, `partitioning`, `window-functions`, `compaction`, `continuous-profiling`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0295_2b95e1f20b`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#tidb-6-1-0-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5444934ec4a155a7d1c1b7e3c7d81fd58e5d4d370ac6867da2d6370ffca14405`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#tidb-6-1-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.1.0 release-note information about new SQL capabilities or observability additions such as list partitioning, TiFlash compaction, window functions, Continuous Profiling, or the Grafana Performance Overview dashboard.
- Retrieval Keywords: TiDB 6.1.0 Release Notes, List partitioning, List COLUMNS partitioning, TiFlash partitioned table dynamic pruning, user-level lock management, non-transactional DML DELETE, ALTER TABLE ... COMPACT, TiFlash compact command, RANK(), DENSE_RANK(), ROW_NUMBER(), Continuous Profiling, ARM architecture, Grafana Performance Overview dashboard, overall performance diagnosis
- Follow-up Guidance: The content points to related user documents for list partitioning, ALTER TABLE ... COMPACT, TiFlash supported pushdown calculations, Dashboard continuous profiling, and performance tuning overview.
- Classification Note: This is classified as a release chunk because it summarizes TiDB 6.1.0 new features across SQL and observability for shared components including TiDB, TiFlash, and Dashboard.

## Official Source Content

# TiDB 6.1.0 Release Notes

Release date: June 13, 2022

TiDB version: 6.1.0

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.1/production-deployment-using-tiup)

In 6.1.0, the key new features or improvements are as follows:

* List partitioning and list COLUMNS partitioning become GA, compatible with MySQL 5.7
* TiFlash partitioned table (dynamic pruning) becomes GA
* Support user-level lock management, compatible with MySQL
* Support non-transactional DML statements (only support `DELETE`)
* TiFlash supports on-demand data compaction
* MPP introduces the window function framework
* TiCDC supports replicating changelogs to Kafka via Avro
* TiCDC supports splitting large transactions during replication, which significantly reduces replication latency caused by large transactions
* The optimistic mode for merging and migrating sharded tables becomes GA
## New Features
### SQL

* List partitioning and list COLUMNS partitioning become GA. Both are compatible with MySQL 5.7.

    User documents: [List partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table#list-partitioning), [List COLUMNS partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table#list-columns-partitioning)

* TiFlash supports initiating a compact command. (experimental)

    TiFlash v6.1.0 introduces the `ALTER TABLE ... COMPACT` statement, which provides a manual way to compact physical data based on the existing background compaction mechanism. With this statement, you can update data in earlier formats and improve read/write performance any time as appropriate. It is recommended that you execute this statement to compact data after upgrading your cluster to v6.1.0. This statement is an extension of the standard SQL syntax and therefore is compatible with MySQL clients. For scenarios other than TiFlash upgrade, usually there is no need to use this statement.

    [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact), [#4145](https://github.com/pingcap/tiflash/issues/4145)

* TiFlash implements the window function framework and supports the following window functions:

    * `RANK()`
    * `DENSE_RANK()`
    * `ROW_NUMBER()`

  [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations), [#33072](https://github.com/pingcap/tidb/issues/33072)
### Observability

* Continuous Profiling supports the ARM architecture and TiFlash.

    [User document](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling)

* Grafana adds a Performance Overview dashboard to provide a system-level entry for overall performance diagnosis.

    As a new dashboard in the TiDB visualized monitoring component Grafana, Performance Overview provides a system-level entry for overall performance diagnosis. According to the top-down performance analysis methodology, the Performance Overview dashboard reorganizes TiDB performance metrics based on database time breakdown and displays these metrics in different colors. By checking these colors, you can identify performance bottlenecks of the entire system at the first glance, which significantly reduces performance diagnosis time and simplifies performance analysis and diagnosis.

    [User document](https://docs.pingcap.com/tidb/stable/performance-tuning-overview)
