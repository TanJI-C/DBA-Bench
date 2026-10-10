# Import and DM validation changes

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.0.md`
- Source Title: `TiDB 7.5.0 Release Notes`
- Source Heading Path: `TiDB 7.5.0 Release Notes > Feature details > Data migration`
- Source Line Ranges: `127-150`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `lightning`, `tidb`
- Topic Tags: `import into`, `physical import mode`, `binlog filter`, `ddl filtering`, `data validation`, `checkpoint`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0057_4f44f5fcb1`
- Source ID: `tidb-docs-8.1:releases/release-7.5.0.md#data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fd822bb60487716e621f4110dae4dcb9fe5f101d342c35deb837f208ef914d4a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.0#data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.0 data migration changes covering `IMPORT INTO`, DM fine-grained DDL filtering and blocking, or real-time checkpoint updates for continuous data validation.
- Retrieval Keywords: IMPORT INTO, Physical Import Mode, TiDB Lightning, CSV SQL PARQUET, empty table, DM Binlog Filter, MODIFY COLUMN, DROP COLUMN, blocking incompatible DDL changes, reporting errors, continuous data validation, real-time checkpoint updates, binlog position, cutover point, checkpoint
- Follow-up Guidance: The source points to the `IMPORT INTO` statement documentation, the DM binlog event filter parameter descriptions, and the continuous data validation cutover-point documentation.
- Classification Note: The chunk is classified under data_pipeline for DM because it covers import workflow changes and DM replication and validation behavior.

## Official Source Content

### Data migration

* Support the `IMPORT INTO` SQL statement (GA) [#46704](https://github.com/pingcap/tidb/issues/46704) @[D3Hunter](https://github.com/D3Hunter)

    In v7.5.0, the `IMPORT INTO` SQL statement becomes generally available (GA). This statement integrates the [Physical Import Mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) capability of TiDB Lightning and allows you to quickly import data in formats such as CSV, SQL, and PARQUET into an empty table in TiDB. This import method eliminates the need for a separate deployment and management of TiDB Lightning, thereby reducing the complexity of data import and greatly improving import efficiency.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into).

* Data Migration (DM) supports blocking incompatible (data-consistency-corrupting) DDL changes [#9692](https://github.com/pingcap/tiflow/issues/9692) @[GMHDBJD](https://github.com/GMHDBJD)

    Before v7.5.0, the DM Binlog Filter feature can only migrate or filter specified events, and the granularity is relatively coarse. For example, it can only filter large granularity of DDL events such as `ALTER`. This method is limited in some scenarios. For example, the application allows `ADD COLUMN` but not `DROP COLUMN`, but they are both filtered by `ALTER` events in the earlier DM versions.

    To address such issues, v7.5.0 refines the granularity of the supported DDL events, such as support filtering `MODIFY COLUMN` (modify the column data type), `DROP COLUMN`, and other fine-grained DDL events that lead to data loss, truncation of data, and loss of precision. You can configure it as needed. This feature also supports blocking incompatible DDL changes and reporting errors for such changes, so that you can intervene manually in time to avoid impacting downstream application data.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter#parameter-descriptions).

* Support real-time checkpoint updates for continuous data validation [#8463](https://github.com/pingcap/tiflow/issues/8463) @[lichunzhu](https://github.com/lichunzhu)

    Before v7.5.0, the [continuous data validation feature](https://docs.pingcap.com/tidb/stable/dm/dm-continuous-data-validation) ensures the data consistency during replication from DM to downstream. This serves as the basis for cutting over business traffic from the upstream database to TiDB. However, due to various factors such as replication delay and waiting for re-validation of inconsistent data, the continuous validation checkpoint must be refreshed every few minutes. This is unacceptable for some business scenarios where the cutover time is limited to tens of seconds.

    With the introduction of real-time updating of checkpoint for continuous data validation, you can now provide the binlog position from the upstream database. Once the continuous validation program detects this binlog position in memory, it immediately refreshes the checkpoint instead of refreshing it every few minutes. Therefore, you can quickly perform cut-off operations based on this immediately updated checkpoint.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dm/dm-continuous-data-validation#set-the-cutover-point-for-continuous-data-validation).
