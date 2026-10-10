# DM data migration feature updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > New features > Data migration`
- Source Line Ranges: `235-268`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `data-migration`, `precheck`, `incremental-migration`, `binlog`, `gtid`, `task-status`, `shard-merge`, `extended-columns`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0355_f160b92fd9`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `990125299b4c20727ffd442fee74fc5282c400152569cd3a591c791090c19379`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.4.0 DM release-note details about extended columns for merged tables, precheck item changes, optional binlog position or GTID in incremental migration, or added task status indicators.
- Retrieval Keywords: DM, Data migration, extended columns, merged table, sharded schemas and tables, upstream data source information, schema name, table name, precheck, mandatory to optional, character sets incompatible with TiDB, primary key constraints, unique key constraints, server_id, primary-secondary configuration, incremental migration, binlog position, GTID, DM Advanced Task Configuration File, task status, status indicators, bytes/s, RPS, rows/s, data export progress, Query Task Status in TiDB Data Migration
- Follow-up Guidance: The source points to DM documentation for extracting table, schema, and source information into the merged table, DM precheck, the DM advanced task configuration file, and querying task status.
- Classification Note: This is a DM release-notes chunk describing new data migration features and behavior changes in TiDB 6.4.0 for self-managed deployments.

## Official Source Content

### Data migration

* DM supports writing upstream data source information to the extended columns of the downstream merged table [#37797](https://github.com/pingcap/tidb/issues/37797) @[lichunzhu](https://github.com/lichunzhu)

    When merging sharded schemas and tables from upstream to TiDB, you can manually add several fields (extended columns) in the target table and specify their values when configuring the DM task. For example, if you specify the names of the upstream sharded schema and table for the extended columns, the data written to the downstream by DM will include the schema name and table name. When the downstream data looks unusual, you can use this feature to quickly locate the data source information in the target table, such as the schema name and table name.

    For more information, see [Extract table, schema, and source information and write into the merged table](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing#extract-table-schema-and-source-information-and-write-into-the-merged-table).

* DM optimizes the pre-check mechanism by changing some mandatory check items to optional ones [#7333](https://github.com/pingcap/tiflow/issues/7333) @[lichunzhu](https://github.com/lichunzhu)

    To run a data migration task smoothly, DM triggers [a precheck](https://docs.pingcap.com/tidb/stable/dm/dm-precheck) automatically at the start of the task and returns the check results. DM starts the migration only after the precheck is passed.

    In v6.4.0, DM changes the following three check items from mandatory to optional, which improves the pass rate of the pre-check:

    - Check whether the upstream tables use character sets that are incompatible with TiDB.
    - Check whether the upstream tables have primary key constraints or unique key constraints
    - Check whether the database ID `server_id` for the upstream database has been specified in the primary-secondary configuration.

* DM supports configuring binlog position and GTID as optional parameters for incremental migration tasks [#7393](https://github.com/pingcap/tiflow/issues/7393) @[GMHDBJD](https://github.com/GMHDBJD)

    Since v6.4.0, you can perform incremental migration directly without specifying the binlog position or GTID. DM automatically obtains the binlog files generated after the task starts from upstream and migrates these incremental data to the downstream. This relieves users from laborious understanding and complicated configuration.

    For more information, see [DM Advanced Task Configuration File](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).

* DM adds more status indicators for migration tasks [#7343](https://github.com/pingcap/tiflow/issues/7343) @[okJiang](https://github.com/okJiang)

    In v6.4.0, DM adds more performance and progress indicators for migration tasks, which helps you understand the migration performance and progress more intuitively and provides you with a reference for troubleshooting.

    * Add status indicators (in bytes/s) showing data importing and exporting performance.
    * Rename the performance indicator for writing data to the downstream database from TPS to RPS (in rows/s).
    * Add progress indicators showing the data export progress of DM full migration tasks.

    For more information about these indicators, see [Query Task Status in TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/dm-query-status).
