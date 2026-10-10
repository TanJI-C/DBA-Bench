# Operate continuous data validation status, errors, and stop actions

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-continuous-data-validation.md`
- Source Title: `Continuous Data Validation in DM`
- Source Heading Path: `Continuous Data Validation in DM > Use continuous data validation | Continuous Data Validation in DM > Use continuous data validation > View the validation status | Continuous Data Validation in DM > Use continuous data validation > Handle error rows | Continuous Data Validation in DM > Stop continuous data validation`
- Source Line Ranges: `78-251`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `validation-status`, `query-status`, `show-error`, `error-rows`, `clear-error`, `ignore-error`, `resolve-error`, `stop-validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0087_a7d9742eab`
- Source ID: `tidb-docs-8.1:dm/dm-continuous-data-validation.md#use-continuous-data-validation`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `881d84d6a156db8a792843dd007aec4ef44cc5324a55750d789bf1ff8a1afaa5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-continuous-data-validation#use-continuous-data-validation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-continuous-data-validation.md

## Retrieval Guidance

- Use When: Use this chunk when you need dmctl commands and status fields for checking continuous data validation, viewing error rows, handling error row states, or stopping validation.
- Retrieval Keywords: dmctl query-status <task-name>, validation status, dmctl validation status <task-name>, --table-stage, dmctl validation show-error, --error, error rows, clear-error, ignore-error, resolve-error, validation stop, processedRowsStatus, pendingRowsStatus, errorRowsStatus, NewErr, ignored, resolved
- Follow-up Guidance: It explains that error rows are handled manually and can be processed by locating the error row id with `validation show-error` and then using `clear-error`, `ignore-error`, or `resolve-error`.
- Classification Note: This chunk is classified as operation because it covers runtime status inspection, error-row handling commands, and stopping continuous data validation.

## Official Source Content

## Use continuous data validation

When you use continuous data validation, you can use dmctl to view the status of the validation and to handle the error rows. "Error rows" refers to the rows that are found to be inconsistent between the upstream and downstream databases.
### View the validation status

You can view the validation status using either of the following methods:

Method 1: run the `dmctl query-status <task-name>` command. If continuous data validation is enabled, the validation result is displayed in the `validation` field of each subtask. Example output:

```json
"subTaskStatus": [
    {
        "name": "test",
        "stage": "Running",
        "unit": "Sync",
        "result": null,
        "unresolvedDDLLockID": "",
        "sync": {
            ...
        },
        "validation": {
            "task": "test", // Task name
            "source": "mysql-01", // Source id
            "mode": "full", // Validation mode
            "stage": "Running", // Current stage. "Running" or "Stopped".
            "validatorBinlog": "(mysql-bin.000001, 5989)", // The binlog position of the validation
            "validatorBinlogGtid": "1642618e-cf65-11ec-9e3d-0242ac110002:1-30", // The GTID position of the validation
            "cutoverBinlogPos": "", // The specified binlog position for cutover
            "cutoverBinlogGTID": "1642618e-cf65-11ec-9e3d-0242ac110002:1-30", // The specified GTID position for cutover
            "result": null, // When the validation is abnormal, show the error message
            "processedRowsStatus": "insert/update/delete: 0/0/0", // Statistics of the processed binlog rows.
            "pendingRowsStatus": "insert/update/delete: 0/0/0", // Statistics of the binlog rows that are not validated yet or that fail to be validated but are not marked as "error rows"
            "errorRowsStatus": "new/ignored/resolved: 0/0/0" // Statistics of the error rows. The three statuses are explained in the next section.
        }
    }
]
```

Method 2: run the `dmctl validation status <taskname>` command.

```
dmctl validation status [--table-stage stage] <task-name> [flags]
Flags:
  -h, --help                 help for status
      --table-stage string   filter validation tables by stage: running/stopped
```

In the preceding command, you can use `--table-stage` to filter the tables that are being validated or stop validation. Example output:

```json
{
    "result": true,
    "msg": "",
    "validators": [
        {
            "task": "test",
            "source": "mysql-01",
            "mode": "full",
            "stage": "Running",
            "validatorBinlog": "(mysql-bin.000001, 6571)",
            "validatorBinlogGtid": "",
            "cutoverBinlogPos": "(mysql-bin.000001, 6571)",
            "cutoverBinlogGTID": "",
            "result": null,
            "processedRowsStatus": "insert/update/delete: 2/0/0",
            "pendingRowsStatus": "insert/update/delete: 0/0/0",
            "errorRowsStatus": "new/ignored/resolved: 0/0/0"
        }
    ],
    "tableStatuses": [
        {
            "source": "mysql-01", // Source id
            "srcTable": "`db`.`test1`", // Source table name
            "dstTable": "`db`.`test1`", // Target table name
            "stage": "Running", // Validation status
            "message": "" // Error message
        }
    ]
}
```

If you want to view the details of the error rows, such as error types and error time, run the `dmctl validation show-error` command:

```
Usage:
  dmctl validation show-error [--error error-state] <task-name> [flags]

Flags:
      --error string   filtering type of error: all, ignored, or unprocessed (default "unprocessed")
  -h, --help           help for show-error
```

Example output:

```json
{
    "result": true,
    "msg": "",
    "error": [
        {
            "id": "1", // Error row id, which will be used in processing error rows
            "source": "mysql-replica-01", // Source id
            "srcTable": "`validator_basic`.`test`", // Source table of the error row
            "srcData": "[0, 0]", // Data of the error row in the source table
            "dstTable": "`validator_basic`.`test`", // Target table of the error row
            "dstData": "[]", // Data of the error row in the target table
            "errorType": "Expected rows not exist", // Error type
            "status": "NewErr", // Error status
            "time": "2022-07-04 13:33:02", // Discovery time of the error row
            "message": "" // Additional information
        }
    ]
}
```
### Handle error rows

After continuous data validation returns error rows, you need to manually handle the error rows.

When continuous data validation finds error rows, the validation does not stop immediately. Instead, it records the error rows for you to handle. Before the error rows are processed, the default status is `unprocessed`. If you manually correct the error rows in the downstream, the validation does not automatically retrieve the latest status of the corrected data. The error rows are still recorded in the `error` field.

If you do not want to see an error row in the validation status, or if you want to mark an error row as resolved, you can locate the error row id using the `validation show-error` command and subsequently handle it with the given error id:

dmctl provides three error handling commands:

- `clear-error`: clear the error row. The `show-error` command does not show the error row anymore.

    ```
    Usage:
      dmctl validation clear-error <task-name> <error-id|--all> [flags]

    Flags:
          --all    all errors
      -h, --help   help for clear-error
    ```

- `ignore-error`: ignore the error row. This error row is marked as "ignored".

    ```
    Usage:
      dmctl validation ignore-error <task-name> <error-id|--all> [flags]

    Flags:
          --all    all errors
      -h, --help   help for ignore-error
    ```

- `resolve-error`: the error row is manually handled and marked as "resolved".

    ```
    Usage:
      dmctl validation resolve-error <task-name> <error-id|--all> [flags]

    Flags:
          --all    all errors
      -h, --help   help for resolve-error
    ```
## Stop continuous data validation

To stop the continuous data validation, run the `validation stop` command:

```
Usage:
  dmctl validation stop [--all-task] [task-name] [flags]

Flags:
      --all-task   whether applied to all tasks
  -h, --help       help for stop
```

For detailed usage, refer to [`dmctl validation start`](#method-2-enable-using-dmctl).
