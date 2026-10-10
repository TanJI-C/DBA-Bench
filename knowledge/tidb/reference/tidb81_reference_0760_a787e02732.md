# TiCDC changefeed CLI and configuration parameters overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-changefeed-config.md`
- Source Title: `CLI and Configuration Parameters of TiCDC Changefeeds`
- Source Heading Path: `CLI and Configuration Parameters of TiCDC Changefeeds | CLI and Configuration Parameters of TiCDC Changefeeds > Changefeed CLI parameters | CLI and Configuration Parameters of TiCDC Changefeeds > Changefeed configuration parameters`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `changefeed`, `cli`, `parameters`, `sink-uri`, `start-ts`, `target-ts`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0760_a787e02732`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-changefeed-config.md#cli-and-configuration-parameters-of-ticdc-changefeeds`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e3630590022b697d3668df77419087bc130899653892720d3720f2f04bb88571`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#cli-and-configuration-parameters-of-ticdc-changefeeds
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-changefeed-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiCDC changefeed create CLI parameters and the documented meanings of --changefeed-id, --sink-uri, --start-ts, --target-ts, and --config.
- Retrieval Keywords: cdc cli changefeed create, --changefeed-id, --sink-uri, --start-ts, --target-ts, --config, TiCDC changefeed CLI parameters, changefeed configuration parameters, ^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$, [scheme]://[userinfo@][host]:[port][/path]?[query_parameters], mysql, tidb, kafka, URI Encoder
- Follow-up Guidance: The source also states that when the sink URI contains special characters such as ! * ' ( ) ; : @ & = + $ , / ? % # [ ], the special characters need to be escaped.
- Classification Note: This is reference content because it defines the changefeed create command syntax and lists the meanings and accepted formats of its parameters.

## Official Source Content

# CLI and Configuration Parameters of TiCDC Changefeeds
## Changefeed CLI parameters

This section introduces the command-line parameters of TiCDC changefeeds by illustrating how to create a replication (changefeed) task:

```shell
cdc cli changefeed create --server=http://10.0.10.25:8300 --sink-uri="mysql://root:123456@127.0.0.1:3306/" --changefeed-id="simple-replication-task"
```

```shell
Create changefeed successfully!
ID: simple-replication-task
Info: {"upstream_id":7178706266519722477,"namespace":"default","id":"simple-replication-task","sink_uri":"mysql://root:xxxxx@127.0.0.1:4000/?time-zone=","create_time":"2024-12-26T15:05:46.679218+08:00","start_ts":438156275634929669,"engine":"unified","config":{"case_sensitive":false,"force_replicate":false,"ignore_ineligible_table":false,"check_gc_safe_point":true,"enable_sync_point":true,"bdr_mode":false,"sync_point_interval":30000000000,"sync_point_retention":3600000000000,"filter":{"rules":["test.*"],"event_filters":null},"mounter":{"worker_num":16},"sink":{"protocol":"","schema_registry":"","csv":{"delimiter":",","quote":"\"","null":"\\N","include_commit_ts":false},"column_selectors":null,"transaction_atomicity":"none","encoder_concurrency":16,"terminator":"\r\n","date_separator":"none","enable_partition_separator":false},"consistent":{"level":"none","max_log_size":64,"flush_interval":2000,"storage":""}},"state":"normal","creator_version":"v8.1.2"}
```

- `--changefeed-id`: The ID of the replication task. The format must match the `^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$` regular expression. If this ID is not specified, TiCDC automatically generates a UUID (the version 4 format) as the ID.
- `--sink-uri`: The downstream address of the replication task. Configure `--sink-uri` according to the following format. Currently, the scheme supports `mysql`, `tidb`, and `kafka`.

    ```
    [scheme]://[userinfo@][host]:[port][/path]?[query_parameters]
    ```

    When the sink URI contains special characters such as `! * ' ( ) ; : @ & = + $ , / ? % # [ ]`, you need to escape the special characters, for example, in [URI Encoder](https://www.urlencoder.org/).

- `--start-ts`: Specifies the starting TSO of the changefeed. From this TSO, the TiCDC cluster starts pulling data. The default value is the current time.
- `--target-ts`: Specifies the ending TSO of the changefeed. To this TSO, the TiCDC cluster stops pulling data. The default value is empty, which means that TiCDC does not automatically stop pulling data.
- `--config`: Specifies the configuration file of the changefeed.
## Changefeed configuration parameters

This section introduces the configuration of a replication task.
