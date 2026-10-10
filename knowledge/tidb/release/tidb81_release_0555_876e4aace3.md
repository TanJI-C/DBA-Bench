# Bug fixes across TiDB, TiKV, PD, TiFlash, BR, TiCDC, Lightning, and NG Monitoring

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.7.md`
- Source Title: `TiDB 7.5.7 Release Notes`
- Source Heading Path: `TiDB 7.5.7 Release Notes > Bug fixes`
- Source Line Ranges: `109-167`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `dashboard`, `tiflash`, `br`, `ticdc`, `lightning`
- Topic Tags: `bug-fixes`, `sql`, `indexes`, `deadlock`, `unsafe-recovery`, `compression`, `sst-ingest`, `grafana`, `timezone`, `metrics`, `shutdown`, `scheduling`, `tso`, `import-into`, `restore`, `pitr`, `log-backup`, `changefeed`, `kafka`, `checkpoint`, `parquet`, `rpc-timeout`, `tsdb`, `memory`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0555_876e4aace3`
- Source ID: `tidb-docs-8.1:releases/release-7.5.7.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d76a340653a36c95bf738cd5e18d10f3d6e000b70198e3abc2b109b73b70dbe1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.7#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.7.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.7 bug fixes across TiDB, TiKV, PD, TiFlash, BR, TiCDC, TiDB Lightning, or NG Monitoring for issues involving SQL checks, indexes, deadlocks, scheduling, TSO, restore, changefeed, Kafka, Parquet import, RPC timeouts, or TSDB memory.
- Retrieval Keywords: TiDB 7.5.7 Release Notes bug fixes, ADMIN CHECK returns success after internal SQL executions fail, #61612, data and indexes became inconsistent after adding multiple indexes through multi-schema change, #61255, deadlock during CPU profiling, #18474, Online Unsafe Recovery blocked by certain TiFlash replicas, #18197, compression algorithm that the client cannot decode, #18079, excessive SST ingest requests under high concurrency, #18452, Ingestion picked level displayed incorrectly in the TiKV dashboard in Grafana, #15990, unexpected Server is busy error after TiKV restarts, #18233, time zone incorrectly for Brazil and Egypt, #16220, incorrect thread memory metrics, #18125, manual compaction tasks during graceful shutdown, #18396, split-merge-interval might not take effect when modified repeatedly, #8404, default value of lease is not correctly set, #9156, TiDB Dashboard TCP connections could lead to PD goroutine leaks, #9402, newly added TiKV nodes might fail to be scheduled, #9145, tidb_enable_tso_follower_proxy might cause the TSO service to become unavailable, #9188, IMPORT INTO or BR restore accidental deletion of SST files during TiFlash panic, #10141, expression index ((NULL)) causes TiFlash to panic, #9891, Exception: Block schema mismatch GROUP BY WITH ROLLUP, #10110, PITR fails to restore indexes larger than 3072 bytes, #58430, log backup uploads to Azure Blob Storage are slow, #18410, BR filtering tables with -f does not check whether the corresponding table exists, #61592, changefeed might get stuck using external storage as the downstream, #9162, changefeed might get stuck after replication traffic exceeds downstream Kafka threshold, #12110, --overwrite-checkpoint-ts in changefeed pause might cause the changefeed to be stuck, #12055, resolved ts lag keeps increasing after scaling in or out TiKV nodes on the same IP address because of outdated store IDs, #12162, TiDB Lightning stuck for several hours when importing Parquet files from cloud storage, #60224, context deadline exceeded when the RPC request to TiKV times out, #61326, TSDB consumes too much memory under high cardinality of time series data, #295
- Follow-up Guidance: The source groups the fixes by component: TiDB, TiKV, PD, TiFlash, BR, TiCDC, TiDB Lightning, and NG Monitoring.
- Classification Note: This chunk is classified as a self-managed release note because the official content is the TiDB 7.5.7 release notes section listing bug fixes by component.

## Official Source Content

- Fix the issue that `ADMIN CHECK` still returns success even after some internal SQL executions fail [#61612](https://github.com/pingcap/tidb/issues/61612) @[joechenrh](https://github.com/joechenrh)
    - Fix the issue that data and indexes became inconsistent after adding multiple indexes through multi-schema change [#61255](https://github.com/pingcap/tidb/issues/61255) @[tangenta](https://github.com/tangenta)

+ TiKV

    - Fix the issue that a deadlock might be triggered during CPU profiling [#18474](https://github.com/tikv/tikv/issues/18474) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that Online Unsafe Recovery might be blocked by certain TiFlash replicas, preventing the commit index from advancing [#18197](https://github.com/tikv/tikv/issues/18197) @[v01dstar](https://github.com/v01dstar)
    - Fix the issue that TiKV might use a compression algorithm that the client cannot decode [#18079](https://github.com/tikv/tikv/issues/18079) @[ekexium](https://github.com/ekexium)
    - Fix the issue that TiKV allows excessive SST ingest requests under high concurrency [#18452](https://github.com/tikv/tikv/issues/18452) @[hbisheng](https://github.com/hbisheng)
    - Fix the issue that `Ingestion picked level` and `Compaction Job Size(files)` are displayed incorrectly in the TiKV dashboard in Grafana [#15990](https://github.com/tikv/tikv/issues/15990) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that the unexpected `Server is busy` error occurs after TiKV restarts [#18233](https://github.com/tikv/tikv/issues/18233) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that TiKV converts the time zone incorrectly for Brazil and Egypt [#16220](https://github.com/tikv/tikv/issues/16220) @[overvenus](https://github.com/overvenus)
    - Fix misleading descriptions in `StoreMsg` log entries in slow logs [#18561](https://github.com/tikv/tikv/issues/18561) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix incorrect thread memory metrics [#18125](https://github.com/tikv/tikv/issues/18125) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that TiKV fails to terminate ongoing manual compaction tasks during graceful shutdown [#18396](https://github.com/tikv/tikv/issues/18396) @[LykxSassinator](https://github.com/LykxSassinator)

+ PD

    - Fix the issue that the `split-merge-interval` configuration item might not take effect when you modify its value repeatedly (such as changing it from `1s` to `1h` and back to `1s`) [#8404](https://github.com/tikv/pd/issues/8404) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that the default value of `lease` is not correctly set [#9156](https://github.com/tikv/pd/issues/9156) @[rleungx](https://github.com/rleungx)
    - Fix the issue that improperly closing TiDB Dashboard TCP connections could lead to PD goroutine leaks [#9402](https://github.com/tikv/pd/issues/9402) @[baurine](https://github.com/baurine)
    - Fix the issue that newly added TiKV nodes might fail to be scheduled [#9145](https://github.com/tikv/pd/issues/9145) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that enabling `tidb_enable_tso_follower_proxy` might cause the TSO service to become unavailable [#9188](https://github.com/tikv/pd/issues/9188) @[Tema](https://github.com/Tema)

+ TiFlash

    - Fix the panic issue caused by accidental deletion of SST files during running `IMPORT INTO` or `BR restore` [#10141](https://github.com/pingcap/tiflash/issues/10141) @[CalvinNeo](https://github.com/CalvinNeo)
    - Fix the issue that creating an expression index in the form of `((NULL))` causes TiFlash to panic [#9891](https://github.com/pingcap/tiflash/issues/9891) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might panic when handling snapshots with irregular Region key-ranges [#10147](https://github.com/pingcap/tiflash/issues/10147) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might consume a large amount of memory when tables in a cluster contain a large number of `ENUM` type columns [#9947](https://github.com/pingcap/tiflash/issues/9947) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might fail to restart after inserting a single row of data larger than 16 MiB [#10052](https://github.com/pingcap/tiflash/issues/10052) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that missing resource control low token signals lead to query throttling [#10137](https://github.com/pingcap/tiflash/issues/10137) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TiFlash might return the `Exception: Block schema mismatch` error when executing SQL statements containing `GROUP BY ... WITH ROLLUP` [#10110](https://github.com/pingcap/tiflash/issues/10110) @[gengliqi](https://github.com/gengliqi)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that PITR fails to restore indexes larger than 3072 bytes [#58430](https://github.com/pingcap/tidb/issues/58430) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that log backup uploads to Azure Blob Storage are slow when transferring large volumes of data [#18410](https://github.com/tikv/tikv/issues/18410) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that BR does not check whether the corresponding table exists in the cluster when filtering tables with `-f` [#61592](https://github.com/pingcap/tidb/issues/61592) @[RidRisR](https://github.com/RidRisR)

    + TiCDC

        - Fix the issue that the changefeed might get stuck when using external storage as the downstream [#9162](https://github.com/pingcap/tiflow/issues/9162) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the changefeed might get stuck after the replication traffic exceeds the traffic threshold of the downstream Kafka [#12110](https://github.com/pingcap/tiflow/issues/12110) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that using the `--overwrite-checkpoint-ts` parameter in the `changefeed pause` command might cause the changefeed to be stuck [#12055](https://github.com/pingcap/tiflow/issues/12055) @[hongyunyan](https://github.com/hongyunyan)
        - Fix the issue that evaluating event filter expressions on tables containing virtual columns might cause a panic [#12206](https://github.com/pingcap/tiflow/issues/12206) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue of case-sensitive matching for column and index names in the dispatcher configuration [#12103](https://github.com/pingcap/tiflow/issues/12103) @[wk989898](https://github.com/wk989898)
        - Fix the issue that the resolved ts lag keeps increasing after scaling in or out TiKV nodes on the same IP address because of outdated store IDs [#12162](https://github.com/pingcap/tiflow/issues/12162) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning can get stuck for several hours when importing Parquet files from cloud storage into TiDB [#60224](https://github.com/pingcap/tidb/issues/60224) @[joechenrh](https://github.com/joechenrh)
        - Fix the issue that TiDB Lightning returns the `context deadline exceeded` error when the RPC request to TiKV times out [#61326](https://github.com/pingcap/tidb/issues/61326) @[OliverS929](https://github.com/OliverS929)

    + NG Monitoring
        - Fix the issue that TSDB consumes too much memory under high cardinality of time series data, and provide a memory configuration option for TSDB [#295](https://github.com/pingcap/ng-monitoring/issues/295) @[mornyx](https://github.com/mornyx)
