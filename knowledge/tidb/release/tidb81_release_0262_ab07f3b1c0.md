# TiDB 5.3.1 bug fixes across database, storage, scheduling, analytics, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.1.md`
- Source Title: `TiDB 5.3.1 Release Notes`
- Source Heading Path: `TiDB 5.3.1 Release Notes > Bug fixes`
- Source Line Ranges: `55-119`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`
- Topic Tags: `release-notes`, `bug-fixes`, `sql-correctness`, `panic`, `latency`, `replication`, `mpp`, `restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0262_ab07f3b1c0`
- Source ID: `tidb-docs-8.1:releases/release-5.3.1.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `98eaceac2e9ae596e7ba28942005e55e20652c7689aad00612f13c545815962e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.3.1 bug fix details for query correctness, panic issues, latency, scheduling, TiFlash behavior, BR restore, or TiCDC-related fixes.
- Retrieval Keywords: TiDB 5.3.1 bug fixes, date_format '\n', alter column set default, tidb_super_read_only, tidb_restricted_read_only, greatest least collation wrong result, MPP task list empty error, index join innerWorker panic, invalid transaction index lookup join, INSERT ... SELECT ... ON DUPLICATE KEY UPDATE panic, peer status Applying snapshot files panic, level0_slowdown_trigger, Resolved TS latency, unsafe_destroy_range, tikv-ctl Region-related information, JointConsensus steps, demoting a voter directly, replication mode of replicas, cold hotspot statistics, cast(arg as decimal(x,y)), max_memory_usage_for_all_queries, str_to_date leading zeros, BR restore Regions unevenly distributed
- Follow-up Guidance: 
- Classification Note: This is a release-notes chunk listing bug fixes in TiDB 5.3.1 across TiDB, TiKV, PD, TiFlash, BR, and TiCDC.

## Official Source Content

## Bug fixes

- TiDB

    - Fix the issue that `date_format` in TiDB handles `'\n'` in a MySQL-incompatible way [#32232](https://github.com/pingcap/tidb/issues/32232)
    - Fix the issue that `alter column set default` wrongly updates the table schema [#31074](https://github.com/pingcap/tidb/issues/31074)
    - Fix a bug that `tidb_super_read_only` is not automatically enabled when `tidb_restricted_read_only` is enabled [#31745](https://github.com/pingcap/tidb/issues/31745)
    - Fix the issue that the `greatest` or `least` function with collation gets a wrong result [#31789](https://github.com/pingcap/tidb/issues/31789)
    - Fix the MPP task list empty error when executing a query [#31636](https://github.com/pingcap/tidb/issues/31636)
    - Fix wrong results of index join caused by an innerWorker panic [#31494](https://github.com/pingcap/tidb/issues/31494)
    - Fix wrong query results after changing the column type from `FLOAT` to `DOUBLE` [#31372](https://github.com/pingcap/tidb/issues/31372)
    - Fix the `invalid transaction` error when executing a query using index lookup join [#30468](https://github.com/pingcap/tidb/issues/30468)
    - Fix wrong query results due to the optimization of `Order By` [#30271](https://github.com/pingcap/tidb/issues/30271)
    - Fix the issue that the configurations of `MaxDays` and `MaxBackups` do not take effect on the slow log [#25716](https://github.com/pingcap/tidb/issues/25716)
    - Fix the issue that executing the `INSERT ... SELECT ... ON DUPLICATE KEY UPDATE` statement gets panic [#28078](https://github.com/pingcap/tidb/issues/28078)

- TiKV

    - Fix the panic issue caused by deleting snapshot files when the peer status is `Applying` [#11746](https://github.com/tikv/tikv/issues/11746)
    - Fix the issue of QPS drop when flow control is enabled and `level0_slowdown_trigger` is set explicitly [#11424](https://github.com/tikv/tikv/issues/11424)
    - Fix the panic issue that occurs when the cgroup controller is not mounted [#11569](https://github.com/tikv/tikv/issues/11569)
    - Fix the issue that the latency of Resolved TS increases after TiKV stops operating [#11351](https://github.com/tikv/tikv/issues/11351)
    - Fix a bug that TiKV cannot delete a range of data (`unsafe_destroy_range` cannot be executed) when the GC worker is busy [#11903](https://github.com/tikv/tikv/issues/11903)
    - Fix the issue that destroying a peer might cause high latency [#10210](https://github.com/tikv/tikv/issues/10210)
    - Fix a bug that the `any_value` function returns a wrong result when regions are empty [#11735](https://github.com/tikv/tikv/issues/11735)
    - Fix the issue that deleting an uninitialized replica might cause an old replica to be recreated [#10533](https://github.com/tikv/tikv/issues/10533)
    - Fix the metadata corruption issue when `Prepare Merge` is triggered after a new election is finished but the isolated peer is not informed [#11526](https://github.com/tikv/tikv/issues/11526)
    - Fix the deadlock issue that happens occasionally when coroutines run too fast [#11549](https://github.com/tikv/tikv/issues/11549)
    - Fix the issue that a down TiKV node causes the resolved timestamp to lag [#11351](https://github.com/tikv/tikv/issues/11351)
    - Fix the issue that batch messages are too large in Raft client implementation [#9714](https://github.com/tikv/tikv/issues/9714)
    - Fix a panic issue that occurs when Region merge, ConfChange, and Snapshot happen at the same time in extreme conditions [#11475](https://github.com/tikv/tikv/issues/11475)
    - Fix the issue that TiKV cannot detect the memory lock when TiKV performs a reverse table scan [#11440](https://github.com/tikv/tikv/issues/11440)
    - Fix the issue that RocksDB flush or compaction causes panic when the disk capacity is full [#11224](https://github.com/tikv/tikv/issues/11224)
    - Fix a bug that tikv-ctl cannot return the correct Region-related information [#11393](https://github.com/tikv/tikv/issues/11393)
    - Fix the issue that the average latency of the by-instance gRPC requests is inaccurate in TiKV metrics [#11299](https://github.com/tikv/tikv/issues/11299)

- PD

    - Fix a bug that the scheduling process has the unnecessary JointConsensus steps in certain cases [#4362](https://github.com/tikv/pd/issues/4362)
    - Fix a bug that the scheduling cannot be executed when demoting a voter directly [#4444](https://github.com/tikv/pd/issues/4444)
    - Fix a data race issue that occurs when updating the configuration of the replication mode of replicas [#4325](https://github.com/tikv/pd/issues/4325)
    - Fix a bug that the Read lock is not released in certain cases [#4354](https://github.com/tikv/pd/issues/4354)
    - Fix the issue that the cold hotspot data cannot be deleted from the hotspot statistics [#4390](https://github.com/tikv/pd/issues/4390)

- TiFlash

    - Fix the issue that `cast(arg as decimal(x,y))` returns a wrong result when the input argument `arg` overflows the range of `decimal(x,y)`
    - Fix the TiFlash crash issue that occurs when `max_memory_usage` and `max_memory_usage_for_all_queries` are enabled
    - Fix the issue that `cast(string as real)` returns a wrong result
    - Fix the issue that `cast(string as decimal)` returns a wrong result
    - Fix potential data inconsistency after altering a primary key column to a larger int data type
    - Fix the bug that when `in` has multiple arguments in the statements like `select (arg0, arg1) in (x,y)`, `in` returns a wrong result
    - Fix the issue that TiFlash might panic when an MPP query is stopped
    - Fix the issue that `str_to_date` returns a wrong result when the input argument has leading zeros
    - Fix the issue that the query returns a wrong result when the filter is in the `where <string>` format
    - Fix the issue that `cast(string as datetime)` returns a wrong result when the input argument `string` is in the `%Y-%m-%d\n%H:%i:%s` format

- Tools

    - Backup & Restore (BR)

        - Fix the potential issue that Regions might be unevenly distributed after a restore operation is finished [#31034](https://github.com/pingcap/tidb/issues/31034)

    - TiCDC
