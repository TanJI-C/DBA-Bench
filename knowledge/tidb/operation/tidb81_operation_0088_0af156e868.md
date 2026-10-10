# Validation cutover point, implementation, and limitations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-continuous-data-validation.md`
- Source Title: `Continuous Data Validation in DM`
- Source Heading Path: `Continuous Data Validation in DM > Set the cutover point for continuous data validation | Continuous Data Validation in DM > Implementation | Continuous Data Validation in DM > Limitations`
- Source Line Ranges: `252-305`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `continuous-validation`, `cutover-point`, `dmctl`, `binlog-position`, `gtid`, `validator`, `error-rows`, `primary-key`, `ddl-limitations`, `data-types`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0088_0af156e868`
- Source ID: `tidb-docs-8.1:dm/dm-continuous-data-validation.md#set-the-cutover-point-for-continuous-data-validation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `86099490bdd8e689817365c862ca4467600f27a444fad7b2ed16bbd0653737bc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-continuous-data-validation#set-the-cutover-point-for-continuous-data-validation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-continuous-data-validation.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM continuous data validation cutover point command syntax, validator implementation flow, or documented limitations for supported tables, DDL, and data types.
- Retrieval Keywords: dmctl validation update <task-name>, --cutover-binlog-gtid, --cutover-binlog-pos, cutover point for continuous data validation, GTID, binlog position, validator, syncer, validation worker, full, fast, error row, meta database, primary key, not-null unique key, DDL limitations, JSON, Binary data, floating-point numbers 10^-6
- Follow-up Guidance: The source also states that failed rows are retried for a specified time and then marked as error rows in the downstream meta database, and that their information can be viewed by querying the migration task.
- Classification Note: This is classified as an operation topic because the content provides the dmctl command to set a validation cutover point and explains runtime validator behavior and operational limitations.

## Official Source Content

## Set the cutover point for continuous data validation

Before switching the application to another database, you might need to perform continuous data validation immediately after the data is replicated to a specific position to ensure data integrity. To achieve this, you can set this specific position as the cutover point for continuous validation.

To set the cutover point for continuous data validation, use the `validation update` command:

```
Usage:
  dmctl validation update <task-name> [flags]

Flags:
      --cutover-binlog-gtid string   specify the cutover binlog gtid for validation, only valid when source config's gtid is enabled, e.g. '1642618e-cf65-11ec-9e3d-0242ac110002:1-30'
      --cutover-binlog-pos string    specify the cutover binlog name for validation, should include binlog name and pos in brackets, e.g. '(mysql-bin.000001, 5989)'
  -h, --help                         help for update
```

* `--cutover-binlog-gtid`: specifies the cutover position for validation, in the format of `1642618e-cf65-11ec-9e3d-0242ac110002:1-30`. Only valid when GTID is enabled in the upstream cluster.
* `--cutover-binlog-pos`: specifies the cutover position for validation, in the format of `(mysql-bin.000001, 5989)`.
* `task-name`: the name of the task for continuous data validation. This parameter is **required**.
## Implementation

The architecture of continuous data validation (validator) in DM is as follows:

![validator summary](/media/dm/dm-validator-summary.jpeg)

The lifecycle of continuous data validation is as follows:

![validator lifecycle](/media/dm/dm-validator-lifecycle.jpeg)

The detailed implementation of continuous data validation is as follows:

1. The validator pulls a binlog event from the upstream and gets the changed rows:
    - The validator only checks an event that has been incrementally migrated by the syncer. If the event has not been processed by the syncer, the validator pauses and waits for the syncer to complete processing.
    - If the event has been processed by the syncer, the validator moves on to the following steps.
2. The validator parses the binlog event and filters out the rows based on the block and allow lists, the table filters, and table routing. After that, the validator submits the changed rows to the validation worker that runs in the background.
3. The validation worker merges the changed rows that affect the same table and the same primary key to avoid validating "expired" data. The changed rows are cached in memory.
4. When the validation worker has accumulated a certain number of changed rows or when a certain time interval is passed, the validation worker queries the downstream database using the primary keys to get the current data and compares it with the changed rows.
5. The validation worker performs the data validation. If the validation mode is `full`, the validation worker compares data of the changed rows with data of the downstream database. if the validation mode is `fast`, the validation worker only checks the existence of the changed rows.
    - If the changed rows pass the validation, the changed row is removed from the memory.
    - If the changed rows fail the validation, the validator does not report an error immediately but waits for a certain time interval before validating the row again.
    - If a changed row cannot pass the validation within the specified time (specified by the user), the validator marks the row as an error row and writes it to the meta database in the downstream. You can view the information of error rows by querying the migration task. For details, refer to [View the validation status](#view-the-validation-status) and [Handle error rows](#handle-error-rows).
## Limitations

- The source table to be validated must have a primary key or a not-null unique key.
- When DM migrates DDL from the upstream database, the following limitations apply:
    - The DDL must not change the primary key, or change the order of columns, or delete existing columns.
    - The table must not be dropped.
- Does not support tasks that use expressions to filter events.
- The precision of floating-point numbers is different between TiDB and MySQL. Differences smaller than 10^-6 are considered equal.
- Does not support the following data types:
    - JSON
    - Binary data
