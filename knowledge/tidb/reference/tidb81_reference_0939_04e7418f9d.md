# TiDB Lightning glossary terms

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-glossary.md`
- Source Title: `TiDB Lightning Glossary`
- Source Heading Path: `TiDB Lightning Glossary | TiDB Lightning Glossary > A | TiDB Lightning Glossary > A > Analyze | TiDB Lightning Glossary > A > `AUTO_INCREMENT_ID` | TiDB Lightning Glossary > B | TiDB Lightning Glossary > B > Back end | TiDB Lightning Glossary > C | TiDB Lightning Glossary > C > Checkpoint | TiDB Lightning Glossary > C > Checksum | TiDB Lightning Glossary > C > Chunk | TiDB Lightning Glossary > C > Compaction | TiDB Lightning Glossary > D | TiDB Lightning Glossary > D > Data engine | TiDB Lightning Glossary > E | TiDB Lightning Glossary > E > Engine | TiDB Lightning Glossary > F | TiDB Lightning Glossary > F > Filter | TiDB Lightning Glossary > I | TiDB Lightning Glossary > I > Import mode | TiDB Lightning Glossary > I > Index engine | TiDB Lightning Glossary > I > Ingest | TiDB Lightning Glossary > K | TiDB Lightning Glossary > K > KV pair | TiDB Lightning Glossary > K > KV encoder | TiDB Lightning Glossary > L | TiDB Lightning Glossary > L > Local checksum | TiDB Lightning Glossary > N | TiDB Lightning Glossary > N > Normal mode | TiDB Lightning Glossary > P | TiDB Lightning Glossary > P > Post-processing | TiDB Lightning Glossary > R | TiDB Lightning Glossary > R > Remote checksum | TiDB Lightning Glossary > S | TiDB Lightning Glossary > S > Scattering | TiDB Lightning Glossary > S > Splitting | TiDB Lightning Glossary > S > SST file`
- Source Line Ranges: `5-194`
- Source Scope: `shared`
- Primary Component: `lightning`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `glossary`, `terminology`, `analyze`, `auto_increment_id`, `backend`, `checkpoint`, `checksum`, `chunk`, `compaction`, `data-engine`, `engine`, `filter`, `import-mode`, `index-engine`, `ingest`, `kv-pair`, `kv-encoder`, `local-checksum`, `normal-mode`, `post-processing`, `remote-checksum`, `scattering`, `splitting`, `sst-file`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0939_04e7418f9d`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-glossary.md#tidb-lightning-glossary`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b27aac1a7c98b2f575421dcac5940b5b740f539f3a62cff5b04938efd08efb8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#tidb-lightning-glossary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-glossary.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs definitions of TiDB Lightning glossary terms appearing in logs, monitoring, configurations, or documentation, such as checkpoint, checksum, import mode, engine, SST file, analyze, and AUTO_INCREMENT_ID.
- Retrieval Keywords: TiDB Lightning Glossary, Analyze, ANALYZE TABLE, post-restore.analyze, AUTO_INCREMENT_ID, Back end, backend, Checkpoint, Checksum, post-restore.checksum, local checksum, remote checksum, Chunk, Compaction, Data engine, mydumper.batch-size, lightning.table-concurrency, Engine, TiKV Importer, import-dir, Filter, Import mode, tidb-lightning-ctl, normal mode, Index engine, lightning.index-concurrency, Ingest, KV pair, KV encoder, Post-processing, Scattering, Splitting, import.region-split-size, SST file
- Follow-up Guidance: The source also points to related details such as Checkpoints, Table Filter, TiDB Lightning architecture, checksum mismatch FAQs, and force revert from import mode to normal mode.
- Classification Note: This chunk is classified as reference because it defines TiDB Lightning terminology and associated identifiers and configuration names rather than describing a task workflow.

## Official Source Content

# TiDB Lightning Glossary

This page explains the special terms used in TiDB Lightning's logs, monitoring, configurations, and documentation.

<!-- A -->
## A
### Analyze

