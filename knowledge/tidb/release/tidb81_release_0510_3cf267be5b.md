# Data migration feature updates in 7.4.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Feature details > Data migration`
- Source Line Ranges: `248-280`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dumpling`, `sql`, `ticdc`
- Topic Tags: `import-into`, `global-sort`, `csv`, `compression`, `data-export`, `pulsar`, `kafka`, `large-messages`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0510_3cf267be5b`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `adc99c21ab1701436f2205651b39bd6009c6f3a04923a5e9bfe9463b60b61754`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about TiDB 7.4.0 data migration enhancements involving IMPORT INTO, Dumpling CSV export, or TiCDC downstream messaging changes.
- Retrieval Keywords: TiDB 7.4.0 Data migration, IMPORT INTO CLOUD_STORAGE_URI, Global Sort experimental, Split_File 256 MiB, import compressed CSV and SQL files, .gzip .gz .zstd .zst .snappy, Dumpling --csv-line-terminator, CSV line terminator \r\n \n, TiCDC replicate to Pulsar, canal-json format, TiCDC Kafka large messages, claim-check pattern, max.message.bytes, external storage reference message
- Follow-up Guidance: The source also points to documentation for the IMPORT INTO statement, Dumpling option list, TiCDC sink to Pulsar, and TiCDC Kafka large message handling.
- Classification Note: This is a release-note feature summary for self-managed TiDB 7.4.0 covering data migration updates across shared, Dumpling, SQL, and TiCDC components.

## Official Source Content

### Data migration

* Enhance the `IMPORT INTO` feature [#46704](https://github.com/pingcap/tidb/issues/46704) @[D3Hunter](https://github.com/D3Hunter)

    Starting from v7.4.0, you can add the `CLOUD_STORAGE_URI` option in the `IMPORT INTO` statement to enable the [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) feature (experimental), which helps boost import performance and stability. In the `CLOUD_STORAGE_URI` option, you can specify a cloud storage address for the encoded data.

    In addition, in v7.4.0, the `IMPORT INTO` feature introduces the following functionalities:

    - Support configuring the `Split_File` option, which allows you to split a large CSV file into multiple 256 MiB small CSV files for parallel processing, improving import performance.
    - Support importing compressed CSV and SQL files. The supported compression formats include `.gzip`, `.gz`, `.zstd`, `.zst`, and `.snappy`.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into).

* Dumpling supports the user-defined terminator when exporting data to CSV files [#46982](https://github.com/pingcap/tidb/issues/46982) @[GMHDBJD](https://github.com/GMHDBJD)

    Before v7.4.0, Dumpling uses `"\r\n"` as the line terminator when exporting data to a CSV file. As a result, certain downstream systems that only recognize `"\n"` as the terminator cannot parse the exported CSV file, or have to use a third-party tool for conversion before parsing the file.

    Starting from v7.4.0, Dumpling introduces a new parameter `--csv-line-terminator`. This parameter allows you to specify a desired terminator when you export data to a CSV file. This parameter supports `"\r\n"` and `"\n"`. The default terminator is `"\r\n"` to keep consistent with earlier versions.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dumpling-overview#option-list-of-dumpling).

* TiCDC supports replicating data to Pulsar [#9413](https://github.com/pingcap/tiflow/issues/9413) @[yumchina](https://github.com/yumchina) @[asddongmen](https://github.com/asddongmen)

    Pulsar is a cloud-native and distributed message streaming platform that significantly enhances your real-time data streaming experience. Starting from v7.4.0, TiCDC supports replicating change data to Pulsar in `canal-json` format to achieve seamless integration with Pulsar. With this feature, TiCDC provides you with the ability to easily capture and replicate TiDB changes to Pulsar, offering new possibilities for data processing and analytics capabilities. You can develop your own consumer applications that read and process newly generated change data from Pulsar to meet specific business needs.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-pulsar).

- TiCDC improves large message handling with claim-check pattern [#9153](https://github.com/pingcap/tiflow/issues/9153) @[3AceShowHand](https://github.com/3AceShowHand)

    Before v7.4.0, TiCDC is unable to send large messages exceeding the maximum message size (`max.message.bytes`) of Kafka to downstream. Starting from v7.4.0, when configuring a changefeed with Kafka as the downstream, you can specify an external storage location for storing the large message, and send a reference message containing the address of the large message in the external storage to Kafka. When consumers receive this reference message, they can retrieve the message content from the external storage address.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#send-large-messages-to-external-storage).
