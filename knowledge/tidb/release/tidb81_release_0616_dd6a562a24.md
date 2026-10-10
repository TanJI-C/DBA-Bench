# TiDB RC3 release highlights and component updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-rc.3.md`
- Source Title: `TiDB RC3 Release Notes`
- Source Heading Path: `TiDB RC3 Release Notes | TiDB RC3 Release Notes > Highlight | TiDB RC3 Release Notes > Detailed updates | TiDB RC3 Release Notes > TiDB | TiDB RC3 Release Notes > Placement Driver (PD) | TiDB RC3 Release Notes > TiKV`
- Source Line Ranges: `5-61`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `tiup`
- Topic Tags: `release-notes`, `mysql-compatibility`, `sql-optimization`, `stability`, `performance`, `privilege-management`, `ddl`, `load-balancing`, `grpc`, `disaster-recovery`, `http-api`, `system-variables`, `query-concurrency`, `data-import`, `hot-region`, `memory-leak-detection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0616_dd6a562a24`
- Source ID: `tidb-docs-8.1:releases/release-rc.3.md#tidb-rc3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `81ab0d6aab18bfbd35cd81b260527721267ad8e99b7f102f8d827935a282c59d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-rc.3#tidb-rc3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-rc.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB RC3 release-note highlights or detailed component updates about MySQL compatibility, SQL optimization, stability, performance, privilege management, DDL, PD, TiKV, or TiDB-Ansible.
- Retrieval Keywords: TiDB RC3 Release Notes, RC3 release highlights, MySQL compatibility, SQL optimization, stability, performance, privilege management, DDL acceleration, TiDB-Ansible, incremental statistics, Merge Sort Join, Index Lookup Join, Optimizer Hint, Cost Based Optimizer, HTTP API data distribution information of tables, system variables query concurrency, split a big transaction into smaller ones to commit, PD gRPC, Disaster Recovery Toolkit, Garbage Collection clear stale data automatically, hot Region scheduling, Client TSO, Region Heartbeat, pd-ctl, Replica configuration dynamically, Timestamp Oracle (TSO), Region information by ID, TiKV gRPC, SST format snapshot, Heap Profile, memory leaks, Streaming SIMD Extensions (SSE), CRC32, Batch Apply, parallel Prewrite, coprocessor thread pool, Loader table level data importing
- Follow-up Guidance: The source also breaks the updates down by TiDB, Placement Driver (PD), and TiKV with feature-specific items such as `pd-ctl`, HTTP API, gRPC, and Loader improvements.
- Classification Note: This chunk is classified as a self-managed release note because the official content is a TiDB RC3 release announcement that summarizes highlights and detailed updates across TiDB, PD, TiKV, and TiDB-Ansible.

## Official Source Content

# TiDB RC3 Release Notes

On June 16, 2017, TiDB RC3 is released! This release is focused on MySQL compatibility, SQL optimization, stability, and performance.
## Highlight

- The privilege management is refined to enable users to manage the data access privileges using the same way as in MySQL.
- DDL is accelerated.
- The load balancing policy and process are optimized for performance.
- TiDB Ansible is open sourced. By using TiDB-Ansible, you can deploy, upgrade, start and shutdown a TiDB cluster with one click.
## Detailed updates
## TiDB

+ The following features are added or improved in the SQL query optimizer:
    - Support incremental statistics
    - Support the `Merge Sort Join` operator
    - Support the `Index Lookup Join` operator
    - Support the `Optimizer Hint` Syntax
    - Optimize the memory consumption of the `Scan`, `Join`, `Aggregation` operators
    - Optimize the Cost Based Optimizer (CBO) framework
    - Refactor `Expression`
+ Support more complete privilege management
+ DDL acceleration
+ Support using HTTP API to get the data distribution information of tables
+ Support using system variables to control the query concurrency
+ Add more MySQL built-in functions
+ Support using system variables to automatically split a big transaction into smaller ones to commit
## Placement Driver (PD)

+ Support gRPC
+ Provide the Disaster Recovery Toolkit
+ Use Garbage Collection to clear stale data automatically
+ Support more efficient data balance
+ Support hot Region scheduling to enable load balancing and speed up the data importing
+ Performance
    - Accelerate getting Client TSO
    - Improve the efficiency of Region Heartbeat processing
+ Improve the `pd-ctl` function
    - Update the Replica configuration dynamically
    - Get the Timestamp Oracle (TSO)
    - Use ID to get the Region information
## TiKV

+ Support gRPC
+ Support the Sorted String Table (SST) format snapshot to improve the load balancing speed of a cluster
+ Support using the Heap Profile to uncover memory leaks
+ Support Streaming SIMD Extensions (SSE) and speed up the CRC32 calculation
+ Accelerate transferring leader for faster load balancing
+ Use Batch Apply to reduce CPU usage and improve the write performance
+ Support parallel Prewrite to improve the transaction write speed
+ Optimize the scheduling of the coprocessor thread pool to reduce the impact of big queries on point get
+ The new Loader supports data importing at the table level, as well as splitting a big table into smaller logical blocks to import concurrently to improve the data importing speed.
