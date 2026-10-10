# New features across TiDB, TiKV, PD, TiFlash, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.2.md`
- Source Title: `TiDB 4.0.2 Release Notes`
- Source Heading Path: `TiDB 4.0.2 Release Notes > New Features`
- Source Line Ranges: `29-73`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`
- Topic Tags: `release-notes`, `new-features`, `sql-hints`, `tls`, `collation`, `sql-variables`, `region-splitting`, `coprocessor-pushdown`, `approx-count-distinct`, `inspection-result`, `bind-info`, `plan-cache`, `slow-query-log`, `backup`, `restore`, `encryption-meta`, `perf-context`, `operators`, `arm`, `mq-sink`, `canal`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0178_1fd3fc2468`
- Source ID: `tidb-docs-8.1:releases/release-4.0.2.md#new-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `139c563d7903ab5433f0dc6957acb69d74f05b6d30fe766bafb33099171fd030`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.2#new-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 4.0.2 new features added across TiDB, TiKV, PD, TiFlash, and TiCDC, including SQL features, schema tables, backup and restore statements, and component capabilities.
- Retrieval Keywords: TiDB 4.0.2 New Features, MEMORY_QUOTA(), INSERT statements, SAN field of TLS certificate, REGEXP() collation, sql_select_limit, splitting the Region for the newly added partition, IF() pushdown, BITXOR() pushdown, BITNEG() pushdown, JSON_LENGTH() pushdown, APPROX_COUNT_DISTINCT(), INFORMATION_SCHEMA.INSPECTION_RESULT, STATUS_ADDRESS, MYSQL.BIND_INFO, SOURCE column, PERFORMANCE_SCHEMA.EVENTS_STATEMENTS_SUMMARY_BY_DIGEST, PLAN_IN_CACHE, PLAN_CACHE_HITS, enable-collect-execution-info, tidb_enable_collect_execution_info, slow query log, tidb_slow_log_masking, storage.block-cache.capacity, BACKUP, RESTORE, encryption-meta, TiKV Control, RocksDB::WriteImpl, remove a leader peer, default store limit for TiFlash stores, rough set filter, ARM architecture, TiCDC capture, delete the TiCDC GC TTL, canal protocol, MQ sink
- Follow-up Guidance: 
- Classification Note: This is classified as a release chunk because the official content lists new features introduced in TiDB 4.0.2 across multiple components and tools.

## Official Source Content

## New Features

+ TiDB

    - Support the `MEMORY_QUOTA()` hint in `INSERT` statements [#18101](https://github.com/pingcap/tidb/pull/18101)
    - Support authentication based on the `SAN` field of TLS certificate [#17698](https://github.com/pingcap/tidb/pull/17698)
    - Support collation for the `REGEXP()` function [#17581](https://github.com/pingcap/tidb/pull/17581)
    - Support the `sql_select_limit` session and global variable [#17604](https://github.com/pingcap/tidb/pull/17604)
    - Support splitting the Region for the newly added partition by default [#17665](https://github.com/pingcap/tidb/pull/17665)
    - Support pushing the `IF()`/`BITXOR()`/`BITNEG()`/`JSON_LENGTH()` functions to the TiFlash Coprocessor [#17651](https://github.com/pingcap/tidb/pull/17651) [#17592](https://github.com/pingcap/tidb/pull/17592)
    - Support a new aggregate function `APPROX_COUNT_DISTINCT()` to calculate the approximate result of `COUNT(DISTINCT)` [#18120](https://github.com/pingcap/tidb/pull/18120)
    - Support collation in TiFlash and pushing collation-related functions to TiFlash [#17705](https://github.com/pingcap/tidb/pull/17705)
    - Add the `STATUS_ADDRESS` column in the `INFORMATION_SCHEMA.INSPECTION_RESULT` table to indicate the status address of servers [#17695](https://github.com/pingcap/tidb/pull/17695)
    - Add the `SOURCE` column in the `MYSQL.BIND_INFO` table to indicate the how the bindings are created [#17587](https://github.com/pingcap/tidb/pull/17587)
    - Add the `PLAN_IN_CACHE` and `PLAN_CACHE_HITS` columns in the `PERFORMANCE_SCHEMA.EVENTS_STATEMENTS_SUMMARY_BY_DIGEST` table to indicate the plan cache usage of SQL statements [#17493](https://github.com/pingcap/tidb/pull/17493)
    - Add the `enable-collect-execution-info` configuration item and the `tidb_enable_collect_execution_info` session variable to control whether to collect execution information of each operator and record the information in the slow query log [#18073](https://github.com/pingcap/tidb/pull/18073) [#18072](https://github.com/pingcap/tidb/pull/18072)
    - Add the `tidb_slow_log_masking` global variable to control whether to desensitize the queries in slow query log [#17694](https://github.com/pingcap/tidb/pull/17694)
    - Add a diagnostic rule in the `INFORMATION_SCHEMA.INSPECTION_RESULT` table for the `storage.block-cache.capacity` TiKV configuration item [#17671](https://github.com/pingcap/tidb/pull/17671)
    - Add the `BACKUP` and `RESTORE` SQL statements to back up and restore data [#15274](https://github.com/pingcap/tidb/pull/15274)

+ TiKV

    - Support the `encryption-meta` command in TiKV Control [#8103](https://github.com/tikv/tikv/pull/8103)
    - Add a perf context metric for `RocksDB::WriteImpl` [#7991](https://github.com/tikv/tikv/pull/7991)

+ PD

    - Support the operator to fail immediately when trying to remove a leader peer [#2551](https://github.com/pingcap/pd/pull/2551)
    - Set a suitable default store limit for TiFlash stores [#2559](https://github.com/pingcap/pd/pull/2559)

+ TiFlash

    - Support new aggregation function `APPROX_COUNT_DISTINCT` in Coprocessor
    - Enable the `rough set filter` feature by default
    - Enable TiFlash to run on the ARM architecture
    - Support pushing down the `JSON_LENGTH` function in Coprocessor

+ Tools

    - TiCDC

        - Support migrating sub-tasks to new `capture`s [#665](https://github.com/pingcap/tiflow/pull/665)
        - Add a `cli` command to delete the TiCDC GC TTL [#652](https://github.com/pingcap/tiflow/pull/652)
        - Support canal protocol in MQ sink [#649](https://github.com/pingcap/tiflow/pull/649)
