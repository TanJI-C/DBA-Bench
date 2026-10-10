# TiDB 4.0 GA bug fixes across TiDB, TiFlash, TiKV, PD, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0-ga.md`
- Source Title: `TiDB 4.0 GA Release Notes`
- Source Heading Path: `TiDB 4.0 GA Release Notes > Bug Fixes`
- Source Line Ranges: `66-116`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `tikv`, `pd`, `br`, `ticdc`
- Topic Tags: `release-notes`, `bug-fixes`, `upgrade`, `partition-pruning`, `monitoring`, `gc`, `encryption`, `network`, `restore`, `cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0142_8fe5febde9`
- Source ID: `tidb-docs-8.1:releases/release-4.0-ga.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c3900e305a7ef6749447008692de6140abd24f53253c2c01abe27520574c9cd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0-ga#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB 4.0 GA bug fixes related to upgrade failure with `mysql.user`, partition pruning and partition selection issues, `Index Merge Join`, Grafana `SELECT` duration metrics, `isolation-read`, TiFlash timeout or `Too Many Pings` issues, TiKV encryption and `DefaultNotFound` fixes, PD scheduler deletion 404 errors, BR cloud storage restore failures, or TiCDC panic, blockage, and CLI-to-PD connectivity issues.
- Retrieval Keywords: TiDB 4.0 GA, Bug Fixes, mysql.user, upgrade failure from v3.1.1 to v4.0, partition pruning, signed and unsigned integers, update statement, Index Merge Join, Grafana, duration, SELECT statement, GC worker, UNIQUE, boolean column, tidb_opt_agg_push_down, isolation-read, tidb.toml, hint, stream aggregation, DIV, TiFlash, batch commands, timeouts, DROP DATABASE, Server_info, Too Many Pings, batch coprocessor, deploy path, TiKV, DefaultNotFound, BR, ReadIndex, master key, storage encryption, lock cf, PD, evict-leader-scheduler, grant-leader-scheduler, pd-ctl, presplit, TiFlash replica, BR restores data from cloud storage, TiCDC, data race, resource leaks, system blockages, CLI cannot connect to PD
- Follow-up Guidance: This chunk also includes multiple system panic fixes across TiDB, TiKV, and TiCDC, plus PD `pd-ctl` scheduler deletion behavior fixes.
- Classification Note: The official content is a release-notes bug-fix section covering TiDB, TiFlash, TiKV, PD, BR, and TiCDC issues in TiDB 4.0 GA.

## Official Source Content

## Bug Fixes

* TiDB

    - Fix the issue of unexpected timeouts when sending and receiving messages by disabling TiDB to send batch commands to TiFlash [#17307](https://github.com/pingcap/tidb/pull/17307)
    - Fix the issue of incorrectly distinguishing signed and unsigned integers during partition pruning, which improves performance [#17230](https://github.com/pingcap/tidb/pull/17230)
    - Fix the issue of upgrade failure from v3.1.1 to v4.0 because of the incompatible `mysql.user` table [#17300](https://github.com/pingcap/tidb/pull/17300)
    - Fix the issue of incorrect selection of the partition in the `update` statement [#17305](https://github.com/pingcap/tidb/pull/17305)
    - Fix system panics when receiving an unknown error message from TiKV [#17380](https://github.com/pingcap/tidb/pull/17380)
    - Fix system panics caused by incorrect processing logic when creating the table that is `key` partitioned [#17242](https://github.com/pingcap/tidb/pull/17242)
    - Fix the issue that the wrong `Index Merge Join` plan is selected because of incorrect optimizer processing logic [#17365](https://github.com/pingcap/tidb/pull/17365)
    - Fix the issue of inaccurate `duration` monitoring metric of the `SELECT` statement in Grafana [#16561](https://github.com/pingcap/tidb/pull/16561)
    - Fix the issue that the GC worker is blocked when the system error occurs [#16915](https://github.com/pingcap/tidb/pull/16915)
    - Fix the issue that the `UNIQUE` constraint on a boolean column results in an incorrect result in a comparison [#17306](https://github.com/pingcap/tidb/pull/17306)
    - Fix system panics caused by incorrect processing logic when `tidb_opt_agg_push_down` is enabled and the aggregation function pushes down the partitioned table [#17328](https://github.com/pingcap/tidb/pull/17328)
    - Fix the issue of accessing failed TiKV nodes in some cases [#17342](https://github.com/pingcap/tidb/pull/17342)
    - Fix the issue that the `isolation-read` configuration item in `tidb.toml` does not take effect [#17322](https://github.com/pingcap/tidb/pull/17322)
    - Fix the issue of incorrect order of output results due to incorrect processing logic when `hint` is used to enforce the stream aggregation [#17347](https://github.com/pingcap/tidb/pull/17347)
    - Fix the behavior that `insert` processes DIV under different `SQL_MODE` [#17314](https://github.com/pingcap/tidb/pull/17314)

* TiFlash

    - Fix the issue that the matching behavior of regular expressions in the search log feature is inconsistent with other components
    - Fix the issue of excessive restart time when nodes write large amounts of data by disabling the delay processing optimization of `Raft Compact Log Command` by default
    - Fix the issue that the system fails to start because TiDB incorrectly processes the `DROP DATABASE` statement in some scenarios
    - Fix the issue that the method of collecting CPU information in `Server_info` is different from that in other components
    - Fix the issue that the error `Too Many Pings` is reported when the `Query` statement is executed if `batch coprocessor` is enabled
    - Fix the issue that Dashboard fails to display the correct `deploy path` information because TiFlash does not report the related information

* TiKV

    - Fix the `DefaultNotFound` error that occurs when backing up using BR  [#7937](https://github.com/tikv/tikv/pull/7937)
    - Fix system panics caused by out-of-order `ReadIndex` packets [#7930](https://github.com/tikv/tikv/pull/7930)
    - Fix the issue that an unexpected error is returned because the read request callback function is not called [#7921](https://github.com/tikv/tikv/pull/7921)
    - Fix system panics caused by incorrectly removing snapshot files when TiKV is restarted [#7927](https://github.com/tikv/tikv/pull/7927)
    - Fix the issue that the `master key` cannot be rotated due to incorrect processing logic in storage encryption [#7898](https://github.com/tikv/tikv/pull/7898)
    - Fix the issue that the received `lock cf` file of the snapshot is not encrypted when the storage encryption is enabled [#7922](https://github.com/tikv/tikv/pull/7922)

* PD

    - Fix the 404 error when deleting `evict-leader-scheduler` or `grant-leader-scheduler` using pd-ctl [#2446](https://github.com/pingcap/pd/pull/2446)
    - Fix the issue that the `presplit` feature might not work properly when the TiFlash replica exists [#2447](https://github.com/pingcap/pd/pull/2447)

* Tools

    + Backup & Restore (BR)
        - Fix the issue that the data restoration fails due to network issues when BR restores data from cloud storage [#298](https://github.com/pingcap/br/pull/298)
    + TiCDC
        - Fix system panics caused by data race [#565](https://github.com/pingcap/tiflow/pull/565) [#566](https://github.com/pingcap/tiflow/pull/566)
        - Fix resource leaks or system blockages caused by incorrect processing logic [#574](https://github.com/pingcap/tiflow/pull/574) [#586](https://github.com/pingcap/tiflow/pull/586)
        - Fix the issue that the command line gets stuck because CLI cannot connect to PD [#579](https://github.com/pingcap/tiflow/pull/579)
