# Create TiCDC Pulsar changefeed

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-pulsar.md`
- Source Title: `Replicate Data to Pulsar`
- Source Heading Path: `Replicate Data to Pulsar | Replicate Data to Pulsar > Create a replication task to replicate incremental data to Pulsar`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `changefeed`, `pulsar`, `sink-uri`, `incremental-replication`, `cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0264_d01b1b7ca7`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-pulsar.md#replicate-data-to-pulsar`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a993b0aab9df6f4fc3bece0720df1e076255eab1f6d8a65c1c56d31472e207d5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-pulsar#replicate-data-to-pulsar
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-pulsar.md

## Retrieval Guidance

- Use When: Use this content when you need the exact TiCDC CLI command and parameter meanings for creating a changefeed that replicates incremental data to Pulsar.
- Retrieval Keywords: cdc cli changefeed create, --server, --sink-uri, --config, --changefeed-id, --start-ts, --target-ts, simple-replication-task, Create changefeed successfully, replicate incremental data to Pulsar
- Follow-up Guidance: It also points to the Sink URI section and the TiCDC changefeed configuration parameters for details about `--sink-uri` and `--config`.
- Classification Note: This is classified as an operation because the content shows the `cdc cli changefeed create` command, its output, and the meanings of the command parameters for creating a replication task.

## Official Source Content

# Replicate Data to Pulsar

This document describes how to create a changefeed that replicates incremental data to Pulsar using TiCDC.
## Create a replication task to replicate incremental data to Pulsar

Create a replication task by running the following command:

```shell
cdc cli changefeed create \
    --server=http://127.0.0.1:8300 \
--sink-uri="pulsar://127.0.0.1:6650/persistent://public/default/yktest?protocol=canal-json" \
--config=./t_changefeed.toml \
--changefeed-id="simple-replication-task"
```

```shell

Create changefeed successfully!
ID: simple-replication-task
Info: {"upstream_id":7277814241002263370,"namespace":"default","id":"simple-replication-task","sink_uri":"pulsar://127.0.0.1:6650/consumer-test?protocol=canal-json","create_time":"2024-12-26T14:42:32.000904+08:00","start_ts":444203257406423044,"config":{"memory_quota":1073741824,"case_sensitive":false,"force_replicate":false,"ignore_ineligible_table":false,"check_gc_safe_point":true,"enable_sync_point":false,"bdr_mode":false,"sync_point_interval":600000000000,"sync_point_retention":86400000000000,"filter":{"rules":["pulsar_test.*"]},"mounter":{"worker_num":16},"sink":{"protocol":"canal-json","csv":{"delimiter":",","quote":"\"","null":"\\N","include_commit_ts":false,"binary_encoding_method":"base64"},"dispatchers":[{"matcher":["pulsar_test.*"],"partition":"","topic":"test_{schema}_{table}"}],"encoder_concurrency":16,"terminator":"\r\n","date_separator":"day","enable_partition_separator":true,"only_output_updated_columns":false,"delete_only_output_handle_key_columns":false,"pulsar_config":{"connection-timeout":30,"operation-timeout":30,"batching-max-messages":1000,"batching-max-publish-delay":10,"send-timeout":30},"advance_timeout":150},"consistent":{"level":"none","max_log_size":64,"flush_interval":2000,"use_file_backend":false},"scheduler":{"enable_table_across_nodes":false,"region_threshold":100000,"write_key_threshold":0},"integrity":{"integrity_check_level":"none","corruption_handle_level":"warn"}},"state":"normal","creator_version":"v8.1.2","resolved_ts":444203257406423044,"checkpoint_ts":444203257406423044,"checkpoint_time":"2024-12-26 14:42:31.410"}
```

The meaning of each parameter is as follows:

- `--server`: the address of a TiCDC server in the TiCDC cluster.
- `--changefeed-id`: the ID of the replication task. The format must match the regular expression `^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$`. If the ID is not specified, TiCDC automatically generates a UUID (in the version 4 format) as the ID.
- `--sink-uri`: the downstream address of the replication task. See [Use Sink URI to configure Pulsar](#sink-uri).
- `--start-ts`: the start TSO of the changefeed. The TiCDC cluster starts pulling data from this TSO. The default value is the current time.
- `--target-ts`: the target TSO of the changefeed. The TiCDC cluster stops pulling data at this TSO. It is empty by default, which means that TiCDC does not automatically stop pulling data.
- `--config`: the changefeed configuration file. See [TiCDC changefeed configuration parameters](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).
