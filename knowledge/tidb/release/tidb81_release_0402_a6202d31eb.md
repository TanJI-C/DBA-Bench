# TiDB 6.5.5 release notes improvements and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.5.md`
- Source Title: `TiDB 6.5.5 Release Notes`
- Source Heading Path: `TiDB 6.5.5 Release Notes | TiDB 6.5.5 Release Notes > Improvements | TiDB 6.5.5 Release Notes > Bug fixes`
- Source Line Ranges: `5-76`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `br`, `ticdc`, `lightning`
- Topic Tags: `release-notes`, `improvements`, `bug-fixes`, `optimizer-hints`, `stale-read`, `schema-cache`, `pd-client`, `monitoring-metrics`, `safe-ts`, `resolved-ts`, `pitr`, `log-backup`, `unsafe-recovery`, `scatter-region`, `replication-latency`, `csv-format`, `sasl`, `password-logging`, `leader-switching`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0402_a6202d31eb`
- Source ID: `tidb-docs-8.1:releases/release-6.5.5.md#tidb-6-5-5-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bb6d935dfa31a2128d1431b973519c152bf88c9fb6f085f44b56390cb392e499`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.5#tidb-6-5-5-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 6.5.5 release notes summary of improvements and bug fixes across TiDB, TiKV, PD, BR, TiCDC, and TiDB Lightning.
- Retrieval Keywords: TiDB 6.5.5 Release Notes, 6.5.5 improvements, 6.5.5 bug fixes, NO_MERGE_JOIN(), NO_INDEX_JOIN(), NO_INDEX_MERGE_JOIN(), NO_HASH_JOIN(), NO_INDEX_HASH_JOIN(), request source information related to the coprocessor, PD client backoff mechanism, monitoring metrics for snapshots, safe-ts, resolved-ts, log backup resolve lock, Stale Read unavailable replica, Schema Cache, Blob file deleted twice, Online Unsafe Recovery, merge abort, scheduler takes a long time to start up, Scatter Region, empty-region-count, PITR, meta-kv, GCS, TiCDC replication latency, CSV format, SASL authentication, user passwords are recorded in some logs, PD Leader is switched, TiDB Lightning fails to start
- Follow-up Guidance: The content groups the listed changes under Improvements and Bug fixes for TiDB, TiKV, PD, BR, TiCDC, and TiDB Lightning in TiDB 6.5.5.
- Classification Note: This is a release-notes chunk because the official content enumerates version 6.5.5 improvements and bug fixes by component rather than a task procedure or reference page.

## Official Source Content

# TiDB 6.5.5 Release Notes

Release date: September 21, 2023

TiDB version: 6.5.5

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Improvements