An operation to rebuild the [statistics](https://docs.pingcap.com/tidb/stable/statistics) information of a TiDB table, which is running the [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) statement.

Because TiDB Lightning imports data without going through TiDB, the statistics information is not automatically updated. Therefore, TiDB Lightning explicitly analyzes every table after importing. This step can be omitted by setting the `post-restore.analyze` configuration to `false`.
### `AUTO_INCREMENT_ID`

Every table has an associated `AUTO_INCREMENT_ID` counter to provide the default value of an auto-incrementing column. In TiDB, this counter is additionally used to assign row IDs.

Because TiDB Lightning imports data without going through TiDB, the `AUTO_INCREMENT_ID` counter is not automatically updated. Therefore, TiDB Lightning explicitly alters `AUTO_INCREMENT_ID` to a valid value. This step is always performed, even if the table has no `AUTO_INCREMENT` columns.

<!-- B -->
## B
### Back end

Back end is the destination where TiDB Lightning sends the parsed result. Also spelled as "backend".

See [TiDB Lightning architecture](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) for details.

<!-- C -->
## C
### Checkpoint

TiDB Lightning continuously saves its progress into a local file or a remote database while importing. This allows it to resume from an intermediate state should it crashes in the process. See the [Checkpoints](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-checkpoints) section for details.
### Checksum

In TiDB Lightning, the checksum of a table is a set of 3 numbers calculated from the content of each KV pair in that table. These numbers are respectively:

* the number of KV pairs,
* total length of all KV pairs, and
* the bitwise-XOR of [CRC-64-ECMA](https://en.wikipedia.org/wiki/Cyclic_redundancy_check) value each pair.

TiDB Lightning [validates the imported data](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#how-to-ensure-the-integrity-of-the-imported-data) by comparing the [local](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#local-checksum) and [remote checksums](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#remote-checksum) of every table. The program would stop if any pair does not match. You can skip this check by setting the `post-restore.checksum` configuration to `false`.

See also the [FAQs](https://docs.pingcap.com/tidb/stable/tidb-lightning/troubleshoot-tidb-lightning#checksum-failed-checksum-mismatched-remote-vs-local) for how to properly handle checksum mismatch.
### Chunk

A continuous range of source data, normally equivalent to a single file in the data source.

When a file is too large, TiDB Lightning might split a file into multiple chunks.
### Compaction

An operation that merges multiple small SST files into one large SST file, and cleans up the deleted entries. TiKV automatically compacts data in background while TiDB Lightning is importing.

> **Note:**
>
> For legacy reasons, you can still configure TiDB Lightning to explicitly trigger a compaction every time a table is imported. However, this is not recommended and the corresponding settings are disabled by default.

See [RocksDB's wiki page on Compaction](https://github.com/facebook/rocksdb/wiki/Compaction) for its technical details.

<!-- D -->
## D
### Data engine

An [engine](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#engine) for sorting actual row data.

When a table is very large, its data is placed into multiple data engines to improve task pipelining and save space of TiKV Importer. By default, a new data engine is opened for every 100 GB of SQL data, which can be configured through the `mydumper.batch-size` setting.

TiDB Lightning processes multiple data engines concurrently. This is controlled by the `lightning.table-concurrency` setting.

<!-- E -->
## E
### Engine

In TiKV Importer, an engine is a RocksDB instance for sorting KV pairs.

TiDB Lightning transfers data to TiKV Importer through engines. It first opens an engine, sends KV pairs to it (with no particular order), and finally closes the engine. The engine sorts the received KV pairs after it is closed. These closed engines can then be further uploaded to the TiKV stores for ingestion.

Engines use TiKV Importer's `import-dir` as temporary storage, which are sometimes referred to as "engine files".

See also [data engine](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#data-engine) and [index engine](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#index-engine).

<!-- F -->
## F
### Filter

A configuration list that specifies which tables to be imported or excluded.

See [Table Filter](https://docs.pingcap.com/tidb/stable/table-filter) for details.

<!-- I -->
## I
### Import mode

A configuration that optimizes TiKV for writing at the cost of degraded read speed and space usage.

TiDB Lightning automatically switches to and off the import mode while running. However, if TiKV gets stuck in import mode, you can use `tidb-lightning-ctl` to [force revert](https://docs.pingcap.com/tidb/stable/tidb-lightning/troubleshoot-tidb-lightning#the-tidb-cluster-uses-lots-of-cpu-resources-and-runs-very-slowly-after-using-tidb-lightning) to [normal mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#normal-mode).
### Index engine

An [engine](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#engine) for sorting indices.

Regardless of number of indices, every table is associated with exactly one index engine.

TiDB Lightning processes multiple index engines concurrently. This is controlled by the `lightning.index-concurrency` setting. Since every table has exactly one index engine, this also configures the maximum number of tables to process at the same time.
### Ingest

An operation which inserts the entire content of an [SST file](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#sst-file) into the RocksDB (TiKV) store.

Ingestion is a very fast operation compared with inserting KV pairs one by one. This operation is the determinant factor for the performance of TiDB Lightning.

See [RocksDB's wiki page on Creating and Ingesting SST files](https://github.com/facebook/rocksdb/wiki/Creating-and-Ingesting-SST-files) for its technical details.

<!-- K -->
## K
### KV pair

Abbreviation of "key-value pair".
### KV encoder

A routine which parses SQL or CSV rows to KV pairs. Multiple KV encoders run in parallel to speed up processing.

<!-- L -->
## L
### Local checksum

The [checksum](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#checksum) of a table calculated by TiDB Lightning itself before sending the KV pairs to TiKV Importer.

<!-- N -->
## N
### Normal mode

The mode where [import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#import-mode) is disabled.

<!-- P -->
## P
### Post-processing

The period of time after the entire data source is parsed and sent to TiKV Importer. TiDB Lightning is waiting for TiKV Importer to upload and [ingest](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#ingest) the [SST files](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#sst-file).

<!-- R -->
## R
### Remote checksum

The [checksum](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#checksum) of a table calculated by TiDB after it has been imported.

<!-- S -->
## S
### Scattering

An operation that randomly reassigns the leader and the peers of a [Region](https://docs.pingcap.com/tidb/stable/glossary#regionpeerraft-group). Scattering ensures that the imported data are distributed evenly among TiKV stores. This reduces stress on PD.
### Splitting

An engine is typically very large (around 100 GB), which is not friendly to TiKV if treated as a single [region](https://docs.pingcap.com/tidb/stable/glossary#regionpeerraft-group). TiKV Importer splits an engine into multiple small [SST files](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#sst-file) (configurable by TiKV Importer's `import.region-split-size` setting) before uploading.
### SST file

SST is the abbreviation of "sorted string table". An SST file is RocksDB's (and thus TiKV's) native storage format of a collection of KV pairs.

TiKV Importer produces SST files from a closed [engine](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#engine). These SST files are uploaded and then [ingested](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-glossary#ingest) into TiKV stores.
