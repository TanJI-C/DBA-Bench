# Changefeed defaults, time zone handling, and Canal output

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-faq.md`
- Source Title: `TiCDC FAQs`
- Source Heading Path: `TiCDC FAQs > How to understand the relationship between the TiCDC time zone and the time zones of the upstream/downstream databases? | TiCDC FAQs > What is the default behavior of TiCDC if I create a replication task without specifying the configuration file in `--config`? | TiCDC FAQs > Does TiCDC support outputting data changes in the Canal protocol?`
- Source Line Ranges: `194-232`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `sql`
- Topic Tags: `time-zone`, `changefeed`, `defaults`, `sink-uri`, `canal-json`, `mq-sink`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0177_4113dd37bc`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-faq.md#how-to-understand-the-relationship-between-the-ticdc-time-zone-and-the-time-zones-of-the-upstream-downstream-databases`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `efd52c36ee53d8da76c756460d440ce996c8fa7a9202097c3f177a0de9c36889`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#how-to-understand-the-relationship-between-the-ticdc-time-zone-and-the-time-zones-of-the-upstream-downstream-databases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiCDC time zone relationships, default changefeed behavior without `--config`, or enabling Canal JSON output with `protocol=canal-json`.
- Retrieval Keywords: --tz, TZ environment variable, time-zone parameter in sink-uri, upstream time zone, downstream time zone, cdc cli changefeed create, --config, default behavior, replicates all tables except system tables, valid indexes, Canal protocol, canal-json, --sink-uri, MQ sinks, Kafka
- Follow-up Guidance: The content points to TiCDC changefeed configurations and Time Zone Support for more details.
- Classification Note: This is classified as configuration because the content explains time zone parameters, changefeed creation defaults, and sink protocol settings such as `protocol=canal-json`.

## Official Source Content

## How to understand the relationship between the TiCDC time zone and the time zones of the upstream/downstream databases?

||Upstream time zone| TiCDC time zone|Downstream time zone|
| :-: | :-: | :-: | :-: |
| Configuration method | See [Time Zone Support](https://docs.pingcap.com/tidb/stable/configure-time-zone) | Configured using the `--tz` parameter when you start the TiCDC server |  Configured using the `time-zone` parameter in `sink-uri` |
| Description | The time zone of the upstream TiDB, which affects DML operations of the timestamp type and DDL operations related to timestamp type columns.| TiCDC assumes that the upstream TiDB's time zone is the same as the TiCDC time zone configuration, and performs related operations on the timestamp column.| The downstream MySQL processes the timestamp in the DML and DDL operations according to the downstream time zone setting.|

 > **Note:**
 >
 > Be careful when you set the time zone of the TiCDC server, because this time zone is used for converting the time type. Keep the upstream time zone, TiCDC time zone, and the downstream time zone consistent. The TiCDC server chooses its time zone in the following priority:
 >
 > - TiCDC first uses the time zone specified using `--tz`.
 > - When `--tz` is not available, TiCDC tries to read the time zone set using the `TZ` environment variable.
 > - When the `TZ` environment variable is not available, TiCDC uses the default time zone of the machine.
## What is the default behavior of TiCDC if I create a replication task without specifying the configuration file in `--config`?

If you use the `cdc cli changefeed create` command without specifying the `-config` parameter, TiCDC creates the replication task in the following default behaviors:

- Replicates all tables except system tables
- Only replicates tables that contain [valid indexes](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#best-practices)
## Does TiCDC support outputting data changes in the Canal protocol?

Yes. Note that for the Canal protocol, TiCDC only supports the JSON output format, while the protobuf format is not officially supported yet. To enable Canal output, specify `protocol` as `canal-json` in the `--sink-uri` configuration. For example:

```shell
cdc cli changefeed create --server=http://127.0.0.1:8300 --sink-uri="kafka://127.0.0.1:9092/cdc-test?kafka-version=2.4.0&protocol=canal-json" --config changefeed.toml
```

> **Note:**
>
> * This feature is introduced in TiCDC 4.0.2.
> * TiCDC currently supports outputting data changes in the Canal-JSON format only to MQ sinks such as Kafka.

For more information, refer to [TiCDC changefeed configurations](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).
