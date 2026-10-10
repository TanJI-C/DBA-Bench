# TiCDC MySQL replication task creation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-mysql.md`
- Source Title: `Replicate Data to MySQL-compatible Databases`
- Source Heading Path: `Replicate Data to MySQL-compatible Databases | Replicate Data to MySQL-compatible Databases > Create a replication task`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `dumpling`, `lightning`, `br`, `tidb`
- Topic Tags: `changefeed`, `replication-task`, `sink-uri`, `start-ts`, `target-ts`, `incremental-replication`, `full-data-initialization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0263_d4b324ca17`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-mysql.md#replicate-data-to-mysql-compatible-databases`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `53b08ca1a08081c68e20079081ef146bea5391681e22c2f8253b1b9ed482d1ce`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#replicate-data-to-mysql-compatible-databases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiCDC command and flags to create a MySQL-compatible changefeed for incremental replication, including start-ts or target-ts details.
- Retrieval Keywords: cdc cli changefeed create, --server, --sink-uri, --changefeed-id, --start-ts, --target-ts, simple-replication-task, Create changefeed successfully, TiCDC only replicates incremental data, Dumpling, TiDB Lightning, BR, backupTS, pos value in the metadata file
- Follow-up Guidance: The source also notes that full data must be initialized with Dumpling/TiDB Lightning or BR, and after that the changefeed start-ts should be set to the backup TSO such as Dumpling metadata pos or BR backupTS.
- Classification Note: This is classified as an operation chunk because it provides the changefeed creation command, flag meanings, and task initialization notes for a replication task.

## Official Source Content

# Replicate Data to MySQL-compatible Databases

This document describes how to replicate incremental data to the downstream TiDB database or other MySQL-compatible databases using TiCDC. It also introduces how to use the eventually consistent replication feature in disaster scenarios.
## Create a replication task

Create a replication task by running the following command:

```shell
cdc cli changefeed create \
    --server=http://10.0.10.25:8300 \
    --sink-uri="mysql://root:123456@127.0.0.1:3306/" \
    --changefeed-id="simple-replication-task"
```

```shell
Create changefeed successfully!
ID: simple-replication-task
Info: {"sink-uri":"mysql://root:123456@127.0.0.1:3306/","opts":{},"create-time":"2023-11-28T22:04:08.103600025+08:00","start-ts":415241823337054209,"target-ts":0,"admin-job-type":0,"sort-engine":"unified","sort-dir":".","config":{"case-sensitive":false,"filter":{"rules":["*.*"],"ignore-txn-start-ts":null,"ddl-allow-list":null},"mounter":{"worker-num":16},"sink":{"dispatchers":null},"scheduler":{"type":"table-number","polling-time":-1}},"state":"normal","history":null,"error":null}
```

- `--server`: The address of any TiCDC server in the TiCDC cluster.
- `--changefeed-id`: The ID of the replication task. The format must match the `^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$` regular expression. If this ID is not specified, TiCDC automatically generates a UUID (the version 4 format) as the ID.
- `--sink-uri`: The downstream address of the replication task. For details, see [Configure sink URI with `mysql`/`tidb`](#configure-sink-uri-for-mysql-or-tidb).
- `--start-ts`: Specifies the starting TSO of the changefeed. From this TSO, the TiCDC cluster starts pulling data. The default value is the current time.
- `--target-ts`: Specifies the ending TSO of the changefeed. To this TSO, the TiCDC cluster stops pulling data. The default value is empty, which means that TiCDC does not automatically stop pulling data.
- `--config`: Specifies the changefeed configuration file. For details, see [TiCDC Changefeed Configuration Parameters](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).

> **Note:**
>
> - TiCDC only replicates incremental data. To initialize full data, use Dumpling/TiDB Lightning or BR.
> - After the full data is initialized, you need to specify the `start-ts` as the TSO when the upstream backup is performed. For example, the `pos` value in the metadata file under the Dumpling directory, or the `backupTS` value in the log output after BR completes the backup.
