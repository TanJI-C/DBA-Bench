# 6.5.12 bug fixes for TiDB, TiKV, and PD

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.12.md`
- Source Title: `TiDB 6.5.12 Release Notes`
- Source Heading Path: `TiDB 6.5.12 Release Notes > Bug fixes`
- Source Line Ranges: `86-129`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`
- Topic Tags: `bug-fixes`, `statistics`, `cte`, `startup-panic`, `cost-estimation`, `join-reorder`, `views`, `generated-columns`, `information-schema`, `follower-read`, `stale-reads`, `peer-destruction`, `flow-control`, `leader-migration`, `one-phase-commit`, `async-commit`, `deadlock`, `gc-worker`, `grafana-metrics`, `region-merge`, `region-split`, `encoding`, `gbk`, `gb18030`, `tso`, `memory-leak`, `leader-switch`, `scheduler`, `pd-ctl`, `region-api`, `security-vulnerabilities`, `trace-data`, `etcd-leader-transition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0387_6da339822a`
- Source ID: `tidb-docs-8.1:releases/release-6.5.12.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3981d4ffc2ae5fabb8911e422b732c7a7e7c7ededb24605ee0c4764061a466d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.12#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.12.md

## Retrieval Guidance

- Use When: Use this chunk when searching the TiDB 6.5.12 release notes for specific bug fixes across TiDB, TiKV, PD, or Dashboard involving the listed errors, system tables, metrics, schedulers, or system variables.
- Retrieval Keywords: TiDB 6.5.12 Bug fixes, loading statistics synchronically timeout handled correctly, CTE incorrect database name, TiDB panic during startup invalid data binding, cost estimation INF/NaN Join Reorder, loading statistics manually null values, creating two views with the same name does not report an error, virtual generated column ON UPDATE inconsistent index data, INFORMATION_SCHEMA.TABLES incorrect results, TiKV Follower Read stale data, TiKV panic destroying a peer, RocksDB flow control time rollback, disk stalls prevent leader migration, one-phase commit 1PC Async Commit latest written data not readable, GC Worker heavy load deadlock, Storage async write duration metric inaccurate, RADIANS() DEGREES() TiKV panic, merging Regions TiKV panic, leader could not be quickly elected after Region split, GBK GB18030 encoding fail, PD allocating TSOs memory leak, tidb_enable_tso_follower_proxy not take effect, PD node generate TSOs even when it is not the Leader, Region syncer during PD Leader switch, evict-leader-scheduler grant-leader-scheduler pd-ctl error message, PD Region API cannot be requested when a large number of Regions exist, TiDB Dashboard cannot read PD trace data correctly, etcd leader transition re-elect a leader, Gin Web Framework v1.10.0 security vulnerabilities
- Follow-up Guidance: This chunk groups the 6.5.12 bug fixes by component, including TiDB, TiKV, PD, and a TiDB Dashboard trace-data fix under the PD section.
- Classification Note: The official content is a self-managed release-notes bug-fix summary for TiDB 6.5.12 covering multiple shared components and operational issues.

## Official Source Content

- Fix the issue that the timeout that occurs when loading statistics synchronically might not be handled correctly [#57710](https://github.com/pingcap/tidb/issues/57710) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that an incorrect database name might be returned when parsing the database name in a CTE [#54582](https://github.com/pingcap/tidb/issues/54582) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that TiDB might panic during startup due to invalid data binding [#58016](https://github.com/pingcap/tidb/issues/58016) @[qw4990](https://github.com/qw4990)
    - Fix the issue that cost estimation might generate invalid INF/NaN values in certain extreme cases, which could lead to incorrect Join Reorder results [#56704](https://github.com/pingcap/tidb/issues/56704) @[winoros](https://github.com/winoros)
    - Fix the issue that loading statistics manually might fail when the statistics file contains null values [#53966](https://github.com/pingcap/tidb/issues/53966) @[King-Dylan](https://github.com/King-Dylan)
    - Fix the issue that creating two views with the same name does not report an error [#58769](https://github.com/pingcap/tidb/issues/58769) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that when a virtual generated column's dependencies contain a column with the `ON UPDATE` attribute, the data of the updated row and its index data might be inconsistent [#56829](https://github.com/pingcap/tidb/issues/56829) @[joechenrh](https://github.com/joechenrh)
    - Fix the issue that the `INFORMATION_SCHEMA.TABLES` system table returns incorrect results [#57345](https://github.com/pingcap/tidb/issues/57345) @[tangenta](https://github.com/tangenta)

+ TiKV

    - Fix the issue that Follower Read might read stale data [#17018](https://github.com/tikv/tikv/issues/17018) @[glorv](https://github.com/glorv)
    - Fix the issue that TiKV might panic when destroying a peer [#18005](https://github.com/tikv/tikv/issues/18005) @[glorv](https://github.com/glorv)
    - Fix the issue that time rollback might cause abnormal RocksDB flow control, leading to performance jitter [#17995](https://github.com/tikv/tikv/issues/17995) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that disk stalls might prevent leader migration, leading to performance jitter [#17363](https://github.com/tikv/tikv/issues/17363) @[hhwyt](https://github.com/hhwyt)
    - Fix the issue that the latest written data might not be readable when only one-phase commit (1PC) is enabled and Async Commit is not enabled [#18117](https://github.com/tikv/tikv/issues/18117) @[zyguan](https://github.com/zyguan)
    - Fix the issue that a deadlock might occur when GC Worker is under heavy load [#18214](https://github.com/tikv/tikv/issues/18214) @[zyguan](https://github.com/zyguan)
    - Fix the issue that the **Storage async write duration** monitoring metric on the TiKV panel in Grafana is inaccurate [#17579](https://github.com/tikv/tikv/issues/17579) @[overvenus](https://github.com/overvenus)
    - Fix the issue that TiKV might panic when executing queries containing `RADIANS()` or `DEGREES()` functions [#17852](https://github.com/tikv/tikv/issues/17852) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that merging Regions might cause TiKV to panic in rare cases [#17840](https://github.com/tikv/tikv/issues/17840) @[glorv](https://github.com/glorv)
    - Fix the issue that the leader could not be quickly elected after Region split [#17602](https://github.com/tikv/tikv/issues/17602) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that encoding might fail when processing GBK/GB18030 encoded data [#17618](https://github.com/tikv/tikv/issues/17618) @[CbcWestwolf](https://github.com/CbcWestwolf)

+ PD

    - Fix the issue that memory leaks might occur when allocating TSOs [#9004](https://github.com/tikv/pd/issues/9004) @[rleungx](https://github.com/rleungx)
    - Fix the issue that the `tidb_enable_tso_follower_proxy` system variable might not take effect [#8947](https://github.com/tikv/pd/issues/8947) @[JmPotato](https://github.com/JmPotato)
    - Fix a potential issue that might cause PD to panic [#8915](https://github.com/tikv/pd/issues/8915) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that memory leaks might occur in long-running clusters [#9047](https://github.com/tikv/pd/issues/9047) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that a PD node might still generate TSOs even when it is not the Leader [#9051](https://github.com/tikv/pd/issues/9051) @[rleungx](https://github.com/rleungx)
    - Fix the issue that Region syncer might not exit in time during the PD Leader switch [#9017](https://github.com/tikv/pd/issues/9017) @[rleungx](https://github.com/rleungx)
    - Fix the issue that when creating `evict-leader-scheduler` or `grant-leader-scheduler` encounters an error, the error message is not returned to pd-ctl [#8759](https://github.com/tikv/pd/issues/8759) @[okJiang](https://github.com/okJiang)
    - Fix the memory leak issue in hotspot cache [#8698](https://github.com/tikv/pd/issues/8698) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that PD's Region API cannot be requested when a large number of Regions exist [#55872](https://github.com/pingcap/tidb/issues/55872) @[rleungx](https://github.com/rleungx)
    - Fix the issue that `evict-leader-scheduler` fails to work properly when it is repeatedly created with the same Store ID [#8756](https://github.com/tikv/pd/issues/8756) @[okJiang](https://github.com/okJiang)
    - Upgrade the version of Gin Web Framework from v1.9.1 to v1.10.0 to fix potential security vulnerabilities [#8643](https://github.com/tikv/pd/issues/8643) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that when using a wrong parameter in `evict-leader-scheduler`, PD does not report errors correctly and some schedulers are unavailable [#8619](https://github.com/tikv/pd/issues/8619) @[rleungx](https://github.com/rleungx)
    - Fix the memory leak issue in label statistics [#8700](https://github.com/tikv/pd/issues/8700) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that TiDB Dashboard cannot read PD `trace` data correctly [#7253](https://github.com/tikv/pd/issues/7253) @[nolouch](https://github.com/nolouch)
    - Fix the memory leak issue in Region statistics [#8710](https://github.com/tikv/pd/issues/8710) @[rleungx](https://github.com/rleungx)
    - Fix the issue that PD cannot quickly re-elect a leader during etcd leader transition [#8823](https://github.com/tikv/pd/issues/8823) @[rleungx](https://github.com/rleungx)

+ TiFlash
