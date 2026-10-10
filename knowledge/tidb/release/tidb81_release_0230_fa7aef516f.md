# TiCDC bug fixes in 5.1.2

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.2.md`
- Source Title: `TiDB 5.1.2 Release Notes`
- Source Heading Path: `TiDB 5.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `145-155`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `bug-fixes`, `panic`, `grpc`, `oom`, `keepalive`, `changefeed`, `ddl`, `metadata`, `rescheduling`, `open-protocol`, `cdclog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0230_fa7aef516f`
- Source ID: `tidb-docs-8.1:releases/release-5.1.2.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `05200241e75fd52d3def75c67a055600126d21030cb9d9ccc5e2d42d6a10df4b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiCDC 5.1.2 bug fixes related to panic, gRPC memory behavior, keepalive errors, changefeed reset or removal errors, DDL restart handling, metadata snapshot isolation, table rescheduling, Open Protocol empty values, or cdclog synchronization.
- Retrieval Keywords: TiCDC 5.1.2 bug fixes, JSON encoding panic string []byte, unsigned tinyint causes TiCDC panic, Reduce gRPC window size to avoid OOM, gRPC keepalive error under high memory pressure, TiCDC Open Protocol empty value issue, DDL handling during manual restarts, EtcdWorker snapshot isolation metadata, multiple processors write data to the same table, TiCDC rescheduling the table, ErrSchemaStorageTableMiss, changefeed reset unexpectedly, ErrGCTTLExceeded, changefeed cannot be removed, synchronize large tables to cdclog
- Follow-up Guidance: 
- Classification Note: This is a release-note bug-fix list for the TiCDC component in a self-managed deployment scope.

## Official Source Content

- Fix a bug that the JSON encoding might cause panic when processing a string type value that is `string` or `[]byte` [#2758](https://github.com/pingcap/tiflow/issues/2758)
        - Reduce gRPC window size to avoid OOM [#2673](https://github.com/pingcap/tiflow/issues/2673)
        - Fix a gRPC `keepalive` error under high memory pressure [#2202](https://github.com/pingcap/tiflow/issues/2202)
        - Fix a bug that an unsigned `tinyint` causes TiCDC to panic [#2648](https://github.com/pingcap/tiflow/issues/2648)
        - Fix an empty value issue in TiCDC Open Protocol. An empty value is no longer output when there is no change in one transaction. [#2612](https://github.com/pingcap/tiflow/issues/2612)
        - Fix a bug in DDL handling during manual restarts [#2603](https://github.com/pingcap/tiflow/issues/2603)
        - Fix the issue that `EtcdWorker`'s snapshot isolation might be wrongly violated when managing the metadata [#2559](https://github.com/pingcap/tiflow/pull/2559)
        - Fix a bug that multiple processors might write data to the same table when TiCDC is rescheduling the table [#2230](https://github.com/pingcap/tiflow/issues/2230)
        - Fix a bug that changefeed might be reset unexpectedly when TiCDC gets the `ErrSchemaStorageTableMiss` error [#2422](https://github.com/pingcap/tiflow/issues/2422)
        - Fix a bug that changefeed cannot be removed when TiCDC gets the `ErrGCTTLExceeded` error [#2391](https://github.com/pingcap/tiflow/issues/2391)
        - Fix a bug that TiCDC fails to synchronize large tables to cdclog [#1259](https://github.com/pingcap/tiflow/issues/1259) [#2424](https://github.com/pingcap/tiflow/issues/2424)
