# TiDB 3.0 GA release overview

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0-ga.md`
- Source Title: `TiDB 3.0 GA Release Notes`
- Source Heading Path: `TiDB 3.0 GA Release Notes | TiDB 3.0 GA Release Notes > Overview`
- Source Line Ranges: `5-22`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `lightning`
- Topic Tags: `release-notes`, `overview`, `stability`, `usability`, `performance`, `new-features`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0085_f305ad614b`
- Source ID: `tidb-docs-8.1:releases/release-3.0-ga.md#tidb-3-0-ga-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9bd3e27fb6c46b13b438a5209c2860a1ab5521a9c04973b25848826deae6a48a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0-ga#tidb-3-0-ga-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 3.0.0 GA release overview, release date, corresponding TiDB Ansible version, and the headline improvements compared with TiDB 2.1.
- Retrieval Keywords: TiDB 3.0 GA Release Notes, June 28, 2019, TiDB version 3.0.0, TiDB Ansible version 3.0.0, Overview, compared with TiDB 2.1, stability, usability, performance, EXPLAIN ANALYZE, SQL Trace, Window Functions, Views, partitioned tables, plugin framework, pessimistic locking, SQL Plan Management, TPC-C benchmarks, Sysbench benchmarks, TPC-H 50G Q15
- Follow-up Guidance: For detailed changes by component, see the TiDB section of the same release notes for feature areas such as SQL optimizer, SQL execution engine, DDL, transactions, permission management, server, and compatibility.
- Classification Note: This is a release overview chunk because the official content summarizes the TiDB 3.0 GA release date, versions, and major improvements and new features across the release.

## Official Source Content

# TiDB 3.0 GA Release Notes

Release date: June 28, 2019

TiDB version: 3.0.0

TiDB Ansible version: 3.0.0
## Overview

On June 28, 2019, TiDB 3.0 GA is released. The corresponding TiDB Ansible version is 3.0.0. Compared with TiDB 2.1, this release has greatly improved in the following aspects:

- Stability. TiDB 3.0 has demonstrated long-term stability for large-scale clusters with up to 150+ nodes and 300+ TB of storage.
- Usability. TiDB 3.0 has multi-facet improvements in usability, including standardized slow query logs, well-developed log file specification, and new features such as `EXPLAIN ANALYZE` and SQL Trace to save operation costs for users.
- Performance. The performance of TiDB 3.0 is 4.5 times greater than TiDB 2.1 in TPC-C benchmarks, and over 1.5 times in Sysbench benchmarks. Thanks to the support for Views, TPC-H 50G Q15 can now run normally.
- New features including Window Functions, Views (**Experimental**), partitioned tables, the plugin framework, pessimistic locking (**Experimental**), and `SQL Plan Management`.
