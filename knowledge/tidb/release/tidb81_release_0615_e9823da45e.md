# TiDB RC2 release highlights across TiDB, PD, and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-rc.2.md`
- Source Title: `TiDB RC2 Release Notes`
- Source Heading Path: `TiDB RC2 Release Notes | TiDB RC2 Release Notes > TiDB | TiDB RC2 Release Notes > PD | TiDB RC2 Release Notes > TiKV`
- Source Line Ranges: `5-52`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `sql`
- Topic Tags: `release-notes`, `mysql-compatibility`, `query-optimizer`, `privilege-management`, `performance`, `stability`, `replica-scheduling`, `async-apply`, `monitoring`, `bug-fixes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0615_e9823da45e`
- Source ID: `tidb-docs-8.1:releases/release-rc.2.md#tidb-rc2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c3ce6c191b99440f4c4c5003182ad9ccac21b7cf596e1534687c4a0fccba713a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-rc.2#tidb-rc2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-rc.2.md

## Retrieval Guidance

- Use When: You need the RC2 release notes that summarize TiDB, PD, and TiKV improvements in MySQL compatibility, query optimization, privilege management, performance, monitoring, and bug fixes.
- Retrieval Keywords: TiDB RC2 Release Notes, MySQL compatibility, SQL query optimizer, basic privilege management, location aware replica scheduling, Async Apply, improve the monitoring system, Fix Bugs
- Follow-up Guidance: 
- Classification Note: This chunk is a release highlights summary for TiDB RC2 and groups changes across TiDB, PD, and TiKV.

## Official Source Content

# TiDB RC2 Release Notes

On March 1, 2017, TiDB RC2 is released! This release is focused on the compatibility with MySQL, SQL query optimizer, system stability and performance in this version. What's more, a new permission management mechanism is added and users can control data access in the same way as the MySQL privilege management system.
## TiDB

+ Query optimizer
    - Collect column/index statistics and use them in the query optimizer
    - Optimize the correlated subquery
    - Optimize the Cost Based Optimizer (CBO) framework
    - Eliminate aggregation using unique key information
    - Refactor expression evaluation framework
    - Convert Distinct to GroupBy
    - Support the topn operation push-down
+ Support basic privilege management
+ Add lots of MySQL built-in functions
+ Improve the Alter Table statement and support the modification of table name, default value and comment
+ Support the Create Table Like statement
+ Support the Show Warnings statement
+ Support the Rename Table statement
+ Restrict the size of a single transaction to avoid the cluster blocking of large transactions
+ Automatically split data in the process of Load Data
+ Optimize the performance of the AddIndex and Delete statement
+ Support "ANSI_QUOTES" sql_mode
+ Improve the monitoring system
+ Fix Bugs
+ Solve the problem of memory leak
## PD

+ Support location aware replica scheduling
+ Conduct fast scheduling based on the number of region
+ pd-ctl support more features
    - Add or delete PD
    - Obtain Region information with Key
    - Add or delete scheduler and operator
    - Obtain cluster label information
## TiKV

+ Support Async Apply to improve the entire write performance
+ Use prefix seek to improve the read performance of Write CF
+ Use memory hint prefix to improve the insert performance of Raft CF
+ Optimize the single read transaction performance
+ Support more push-down expressions
+ Improve the monitoring system
+ Fix Bugs
