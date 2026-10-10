# Component improvements across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.0.md`
- Source Title: `TiDB 5.4 Release Notes`
- Source Heading Path: `TiDB 5.4 Release Notes > Improvements`
- Source Line Ranges: `353-408`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`, `dumpling`, `dashboard`
- Topic Tags: `improvements`, `plan-cache`, `coprocessor`, `disk-protection`, `logging`, `hotspot`, `dashboard`, `backup`, `replication`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0276_9fbd8d7435`
- Source ID: `tidb-docs-8.1:releases/release-5.4.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f2ae89b662ec43c2994bfe7f382174c107fda1a36d71c7b5357f8332ca0b1900`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.4 improvement summaries across TiDB, TiKV, PD, TiFlash, and tools such as BR, TiCDC, DM, Lightning, and Dumpling.
- Retrieval Keywords: ADMIN {SESSION | INSTANCE | GLOBAL} PLAN_CACHE, clear the cached query plan, paging API, read-through-lock, disk protection mechanism, archiving and rotating logs, Raft client, substring pushdown, Read Committed isolation level, backup operations thread pool, Apply thread pool, Store thread pool, snap-generator, historic hotspot information, HTTP component signature, TiDB Dashboard v2021.12.31, local operators, gRPC thread count, encrypted backup key validity check, EventFeed retry rate limited, replication latency many tables, KV client recover store down, relay is enabled CPU, optimistic transactions by default, TiDB-backend mode, Dumpling checks the database version, default collation, CREATE DATABASE, CREATE TABLE
- Follow-up Guidance: 
- Classification Note: This is a release-note chunk listing cross-component improvements in TiDB 5.4.0 rather than a single feature workflow or procedure.

## Official Source Content

## Improvements

+ TiDB

    - Support the `ADMIN {SESSION | INSTANCE | GLOBAL} PLAN_CACHE` syntax to clear the cached query plan [#30370](https://github.com/pingcap/tidb/pull/30370)

+ TiKV

    - Coprocessor supports paging API to process requests in a stream-like way [#11448](https://github.com/tikv/tikv/issues/11448)
    - Support `read-through-lock` so that read operations do not need to wait for secondary locks to be resolved [#11402](https://github.com/tikv/tikv/issues/11402)
    - Add a disk protection mechanism to avoid panic caused by disk space drainage [#10537](https://github.com/tikv/tikv/issues/10537)
    - Support archiving and rotating logs [#11651](https://github.com/tikv/tikv/issues/11651)
    - Reduce the system call by the Raft client and increase CPU efficiency [#11309](https://github.com/tikv/tikv/issues/11309)
    - Coprocessor supports pushing down substring to TiKV [#11495](https://github.com/tikv/tikv/issues/11495)
    - Improve the scan performance by skip reading locks in the Read Committed isolation level [#11485](https://github.com/tikv/tikv/issues/11485)
    - Reduce the default thread pool size used by backup operations and limit the use of thread pool when the stress is high [#11000](https://github.com/tikv/tikv/issues/11000)
    - Support dynamically adjusting the sizes of the Apply thread pool and the Store thread pool [#11159](https://github.com/tikv/tikv/issues/11159)
    - Support configuring the size of the `snap-generator` thread pool [#11247](https://github.com/tikv/tikv/issues/11247)
    - Optimize the issue of global lock race that occurs when there are many files with frequent reads and writes [#250](https://github.com/tikv/rocksdb/pull/250)

+ PD

    - Record the historic hotspot information by default [#25281](https://github.com/pingcap/tidb/issues/25281)
    - Add signature for the HTTP component to identify the request source [#4490](https://github.com/tikv/pd/issues/4490)
    - Update TiDB Dashboard to v2021.12.31 [#4257](https://github.com/tikv/pd/issues/4257)

+ TiFlash

    - Optimize the communication of local operators
    - Increase the non-temporary thread count of gRPC to avoid the frequent creation or destruction of threads

+ Tools

    + Backup & Restore (BR)

        - Add a validity check for the key when BR performs encrypted backup [#29794](https://github.com/pingcap/tidb/issues/29794)

    + TiCDC

        - Reduce the count of "EventFeed retry rate limited" logs [#4006](https://github.com/pingcap/tiflow/issues/4006)
        - Reduce the replication latency when replicating many tables [#3900](https://github.com/pingcap/tiflow/issues/3900)
        - Reduce the time for the KV client to recover when a TiKV store is down [#3191](https://github.com/pingcap/tiflow/issues/3191)

    + TiDB Data Migration (DM)

        - Lower the usage rate of CPU when the relay is enabled [#2214](https://github.com/pingcap/dm/issues/2214)

    + TiDB Lightning

        - Use optimistic transactions by default to write data to improve performance in TiDB-backend mode [#30953](https://github.com/pingcap/tidb/pull/30953)

    + Dumpling

        - Improve compatibility when Dumpling checks the database version [#29500](https://github.com/pingcap/tidb/pull/29500)
        - Add the default collation when dumping `CREATE DATABASE` and `CREATE TABLE` [#3420](https://github.com/pingcap/tiflow/issues/3420)
