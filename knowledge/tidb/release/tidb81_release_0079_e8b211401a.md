# TiDB 2.1.7 release notes and component changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.7.md`
- Source Title: `TiDB 2.1.7 Release Notes`
- Source Heading Path: `TiDB 2.1.7 Release Notes | TiDB 2.1.7 Release Notes > TiDB | TiDB 2.1.7 Release Notes > PD | TiDB 2.1.7 Release Notes > Tools | TiDB 2.1.7 Release Notes > TiDB Ansible`
- Source Line Ranges: `5-41`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `ecosystem`
- Topic Tags: `release-notes`, `bug-fixes`, `compatibility`, `sql-functions`, `plugin-framework`, `binlog`, `pump`, `drainer`, `pd-scheduling`, `generated-columns`, `prometheus-retention`, `ansible`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0079_e8b211401a`
- Source ID: `tidb-docs-8.1:releases/release-2.1.7.md#tidb-2-1-7-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `044cadb2fb6efa88c2916794a2d44d31863327b32ab01d44fbc80d9641a00720`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.7#tidb-2-1-7-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.7.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 2.1.7 release notes that summarize bug fixes, compatibility changes, new SQL-visible metadata, PD scheduling fixes, binlog generated-column support, and TiDB Ansible monitoring retention changes.
- Retrieval Keywords: TiDB 2.1.7 Release Notes, TiDB version 2.1.7, TiDB Ansible version 2.1.7, check-mb4-value-in-utf8, str_to_date built-in function, last_day built-in function, infoschema.tables tidb_table_id, tidb_indexes system table, Truncate Table Delete to Drop privilege, subqueries in the DO statement, default_week_format week function, plugin framework, log_bin system variable, Pump/Drainer status by using SQL statements, aggregate function calculates JSON data panic, PD balance-region transferring leader step number of replicas is one, replicating generated columns by using binlog, Prometheus monitoring data 30d
- Follow-up Guidance: The source also points to component-specific sections for TiDB, PD, Tools, and TiDB Ansible within the same TiDB 2.1.7 release notes.
- Classification Note: This is a release-notes chunk for a self-managed deployment scope because the official content is the TiDB 2.1.7 release notes listing component changes across TiDB, PD, Tools, and TiDB Ansible.

## Official Source Content

# TiDB 2.1.7 Release Notes

Release Date: March 28, 2019

TiDB version: 2.1.7

TiDB Ansible version: 2.1.7
## TiDB

- Fix the issue of longer startup time when upgrading the program caused by canceling DDL operations [#9768](https://github.com/pingcap/tidb/pull/9768)
- Fix the issue that the `check-mb4-value-in-utf8` configuration item is in the wrong position in the `config.example.toml` file [#9852](https://github.com/pingcap/tidb/pull/9852)
- Improve the compatibility of the `str_to_date` built-in function with MySQL [#9817](https://github.com/pingcap/tidb/pull/9817)
- Fix the compatibility issue of the `last_day` built-in function [#9750](https://github.com/pingcap/tidb/pull/9750)
- Add the `tidb_table_id` column for `infoschema.tables` to facilitate getting `table_id` by using SQL statements and add the `tidb_indexes` system table to manage the relationship between Table and Index [#9862](https://github.com/pingcap/tidb/pull/9862)
- Add a check about the null definition of Table Partition [#9663](https://github.com/pingcap/tidb/pull/9663)
- Change the privileges required by `Truncate Table` from `Delete` to `Drop` to make it consistent with MySQL [#9876](https://github.com/pingcap/tidb/pull/9876)
- Support using subqueries in the `DO` statement [#9877](https://github.com/pingcap/tidb/pull/9877)
- Fix the issue that the `default_week_format` variable does not take effect in the `week` function [#9753](https://github.com/pingcap/tidb/pull/9753)
- Support the plugin framework [#9880](https://github.com/pingcap/tidb/pull/9880), [#9888](https://github.com/pingcap/tidb/pull/9888)
- Support checking the enabling state of binlog by using the `log_bin` system variable [#9634](https://github.com/pingcap/tidb/pull/9634)
- Support checking the Pump/Drainer status by using SQL statements [#9896](https://github.com/pingcap/tidb/pull/9896)
- Fix the compatibility issue about checking mb4 character on utf8 when upgrading TiDB [#9887](https://github.com/pingcap/tidb/pull/9887)
- Fix the panic issue when the aggregate function calculates JSON data in some cases [#9927](https://github.com/pingcap/tidb/pull/9927)
## PD

- Fix the issue that the transferring leader step cannot be created in the balance-region when the number of replicas is one [#1462](https://github.com/pingcap/pd/pull/1462)
## Tools

- Support replicating generated columns by using binlog
## TiDB Ansible

Change the default retention time of Prometheus monitoring data to 30d
