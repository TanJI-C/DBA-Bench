# TiDB 4.0.3 release notes: overview, new features, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.3.md`
- Source Title: `TiDB 4.0.3 Release Notes`
- Source Heading Path: `TiDB 4.0.3 Release Notes | TiDB 4.0.3 Release Notes > New Features | TiDB 4.0.3 Release Notes > Improvements`
- Source Line Ranges: `5-101`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tiflash`, `br`, `ticdc`, `dumpling`, `tidb`, `tikv`, `pd`, `lightning`
- Topic Tags: `release-notes`, `new-features`, `improvements`, `dashboard`, `encryption`, `backup`, `restore`, `changefeed`, `kafka`, `tls`, `mysql-ssl`, `avro`, `pulsar`, `csv`, `logging`, `batch-cop`, `auto-random`, `system-tables`, `json-logs`, `pprof`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0181_6f5d26e7a0`
- Source ID: `tidb-docs-8.1:releases/release-4.0.3.md#tidb-4-0-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `75c8f7f2ee32eda1a135d9627929d4e726449ecf4e613b1cd7cd1f302b945861`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.3#tidb-4-0-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 4.0.3 release summary of new features and improvements across TiDB, TiKV, PD, TiFlash, TiDB Dashboard, BR, TiCDC, Dumpling, and TiDB Lightning.
- Retrieval Keywords: TiDB 4.0.3 Release Notes, Release date July 24 2020, TiDB Dashboard SQL Statements page search, TiFlash proxy file encryption, BR compressing backup files zstd lz4 snappy, TiCDC kafka-client-id sink-uri, TiCDC changefeed configuration offline, customized changefeed name, TLS and MySQL SSL connection, Avro format, Apache Pulsar sink, Dumpling CSV separator and delimiter, tidb_log_desensitization, tidb_allow_batch_cop, tidb_decode_plan, tiflash_tables, tiflash_segments, AUTO RANDOM general availability, experimental.allow-auto-random, tidb_allow_auto_random_explicit_insert, backup.num-threads, PD JSON formatted log, BR JSON logs, BR enabling pprof during runtime, TiDB Lightning black-white-list deprecate
- Follow-up Guidance: The chunk also lists exact configuration names, system tables, and component-specific changes such as `backup.num-threads`, `tidb_allow_auto_random_explicit_insert`, `tiflash_tables`, and `tiflash_segments`.
- Classification Note: This is a self-managed release-notes chunk covering the TiDB 4.0.3 overview of new features and improvements shared across multiple components.

## Official Source Content

# TiDB 4.0.3 Release Notes

Release date: July 24, 2020

TiDB version: 4.0.3
## New Features

+ TiDB Dashboard

    - Display detailed TiDB Dashboard version information [#679](https://github.com/pingcap-incubator/tidb-dashboard/pull/679)
    - Show browser compatibility notice for unsupported browsers or outdated browsers [#654](https://github.com/pingcap-incubator/tidb-dashboard/pull/654)
    - Support searching in the **SQL Statements** page [#658](https://github.com/pingcap-incubator/tidb-dashboard/pull/658)

+ TiFlash

    - Implement file encryption in TiFlash proxy

+ Tools

    + Backup & Restore (BR)

        - Support compressing backup files using zstd, lz4 or snappy [#404](https://github.com/pingcap/br/pull/404)

    + TiCDC

        - Support configuring `kafka-client-id` in MQ sink-uri [#706](https://github.com/pingcap/tiflow/pull/706)
        - Support updating `changefeed` configuration offline [#699](https://github.com/pingcap/tiflow/pull/699)
        - Support setting customized `changefeed` name [#727](https://github.com/pingcap/tiflow/pull/727)
        - Support TLS and MySQL SSL connection [#347](https://github.com/pingcap/tiflow/pull/347)
        - Support outputting changes in the Avro format [#753](https://github.com/pingcap/tiflow/pull/753)
        - Support the Apache Pulsar sink [#751](https://github.com/pingcap/tiflow/pull/751)

    + Dumpling

        - Support the specialized CSV separator and delimiter [#116](https://github.com/pingcap/dumpling/pull/116)
        - Support specifying the format of the output file name [#122](https://github.com/pingcap/dumpling/pull/122)
## Improvements

+ TiDB

    - Add the `tidb_log_desensitization` global variable to control whether to do desensitization when logging SQL queries [#18581](https://github.com/pingcap/tidb/pull/18581)
    - Enable `tidb_allow_batch_cop` by default [#18552](https://github.com/pingcap/tidb/pull/18552)
    - Speed up canceling a query [#18505](https://github.com/pingcap/tidb/pull/18505)
    - Add a header for the `tidb_decode_plan` result [#18501](https://github.com/pingcap/tidb/pull/18501)
    - Make the configuration checker compatible with earlier versions of the configuration file [#18046](https://github.com/pingcap/tidb/pull/18046)
    - Enable collecting the execution information by default [#18518](https://github.com/pingcap/tidb/pull/18518)
    - Add the `tiflash_tables` and `tiflash_segments` system tables [#18536](https://github.com/pingcap/tidb/pull/18536)
    - Move `AUTO RANDOM` out of experimental features and announce its general availability. The improvements and compatibility changes are as follows:
        - Deprecate `experimental.allow-auto-random` in the configuration file. No matter how this item is configured, you can always define the `AUTO RANDOM` feature on columns. [#18613](https://github.com/pingcap/tidb/pull/18613) [#18623](https://github.com/pingcap/tidb/pull/18623)
        - Add the `tidb_allow_auto_random_explicit_insert` session variable to control the explicit writes on `AUTO RANDOM` columns. The default value is `false`. This is to avoid the unexpected `AUTO_RANDOM_BASE` update caused by explicit writes on columns. [#18508](https://github.com/pingcap/tidb/pull/18508)
        - Allow defining `AUTO_RANDOM` only on `BIGINT` and `UNSIGNED BIGINT` columns and restrict the maximum number of shard bits to `15`, which avoids the allocatable space being consumed too quickly [#18538](https://github.com/pingcap/tidb/pull/18538)
        - Do not trigger the `AUTO_RANDOM_BASE` update when defining the `AUTO_RANDOM` attribute on the `BIGINT` column and inserting the negative value into the primary key [#17987](https://github.com/pingcap/tidb/pull/17987)
        - Use the highest bit of an integer for ID allocation when defining the `AUTO_RANDOM` attribute on `UNSIGNED BIGINT` columns, which gets more allocable space [#18404](https://github.com/pingcap/tidb/pull/18404)
        - Support updating the `AUTO_RANDOM` attribute in the result of `SHOW CREATE TABLE` [#18316](https://github.com/pingcap/tidb/pull/18316)

+ TiKV

    - Introduce the new `backup.num-threads` configuration to control the size of the backup thread pool [#8199](https://github.com/tikv/tikv/pull/8199)
    - Do not send store heartbeats when receiving snapshots [#8136](https://github.com/tikv/tikv/pull/8136)
    - Support dynamically changing the shared block cache's capacity [#8232](https://github.com/tikv/tikv/pull/8232)

+ PD

    - Support the JSON formatted log [#2565](https://github.com/pingcap/pd/pull/2565)

+ TiDB Dashboard

    - Improve the Key Visualizer bucket merge for cold logical ranges [#674](https://github.com/pingcap-incubator/tidb-dashboard/pull/674)
    - Rename the configuration item of `disable-telemetry` to `enable-telemetry` for consistency [#684](https://github.com/pingcap-incubator/tidb-dashboard/pull/684)
    - Show the progress bar when switching pages [#661](https://github.com/pingcap-incubator/tidb-dashboard/pull/661)
    - Ensure that the slow log search now follows the same behavior as log search when there are space separators [#682](https://github.com/pingcap-incubator/tidb-dashboard/pull/682)

+ TiFlash

    - Change the unit of the **DDL Jobs** panel in Grafana to `operations per minute`
    - Add a new dashboard in Grafana to show more metrics about **TiFlash-Proxy**
    - Reduce IOPS in TiFlash proxy

+ Tools

    + TiCDC

        - Replace table ID with table name in metrics [#695](https://github.com/pingcap/tiflow/pull/695)

    + Backup & Restore (BR)

        - Support outputting JSON logs [#336](https://github.com/pingcap/br/issues/336)
        - Support enabling pprof during runtime [#372](https://github.com/pingcap/br/pull/372)
        - Speed up DDL executions by sending DDL concurrently during restore [#377](https://github.com/pingcap/br/pull/377)

    + TiDB Lightning

        - Deprecate `black-white-list` with a newer and easier-to-understand filter format [#332](https://github.com/pingcap/tidb-lightning/pull/332)
