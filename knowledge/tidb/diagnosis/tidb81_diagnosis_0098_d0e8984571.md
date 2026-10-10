# TiDB Lightning error report tables and query details

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-error-resolution.md`
- Source Title: `TiDB Lightning Error Resolution`
- Source Heading Path: `TiDB Lightning Error Resolution > Error report`
- Source Line Ranges: `54-160`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`
- Topic Tags: `error-report`, `task-info-schema`, `type-error-table`, `conflict-records`, `logs`, `terminal-output`, `file-offsets`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0098_d0e8984571`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-error-resolution.md#error-report`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4d52baffdc1efa13c1b9a0a701c84bea1d30a92afa58f6483fff57e54766c1dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-error-resolution#error-report
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-error-resolution.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving where TiDB Lightning writes import error reports, what tables and columns store type or conflict errors, and how file offsets are shown in reports.
- Retrieval Keywords: Error report, lightning_task_info, lightning.task-info-schema-name, type_error_v1, conflict_error_v1, conflict_records, conflict_error_v2, task_id, create_time, table_name, path, offset, error, index_name, key_data, row_data, raw_key, raw_value, raw_handle, raw_row, terminal error report, log file, Detect 1000 data type errors in total, file offset, head -c 183 file.csv | tail, tail -c +183 file.csv | head, :goto 183, 183go
- Follow-up Guidance: The source includes example shell and vim commands for jumping near a reported byte offset in the source file.
- Classification Note: This is classified as diagnosis because the content explains the emitted error summary, the downstream TiDB tables that store error details, and the fields used to inspect those errors.

## Official Source Content

## Error report

If TiDB Lightning encounters errors during the import, it outputs a statistics summary about these errors in both your terminal and the log file when it exits.

* The error report in the terminal is similar to the following table:

    | # | ERROR TYPE | ERROR COUNT | ERROR DATA TABLE |
    | - | --- | --- | ------ |
    | 1 | Data Type | 1000 | `lightning_task_info`.`type_error_v1` |

* The error report in the TiDB Lightning log file is as follows:

    ```shell
    [2022/03/13 05:33:57.736 +08:00] [WARN] [errormanager.go:459] ["Detect 1000 data type errors in total, please refer to table `lightning_task_info`.`type_error_v1` for more details"]
    ```

All errors are written to tables in the `lightning_task_info` database in the downstream TiDB cluster. After the import is completed, if the error data is collected, you can view the errors in the database and process them manually.

You can change the database name by configuring `lightning.task-info-schema-name`.

```toml
[lightning]
task-info-schema-name = 'lightning_task_info'
```

TiDB Lightning creates 3 tables in this database:

```sql
CREATE TABLE type_error_v1 (
    task_id     bigint NOT NULL,
    create_time datetime(6) NOT NULL DEFAULT now(6),
    table_name  varchar(261) NOT NULL,
    path        varchar(2048) NOT NULL,
    offset      bigint NOT NULL,
    error       text NOT NULL,
    row_data    text NOT NULL
);

CREATE TABLE conflict_error_v1 (
    task_id     bigint NOT NULL,
    create_time datetime(6) NOT NULL DEFAULT now(6),
    table_name  varchar(261) NOT NULL,
    index_name  varchar(128) NOT NULL,
    key_data    text NOT NULL,
    row_data    text NOT NULL,
    raw_key     mediumblob NOT NULL,
    raw_value   mediumblob NOT NULL,
    raw_handle  mediumblob NOT NULL,
    raw_row     mediumblob NOT NULL,
    KEY (task_id, table_name)
);
CREATE TABLE conflict_records (
    task_id     bigint NOT NULL,
    create_time datetime(6) NOT NULL DEFAULT now(6),
    table_name  varchar(261) NOT NULL,
    path        varchar(2048) NOT NULL,
    offset      bigint NOT NULL,
    error           text NOT NULL,
    row_id        bigint NOT NULL COMMENT 'the row id of the conflicting row',
    row_data    text NOT NULL COMMENT 'the row data of the conflicting row',
    KEY (task_id, table_name)
);
```

`type_error_v1` records all [type errors](#type-error) managed by `lightning.max-error`. Each error corresponds to one row.

`conflict_error_v2` records conflicts managed by the `conflict` configuration group in the physical import mode. Each pair of conflicts corresponds to two rows.

`conflict_records` records conflicts managed by the `conflict` configuration group in both the logical import mode and physical import mode. Each error corresponds to one row.

| Column       | Syntax | Type | Conflict | Description                                                                                                                         |
| ------------ | ------ | ---- | -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| task_id      | ✓      | ✓    | ✓        | The TiDB Lightning task ID that generates this error                                                                                    |
| create_time | ✓      | ✓    | ✓        | The time at which the error is recorded                                                                                                         |
| table_name   | ✓      | ✓    | ✓        | The name of the table that contains the error, in the form of ``'`db`.`tbl`'``                                                                |
| path         | ✓      | ✓    |          | The path of the file that contains the error                                                                                               |
| offset       | ✓      | ✓    |          | The byte position in the file where the error is found                                                                                  |
| error        | ✓      | ✓    |          | The error message                                                                                                                       |
| context      | ✓      |      |          | The text that surrounds the error                                                                                                          |
| index_name   |        |      | ✓        | The name of the unique key in conflict. It is `'PRIMARY'` for primary key conflicts.                                                          |
| key_data     |        |      | ✓        | The formatted key handle of the row that causes the error. The content is for human reference only, and not intended to be machine-readable. |
| row_data     |        | ✓    | ✓        | The formatted row data that causes the error. The content is for human reference only, and not intended to be machine-readable              |
| raw_key      |        |      | ✓        | The key of the conflicted KV pair                                                                                                       |
| raw_value    |        |      | ✓        | The value of the conflicted KV pair                                                                                                     |
| raw_handle   |        |      | ✓        | The row handle of the conflicted row                                                                                                    |
| raw_row      |        |      | ✓        | The encoded value of the conflicted row                                                                                                 |

> **Note:**
>
> The error report records the file offset, not line/column number which is inefficient to obtain. You can quickly jump near a byte position (using 183 as example) using the following commands:
>
> * shell, printing the first several lines.
>
>     ```shell
>     head -c 183 file.csv | tail
>     ```
>
> * shell, printing the next several lines:
>
>     ```shell
>     tail -c +183 file.csv | head
>     ```
>
> * vim — `:goto 183` or `183go`
