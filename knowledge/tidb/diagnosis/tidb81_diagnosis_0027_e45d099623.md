# DM error system and troubleshooting workflow

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-error-handling.md`
- Source Title: `Handle Errors in TiDB Data Migration`
- Source Heading Path: `Handle Errors in TiDB Data Migration | Handle Errors in TiDB Data Migration > Error system | Handle Errors in TiDB Data Migration > Troubleshooting`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `error-codes`, `error-classes`, `error-scope`, `severity`, `troubleshooting`, `logs`, `resume-task`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0027_e45d099623`
- Source ID: `tidb-docs-8.1:dm/dm-error-handling.md#handle-errors-in-tidb-data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `365f0d9d7aefecbd1e6fda5e49263209e0c196197cf2e50737f0e745733a9056`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#handle-errors-in-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-error-handling.md

## Retrieval Guidance

- Use When: Use this chunk when identifying DM error fields, error classes, scope and severity, or when following the documented DM troubleshooting workflow with query-status, logs, and resume-task.
- Retrieval Keywords: DM error system, code class scope level message workaround, query-status, resume-task ${task name}, DM-master log files, DM-worker log files, error code lists, database functional config binlog-op checkpoint task-check relay-unit dump-unit load-unit sync-unit dm-master dm-worker dmctl
- Follow-up Guidance: After the error is resolved, restart the task using dmctl with `resume-task ${task name}`, and in some cases refer to Reset the Data Migration Task.
- Classification Note: The content is classified as diagnosis because it defines DM error metadata such as `code`, `class`, `scope`, and `level`, and provides a troubleshooting sequence using status output and logs.

## Official Source Content

# Handle Errors in TiDB Data Migration

This document introduces the error system and how to handle common errors when you use DM.
## Error system

In the error system, usually, the information of a specific error is as follows:

- `code`: error code.

    DM uses the same error code for the same error type. An error code does not change as the DM version changes.

    Some errors might be removed during the DM iteration, while the error codes are not. DM uses a new error code instead of an existing one for a new error.

- `class`: error type.

    It is used to mark the component where an error occurs (error source).

    The following table displays all error types, error sources, and error samples.

    |  <div style="width: 100px;">Error Type</div>    |   Error Source            | Error Sample                                                     |
    | :-------------- | :------------------------------ | :------------------------------------------------------------ |
    | `database`       |  Database operations         | `[code=10003:class=database:scope=downstream:level=medium] database driver: invalid connection` |
    | `functional`     |  Underlying functions of DM           | `[code=11005:class=functional:scope=internal:level=high] not allowed operation: alter multiple tables in one statement` |
    | `config`         |  Incorrect configuration                      | `[code=20005:class=config:scope=internal:level=medium] empty source-id not valid` |
    | `binlog-op`      |  Binlog operations          | `[code=22001:class=binlog-op:scope=internal:level=high] empty UUIDs not valid` |
    | `checkpoint`     |  checkpoint operations  | `[code=24002:class=checkpoint:scope=internal:level=high] save point bin.1234 is older than current pos bin.1371` |
    | `task-check`     |  Performing task check       | `[code=26003:class=task-check:scope=internal:level=medium] new table router error` |
    | `relay-event-lib`|  Executing the basic functions of the relay module | `[code=28001:class=relay-event-lib:scope=internal:level=high] parse server-uuid.index` |
    | `relay-unit`     |  relay processing unit    | `[code=30015:class=relay-unit:scope=upstream:level=high] TCPReader get event: ERROR 1236 (HY000): Could not open log file` |
    | `dump-unit`      |   dump processing unit    | `[code=32001:class=dump-unit:scope=internal:level=high] mydumper runs with error: CRITICAL **: 15:12:17.559: Error connecting to database: Access denied for user 'root'@'172.17.0.1' (using password: NO)` |
    | `load-unit`      |  load processing unit    | `[code=34002:class=load-unit:scope=internal:level=high] corresponding ending of sql: ')' not found` |
    | `sync-unit`      |  sync processing unit     | `[code=36027:class=sync-unit:scope=internal:level=high] Column count doesn't match value count: 9 (columns) vs 10 (values)` |
    | `dm-master`      |   DM-master service | `[code=38008:class=dm-master:scope=internal:level=high] grpc request error: rpc error: code = Unavailable desc = all SubConns are in TransientFailure, latest connection error: connection error: desc = "transport: Error while dialing dial tcp 172.17.0.2:8262: connect: connection refused"` |
    | `dm-worker`      |  DM-worker service  | `[code=40066:class=dm-worker:scope=internal:level=high] ExecuteDDL timeout, try use query-status to query whether the DDL is still blocking` |
    | `dm-tracer`      |  DM-tracer service  | `[code=42004:class=dm-tracer:scope=internal:level=medium] trace event test.1 not found` |
    | `schema-tracker` | schema-tracker (during incremental data replication)   | `[code=44006:class=schema-tracker:scope=internal:level=high],"cannot track DDL: ALTER TABLE test DROP COLUMN col1"` |
    | `scheduler`      | Scheduling operations (of data migration tasks)   | `[code=46001:class=scheduler:scope=internal:level=high],"the scheduler has not started"` |
    | `dmctl`          | An error occurs within dmctl or when it interacts with other components | `[code=48001:class=dmctl:scope=internal:level=high],"can not create grpc connection"` |

