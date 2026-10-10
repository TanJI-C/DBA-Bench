# DM common error handling and invalid connection cause

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-error-handling.md`
- Source Title: `Handle Errors in TiDB Data Migration`
- Source Heading Path: `Handle Errors in TiDB Data Migration > Handle common errors | Handle Errors in TiDB Data Migration > Handle common errors > What can I do when a migration task is interrupted with the `invalid connection` error returned? | Handle Errors in TiDB Data Migration > Handle common errors > What can I do when a migration task is interrupted with the `invalid connection` error returned? > Reason`
- Source Line Ranges: `94-115`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `tikv`
- Topic Tags: `common-errors`, `invalid-connection`, `bad-connection`, `grpc`, `dump-unit`, `task-check`, `password-encryption`, `network-failure`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0028_e147151dc6`
- Source ID: `tidb-docs-8.1:dm/dm-error-handling.md#handle-common-errors`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `52f15946f5a34fa5921e6ed2c17e4a2ed1dfc5da4afcaaf4a1926407be7a032c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#handle-common-errors
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-error-handling.md

## Retrieval Guidance

- Use When: Use this chunk when looking up common DM error codes such as `code=10003` invalid connection, `code=10002` bad connection, `code=38008` gRPC communication error, or related handling notes.
- Retrieval Keywords: Handle common errors, code=10003, invalid connection, code=10002, bad connection, code=38008, gRPC communication among DM components, code=32001, mydumper: argument list too long., extra-args, --regex '.*\\.hello$', code=20010, decrypting the database password, correctly encrypted using dmctl, code=26002, task check fails to establish database connection, TiKV busy
- Follow-up Guidance: The `invalid connection` section explains that anomalies such as network failure, TiDB restart, and TiKV busy can occur between DM and the downstream TiDB database and that part of the current request data has been sent to TiDB.
- Classification Note: The content is classified as diagnosis because it maps specific DM error codes to their descriptions, causes, and documented handling guidance for common failure cases.

## Official Source Content

## Handle common errors

| <div style="width: 100px;">Error Code</div>       | Error Description                                                     |  How to Handle                                                    |
| :----------- | :------------------------------------------------------------ | :----------------------------------------------------------- |
| `code=10001` |  Abnormal database operation.                                              |  Further analyze the error message and error stack.                                |
| `code=10002` | The `bad connection` error from the underlying database. It usually indicates that the connection between DM and the downstream TiDB instance is abnormal (possibly caused by network failure or TiDB restart) and the currently requested data is not sent to TiDB. |  DM provides automatic recovery for such error. If the recovery is not successful for a long time, check the network or TiDB status. |
| `code=10003` | The `invalid connection` error from the underlying database. It usually indicates that the connection between DM and the downstream TiDB instance is abnormal (possibly caused by network failure or TiDB restart) and the currently requested data is partly sent to TiDB.  | DM provides automatic recovery for such error. If the recovery is not successful for a long time, further check the error message and analyze the information based on the actual situation. |
| `code=10005` |  Occurs when performing the `QUERY` type SQL statements.                                         |                                                              |
| `code=10006` |  Occurs when performing the `EXECUTE` type SQL statements, including DDL statements and DML statements of the `INSERT`, `UPDATE`or `DELETE` type. For more detailed error information, check the error message which usually includes the error code and error information returned for database operations.
|                                                              |
| `code=11006` |  Occurs when the built-in parser of DM parses the incompatible DDL statements.          |  Refer to [Data Migration - incompatible DDL statements](https://docs.pingcap.com/tidb/stable/dm/dm-faq#how-to-handle-incompatible-ddl-statements) for solution. |
| `code=20010` |   Occurs when decrypting the database password that is provided in task configuration.                   |  Check whether the downstream database password provided in the configuration task is [correctly encrypted using dmctl](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#encrypt-the-database-password). |
| `code=26002` |  The task check fails to establish database connection. For more detailed error information, check the error message which usually includes the error code and error information returned for database operations. |  Check whether the machine where DM-master is located has permission to access the upstream. |
| `code=32001` |   Abnormal dump processing unit                                            |  If the error message contains `mydumper: argument list too long.`, configure the table to be exported by manually adding the `--regex` regular expression in the Mydumper argument `extra-args` in the `task.yaml` file according to the block-allow list. For example, to export all tables named `hello`, add `--regex '.*\\.hello$'`; to export all tables, add `--regex '.*'`. |
| `code=38008` |  An error occurs in the gRPC communication among DM components.                                     |   Check `class`. Find out the error occurs in the interaction of which components. Determine the type of communication error. If the error occurs when establishing gRPC connection, check whether the communication server is working normally. |
### What can I do when a migration task is interrupted with the `invalid connection` error returned?
#### Reason

The `invalid connection` error indicates that anomalies have occurred in the connection between DM and the downstream TiDB database (such as network failure, TiDB restart, and TiKV busy) and that a part of the data for the current request has been sent to TiDB.
