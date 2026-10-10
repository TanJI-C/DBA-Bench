# TiFlash maintenance overview, version check, logs, and system table

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/maintain-tiflash.md`
- Source Title: `Maintain a TiFlash Cluster`
- Source Heading Path: `Maintain a TiFlash Cluster | Maintain a TiFlash Cluster > Check the TiFlash version | Maintain a TiFlash Cluster > TiFlash critical logs | Maintain a TiFlash Cluster > TiFlash system table`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `pd`
- Topic Tags: `maintenance`, `version`, `logs`, `coprocessor`, `replication`, `system-table`, `information-schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0476_f387a4b09a`
- Source ID: `tidb-docs-8.1:tiflash/maintain-tiflash.md#maintain-a-tiflash-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fab9ffc7373ce0f8b1f182cd99f12138724dda309c1c030c3b211754e9853b86`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/maintain-tiflash#maintain-a-tiflash-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/maintain-tiflash.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiFlash maintenance basics such as checking the TiFlash version, interpreting TiFlash critical logs for replication or Coprocessor requests, or identifying columns in the information_schema.tiflash_replica system table.
- Retrieval Keywords: Maintain a TiFlash Cluster, ./tiflash version, LD_LIBRARY_PATH, libtiflash_proxy.so, TiFlash version, [logger], tiflash.toml, TiFlash critical logs, KVStore: Start to persist, CoprocessorHandler, Handling DAG request, Handle DAG request done, thread ID, information_schema.tiflash_replica, TABLE_SCHEMA, TABLE_NAME, TABLE_ID, REPLICA_COUNT, LOCATION_LABELS, AVAILABLE, PROGRESS
- Follow-up Guidance: The source also states that related Coprocessor logs can be located by finding the beginning or end of a request and tracing the thread ID printed at the start of the log.
- Classification Note: This is classified as a self-managed TiFlash operation topic because the content describes routine maintenance tasks, log inspection, version checking, and a TiFlash system table.

## Official Source Content

# Maintain a TiFlash Cluster

This document describes how to perform common operations when you maintain a [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) cluster, including checking the TiFlash version. This document also introduces critical logs and a system table of TiFlash.
## Check the TiFlash version

There are two ways to check the TiFlash version:

- If the binary file name of TiFlash is `tiflash`, you can check the version by executing the `./tiflash version` command.

    However, to execute the above command, you need to add the directory path which includes the `libtiflash_proxy.so` dynamic library to the `LD_LIBRARY_PATH` environment variable. This is because the running of TiFlash relies on the `libtiflash_proxy.so` dynamic library.

    For example, when `tiflash` and `libtiflash_proxy.so` are in the same directory, you can first switch to this directory, and then use the following command to check the TiFlash version:

    ```shell
    LD_LIBRARY_PATH=./ ./tiflash version
    ```

- Check the TiFlash version by referring to the TiFlash log. For the log path, see the `[logger]` part in [the `tiflash.toml` file](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file). For example:

    ```
    <information>: TiFlash version: TiFlash 0.2.0 master-375035282451103999f3863c691e2fc2
    ```
## TiFlash critical logs

| Log Information | Log Description |
|---------------|-------------------|
| `[INFO] [<unknown>] ["KVStore: Start to persist [region 47, applied: term 6 index 10]"] [thread_id=23]` | Data starts to be replicated (the number in the square brackets at the start of the log refers to the thread ID |
| `[DEBUG] [<unknown>] ["CoprocessorHandler: grpc::Status DB::CoprocessorHandler::execute(): Handling DAG request"] [thread_id=30]` | Handling DAG request, that is, TiFlash starts to handle a Coprocessor request |
| `[DEBUG] [<unknown>] ["CoprocessorHandler: grpc::Status DB::CoprocessorHandler::execute(): Handle DAG request done"] [thread_id=30]` | Handling DAG request done, that is, TiFlash finishes handling a Coprocessor request |

You can find the beginning or the end of a Coprocessor request, and then locate the related logs of the Coprocessor request through the thread ID printed at the start of the log.
## TiFlash system table

The column names and their descriptions of the `information_schema.tiflash_replica` system table are as follows:

| Column Name | Description |
|---------------|-----------|
| TABLE_SCHEMA | Database name |
| TABLE_NAME | Table name |
| TABLE_ID | Table ID |
| REPLICA_COUNT | Number of TiFlash replicas |
|LOCATION_LABELS | The hint for PD, based on which multiple replicas in a Region are scattered |
| AVAILABLE | Available or not (0/1)|
| PROGRESS | Replication progress [0.0~1.0] |
