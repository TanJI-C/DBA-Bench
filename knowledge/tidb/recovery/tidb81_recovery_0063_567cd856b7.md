# Handle parallel import node failures and checksum wait errors

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-distributed-import.md`
- Source Title: `Use TiDB Lightning to Import Data in Parallel`
- Source Heading Path: `Use TiDB Lightning to Import Data in Parallel > Handle errors | Use TiDB Lightning to Import Data in Parallel > Handle errors > Some TiDB Lightning nodes exit abnormally | Use TiDB Lightning to Import Data in Parallel > Handle errors > During an import, an error "Target table is calculating checksum. Please wait until the checksum is finished and try again" is reported`
- Source Line Ranges: `185-209`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `shared`
- Topic Tags: `error-handling`, `checkpoint`, `restart`, `oom`, `network-timeout`, `checksum`, `failed-tasks`, `filter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0063_567cd856b7`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-distributed-import.md#handle-errors`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1bc9c7285cac701daae6295317aa6fe59e43a4cc077ddd06ac481059cb1703dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import#handle-errors
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-distributed-import.md

## Retrieval Guidance

- Use When: Use this chunk when parallel TiDB Lightning nodes fail and you need the documented recovery paths for normal exit, OOM, network timeout, data inaccuracy, or the checksum wait error.
- Retrieval Keywords: Some TiDB Lightning nodes exit abnormally, checkpoint-error-ignore, --checkpoint-error-ignore=all, checkpoint-error-destroy, filter parameter, network timeout, OOM, checksum mismatch, Target table is calculating checksum. Please wait until the checksum is finished and try again, restart failed tasks, restart from checkpoints
- Follow-up Guidance: For the checksum wait error, wait until checksum finishes and then restart the failed tasks; for data inaccuracy errors, run `checkpoint-error-destroy` on all Lightning nodes and re-import failed tables using the `filter` parameter on all nodes.
- Classification Note: This is classified as a recovery chunk because the content describes how to handle abnormal exits and checksum-related import failures using checkpoint and restart procedures.

## Official Source Content

## Handle errors
### Some TiDB Lightning nodes exit abnormally

If one or more TiDB Lightning nodes exit abnormally during a parallel import, identify the cause based on the logged error, and handle the error according to the error type:

- If the error shows normal exit (for example, exit in response to a kill command) or termination by the operating system due to OOM, adjust the configuration and then restart the TiDB Lightning nodes.

- If the error has no impact on data accuracy, for example, network timeout, perform the following steps:

    1. Run the [`checkpoint-error-ignore`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-checkpoints#--checkpoint-error-ignore) command with the setting `--checkpoint-error-ignore=all` on all failed nodes to clean errors in the checkpoint source data.

    2. Restart these nodes to continue importing data from checkpoints.

- If you see errors in the log that result in data inaccuracies, such as a checksum mismatch indicating invalid data in the source file, you can perform the following steps to resolve this issue:

    1. Run the [`checkpoint-error-destroy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-checkpoints#--checkpoint-error-destroy) command on all Lightning nodes, including successful nodes. This command removes the imported data from failed tables and resets the checkpoint status of these tables to "not yet started".

    2. Reconfigure and import the data of failed tables by using the [`filter`](https://docs.pingcap.com/tidb/stable/table-filter) parameter on all TiDB Lightning nodes, including normally exiting nodes.

        When you reconfigure the Lightning parallel import task, do not include the `checkpoint-error-destroy` command in the startup script of each Lightning node. Otherwise, this command deletes shared metadata used by multiple parallel import tasks, which might cause issues during data import. For example, if a second Lightning import task is started, it will delete the metadata written by the first task, leading to abnormal data import.
### During an import, an error "Target table is calculating checksum. Please wait until the checksum is finished and try again" is reported

Some parallel imports involve a large number of tables or tables with a small volume of data. In this case, it is possible that before one or more tasks start processing a table, other tasks of this table have finished and data checksum is in progress. At this time, an error `Target table is calculating checksum. Please wait until the checksum is finished and try again` is reported. In this case, you can wait for the completion of checksum and then restart the failed tasks. The error disappears and data accuracy is not affected.
