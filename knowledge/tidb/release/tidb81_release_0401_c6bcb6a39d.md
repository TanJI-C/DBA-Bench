# Bug fixes for TiCDC, DM, Lightning, Dumpling, and TiDB Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.4.md`
- Source Title: `TiDB 6.5.4 Release Notes`
- Source Heading Path: `TiDB 6.5.4 Release Notes > Bug fixes`
- Source Line Ranges: `162-201`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `dm`, `lightning`, `dumpling`
- Topic Tags: `bug-fixes`, `replication`, `kafka`, `changefeed`, `redo-log`, `pd-availability`, `data-consistency`, `validator`, `collation`, `logical-import`, `checksum`, `csv-import`, `s3-export`, `etcd-client`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0401_c6bcb6a39d`
- Source ID: `tidb-docs-8.1:releases/release-6.5.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e7e1ee753488df8c6c819ef1774f2f11593364857f913bd2de0b146ca37673f2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.4.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.5.4 release-note fixes for TiCDC, DM, Lightning, Dumpling, or TiDB Binlog issues involving replication tasks, Kafka, changefeed, validator, checksum, CSV import, S3 export, or etcd client behavior.
- Retrieval Keywords: TiDB 6.5.4 Bug fixes, TiCDC replication task get stuck downstream error retries, synchronizing to Kafka short retry intervals, Kafka Sink indefinitely block changefeed progress, changefeeds fail temporary unavailability of PD, redo log enabled exception downstream, TiCDC rename DDL operations incorrectly synchronize, multiple unique key rows one transaction write conflicts, Avro protocol incorrectly identifies Enum type values, DM unique key column name is null panic, validator handles errors incorrectly deadlock retry mechanism, collation causality key, TiDB Lightning Region is unavailable checksum SSL enabled, checksum = "optional" still reports errors, logical import mode table B does not exist, importing CSV data route panic, PD cluster address changes data import fails, some PD nodes fail data import fails, AUTO_ID_CACHE=1 base value of the ID allocator is incorrect, NEXT_GLOBAL_ROW_ID data type is wrong, Dumpling Amazon S3 exported file is lost, TiDB Binlog etcd client synchronize latest node information during initialization
- Follow-up Guidance: The source groups these items under TiCDC, TiDB Data Migration (DM), TiDB Lightning, Dumpling, and TiDB Binlog bug fixes in the TiDB 6.5.4 release notes.
- Classification Note: This chunk is classified as a release note because it enumerates bug fixes by component in TiDB 6.5.4 for self-managed deployments.

## Official Source Content

- Fix the issue that the replication task might get stuck when the downstream encounters an error and retries [#9450](https://github.com/pingcap/tiflow/issues/9450) @[hicqu](https://github.com/hicqu)
        - Fix the issue that the replication task fails due to short retry intervals when synchronizing to Kafka [#9504](https://github.com/pingcap/tiflow/issues/9504) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that TiCDC might cause synchronization write conflicts when modifying multiple unique key rows in one transaction on the upstream [#9430](https://github.com/pingcap/tiflow/issues/9430) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that TiCDC might incorrectly synchronize rename DDL operations [#9488](https://github.com/pingcap/tiflow/issues/9488) [#9378](https://github.com/pingcap/tiflow/issues/9378) [#9531](https://github.com/pingcap/tiflow/issues/9531) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the replication task might get stuck when the downstream encounters a short-term failure [#9542](https://github.com/pingcap/tiflow/issues/9542) [#9272](https://github.com/pingcap/tiflow/issues/9272)[#9582](https://github.com/pingcap/tiflow/issues/9582) [#9592](https://github.com/pingcap/tiflow/issues/9592) @[hicqu](https://github.com/hicqu)
        - Fix the panic issue that might occur when the TiCDC node status changes [#9354](https://github.com/pingcap/tiflow/issues/9354) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that when Kafka Sink encounters errors it might indefinitely block changefeed progress [#9309](https://github.com/pingcap/tiflow/issues/9309) @[hicqu](https://github.com/hicqu)
        - Fix the issue that when the downstream is Kafka, TiCDC queries the downstream metadata too frequently and causes excessive workload in the downstream [#8957](https://github.com/pingcap/tiflow/issues/8957) [#8959](https://github.com/pingcap/tiflow/issues/8959) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the data inconsistency issue that might occur when some TiCDC nodes are isolated from the network [#9344](https://github.com/pingcap/tiflow/issues/9344) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the replication task might get stuck when the redo log is enabled and there is an exception downstream [#9172](https://github.com/pingcap/tiflow/issues/9172) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that changefeeds would fail due to the temporary unavailability of PD [#9294](https://github.com/pingcap/tiflow/issues/9294) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue of too many downstream logs caused by frequently setting the downstream bidirectional replication-related variables when replicating data to TiDB or MySQL [#9180](https://github.com/pingcap/tiflow/issues/9180) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that Avro protocol incorrectly identifies `Enum` type values [#9259](https://github.com/pingcap/tiflow/issues/9259) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiDB Data Migration (DM)

        - Fix the panic issue when the unique key column name is null [#9247](https://github.com/pingcap/tiflow/issues/9247) @[lance6716](https://github.com/lance6716)
        - Fix the deadlock issue that might occur when the validator handles errors incorrectly, and optimize the retry mechanism [#9257](https://github.com/pingcap/tiflow/issues/9257) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that collation is not considered when calculating the causality key [#9489](https://github.com/pingcap/tiflow/issues/9489) @[hihihuhu](https://github.com/hihihuhu)

    + TiDB Lightning

        - Fix the issue that the disk quota check might block when an engine is importing data [#44867](https://github.com/pingcap/tidb/issues/44867) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that checksum reports an error `Region is unavailable` when SSL is enabled on the target cluster [#45462](https://github.com/pingcap/tidb/issues/45462) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that encoding errors cannot be logged correctly [#44321](https://github.com/pingcap/tidb/issues/44321) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that route might panic when importing CSV data [#43284](https://github.com/pingcap/tidb/issues/43284) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that importing table A in logical import mode might mistakenly report that table B does not exist [#44614](https://github.com/pingcap/tidb/issues/44614) @[dsdashun](https://github.com/dsdashun)
        - Fix the issue that the data type is wrong when saving `NEXT_GLOBAL_ROW_ID` [#45427](https://github.com/pingcap/tidb/issues/45427) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that checksum still reports errors when `checksum = "optional"` [#45382](https://github.com/pingcap/tidb/issues/45382) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that data import fails when the PD cluster address changes [#43436](https://github.com/pingcap/tidb/issues/43436) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the issue that data import fails when some PD nodes fail [#43400](https://github.com/pingcap/tidb/issues/43400) @[lichunzhu](https://github.com/lichunzhu)
        - Fix the issue that when a table with auto-incremental columns sets `AUTO_ID_CACHE=1`, the base value of the ID allocator is incorrect [#46100](https://github.com/pingcap/tidb/issues/46100) @[D3Hunter](https://github.com/D3Hunter)

    + Dumpling

        - Fix the issue that the exported file is lost due to unprocessed file writer closing error when exporting to Amazon S3 [#45353](https://github.com/pingcap/tidb/issues/45353) @[lichunzhu](https://github.com/lichunzhu)

    + TiDB Binlog

        - Fix the issue that the etcd client does not automatically synchronize the latest node information during initialization [#1236](https://github.com/pingcap/tidb-binlog/issues/1236) @[lichunzhu](https://github.com/lichunzhu)
