# TiDB 3.0.10 release overview and TiDB fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.10.md`
- Source Title: `TiDB 3.0.10 Release Notes`
- Source Heading Path: `TiDB 3.0.10 Release Notes | TiDB 3.0.10 Release Notes > TiDB`
- Source Line Ranges: `5-49`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `release-notes`, `warning`, `bug-fixes`, `join`, `transactions`, `pointget`, `partitioning`, `statistics`, `monitoring`, `deadlock`, `sql-bindings`, `privileges`, `json`, `memory-usage`, `panic`, `performance`, `audit-logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0100_3b596ae8c3`
- Source ID: `tidb-docs-8.1:releases/release-3.0.10.md#tidb-3-0-10-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9c85e4e85abea9ff277c49d79e6cc55a9fb62e674851c0a1d7a646a4a94bf20`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.10#tidb-3-0-10-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.10.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.10 release-note details about TiDB fixes, warnings, monitoring items, panics, transaction behavior, SQL bindings, partitioning, JSON, privileges, or PointGet behavior.
- Retrieval Keywords: TiDB 3.0.10 Release Notes, Warning latest 3.0.x version, IndexLookUpJoin OtherCondition InnerRange wrong Join results, tidb_pprof_sql_cpu configuration item deleted, tidb_pprof_sql_cpu variable added, global privileges query all databases, PointGet transaction timeout data visibility, pessimistic transaction delayed activation, unixtimestamp table partitions time zone, tidb_session_statement_deadlock_detect_duration_seconds, GC workers system panic, IsTrue function expression name, memory usage counted inaccurately, CM-Sketch statistics initialization panic, partition pruning partitioned tables, SQL bindings default database name, json_key compatible with MySQL, automatically updating the statistics of partitioned tables, PointGet plan ID expected to be 1, SQL bindings do not match exactly panic, tidb_session_statement_pessimistic_retry_count, show binding privilege check, backoff logic killed tag query cannot be killed, statement summary internal locks, parsing strings to time incompatible with MySQL, user login failures audit logs, tidb_session_ statement_lock_keys_count, JSON characters &, <, > incorrectly escaped, HashJoin building a hash table excessive memory usage panic, SQL binding illegal records panic, Truncated error detection decimal division, granting users privileges on a table that does not exist
- Follow-up Guidance: The source also states that some known issues were found in this version and are fixed in newer versions, and it recommends using the latest 3.0.x version.
- Classification Note: This is classified as a TiDB release-notes chunk because the content is the TiDB section of the 3.0.10 release notes and lists TiDB-specific fixes, behavior changes, and monitoring items.

## Official Source Content

# TiDB 3.0.10 Release Notes

Release date: February 20, 2020

TiDB version: 3.0.10

TiDB Ansible version: 3.0.10

> **Warning:**
>
> Some known issues are found in this version, and these issues are fixed in new versions. It is recommended that you use the latest 3.0.x version.
## TiDB

- Fix wrong `Join` results when `IndexLookUpJoin` uses `OtherCondition` to construct `InnerRange` [#14599](https://github.com/pingcap/tidb/pull/14599)
- Delete the `tidb_pprof_sql_cpu` configuration item and add the `tidb_pprof_sql_cpu` variable [#14416](https://github.com/pingcap/tidb/pull/14416)
- Fix the issue that users can query all databases only when they have global privileges [#14386](https://github.com/pingcap/tidb/pull/14386)
- Fix the issue that data visibility does not meet expectations due to transaction timeout when executing `PointGet` operations [#14480](https://github.com/pingcap/tidb/pull/14480)
- Change the timing of pessimistic transaction activation to delayed activation, consistent with the optimistic transaction mode [#14474](https://github.com/pingcap/tidb/pull/14474)
- Fix the incorrect time zone results when the `unixtimestamp` expression calculates the time zone of the table partitions [#14476](https://github.com/pingcap/tidb/pull/14476)
- Add the `tidb_session_statement_deadlock_detect_duration_seconds` monitoring item to monitor deadlock detection duration [#14484](https://github.com/pingcap/tidb/pull/14484)
- Fix the system panic issue caused by some logic errors of GC workers [#14439](https://github.com/pingcap/tidb/pull/14439)
- Correct the expression name of the `IsTrue` function [#14516](https://github.com/pingcap/tidb/pull/14516)
- Fix the issue that some memory usage is counted inaccurately [#14533](https://github.com/pingcap/tidb/pull/14533)
- Fix the system panic issue caused by incorrect processing logic during CM-Sketch statistics initialization [#14470](https://github.com/pingcap/tidb/pull/14470)
- Fix the issue of inaccurate partition pruning when querying partitioned tables [#14546](https://github.com/pingcap/tidb/pull/14546)
- Fix the issue that the default database name of the SQL statement in SQL bindings is set incorrectly [#14548](https://github.com/pingcap/tidb/pull/14548)
- Fix the issue that `json_key` is not compatible with MySQL [#14561](https://github.com/pingcap/tidb/pull/14561)
- Add the feature of automatically updating the statistics of partitioned tables [#14566](https://github.com/pingcap/tidb/pull/14566)
- Fix the issue that the plan ID changes when the `PointGet` operation is executed (the plan ID is expected to be `1` always) [#14595](https://github.com/pingcap/tidb/pull/14595)
- Fix the system panic issue caused by incorrect processing logic when SQL bindings do not match exactly [#14263](https://github.com/pingcap/tidb/pull/14263)
- Add the `tidb_session_statement_pessimistic_retry_count` monitoring item to monitor the number of retries after the failure to lock pessimistic transactions [#14619](https://github.com/pingcap/tidb/pull/14619)
- Fix the incorrect privilege check for `show binding` statements [#14618](https://github.com/pingcap/tidb/pull/14618)
- Fix the issue that the query cannot be killed because the `backoff` logic does not include checking the `killed` tag [#14614](https://github.com/pingcap/tidb/pull/14614)
- Improve the performance of statement summary by reducing the time to hold internal locks [#14627](https://github.com/pingcap/tidb/pull/14627)
- Fix the issue that TiDB's result of parsing strings to time is incompatible with MySQL [#14570](https://github.com/pingcap/tidb/pull/14570)
- Record the user login failures in audit logs [#14620](https://github.com/pingcap/tidb/pull/14620)
- Add the `tidb_session_ statement_lock_keys_count` monitoring item to monitor the number of lock keys for pessimistic transactions [#14634](https://github.com/pingcap/tidb/pull/14634)
- Fix the issue that characters in JSON such as `&`, `<`, and `>` are incorrectly escaped [#14637](https://github.com/pingcap/tidb/pull/14637)
- Fix the system panic issue caused by excessive memory usage when the `HashJoin` operation is building a hash table [#14642](https://github.com/pingcap/tidb/pull/14642)
- Fix the panic issue caused by incorrect processing logic when an SQL binding processes illegal records [#14645](https://github.com/pingcap/tidb/pull/14645)
- ix a MySQL incompatibility issue by adding Truncated error detection to decimal division calculation [#14673](https://github.com/pingcap/tidb/pull/14673)
- Fix the issue of successfully granting users privileges on a table that does not exist [#14611](https://github.com/pingcap/tidb/pull/14611)
