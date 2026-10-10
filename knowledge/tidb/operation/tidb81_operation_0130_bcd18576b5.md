# Manual purge of relay logs with dmctl

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/relay-log.md`
- Source Title: `Data Migration Relay Log`
- Source Heading Path: `Data Migration Relay Log > Use relay log > Purge relay logs > Manual purge`
- Source Line Ranges: `270-313`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `relay-log`, `purge`, `dmctl`, `binlog`, `subdir`, `manual-operations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0130_bcd18576b5`
- Source ID: `tidb-docs-8.1:dm/relay-log.md#manual-purge`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d08cc760c97b6810fad04c94d2ce30bdde4b8d753825b30d3a2a60daa9ee9000`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/relay-log#manual-purge
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/relay-log.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how the dmctl `purge-relay` command purges relay logs before a specified binlog and how `--sub-dir` changes the purge scope.
- Retrieval Keywords: purge-relay, dmctl purge relay logs, --filename mysql-bin.000001, --sub-dir, subdir, manual purge, relay logs before specified binlog, server-uuid.index, mysql-replica-01
- Follow-up Guidance: The examples show that specifying `--sub-dir e4e0e8ab-09cc-11e9-9220-82cc35207219.000002` retains files in that subdir and later subdirs, while omitting `--sub-dir` purges all relay logs before the current relay log sub-directory.
- Classification Note: This is classified as an operation chunk because the official content demonstrates manual relay log purging with concrete `purge-relay` command usage and purge results.

## Official Source Content

#### Manual purge

Manual purge means using the `purge-relay` command provided by dmctl to specify `subdir` and the binlog name thus to purge all the relay logs **before** the specified binlog. If the `-subdir` option in the command is not specified, all relay logs **before** the current relay log sub-directory are purged.

Assuming that the directory structure of the current relay log is as follows:

```
$ tree .
.
|-- deb76a2b-09cc-11e9-9129-5242cf3bb246.000001
|   |-- mysql-bin.000001
|   |-- mysql-bin.000002
|   |-- mysql-bin.000003
|   `-- relay.meta
|-- deb76a2b-09cc-11e9-9129-5242cf3bb246.000003
|   |-- mysql-bin.000001
|   `-- relay.meta
|-- e4e0e8ab-09cc-11e9-9220-82cc35207219.000002
|   |-- mysql-bin.000001
|   `-- relay.meta
`-- server-uuid.index

$ cat server-uuid.index
deb76a2b-09cc-11e9-9129-5242cf3bb246.000001
e4e0e8ab-09cc-11e9-9220-82cc35207219.000002
deb76a2b-09cc-11e9-9129-5242cf3bb246.000003
```

+ Executing the following `purge-relay` command in dmctl purges all relay log files **before** `e4e0e8ab-09cc-11e9-9220-82cc35207219.000002/mysql-bin.000001`, which are all relay log files in `deb76a2b-09cc-11e9-9129-5242cf3bb246.000001`. Files in `e4e0e8ab-09cc-11e9-9220-82cc35207219.000002` and `deb76a2b-09cc-11e9-9129-5242cf3bb246.000003` are retained.

    ```bash
    purge-relay -s mysql-replica-01 --filename mysql-bin.000001 --sub-dir e4e0e8ab-09cc-11e9-9220-82cc35207219.000002
    ```

+ Executing the following `purge-relay` command in dmctl purges all relay log files **before the current** (`deb76a2b-09cc-11e9-9129-5242cf3bb246.000003`) directory's `mysql-bin.000001`, which are all relay log files in `deb76a2b-09cc-11e9-9129-5242cf3bb246.000001` and `e4e0e8ab-09cc-11e9-9220-82cc35207219.000002`. Files in `deb76a2b-09cc-11e9-9129-5242cf3bb246.000003` are retained.

    ```bash
    purge-relay -s mysql-replica-01 --filename mysql-bin.000001
    ```
