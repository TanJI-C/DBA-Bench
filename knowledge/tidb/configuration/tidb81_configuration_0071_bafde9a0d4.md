# Continuous data validation overview and enabling methods

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-continuous-data-validation.md`
- Source Title: `Continuous Data Validation in DM`
- Source Heading Path: `Continuous Data Validation in DM | Continuous Data Validation in DM > User scenario | Continuous Data Validation in DM > Enable continuous data validation | Continuous Data Validation in DM > Enable continuous data validation > Method 1: Enable in the task configuration file | Continuous Data Validation in DM > Enable continuous data validation > Method 2: Enable using dmctl`
- Source Line Ranges: `5-77`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `continuous-data-validation`, `incremental-migration`, `data-consistency`, `task-configuration`, `dmctl`, `validation-mode`, `start-time`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0071_bafde9a0d4`
- Source ID: `tidb-docs-8.1:dm/dm-continuous-data-validation.md#continuous-data-validation-in-dm`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3536b249b420c60e069dbe20bf70d7032132420240d28ed6d31871fe0480559a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-continuous-data-validation#continuous-data-validation-in-dm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-continuous-data-validation.md

## Retrieval Guidance

- Use When: Use this chunk when you need how to enable DM continuous data validation for incremental migration, including task configuration fields or the dmctl start command options.
- Retrieval Keywords: Continuous Data Validation in DM, validator-config-name, validators, mode: full, mode: fast, mode: none, worker-count, row-error-delay, dmctl validation start, --mode, --start-time, --all-task, task configuration file, incremental migration, data consistency
- Follow-up Guidance: It also provides the example command `dmctl --master-addr=127.0.0.1:8261 validation start --start-time 2021-10-21T00:01:00 --mode full my_dm_task`.
- Classification Note: This chunk is classified as configuration because it defines task configuration items and dmctl parameters used to enable continuous data validation.

## Official Source Content

# Continuous Data Validation in DM

This document describes how to use continuous data validation in DM, its working principles, and its limitations.
## User scenario

In the process of incrementally migrating data from the upstream database to the downstream database, there is a small probability that the flow of data leads to data corruption or data loss. For scenarios where data consistency is required, such as the credit and securities industries, after the migration is complete, you can perform full data validation to ensure data consistency.

However, in incremental migration scenarios, the upstream and downstream are continuously writing data. Because data is constantly changing in the upstream and downstream, it is difficult to perform full data validation (for example, use [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview)) to all data in the tables.

In incremental migration scenarios, you can use the continuous data validation feature in DM. This feature ensures data integrity and consistency during incremental migration where data is continuously written into the downstream.
## Enable continuous data validation

You can enable continuous data validation using either of the following methods:

- Enable in the task configuration file.
- Enable using dmctl.
### Method 1: Enable in the task configuration file

To enable continuous data validation, add the following configuration items to the task configuration file:

```yaml
# Add the following configuration items to the upstream database that needs to be validated:
mysql-instances:
  - source-id: "mysql1"
    block-allow-list: "bw-rule-1"
    validator-config-name: "global"
validators:
  global:
    mode: full # "fast" is also allowed. "none" is the default mode, which means no validation is performed.
    worker-count: 4 # The number of validation workers in the background. The default value is 4.
    row-error-delay: 30m # If a row cannot pass the validation within the specified time, it will be marked as an error row. The default value is 30m, which means 30 minutes.
```

The configuration items are described as follows:

* `mode`: validation mode. The possible values are `none`, `full`, and `fast`.
    * `none`: the default value, which means no validation is performed.
    * `full`: compares the changed row and the row obtained in the downstream database.
    * `fast`: only checks if the changed row exists in the downstream database.
* `worker-count`: the number of validation workers in the background. Each worker is a goroutine.
* `row-error-delay`: if a row cannot pass the validation within the specified time, it will be marked as an error row. The default value is 30 minutes.

For the complete configuration, refer to [DM Advanced Task Configuration File](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).
### Method 2: Enable using dmctl

To enable continuous data validation, run the `dmctl validation start` command:

```
Usage:
  dmctl validation start [--all-task] [task-name] [flags]

Flags:
      --all-task            whether applied to all tasks
  -h, --help                help for start
      --mode string         specify the mode of validation: full (default), fast; this flag will be ignored if the validation task has been ever enabled but currently paused (default "full")
      --start-time string   specify the start time of binlog for validation, e.g. '2021-10-21 00:01:00' or 2021-10-21T00:01:00
```

* `--mode`: specify the validation mode. The possible values are `fast` and `full`.
* `--start-time`: specify the start time for validation. The format follows `2021-10-21 00:01:00` or `2021-10-21T00:01:00`.
* `task`: specify the name of the task to enable continuous validation for. You can use `--all-task` to enable validation for all tasks.

For example:

```shell
dmctl --master-addr=127.0.0.1:8261 validation start --start-time 2021-10-21T00:01:00 --mode full my_dm_task
```
