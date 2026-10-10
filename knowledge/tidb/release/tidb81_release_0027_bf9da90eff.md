# TiDB 2.0.1 release notes across TiDB, PD, and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0.1.md`
- Source Title: `TiDB 2.0.1 Release Notes`
- Source Heading Path: `TiDB 2.0.1 Release Notes | TiDB 2.0.1 Release Notes > TiDB | TiDB 2.0.1 Release Notes > PD | TiDB 2.0.1 Release Notes > TiKV`
- Source Line Ranges: `5-49`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `mysql-compatibility`, `stability`, `ddl`, `statistics`, `binlog`, `slow-log`, `scheduler`, `region-balance`, `learner`, `raftstore`, `dirty-read`, `delete-range`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0027_bf9da90eff`
- Source ID: `tidb-docs-8.1:releases/release-2.0.1.md#tidb-2-0-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9497c898e886f5cbaf670207fd54d080295f487dfd4f24afab3d3fc1544361f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0.1#tidb-2-0-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the official TiDB 2.0.1 release-note summary of changes across TiDB, PD, and TiKV, including compatibility, stability, DDL, statistics, scheduler, Learner, raftstore, slow log, and Delete Range updates.
- Retrieval Keywords: TiDB 2.0.1 Release Notes, TiDB 2.0.1, tidb_auto_analyze_ratio, Add Index, DDL job information, ADMIN CHECK INDEX, UNION statement, TIME type, Binlog failure, Coprocessor slow log, SIGTERM, Scatter Range scheduler, Merge Region, Learner related metrics, etcd leader and the PD leader are not replicated, packet size is too large, SELECT FOR UPDATE prevents others from reading, raftstore, dirty read, read thread pool configuration, Delete Range
- Follow-up Guidance: The source groups the changes under the TiDB, PD, and TiKV sections of the TiDB 2.0.1 Release Notes.
- Classification Note: This is a self-managed release-notes chunk because the official content enumerates fixes and improvements delivered in TiDB 2.0.1 across the shared components TiDB, PD, and TiKV.

## Official Source Content

# TiDB 2.0.1 Release Notes

On May 16, 2018, TiDB 2.0.1 is released. Compared with TiDB 2.0.0 (GA), this release has great improvement in MySQL compatibility and system stability.
## TiDB

- Update the progress of `Add Index` to the DDL job information in real time
- Add the `tidb_auto_analyze_ratio` session variable to control the threshold value of automatic statistics update
- Fix an issue that not all residual states are cleaned up when the transaction commit fails
- Fix a bug about adding indexes in some conditions
- Fix the correctness related issue when DDL modifies surface operations in some concurrent scenarios
- Fix a bug that the result of `LIMIT` is incorrect in some conditions
- Fix a capitalization issue of the `ADMIN CHECK INDEX` statement to make its index name case insensitive
- Fix a compatibility issue of the `UNION` statement
- Fix a compatibility issue when inserting data of `TIME` type
- Fix a goroutine leak issue caused by `copIteratorTaskSender` in some conditions
- Add an option for TiDB to control the behaviour of Binlog failure
- Refactor the `Coprocessor` slow log to distinguish between the scenario of tasks with long processing time and long waiting time
- Log nothing when meeting MySQL protocol handshake error, to avoid too many logs caused by the load balancer Keep Alive mechanism
- Refine the "Out of range value for column" error message
- Fix a bug when there is a subquery in an `Update` statement
- Change the behaviour of handling `SIGTERM`, and do not wait for all queries to terminate anymore
## PD

- Add the `Scatter Range` scheduler to balance Regions with the specified key range
- Optimize the scheduling of Merge Region to prevent the newly split Region from being merged
- Add Learner related metrics
- Fix the issue that the scheduler is mistakenly deleted after restart
- Fix the error that occurs when parsing the configuration file
- Fix the issue that the etcd leader and the PD leader are not replicated
- Fix the issue that Learner still appears after it is closed
- Fix the issue that Regions fail to load because the packet size is too large
## TiKV

- Fix the issue that `SELECT FOR UPDATE` prevents others from reading
- Optimize the slow query log
- Reduce the number of `thread_yield` calls
- Fix the bug that raftstore is accidentally blocked when generating the snapshot
- Fix the issue that Learner cannot be successfully elected in special conditions
- Fix the issue that split might cause dirty read in extreme conditions
- Correct the default value of the read thread pool configuration
- Speed up Delete Range