- `scope`: Error scope.

    It is used to mark the scope and source of DM objects when an error occurs. `scope` includes four types: `not-set`, `upstream`, `downstream`, and `internal`.

    If the logic of the error directly involves requests between upstream and downstream databases, the scope is set to `upstream` or `downstream`; otherwise, it is currently set to `internal`.

- `level`: Error level.

    The severity level of the error, including `low`, `medium`, and `high`.

    - The `low` level error usually relates to user operations and incorrect inputs. It does not affect migration tasks.
    - The `medium` level error usually relates to user configurations. It affects some newly started services; however, it does not affect the existing DM migration status.
    - The `high` level error usually needs your attention, since you need to resolve it to avoid the possible interruption of a migration task.

- `message`: Error descriptions.

    Detailed descriptions of the error. To wrap and store every additional layer of error message on the error call chain, the [errors.Wrap](https://godoc.org/github.com/pkg/errors#hdr-Adding_context_to_an_error) mode is adopted. The message description wrapped at the outermost layer indicates the error in DM and the message description wrapped at the innermost layer indicates the error source.

- `workaround`: Error handling methods (optional)

    The handling methods for this error. For some confirmed errors (such as configuration errors), DM gives the corresponding manual handling methods in `workaround`.

- Error stack information (optional)

    Whether DM outputs the error stack information depends on the error severity and the necessity. The error stack records the complete stack call information when the error occurs. If you cannot figure out the error cause based on the basic information and the error message, you can trace the execution path of the code when the error occurs using the error stack.

For the complete list of error codes, refer to the [error code lists](https://github.com/pingcap/tiflow/blob/release-8.1/dm/_utils/terror_gen/errors_release.txt).
## Troubleshooting

If you encounter an error while running DM, take the following steps to troubleshoot this error:

1. Execute the `query-status` command to check the task running status and the error output.

2. Check the log files related to the error. The log files are on the DM-master and DM-worker nodes. To get key information about the error, refer to the [error system](#error-system). Then check the [Handle Common Errors](#handle-common-errors) section to find the solution.

3. If the error is not covered in this document, and you cannot solve the problem by checking the log or monitoring metrics, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

4. After the error is resolved, restart the task using dmctl.

    ```bash
    resume-task ${task name}
    ```

However, you need to reset the data migration task in some cases. For details, refer to [Reset the Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-faq#how-to-reset-the-data-migration-task).
