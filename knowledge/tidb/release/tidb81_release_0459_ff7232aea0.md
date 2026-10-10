# Improvements and bug fixes section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.2.md`
- Source Title: `TiDB 7.1.2 Release Notes`
- Source Heading Path: `TiDB 7.1.2 Release Notes > Improvements | TiDB 7.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `27-81`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`
- Topic Tags: `release-notes`, `improvements`, `bug-fixes`, `optimizer`, `observability`, `upgrade`, `compaction`, `memory`, `backoff`, `metrics`, `restore`, `backup`, `changefeed`, `ddl`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0459_ff7232aea0`
- Source ID: `tidb-docs-8.1:releases/release-7.1.2.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e034d4716fc5ee0c7cdb662b364f0c3283bb47d61b99e28a570981391d98ac95`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.2#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.2 improvements across TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, and TiDB Lightning before the bug fixes list begins.
- Retrieval Keywords: TiDB 7.1.2 Release Notes, Improvements, Bug fixes, NO_MERGE_JOIN(), NO_INDEX_JOIN(), NO_INDEX_MERGE_JOIN(), NO_HASH_JOIN(), NO_INDEX_HASH_JOIN(), request source information related to the coprocessor, /upgrade/start, upgrade/finish, Max gap of safe-ts, Min safe ts region, tikv-ctl get-region-read-progress, TTL, periodic compaction, PD client backoff, GetRegions cancel mechanism, TiFlash memory usage of index data, Grafana, MaxIdleConns, MaxIdleConnsPerHost, WaitTiflashReady, Kafka Sink sending only handle key data, ADD INDEX DDL, strict optimistic mode, checksum-via-sql, no leader error
- Follow-up Guidance: The chunk continues into the Bug fixes section after the TiDB subsection heading.
- Classification Note: This is a release-notes improvements chunk because it enumerates new hints, APIs, metrics, configuration exposure, and tool behavior changes introduced in 7.1.2.

## Official Source Content

## Improvements

+ TiDB

    - Add new optimizer hints, including [`NO_MERGE_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_merge_joint1_name--tl_name-), [`NO_INDEX_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_joint1_name--tl_name-), [`NO_INDEX_MERGE_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_merge_joint1_name--tl_name-), [`NO_HASH_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_hash_joint1_name--tl_name-), and [`NO_INDEX_HASH_JOIN()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_index_hash_joint1_name--tl_name-) [#45520](https://github.com/pingcap/tidb/issues/45520) @[qw4990](https://github.com/qw4990)
    - Add request source information related to the coprocessor [#46514](https://github.com/pingcap/tidb/issues/46514) @[you06](https://github.com/you06)
    - Add the `/upgrade/start` and `upgrade/finish` APIs to mark the start and end of the upgrade status for TiDB nodes [#47172](https://github.com/pingcap/tidb/issues/47172) @[zimulala](https://github.com/zimulala)

+ TiKV

    - Optimize the compaction mechanism: when a Region is split, if there is no key to split, a compaction is triggered to eliminate excessive MVCC versions [#15282](https://github.com/tikv/tikv/issues/15282) @[SpadeA-Tang](https://github.com/SpadeA-Tang)
    - Eliminate LRUCache in Router objects to reduce memory usage and prevent OOM [#15430](https://github.com/tikv/tikv/issues/15430) @[Connor1996](https://github.com/Connor1996)
    - Add the `Max gap of safe-ts` and `Min safe ts region` metrics and introduce the `tikv-ctl get-region-read-progress` command to better observe and diagnose the status of resolved-ts and safe-ts [#15082](https://github.com/tikv/tikv/issues/15082) @[ekexium](https://github.com/ekexium)
    - Expose some RocksDB configurations in TiKV that allow users to disable features such as TTL and periodic compaction [#14873](https://github.com/tikv/tikv/issues/14873) @[LykxSassinator](https://github.com/LykxSassinator)
    - Add the backoff mechanism for the PD client in the process of connection retries, which gradually increases retry intervals during error retries to reduce PD pressure [#15428](https://github.com/tikv/tikv/issues/15428) @[nolouch](https://github.com/nolouch)
    - Avoid holding mutex when writing Titan manifest files to prevent affecting other threads [#15351](https://github.com/tikv/tikv/issues/15351) @[Connor1996](https://github.com/Connor1996)
    - Optimize memory usage of Resolver to prevent OOM [#15458](https://github.com/tikv/tikv/issues/15458) @[overvenus](https://github.com/overvenus)

+ PD

    - Optimize the backoff mechanism in the PD caller to reduce the frequency of RPC requests when a call fails [#6556](https://github.com/tikv/pd/issues/6556) @[nolouch](https://github.com/nolouch) @[rleungx](https://github.com/rleungx) @[HuSharp](https://github.com/HuSharp)
    - Introduce the cancel mechanism for the `GetRegions` interface to release CPU and memory in time when the caller is disconnected [#6835](https://github.com/tikv/pd/issues/6835) @[lhy1024](https://github.com/lhy1024)

+ TiFlash

    - Add monitoring metrics for the memory usage of index data in Grafana [#8050](https://github.com/pingcap/tiflash/issues/8050) @[hongyunyan](https://github.com/hongyunyan)

+ Tools

    + Backup & Restore (BR)

        - Enhance support for connection reuse of log backup and PITR restore tasks by setting `MaxIdleConns` and `MaxIdleConnsPerHost` parameters in the HTTP client [#46011](https://github.com/pingcap/tidb/issues/46011) @[Leavrth](https://github.com/Leavrth)
        - Reduce the CPU overhead of log backup `resolve lock` [#40759](https://github.com/pingcap/tidb/issues/40759) @[3pointer](https://github.com/3pointer)
        - Add a new restore parameter `WaitTiflashReady`. When this parameter is enabled, the restore operation will be completed after TiFlash replicas are successfully replicated [#43828](https://github.com/pingcap/tidb/issues/43828) [#46302](https://github.com/pingcap/tidb/issues/46302) @[3pointer](https://github.com/3pointer)

    + TiCDC

        - Optimize several TiCDC monitoring metrics and alarm rules [#9047](https://github.com/pingcap/tiflow/issues/9047) @[asddongmen](https://github.com/asddongmen)
        - Kafka Sink supports [sending only handle key data](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#handle-messages-that-exceed-the-kafka-topic-limit) when a message is too large, avoiding changefeed failure caused by excessive message size [#9680](https://github.com/pingcap/tiflow/issues/9680) @[3AceShowHand](https://github.com/3AceShowHand)
        - Optimize the execution logic of replicating the `ADD INDEX` DDL operations to avoid blocking subsequent DML statements [#9644](https://github.com/pingcap/tiflow/issues/9644) @[sdojjy](https://github.com/sdojjy)
        - Refine the status message when TiCDC retries after a failure [#9483](https://github.com/pingcap/tiflow/issues/9483) @[asddongmen](https://github.com/asddongmen)

    + TiDB Data Migration (DM)

        - Support strict optimistic mode for incompatible DDL statements [#9112](https://github.com/pingcap/tiflow/issues/9112) @[GMHDBJD](https://github.com/GMHDBJD)

    + TiDB Lightning

        - Change the default value of `checksum-via-sql` to `false` to improve the performance of import tasks [#45368](https://github.com/pingcap/tidb/issues/45368) [#45094](https://github.com/pingcap/tidb/issues/45094) @[GMHDBJD](https://github.com/GMHDBJD)
        - Optimize the retry logic of TiDB Lightning for the `no leader` error during the data import phase [#46253](https://github.com/pingcap/tidb/issues/46253) @[lance6716](https://github.com/lance6716)
## Bug fixes

+ TiDB
