# TiDB Lightning monitoring metrics reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/monitor-tidb-lightning.md`
- Source Title: `TiDB Lightning Monitoring`
- Source Heading Path: `TiDB Lightning Monitoring > Monitoring metrics`
- Source Line Ranges: `124-240`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `shared`
- Topic Tags: `metrics`, `prometheus`, `namespace`, `counters`, `gauges`, `histograms`, `workers`, `engines`, `chunks`, `checksum`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0934_131361b72f`
- Source ID: `tidb-docs-8.1:tidb-lightning/monitor-tidb-lightning.md#monitoring-metrics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5cc9d9ed2ec654aa6b08a466d21919747ed5a345c7d6821d1e0c61317ffedb4a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/monitor-tidb-lightning#monitoring-metrics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/monitor-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Lightning Prometheus metrics reference, including the lightning_* namespace, metric types, and label meanings.
- Retrieval Keywords: Monitoring metrics, lightning_*, lightning_importer_engine, lightning_idle_workers, lightning_kv_encoder, lightning_tables, lightning_engines, lightning_chunks, lightning_import_seconds, lightning_row_read_bytes, lightning_row_encode_seconds, lightning_row_kv_deliver_seconds, lightning_block_deliver_seconds, lightning_block_deliver_bytes, lightning_chunk_parser_read_block_seconds, lightning_checksum_seconds, lightning_apply_worker_seconds, Counter, Gauge, Histogram, type open closed, state pending written closed imported completed, result success failure, estimated running finished failed, name table index region io closed-engine
- Follow-up Guidance: The source enumerates labels such as state, result, type, and name, including values like pending, written, imported, success, failure, open, closed, and closed-engine.
- Classification Note: This is classified as reference because the content is a metrics catalog describing exact metric names, types, and labels for TiDB Lightning.

## Official Source Content

## Monitoring metrics

This section explains the monitoring metrics of `tidb-lightning`.

Metrics provided by `tidb-lightning` are listed under the namespace `lightning_*`.

- **`lightning_importer_engine`** (Counter)

    Counts open and closed engine files. Labels:

    - **type**:
        * `open`
        * `closed`

- **`lightning_idle_workers`** (Gauge)

    Counts idle workers. Labels:

    - **name**:
        * `table`: the remainder of `table-concurrency`, normally 0 until the end of the process
        * `index`: the remainder of `index-concurrency`, normally 0 until the end of the process
        * `region`: the remainder of `region-concurrency`, normally 0 until the end of the process
        * `io`: the remainder of `io-concurrency`, normally close to configured value (default 5), and close to 0 means the disk is too slow
        * `closed-engine`: number of engines which have been closed but not yet cleaned up, normally close to index + table-concurrency (default 8). A value close to 0 means TiDB Lightning is faster than TiKV Importer, which might cause TiDB Lightning to stall

- **`lightning_kv_encoder`** (Counter)

    Counts open and closed KV encoders. KV encoders are in-memory TiDB instances that convert SQL `INSERT` statements into KV pairs. The net values need to be bounded in a healthy situation. Labels:

    - **type**:
        * `open`
        * `closed`

* **`lightning_tables`** (Counter)

    Counts processed tables and their statuses. Labels:

    - **state**: the status of the table, indicating which phase should be completed
        * `pending`: not yet processed
        * `written`: all data encoded and sent
        * `closed`: all corresponding engine files closed
        * `imported`: all engine files have been imported into the target cluster
        * `altered_auto_inc`: AUTO_INCREMENT ID altered
        * `checksum`: checksum performed
        * `analyzed`: statistics analysis performed
        * `completed`: the table has been fully imported and verified
    - **result**: the result of the current phase
        * `success`: the phase completed successfully
        * `failure`: the phase failed (did not complete)

* **`lightning_engines`** (Counter)

    Counts number of engine files processed and their status. Labels:

    - **state**: the status of the engine, indicating which phase should be completed
        * `pending`: not yet processed
        * `written`: all data encoded and sent
        * `closed`: engine file closed
        * `imported`: the engine file has been imported into the target cluster
        * `completed`: the engine has been fully imported
    - **result**: the result of the current phase
        * `success`: the phase completed successfully
        * `failure`: the phase failed (did not complete)

- **`lightning_chunks`** (Counter)

    Counts number of chunks processed and their status. Labels:

    - **state**: a chunk's status, indicating which phase the chunk is in
        * `estimated`: (not a state) this value gives total number of chunks in current task
        * `pending`: loaded but not yet processed
        * `running`: data are being encoded and sent
        * `finished`: the entire chunk has been processed
        * `failed`: errors happened during processing

- **`lightning_import_seconds`** (Histogram)

    Bucketed histogram for the time needed to import a table.

- **`lightning_row_read_bytes`** (Histogram)

    Bucketed histogram for the size of a single SQL row.

- **`lightning_row_encode_seconds`** (Histogram)

    Bucketed histogram for the time needed to encode a single SQL row into KV pairs.

- **`lightning_row_kv_deliver_seconds`** (Histogram)

    Bucketed histogram for the time needed to deliver a set of KV pairs corresponding to one single SQL row.

- **`lightning_block_deliver_seconds`** (Histogram)

    Bucketed histogram for the time needed to deliver a block of KV pairs to Importer.

- **`lightning_block_deliver_bytes`** (Histogram)

    Bucketed histogram for the uncompressed size of a block of KV pairs delivered to Importer.

- **`lightning_chunk_parser_read_block_seconds`** (Histogram)

    Bucketed histogram for the time needed by the data file parser to read a block.

- **`lightning_checksum_seconds`** (Histogram)

    Bucketed histogram for the time needed to compute the checksum of a table.

- **`lightning_apply_worker_seconds`** (Histogram)

    Bucketed histogram for the time needed to acquire an idle worker (see also the `lightning_idle_workers` gauge). Labels:

    - **name**:
        * `table`
        * `index`
        * `region`
        * `io`
        * `closed-engine`
