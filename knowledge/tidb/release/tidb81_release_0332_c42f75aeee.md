# Bug fixes for TiKV and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > Bug fixes`
- Source Line Ranges: `413-435`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `br`, `pd`
- Topic Tags: `bug-fixes`, `pessimistic-transactions`, `async-commit`, `api-version`, `region-size`, `pd-reconnect`, `type-conversion`, `time-parsing`, `rocksdb`, `configuration-validation`, `region-split`, `region-merge`, `statistics`, `encryption-keys`, `qps`, `backup-rate-limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0332_c42f75aeee`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9743c40a545727d49687703fdc6505734a7c1b232fea3b3f77b930bba12a5cc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.2.0 bug fixes in TiKV or BR related to pessimistic transactions, async commit, PD reconnects, Region split or merge panics, configuration validation, statistics analysis, encryption keys, QPS drop, or BR backup rate limit behavior.
- Retrieval Keywords: TiDB 6.2.0 bug fixes, TiKV bug fixes, BR bug fixes, WriteConflict pessimistic transactions, duplicate commit records async commit, storage.api-version 1 to 2 panic, inconsistent Region size configuration TiKV PD, TiKV keeps reconnecting PD clients, empty string type conversion panic, DATETIME fraction Z time parsing error, Apply operator perf context RocksDB coarse-grained, backup import cdc invalid configuration fails to start, peer being split and destroyed panic, source peer catches up logs by snapshot Region merge panic, analyzing statistics max_sample_size 0 panic, encryption keys not cleaned up Raft Engine, get_valid_int_prefix incompatible with TiDB, FLOAT incorrectly converted to INT, Commit Log Duration of a new Region too high QPS drop, PD does not reconnect to TiKV after Region heartbeat is interrupted, BR does not reset the rate limit after finishing a rate-limited backup task
- Follow-up Guidance: The chunk also notes a BR fix where the rate limit is not reset after a rate-limited backup task finishes.
- Classification Note: This is a release-note bug-fix summary for TiKV and BR in TiDB 6.2.0, listing corrected issues and the affected components or behaviors.

## Official Source Content

- Avoid reporting `WriteConflict` errors in pessimistic transactions [#11612](https://github.com/tikv/tikv/issues/11612) @[sticnarf](https://github.com/sticnarf)
    - Fix the possible duplicate commit records in pessimistic transactions when async commit is enabled [#12615](https://github.com/tikv/tikv/issues/12615) @[sticnarf](https://github.com/sticnarf)
    - Fix the issue that TiKV panics when modifying the `storage.api-version` from `1` to `2` [#12600](https://github.com/tikv/tikv/issues/12600) @[pingyu](https://github.com/pingyu)
    - Fix the issue of inconsistent Region size configuration between TiKV and PD [#12518](https://github.com/tikv/tikv/issues/12518) @[5kbpers](https://github.com/5kbpers)
    - Fix the issue that TiKV keeps reconnecting PD clients [#12506](https://github.com/tikv/tikv/issues/12506), [#12827](https://github.com/tikv/tikv/issues/12827) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that TiKV panics when performing type conversion for an empty string [#12673](https://github.com/tikv/tikv/issues/12673) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue of time parsing error that occurs when the `DATETIME` values contain a fraction and `Z` [#12739](https://github.com/tikv/tikv/issues/12739) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that the perf context written by the Apply operator to TiKV RocksDB is coarse-grained [#11044](https://github.com/tikv/tikv/issues/11044) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that TiKV fails to start when the configuration of [backup](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#backup)/[import](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#import)/[cdc](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#cdc) is invalid [#12771](https://github.com/tikv/tikv/issues/12771) @[3pointer](https://github.com/3pointer)
    - Fix the panic issue that might occur when a peer is being split and destroyed at the same time [#12825](https://github.com/tikv/tikv/issues/12825) @[BusyJay](https://github.com/BusyJay)
    - Fix the panic issue that might occur when the source peer catches up logs by snapshot in the Region merge process [#12663](https://github.com/tikv/tikv/issues/12663) @[BusyJay](https://github.com/BusyJay)
    - Fix the panic issue caused by analyzing statistics when `max_sample_size` is set to `0` [#11192](https://github.com/tikv/tikv/issues/11192) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that encryption keys are not cleaned up when Raft Engine is enabled [#12890](https://github.com/tikv/tikv/issues/12890) @[tabokie](https://github.com/tabokie)
    - Fix the issue that the `get_valid_int_prefix` function is incompatible with TiDB. For example, the `FLOAT` type was incorrectly converted to `INT` [#13045](https://github.com/tikv/tikv/issues/13045) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the Commit Log Duration of a new Region is too high, which causes QPS to drop [#13077](https://github.com/tikv/tikv/issues/13077) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that PD does not reconnect to TiKV after the Region heartbeat is interrupted [#12934](https://github.com/tikv/tikv/issues/12934) @[bufferflies](https://github.com/bufferflies)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that BR does not reset the rate limit after finishing a rate-limited backup task [#31722](https://github.com/pingcap/tidb/issues/31722) @[MoCuishle28](https://github.com/MoCuishle28)
