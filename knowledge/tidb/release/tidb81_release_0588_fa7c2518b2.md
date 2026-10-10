# Bug fixes for PD, TiFlash, and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Bug fixes`
- Source Line Ranges: `526-565`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tiflash`, `br`, `tikv`, `tidb`
- Topic Tags: `bug-fixes`, `pd`, `tiflash`, `backup-restore`, `stability`, `replica-migration`, `pitr`, `flashback`, `log-backup`, `restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0588_fa7c2518b2`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `238a7be1d54b3b27d6ba91a4a398814da39a4849192ec9585b4613dfaf40fd2f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.0.0 bug fixes in PD, TiFlash, or BR related to TSO, schedulers, monitoring metrics, TLS inconsistency, replica migration, PITR, FLASHBACK CLUSTER TO, log backup, or restore behavior.
- Retrieval Keywords: TiDB 8.0.0 bug fixes, PD MergeLabels data race, evict-leader-scheduler no output, learner-peer-count leader switch, watch etcd memory leak, TSO logs error cause, negative monitoring metrics after restart, Leader lease expires later than log time, TLS switches between TiDB and PD are inconsistent, pd-ctl cannot remove a scheduler that contains special characters, PD client blocked when obtaining TSO, TiFlash panic unstable network connections with PD during replica migration, TiFlash memory usage increases significantly due to slow queries, removing and then re-adding TiFlash replicas data corruption, TiFlash replica data accidentally deleted after PITR, FLASHBACK CLUSTER TO data anomalies, ALTER TABLE ... MODIFY COLUMN ... NOT NULL TiFlash panics, disaggregated storage and compute architecture queries permanently blocked after network isolation, TiFlash panic during shutdown, remote reads data race, CAST(AS JSON) does not de-duplicate the JSON object key, ENUM column crash during chunk encoding, BR log backup checkpoint gets stuck, Region is split or merged immediately after it becomes a leader, TiKV panics when a full backup fails to find a peer, log backup gets stuck after changing the TiKV IP address, BR cannot retry while reading file content from S3, the target cluster is not fresh, stopping a log backup task causes TiDB to crash, data restore is slowed down due to absence of a leader on a TiKV node, full restore still requires the target cluster to be empty, --filter option
- Follow-up Guidance: 
- Classification Note: The official content is a release-notes bug-fix list for PD, TiFlash, and Backup & Restore in TiDB 8.0.0.

## Official Source Content

- Fix the issue that data race occurs when the `MergeLabels` function is called [#7535](https://github.com/tikv/pd/issues/7535) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that there is no output when the `evict-leader-scheduler` interface is called [#7672](https://github.com/tikv/pd/issues/7672) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that the PD monitoring item `learner-peer-count` does not synchronize the old value after a leader switch [#7728](https://github.com/tikv/pd/issues/7728) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the memory leak issue that occurs when `watch etcd` is not turned off correctly [#7807](https://github.com/tikv/pd/issues/7807) @[rleungx](https://github.com/rleungx)
    - Fix the issue that some TSO logs do not print the error cause [#7496](https://github.com/tikv/pd/issues/7496) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that there are unexpected negative monitoring metrics after restart [#4489](https://github.com/tikv/pd/issues/4489) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that the Leader lease expires later than the log time [#7700](https://github.com/tikv/pd/issues/7700) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that TiDB panics when TLS switches between TiDB (the PD client) and PD are inconsistent [#7900](https://github.com/tikv/pd/issues/7900) [#7902](https://github.com/tikv/pd/issues/7902) [#7916](https://github.com/tikv/pd/issues/7916) @[CabinfeverB](https://github.com/CabinfeverB)
    - Fix the issue that Goroutine leaks when it is not closed properly [#7782](https://github.com/tikv/pd/issues/7782) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that pd-ctl cannot remove a scheduler that contains special characters [#7798](https://github.com/tikv/pd/issues/7798) @[JmPotato](https://github.com/JmPotato)
    - Fix the issue that the PD client might be blocked when obtaining TSO [#7864](https://github.com/tikv/pd/issues/7864) @[CabinfeverB](https://github.com/CabinfeverB)

+ TiFlash

    - Fix the issue that TiFlash might panic due to unstable network connections with PD during replica migration [#8323](https://github.com/pingcap/tiflash/issues/8323) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that the memory usage increases significantly due to slow queries [#8564](https://github.com/pingcap/tiflash/issues/8564) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that removing and then re-adding TiFlash replicas might lead to data corruption in TiFlash [#8695](https://github.com/pingcap/tiflash/issues/8695) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash replica data might be accidentally deleted after performing point-in-time recovery (PITR) or executing `FLASHBACK CLUSTER TO`, which might result in data anomalies [#8777](https://github.com/pingcap/tiflash/issues/8777) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash panics after executing `ALTER TABLE ... MODIFY COLUMN ... NOT NULL`, which changes nullable columns to non-nullable [#8419](https://github.com/pingcap/tiflash/issues/8419) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that in the disaggregated storage and compute architecture, queries might be permanently blocked after network isolation [#8806](https://github.com/pingcap/tiflash/issues/8806) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that in the disaggregated storage and compute architecture, TiFlash might panic during shutdown [#8837](https://github.com/pingcap/tiflash/issues/8837) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might crash due to data race in case of remote reads [#8685](https://github.com/pingcap/tiflash/issues/8685) @[solotzg](https://github.com/solotzg)
    - Fix the issue that the `CAST(AS JSON)` function does not de-duplicate the JSON object key [#8712](https://github.com/pingcap/tiflash/issues/8712) @[SeaRise](https://github.com/SeaRise)
    - Fix the issue that the `ENUM` column might cause TiFlash to crash during chunk encoding [#8674](https://github.com/pingcap/tiflash/issues/8674) @[yibin87](https://github.com/yibin87)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the log backup checkpoint gets stuck when a Region is split or merged immediately after it becomes a leader [#16469](https://github.com/tikv/tikv/issues/16469) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that TiKV panics when a full backup fails to find a peer in some extreme cases [#16394](https://github.com/tikv/tikv/issues/16394) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that log backup gets stuck after changing the TiKV IP address on the same node [#50445](https://github.com/pingcap/tidb/issues/50445) @[3pointer](https://github.com/3pointer)
        - Fix the issue that BR cannot retry when encountering an error while reading file content from S3 [#49942](https://github.com/pingcap/tidb/issues/49942) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that when resuming from a checkpoint after data restore fails, an error `the target cluster is not fresh` occurs [#50232](https://github.com/pingcap/tidb/issues/50232) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that stopping a log backup task causes TiDB to crash [#50839](https://github.com/pingcap/tidb/issues/50839) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that data restore is slowed down due to absence of a leader on a TiKV node [#50566](https://github.com/pingcap/tidb/issues/50566) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that full restore still requires the target cluster to be empty after the `--filter` option is specified [#51009](https://github.com/pingcap/tidb/issues/51009) @[3pointer](https://github.com/3pointer)

    + TiCDC
