# Bug fixes for TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.4.md`
- Source Title: `TiDB 5.0.4 Release Notes`
- Source Heading Path: `TiDB 5.0.4 Release Notes > Bug Fixes`
- Source Line Ranges: `179-198`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `bug fixes`, `changefeed`, `data inconsistency`, `grpc`, `oom`, `ddl`, `owner switch`, `cli compatibility`, `open protocol`, `metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0215_a2db802aa2`
- Source ID: `tidb-docs-8.1:releases/release-5.0.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4492531afea4d745178b16c6db8642fdf6069ff29259f205113bd689ab9cedaa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.4.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiCDC 5.0.4 bug fixes for changefeed, data inconsistency, gRPC memory pressure, owner switch, DDL handling, Open Protocol output, metadata management, or CLI compatibility issues.
- Retrieval Keywords: TiCDC 5.0.4 Bug Fixes, process panic encoding mysql.TypeString mysql.TypeVarString mysql.TypeVarchar into JSON, #2758, multiple processors write data to the same table re-scheduled data inconsistency, #2417, decrease gRPC window size avoid OOM captures too many Regions, #2724, gRPC connection frequently broken memory pressure high, #2202, panic on unsigned TINYINT type, #2648, TiCDC Open Protocol outputs an empty value inserting a transaction and deleting data of the same row, #2612, DDL handling fails changefeed starts at the finish TS of a schema change, #2603, irresponsive downstreams interrupt replication task in old owner until the task times out, #2295, metadata management bug, #2558, data inconsistency after TiCDC owner switch, #2230, outdated capture capture list command, #2388, ErrSchemaStorageTableMiss DDL Job duplication, #2422, changefeed cannot be removed ErrGCTTLExceeded, #2391, replicating large tables to cdclog fails, #1259, #2424, CLI backward compatibility issue, #2373, insecure concurrent access map in SinkManager, #2299, potential DDL loss owner crashes executing DDL statements, #1260, lock is resolved immediately after a Region is initialized, #2188, extra partition dispatching adding a new partitioned table, #2263, TiCDC keeps warning on removed changefeeds, #2156
- Follow-up Guidance: 
- Classification Note: The official content is a release-notes bug-fix list specifically for the TiCDC component in TiDB 5.0.4.

## Official Source Content

- Fix the issue of process panic that occurs when encoding the data types such as `mysql.TypeString, mysql.TypeVarString, mysql.TypeVarchar` into JSON [#2758](https://github.com/pingcap/tiflow/issues/2758)
        - Fix a data inconsistency issue that occurs because multiple processors might write data to the same table when this table is being re-scheduled [#2417](https://github.com/pingcap/tiflow/pull/2417)
        - Decrease the gRPC window size to avoid the OOM that occurs when TiCDC captures too many Regions [#2724](https://github.com/pingcap/tiflow/pull/2724)
        - Fix the error that the gRPC connection is frequently broken when the memory pressure is high [#2202](https://github.com/pingcap/tiflow/issues/2202)
        - Fix a bug that causes TiCDC to panic on the unsigned `TINYINT` type [#2648](https://github.com/pingcap/tiflow/issues/2648)
        - Fix the issue that TiCDC Open Protocol outputs an empty value when inserting a transaction and deleting data of the same row in the upstream [#2612](https://github.com/pingcap/tiflow/issues/2612)
        - Fix a bug that DDL handling fails when a changefeed starts at the finish TS of a schema change [#2603](https://github.com/pingcap/tiflow/issues/2603)
        - Fix the issue that irresponsive downstreams interrupt the replication task in old owner until the task times out [#2295](https://github.com/pingcap/tiflow/issues/2295)
        - Fix a bug in metadata management [#2558](https://github.com/pingcap/tiflow/pull/2558)
        - Fix the issue of data inconsistency that occurs after the TiCDC owner switch [#2230](https://github.com/pingcap/tiflow/issues/2230)
        - Fix the issue that outdated capture might appear in the output of the `capture list` command [#2388](https://github.com/pingcap/tiflow/issues/2388)
        - Fix the `ErrSchemaStorageTableMiss` error that occurs when the DDL Job duplication is encountered in the integrated test [#2422](https://github.com/pingcap/tiflow/issues/2422)
        - Fix the bug that a changefeed cannot be removed if the `ErrGCTTLExceeded` error occurs [#2391](https://github.com/pingcap/tiflow/issues/2391)
        - Fix a bug that replicating large tables to cdclog fails [#1259](https://github.com/pingcap/tiflow/issues/1259) [#2424](https://github.com/pingcap/tiflow/issues/2424)
        - Fix the CLI backward compatibility issue [#2373](https://github.com/pingcap/tiflow/issues/2373)
        - Fix the issue of insecure concurrent access to the map in `SinkManager` [#2299](https://github.com/pingcap/tiflow/pull/2299)
        - Fix the issue of potential DDL loss when the owner crashes when executing DDL statements [#1260](https://github.com/pingcap/tiflow/issues/1260)
        - Fix the issue that the lock is resolved immediately after a Region is initialized [#2188](https://github.com/pingcap/tiflow/issues/2188)
        - Fix the issue of extra partition dispatching that occurs when adding a new partitioned table [#2263](https://github.com/pingcap/tiflow/pull/2263)
        - Fix the issue that TiCDC keeps warning on removed changefeeds [#2156](https://github.com/pingcap/tiflow/issues/2156)
