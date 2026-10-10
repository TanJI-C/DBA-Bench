# 6.0.0-DMR overview, release strategy, and early new features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes | TiDB 6.0.0 Release Notes > Release strategy changes | TiDB 6.0.0 Release Notes > New features | TiDB 6.0.0 Release Notes > New features > SQL | TiDB 6.0.0 Release Notes > New features > Transaction | TiDB 6.0.0 Release Notes > New features > Observability`
- Source Line Ranges: `5-86`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `dashboard`, `pd`, `tikv`, `tiflash`
- Topic Tags: `release-notes`, `dmr`, `lts`, `sql-placement-rules`, `tiflash-replicas`, `transaction-consistency`, `top-sql`, `continuous-profiling`, `observability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0285_1c2ee5a99e`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#tidb-6-0-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c9efbf6d8ff8fe3ff1aa40bc917d1d41e193a063e1c6c032bc6ffef9138353c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#tidb-6-0-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this release note chunk when you need the TiDB 6.0.0-DMR overview, the release strategy changes between LTS releases and Development Milestone Releases, or the list of early new features.
- Retrieval Keywords: TiDB 6.0.0 Release Notes, 6.0.0-DMR, Long-Term Support Releases, Development Milestone Releases, placement rules in SQL, Top SQL, Continuous Profiling, TiFlash replicas by databases, tidb_enable_mutation_checker, tidb_txn_assertion_level, TiDB Dashboard, DM WebUI, PingCAP Clinic, TiDB Enterprise Manager
- Follow-up Guidance: See the linked user documentation for placement rules in SQL, Top SQL, and Continuous Profiling if you need the feature-specific details.
- Classification Note: This chunk is a general release overview that summarizes the 6.0.0-DMR release strategy and multiple highlighted new features across SQL, Transaction, and Observability.

## Official Source Content

# TiDB 6.0.0 Release Notes

Release date: April 7, 2022

TiDB version: 6.0.0-DMR

> **Note:**
>
> The TiDB 6.0.0-DMR documentation has been [archived](https://docs-archive.pingcap.com/tidb/v6.0/). PingCAP encourages you to use [the latest LTS version](https://docs.pingcap.com/tidb/stable) of the TiDB database.

In 6.0.0-DMR, the key new features or improvements are as follows:

- Support placement rules in SQL to provide more flexible management for data placement.
- Add a consistency check between data and indexes at the kernel level, which improves system stability and robustness, with only very low resource overhead.
- Provide Top SQL, a self-serving database performance monitoring and diagnosis feature for non-experts.
- Support Continuous Profiling that collects cluster performance data all the time, reducing MTTR for technical experts.
- Cache hotspot small tables in memory, which greatly improves the access performance, improves the throughput and reduces access latency.
- Optimize in-memory pessimistic locking. Under the performance bottleneck caused by pessimistic locks, memory optimization for pessimistic locks can effectively reduce latency by 10% and increase QPS by 10%.
- Enhance prepared statements to share execution plans, which lessens CPU resource consumption and improves SQL execution efficiency.
- Improve the computing performance of the MPP engine by supporting pushing down more expressions and the general availability (GA) of the elastic thread pool.
- Add DM WebUI to facilitate managing a large number of migration tasks.
- Improve the stability and efficiency of TiCDC when replicating data in large clusters. TiCDC now supports replicating 100,000 tables simultaneously.
- Accelerate leader balancing after restarting TiKV nodes, which improves the speed of business recovery after a restart.
- Support canceling the automatic update of statistics, which reduces resource contention and limits the impact on SQL performance.
- Provide PingCAP Clinic, an automatic diagnosis service for TiDB clusters (Technical Preview version).
- Provide TiDB Enterprise Manager, an enterprise-level database management platform.

Also, as a core component of TiDB's HTAP solution, TiFlash<sup>TM</sup> is officially open source in this release. For details, see [TiFlash repository](https://github.com/pingcap/tiflash).
## Release strategy changes

Starting from TiDB v6.0.0, TiDB provides two types of releases:

- Long-Term Support Releases

    Long-Term Support (LTS) releases are released approximately every six months. An LTS release introduces new features and improvements, and accepts patch releases within its release lifecycle. For example, v6.1.0 will be an LTS release.

- Development Milestone Releases

    Development Milestone Releases (DMR) are released approximately every two months. A DMR introduces new features and improvements, but does not accept patch releases. It is not recommended for users to use DMR in production environments. For example, v6.0.0-DMR is a DMR.

TiDB v6.0.0 is a DMR, and its version is 6.0.0-DMR.
## New features
### SQL

- SQL-based placement rules for data

    TiDB is a distributed database with excellent scalability. Usually, data is deployed across multiple servers or even multiple data centers. Therefore, data scheduling management is one of the most important basic capabilities of TiDB. In most cases, users do not need to care about how to schedule and manage data. However, with the increasing application complexity, deployment changes caused by isolation and access latency have become new challenges for TiDB. Since v6.0.0, TiDB officially provides data scheduling and management capabilities based on SQL interfaces. It supports flexible scheduling and management in dimensions such as replica counts, role types, and placement locations for any data. TiDB also supports more flexible management for data placement in multi-service shared clusters and cross-AZ deployments.

    [User document](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql)

- Support building TiFlash replicas by databases. To add TiFlash replicas for all tables in a database, you only need to use a single SQL statement, which greatly saves operation and maintenance costs.

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas#create-tiflash-replicas-for-databases)
### Transaction

- Add a check for data index consistency at the kernel level

    Add a check for data index consistency when a transaction is executed, which improves system stability and robustness, with only very low resource overhead. You can control the check behavior using the `tidb_enable_mutation_checker` and `tidb_txn_assertion_level` variables. With the default configuration, the QPS drop is controlled within 2% in most scenarios. For the error description of the consistency check, see [user document](https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors).
### Observability

- Top SQL: Performance diagnosis for non-experts

    Top SQL is a self-serving database performance monitoring and diagnosis feature in TiDB Dashboard, for DBAs and App developers, which is now generally available in TiDB v6.0.

    Unlike existing diagnostic features for experts, Top SQL is designed for non-experts: you do not need to traverse thousands of monitoring charts to find correlations or understand TiDB internal mechanisms such as Raft Snapshot, RocksDB, MVCC, and TSO. To use Top SQL for analyzing database load quickly and improving App performance, only basic database knowledge (such as index, lock conflict, and execution plans) is needed.

    Top SQL is not enabled by default. When enabled, Top SQL provides you with the real-time CPU load of each TiKV or TiDB node. Therefore, you can spot SQL statements consuming high CPU loads at first glimpse, and quickly analyze the issues such as database hotspots and sudden load increases. For example, you can use Top SQL to pinpoint and diagnose an unusual query that consumes 90% CPU of a single TiKV node.

    [User documentation](https://docs.pingcap.com/tidb/stable/dashboard/top-sql)

- Support Continuous Profiling

    TiDB Dashboard introduces the Continuous Profiling feature, which is now generally available in TiDB v6.0. Continuous profiling is not enabled by default. When enabled, the performance data of individual TiDB, TiKV, and PD instances will be collected all the time, with negligible overhead. With history performance data, technical experts can backtrack and pinpoint the root causes of issues like high memory consumption, even when the issues are difficult to reproduce. In this way, the mean time to recovery (MTTR) can be reduced.

    [User document](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling)
