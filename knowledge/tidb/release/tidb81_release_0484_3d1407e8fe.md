# Bug fixes for TiDB and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.6.md`
- Source Title: `TiDB 7.1.6 Release Notes`
- Source Heading Path: `TiDB 7.1.6 Release Notes > Bug fixes`
- Source Line Ranges: `178-205`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `lightning`, `ticdc`, `shared`
- Topic Tags: `bug-fixes`, `ttl`, `cast`, `add-index`, `rawkv`, `traffic-control`, `raft-engine`, `cdc`, `log-backup`, `resolved-ts`, `data-import`, `sst`, `oom`, `bloom-filter`, `grpc-compression`, `deadlock-detection`, `decimal`, `timezone`, `kms`, `master-key-rotation`, `grafana-metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0484_3d1407e8fe`
- Source ID: `tidb-docs-8.1:releases/release-7.1.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `464bccc52deca0270d47b582909bb7e4b94f10455d0269706678174e6f5d3941`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.1.6 bug fixes for TiDB or TiKV issues involving TTL, CAST, ADD INDEX, RawKV, CDC or log-backup resolved_ts lag, TiDB Lightning SST import, OOM, grpc-compression-type, KMS master key rotation, tikv-ctl raft region output, Grafana metrics, or time zone conversion.
- Retrieval Keywords: TiDB 7.1.6 bug fixes, TiKV 7.1.6 bug fixes, existing TTL tasks are executed unexpectedly frequently, upgraded from v6.5 to v7.5 or later, CAST function does not support explicitly setting the character set, ADD INDEX index length limitation, RawKvMaxTimestampNotSynced, errorpb.Error.max_ts_not_synced, must_raw_put retry mechanism, traffic control after deleting large tables or partitions, Raft Engine MemTable outdated indexes panic, check_leader, advance-ts-interval, resolved_ts lag, CDC and log-backup, SST files imported by TiDB Lightning are lost after TiKV is restarted, sst_importer SST files, OOM during data import, bloom filters incompatible earlier than v7.1, grpc-compression-type, deadlock detection might cause TiKV OOM, DECIMAL type decimal part is incorrect, CONV() overflow TiKV panic, stale replica processes Raft snapshots, highly concurrent Coprocessor requests might cause TiKV OOM, master key rotation, Key Management Service, KMS, tikv-ctl raft region, Region status information, Storage async write duration, TiKV panel in Grafana, Brazil and Egypt time zone incorrectly
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a self-managed release bug-fix summary for TiDB and TiKV in the TiDB 7.1.6 Release Notes.

## Official Source Content

- Fix the issue that existing TTL tasks are executed unexpectedly frequently in a cluster that is upgraded from v6.5 to v7.5 or later [#56539](https://github.com/pingcap/tidb/issues/56539) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `CAST` function does not support explicitly setting the character set [#55677](https://github.com/pingcap/tidb/issues/55677) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that TiDB does not check the index length limitation when executing `ADD INDEX` [#56930](https://github.com/pingcap/tidb/issues/56930) @[fzzf678](https://github.com/fzzf678)

+ TiKV

    - Add the `RawKvMaxTimestampNotSynced` error, log detailed error information in `errorpb.Error.max_ts_not_synced`, and add a retry mechanism for the `must_raw_put` operation when this error occurs [#16789](https://github.com/tikv/tikv/issues/16789) @[pingyu](https://github.com/pingyu)
    - Fix a traffic control issue that might occur after deleting large tables or partitions [#17304](https://github.com/tikv/tikv/issues/17304) @[SpadeA-Tang](https://github.com/SpadeA-Tang)
    - Fix the panic issue that occurs when read threads access outdated indexes in the MemTable of the Raft Engine [#17383](https://github.com/tikv/tikv/issues/17383) @[LykxSassinator](https://github.com/LykxSassinator)
    - Fix the issue that CDC and log-backup do not limit the timeout of `check_leader` using the `advance-ts-interval` configuration, causing the `resolved_ts` lag to be too large when TiKV restarts normally in some cases [#17107](https://github.com/tikv/tikv/issues/17107) @[SpadeA-Tang](https://github.com/SpadeA-Tang)
    - Fix the issue that SST files imported by TiDB Lightning are lost after TiKV is restarted [#15912](https://github.com/tikv/tikv/issues/15912) @[lance6716](https://github.com/lance6716)
    - Fix the issue that TiKV might panic due to ingesting deleted `sst_importer` SST files [#15053](https://github.com/tikv/tikv/issues/15053) @[lance6716](https://github.com/lance6716)
    - Fix the issue that when there are a large number of Regions in a TiKV instance, TiKV might be OOM during data import [#16229](https://github.com/tikv/tikv/issues/16229) @[SpadeA-Tang](https://github.com/SpadeA-Tang)
    - Fix the issue that bloom filters are incompatible between earlier versions (earlier than v7.1) and later versions [#17272](https://github.com/tikv/tikv/issues/17272) @[v01dstar](https://github.com/v01dstar)
    - Fix the issue that setting the gRPC message compression method via `grpc-compression-type` does not take effect on messages sent from TiKV to TiDB [#17176](https://github.com/tikv/tikv/issues/17176) @[ekexium](https://github.com/ekexium)
    - Fix the issue of unstable test cases, ensuring that each test uses an independent temporary directory to avoid online configuration changes affecting other test cases [#16871](https://github.com/tikv/tikv/issues/16871) @[glorv](https://github.com/glorv)
    - Fix the issue that when a large number of transactions are queuing for lock release on the same key and the key is frequently updated, excessive pressure on deadlock detection might cause TiKV OOM issues [#17394](https://github.com/tikv/tikv/issues/17394) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that the decimal part of the `DECIMAL` type is incorrect in some cases [#16913](https://github.com/tikv/tikv/issues/16913) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that the `CONV()` function in queries might overflow during numeric system conversion, leading to TiKV panic [#16969](https://github.com/tikv/tikv/issues/16969) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that TiKV might panic when a stale replica processes Raft snapshots, triggered by a slow split operation and immediate removal of the new replica [#17469](https://github.com/tikv/tikv/issues/17469) @[hbisheng](https://github.com/hbisheng)
    - Fix the issue that highly concurrent Coprocessor requests might cause TiKV OOM [#16653](https://github.com/tikv/tikv/issues/16653) @[overvenus](https://github.com/overvenus)
    - Fix the issue that prevents master key rotation when the master key is stored in a Key Management Service (KMS) [#17410](https://github.com/tikv/tikv/issues/17410) @[hhwyt](https://github.com/hhwyt)
    - Fix the issue that the output of the `raft region` command in tikv-ctl does not include the Region status information [#17037](https://github.com/tikv/tikv/issues/17037) @[glorv](https://github.com/glorv)
    - Fix the issue that the **Storage async write duration** monitoring metric on the TiKV panel in Grafana is inaccurate [#17579](https://github.com/tikv/tikv/issues/17579) @[overvenus](https://github.com/overvenus)
    - Fix the issue that TiKV converts the time zone incorrectly for Brazil and Egypt [#16220](https://github.com/tikv/tikv/issues/16220) @[overvenus](https://github.com/overvenus)

+ PD
