# TiDB 2.0.10 release notes and component fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0.10.md`
- Source Title: `TiDB 2.0.10 Release Notes`
- Source Heading Path: `TiDB 2.0.10 Release Notes | TiDB 2.0.10 Release Notes > TiDB | TiDB 2.0.10 Release Notes > PD | TiDB 2.0.10 Release Notes > TiKV`
- Source Line Ranges: `5-39`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `bug-fixes`, `compatibility`, `stability`, `ddl`, `sql-mode`, `query-results`, `statistics`, `memory-usage`, `deadlock`, `leader-transfer`, `region-heartbeat`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0028_a05093a2e0`
- Source ID: `tidb-docs-8.1:releases/release-2.0.10.md#tidb-2-0-10-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a88c2ac545dafebbe98f0005b1f26c39d62d254384b5f50d2884d118840b5c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0.10#tidb-2-0-10-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0.10.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official TiDB 2.0.10 release notes that summarize compatibility and stability fixes across TiDB, PD, and TiKV.
- Retrieval Keywords: TiDB 2.0.10 Release Notes, TiDB Ansible 2.0.10, canceling a DDL job, ORDER BY and UNION clauses cannot quote the column including a table name, UNCOMPRESS function incorrect input length, ANSI_QUOTES SQL_MODE when upgrading TiDB, select returns the wrong result, TiDB cannot exit when it receives the exit signal, IndexLookUpJoin returns the wrong result, GetVar or SetVar, UNION clauses result length is incorrect, PREPARE FROM @var_name, dumping statistics information panic, statistics estimation issue of point queries, default enum value is a string, too much memory is consumed in the scenario of wide tables, Parser incorrectly formats the mod opcode, adding foreign key constraints panic, YEAR column type incorrectly converts the zero value, VALUES function argument is not a column, Disable Plan Cache for statements containing subqueries, RaftCluster cannot stop caused by deadlock, Avoid transferring the leader to a newly created peer, Fix redundant Region heartbeats
- Follow-up Guidance: The source groups the fixes by component under TiDB, PD, and TiKV for TiDB 2.0.10.
- Classification Note: This is a self-managed release-notes chunk because the official content is the TiDB 2.0.10 release notes listing component bug fixes and stability improvements.

## Official Source Content

# TiDB 2.0.10 Release Notes

On December 18, 2018, TiDB 2.0.10 is released. The corresponding TiDB Ansible 2.0.10 is also released. Compared with TiDB 2.0.9, this release has great improvement in system compatibility and stability.
## TiDB

- Fix the possible issue caused by canceling a DDL job [#8513](https://github.com/pingcap/tidb/pull/8513)
- Fix the issue that the `ORDER BY` and `UNION` clauses cannot quote the column including a table name [#8514](https://github.com/pingcap/tidb/pull/8514)
- Fix the issue that the `UNCOMPRESS` function does not judge the incorrect input length [#8607](https://github.com/pingcap/tidb/pull/8607)
- Fix the issue encountered by `ANSI_QUOTES SQL_MODE` when upgrading TiDB [#8575](https://github.com/pingcap/tidb/pull/8575)
- Fix the issue that `select` returns the wrong result in some cases [#8570](https://github.com/pingcap/tidb/pull/8570)
- Fix the possible issue that TiDB cannot exit when it receives the exit signal [#8501](https://github.com/pingcap/tidb/pull/8501)
- Fix the issue that `IndexLookUpJoin` returns the wrong result in some cases [#8508](https://github.com/pingcap/tidb/pull/8508)
- Avoid pushing down the filter containing `GetVar` or `SetVar` [#8454](https://github.com/pingcap/tidb/pull/8454)
- Fix the issue that the result length of the `UNION` clauses is incorrect in some cases [#8491](https://github.com/pingcap/tidb/pull/8491)
- Fix the issue of `PREPARE FROM @var_name` [#8488](https://github.com/pingcap/tidb/pull/8488)
- Fix the panic issue when dumping statistics information in some cases [#8464](https://github.com/pingcap/tidb/pull/8464)
- Fix the statistics estimation issue of point queries in some cases [#8493](https://github.com/pingcap/tidb/pull/8493)
- Fix the panic issue when the returned default `enum` value is a string [#8476](https://github.com/pingcap/tidb/pull/8476)
- Fix the issue that too much memory is consumed in the scenario of wide tables [#8467](https://github.com/pingcap/tidb/pull/8467)
- Fix the issue encountered when Parser incorrectly formats the mod opcode [#8431](https://github.com/pingcap/tidb/pull/8431)
- Fix the panic issue caused by adding foreign key constraints in some cases [#8421](https://github.com/pingcap/tidb/pull/8421), [#8410](https://github.com/pingcap/tidb/pull/8410)
- Fix the issue that the `YEAR` column type incorrectly converts the zero value [#8396](https://github.com/pingcap/tidb/pull/8396)
- Fix the panic issue occurred when the argument of the `VALUES` function is not a column [#8404](https://github.com/pingcap/tidb/pull/8404)
- Disable Plan Cache for statements containing subqueries [#8395](https://github.com/pingcap/tidb/pull/8395)
## PD

- Fix the possible issue that RaftCluster cannot stop caused by deadlock [#1370](https://github.com/pingcap/pd/pull/1370)
## TiKV

- Avoid transferring the leader to a newly created peer, to optimize the possible delay [#3929](https://github.com/tikv/tikv/pull/3929)
- Fix redundant Region heartbeats [#3930](https://github.com/tikv/tikv/pull/3930)
