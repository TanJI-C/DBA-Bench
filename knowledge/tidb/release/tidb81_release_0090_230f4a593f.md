# PD, TiKV, and tools changes in TiDB 3.0.0 Beta.1

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.0-beta.1.md`
- Source Title: `TiDB 3.0.0 Beta.1 Release Notes`
- Source Heading Path: `TiDB 3.0.0 Beta.1 Release Notes > PD | TiDB 3.0.0 Beta.1 Release Notes > TiKV | TiDB 3.0.0 Beta.1 Release Notes > Tools`
- Source Line Ranges: `66-108`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`, `lightning`, `ecosystem`
- Topic Tags: `release-notes`, `pd`, `scheduling`, `simulator`, `monitoring`, `tombstone-store`, `tikv`, `coprocessor`, `tablescan`, `vectorization`, `logging`, `raw-read`, `metrics`, `batch-system`, `tikv-ctl`, `binlog`, `lightning`, `import`, `compaction`, `csv`, `sync-diff-inspector`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0090_230f4a593f`
- Source ID: `tidb-docs-8.1:releases/release-3.0.0-beta.1.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `966d4cfebdabc602fd89fc888d6ea38fc2b0e4000764aad24bc5ccee2cf648d2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.0-beta.1#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.0-beta.1.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 3.0.0 Beta.1 release-note details about PD, TiKV, TiDB Binlog, Lightning, or sync-diff-inspector changes.
- Retrieval Keywords: TiDB 3.0.0 Beta.1, PD, hotspot scheduling configurable, store address as the dimension monitoring item, GetStores overhead, Tombstone Store, Simulator, different heartbeat intervals, importing data case, TiKV, Coprocessor, TableScan, Single TableScan, BatchRows, BatchColumn, VectorLike, BatchExecutor, RPN format, BatchTableScanExecutor, Local Reader, Raw Read interface, configuration information metrics, key exceeding bound, panic or return an error, INSERT operation, prewrite succeed only when keys do not exist, Batch Get, Batch System, tikv-ctl, Raw scan, TiDB Binlog, Arbiter, Kafka, replicate the data into MySQL, generated columns, Lightning, Level-1 compaction, table_concurrency, import engines, intermediate state SST, TiKV-Importer, separate import of data and indexes, importing CSV files, sync-diff-inspector, TiDB statistics to split chunks, multiple columns to split chunks
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a shared release-notes section because the official content summarizes changes across PD, TiKV, and multiple tools in TiDB 3.0.0 Beta.1.

## Official Source Content

## PD

+ Unify the [log format](https://github.com/tikv/rfcs/blob/master/text/0018-unified-log-format.md) for easy collection and analysis by tools
+ Simulator
    - Support different heartbeat intervals in different stores [#1418](https://github.com/pingcap/pd/pull/1418)
    - Add a case about importing data [#1263](https://github.com/pingcap/pd/pull/1263)
+ Make hotspot scheduling configurable [#1412](https://github.com/pingcap/pd/pull/1412)
+ Add the store address as the dimension monitoring item to replace the previous Store ID [#1429](https://github.com/pingcap/pd/pull/1429)
+ Optimize the `GetStores` overhead to speed up the Region inspection cycle [#1410](https://github.com/pingcap/pd/pull/1410)
+ Add an interface to delete the Tombstone Store [#1472](https://github.com/pingcap/pd/pull/1472)
## TiKV

+ Optimize the Coprocessor calculation execution framework and implement the TableScan section, with the Single TableScan performance improved by 5% ~ 30%
    - Implement the definition of the `BatchRows` row and the `BatchColumn` column [#3660](https://github.com/tikv/tikv/pull/3660)
    - Implement `VectorLike` to support accessing encoded and decoded data in the same way [#4242](https://github.com/tikv/tikv/pull/4242)
    - Define the `BatchExecutor` to interface and implement the way of converting requests to `BatchExecutor` [#4243](https://github.com/tikv/tikv/pull/4243)
    - Implement transforming the expression tree into the RPN format [#4329](https://github.com/tikv/tikv/pull/4329)
    - Implement the `BatchTableScanExecutor` vectorization operator to accelerate calculation [#4351](https://github.com/tikv/tikv/pull/4351)
+ Unify the [log format](https://github.com/tikv/rfcs/blob/master/text/0018-unified-log-format.md) for easy collection and analysis by tools
+ Support using the Local Reader to read in the Raw Read interface [#4222](https://github.com/tikv/tikv/pull/4222)
+ Add metrics about configuration information [#4206](https://github.com/tikv/tikv/pull/4206)
+ Add metrics about key exceeding bound [#4255](https://github.com/tikv/tikv/pull/4255)
+ Add an option to control panic or return an error when encountering the key exceeding bound error [#4254](https://github.com/tikv/tikv/pull/4254)
+ Add support for the `INSERT` operation, make prewrite succeed only when keys do not exist, and eliminate `Batch Get` [#4085](https://github.com/tikv/tikv/pull/4085)
+ Use more fair batch strategy in the Batch System [#4200](https://github.com/tikv/tikv/pull/4200)
+ Support Raw scan in tikv-ctl [#3825](https://github.com/tikv/tikv/pull/3825)
## Tools

+ TiDB Binlog
    - Add the Arbiter tool that supports reading binlog from Kafka and replicate the data into MySQL
    - Support filtering files that do not need to be replicated
    - Support replicating generated columns
+ Lightning
    - Support disabling TiKV periodic Level-1 compaction, and when the TiKV cluster version is 2.1.4 or later, Level-1 compaction is automatically executed in the import mode [#119](https://github.com/pingcap/tidb-lightning/pull/119), [#4199](https://github.com/tikv/tikv/pull/4199)
    - Add the `table_concurrency` configuration item to limit the number of import engines ("16" by default) and avoid overusing the importer disk space [#119](https://github.com/pingcap/tidb-lightning/pull/119)
    - Support saving the intermediate state SST to the disk, to reduce memory usage [#4369](https://github.com/tikv/tikv/pull/4369)
    - Optimize the import performance of TiKV-Importer and support separate import of data and indexes for large tables [#132](https://github.com/pingcap/tidb-lightning/pull/132)
    - Support importing CSV files [#111](https://github.com/pingcap/tidb-lightning/pull/111)
+ Data replication comparison tool (sync-diff-inspector)
    - Support using TiDB statistics to split chunks to be compared [#197](https://github.com/pingcap/tidb-tools/pull/197)
    - Support using multiple columns to split chunks to be compared [#197](https://github.com/pingcap/tidb-tools/pull/197)