+ TiDB

    - Add new optimizer hints, including [`NO_MERGE_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_merge_joint1_name--tl_name-), [`NO_INDEX_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_joint1_name--tl_name-), [`NO_INDEX_MERGE_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_merge_joint1_name--tl_name-), [`NO_HASH_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_hash_joint1_name--tl_name-), and [`NO_INDEX_HASH_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_hash_joint1_name--tl_name-) [#45520](https://github.com/pingcap/tidb/issues/45520) @[qw4990](https://github.com/qw4990)
    - Add request source information related to the coprocessor [#46514](https://github.com/pingcap/tidb/issues/46514) @[you06](https://github.com/you06)

+ TiKV

    - Add the backoff mechanism for the PD client in the process of connection retries, which gradually increases retry intervals during error retries to reduce PD pressure [#15428](https://github.com/tikv/tikv/issues/15428) @[nolouch](https://github.com/nolouch)
    - Add monitoring metrics for snapshots [#15401](https://github.com/tikv/tikv/issues/15401) @[SpadeA-Tang](https://github.com/SpadeA-Tang)
    - Improve stability of PITR checkpoint lag during leader transfers [#13638](https://github.com/tikv/tikv/issues/13638) @[YuJuncen](https://github.com/YuJuncen)
    - Add logs and monitoring metrics related to `safe-ts` [#15082](https://github.com/tikv/tikv/issues/15082) @[ekexium](https://github.com/ekexium)
    - Provide more logs and monitoring metrics for `resolved-ts` [#15082](https://github.com/tikv/tikv/issues/15082) @[ekexium](https://github.com/ekexium)

+ Tools

    + Backup & Restore (BR)

        - Reduce the CPU overhead of log backup `resolve lock` [#40759](https://github.com/pingcap/tidb/issues/40759) @[3pointer](https://github.com/3pointer)
## Bug fixes

+ TiDB

    - Fix the issue that Stale Read might select an unavailable replica [#46198](https://github.com/pingcap/tidb/issues/46198) @[zyguan](https://github.com/zyguan)
    - Fix the issue that additional overhead is incurred due to the incompatibility between Stale Read and Schema Cache [#43481](https://github.com/pingcap/tidb/issues/43481) @[crazycs520](https://github.com/crazycs520)

+ TiKV

    - Fix the issue that TiKV fails to start when Titan is enabled and the `Blob file deleted twice` error occurs [#15454](https://github.com/tikv/tikv/issues/15454) @[Connor1996](https://github.com/Connor1996)
    - Fix the issue that Online Unsafe Recovery cannot handle merge abort [#15580](https://github.com/tikv/tikv/issues/15580) @[v01dstar](https://github.com/v01dstar)

+ PD

    - Fix the issue that the scheduler takes a long time to start up [#6920](https://github.com/tikv/pd/issues/6920) @[HuSharp](https://github.com/HuSharp)
    - Fix the issue that the logic for handling Leaders and Peers in Scatter Region is inconsistent [#6962](https://github.com/tikv/pd/issues/6962) @[bufferflies](https://github.com/bufferflies)
    - Fix the issue that the `empty-region-count` monitoring metric is abnormal when the cluster is restarted or the PD Leader is switched [#7008](https://github.com/tikv/pd/issues/7008) @[CabinfeverB](https://github.com/CabinfeverB)
    
+ Tools

    + Backup & Restore (BR)

        - Fix the issue that restoring implicit primary keys by PITR might lead to conflicts [#46520](https://github.com/pingcap/tidb/issues/46520) @[3pointer](https://github.com/3pointer)
        - Fix the issue that an error occurs when PITR recovers the meta-kv [#46578](https://github.com/pingcap/tidb/issues/46578) @[Leavrth](https://github.com/Leavrth)
        - Fix an error in BR integration test cases [#46561](https://github.com/pingcap/tidb/issues/46561) @[purelind](https://github.com/purelind)
        - Fix the issue that PITR fails to restore data from GCS [#47022](https://github.com/pingcap/tidb/issues/47022) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Fix the issue of high TiCDC replication latency caused by network isolation of PD nodes [#9565](https://github.com/pingcap/tiflow/issues/9565) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that TiCDC incorrectly changes the `UPDATE` operation to `INSERT` when using the CSV format [#9658](https://github.com/pingcap/tiflow/issues/9658) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that user passwords are recorded in some logs [#9690](https://github.com/pingcap/tiflow/issues/9690) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that using the SASL authentication might cause TiCDC to panic [#9669](https://github.com/pingcap/tiflow/issues/9669) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that TiCDC replication tasks might fail in some corner cases [#9685](https://github.com/pingcap/tiflow/issues/9685) [#9697](https://github.com/pingcap/tiflow/issues/9697) [#9695](https://github.com/pingcap/tiflow/issues/9695) [#9736](https://github.com/pingcap/tiflow/issues/9736) @[hicqu](https://github.com/hicqu) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that TiCDC cannot recover quickly from TiKV node failures when there are a lot of Regions upstream [#9741](https://github.com/pingcap/tiflow/issues/9741) @[sdojjy](https://github.com/sdojjy)
    
    + TiDB Lightning

        - Fix the issue that TiDB Lightning fails to start when TiCDC is deployed on the target server [#41040](https://github.com/pingcap/tidb/issues/41040) @[lance6716](https://github.com/lance6716)
        - Fix the issue that TiDB Lightning fails to start when PD topology is changed [#46688](https://github.com/pingcap/tidb/issues/46688) @[lance6716](https://github.com/lance6716)
        - Fix the issue that TiDB Lightning cannot continue importing data after PD switching Leaders [#46540](https://github.com/pingcap/tidb/issues/46540) @[lance6716](https://github.com/lance6716)
        - Fix the issue that precheck cannot accurately detect the presence of a running TiCDC in the target cluster [#41040](https://github.com/pingcap/tidb/issues/41040) @[lance6716](https://github.com/lance6716)
