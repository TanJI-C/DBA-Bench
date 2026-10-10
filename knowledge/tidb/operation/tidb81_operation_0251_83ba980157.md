# TiCDC changefeed creation, status, and replication progress verification

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-faq.md`
- Source Title: `TiCDC FAQs`
- Source Heading Path: `TiCDC FAQs | TiCDC FAQs > How do I choose `start-ts` when creating a task in TiCDC? | TiCDC FAQs > Why can't some tables be replicated when I create a task in TiCDC? | TiCDC FAQs > How do I view the state of TiCDC replication tasks? | TiCDC FAQs > How to verify if TiCDC has replicated all updates after upstream stops updating?`
- Source Line Ranges: `5-162`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `changefeed`, `start-ts`, `table-eligibility`, `checkpoint`, `replication-progress`, `tso`, `syncpoint`, `cdc-cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0251_83ba980157`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-faq.md#ticdc-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9bfeea5d942acf5d005861714797340d8017586f231eaa70ce7d683ac8de312`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#ticdc-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-faq.md

## Retrieval Guidance

- Use When: Use this chunk when you need official guidance on choosing `start-ts`, understanding `some tables are not eligible to replicate`, checking changefeed `state` and `checkpoint` with `cdc cli changefeed list`, or verifying TiCDC replication completeness by comparing upstream TSO with TiCDC progress.
- Retrieval Keywords: start-ts, tikv_gc_safe_point, Timestamp Oracle (TSO), cdc cli changefeed create, some tables are not eligible to replicate, cdc cli changefeed list, checkpoint, state, TIDB_CURRENT_TSO(), TIDB_PARSE_TSO(), tidb_cdc.syncpoint_v1, Syncpoint, sync-point-interval, replication progress, verify all updates have been replicated
- Follow-up Guidance: It also provides two grounded ways to verify replication progress: querying the changefeed checkpoint with `cdc cli changefeed list` or querying `tidb_cdc.syncpoint_v1` when the Syncpoint feature is enabled.
- Classification Note: This is classified as operation because the content explains how to create and inspect TiCDC changefeeds and how to verify ongoing replication progress using CLI output, TSO functions, and Syncpoint data.

## Official Source Content

# TiCDC FAQs

This document introduces the common questions that you might encounter when using TiCDC.

> **Note:**
>
> In this document, the server address specified in `cdc cli` commands is `--server=http://127.0.0.1:8300`. When you use the command, replace the address with your actual PD address.
## How do I choose `start-ts` when creating a task in TiCDC?

The `start-ts` of a replication task corresponds to a Timestamp Oracle (TSO) in the upstream TiDB cluster. TiCDC requests data from this TSO in a replication task. Therefore, the `start-ts` of the replication task must meet the following requirements:

- The value of `start-ts` is larger than the `tikv_gc_safe_point` value of the current TiDB cluster. Otherwise, an error occurs when you create a task.
- Before starting a task, ensure that the downstream has all data before `start-ts`. For scenarios such as replicating data to message queues, if the data consistency between upstream and downstream is not required, you can relax this requirement according to your application need.

If you do not specify `start-ts`, or specify `start-ts` as `0`, when a replication task is started, TiCDC gets a current TSO and starts the task from this TSO.
## Why can't some tables be replicated when I create a task in TiCDC?

When you execute `cdc cli changefeed create` to create a replication task, TiCDC checks whether the upstream tables meet the [replication requirements](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#best-practices). If some tables do not meet the requirements, `some tables are not eligible to replicate` is returned with a list of ineligible tables. You can choose `Y` or `y` to continue creating the task, and all updates on these tables are automatically ignored during the replication. If you choose an input other than `Y` or `y`, the replication task is not created.
## How do I view the state of TiCDC replication tasks?

To view the status of TiCDC replication tasks, use `cdc cli`. For example:

```shell
cdc cli changefeed list --server=http://127.0.0.1:8300
```

The expected output is as follows:

```json
[{
    "id": "4e24dde6-53c1-40b6-badf-63620e4940dc",
    "summary": {
      "state": "normal",
      "tso": 417886179132964865,
      "checkpoint": "2020-07-07 16:07:44.881",
      "error": null
    }
}]
```

* `checkpoint`: TiCDC has replicated all data before this timestamp to downstream.
* `state`: The state of this replication task. For more information about each state and its meaning, see [Changefeed states](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-overview#changefeed-state-transfer).

> **Note:**
>
> This feature is introduced in TiCDC 4.0.3.
## How to verify if TiCDC has replicated all updates after upstream stops updating?

After the upstream TiDB cluster stops updating, you can verify if replication is complete by comparing the latest [TSO](https://docs.pingcap.com/tidb/stable/glossary#tso) timestamp of the upstream TiDB cluster with the replication progress in TiCDC. If the TiCDC replication progress timestamp is greater than or equal to the upstream TiDB cluster's TSO, then all updates have been replicated. To verify replication completeness, perform the following steps:

1. Get the latest TSO timestamp from the upstream TiDB cluster.

    > **Note:**
    >
    > Use the [`TIDB_CURRENT_TSO()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_current_tso) function to get the current TSO, instead of using functions like `NOW()` that return the current time.

    The following example uses [`TIDB_PARSE_TSO()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_parse_tso) to convert the TSO to a readable time format for further comparison:

    ```sql
    BEGIN;
    SELECT TIDB_PARSE_TSO(TIDB_CURRENT_TSO());
    ROLLBACK;
    ```

    The output is as follows:

    ```sql
    +------------------------------------+
    | TIDB_PARSE_TSO(TIDB_CURRENT_TSO()) |
    +------------------------------------+
    | 2024-11-12 20:35:34.848000         |
    +------------------------------------+
    ```

2. Get the replication progress in TiCDC.

    You can check the replication progress in TiCDC using one of the following methods:

    * **Method 1**: query the checkpoint of the changefeed (recommended).

        Use the [TiCDC command-line tool](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed) `cdc cli` to view the checkpoint for all replication tasks:

        ```shell
        cdc cli changefeed list --server=http://127.0.0.1:8300
        ```

        The output is as follows:

        ```json
        [
          {
            "id": "syncpoint",
            "namespace": "default",
            "summary": {
              "state": "normal",
              "tso": 453880043653562372,
              "checkpoint": "2024-11-12 20:36:01.447",
              "error": null
            }
          }
        ]
        ```

        In the output, `"checkpoint": "2024-11-12 20:36:01.447"` indicates that TiCDC has replicated all upstream TiDB changes before this time. If this timestamp is greater than or equal to the upstream TiDB cluster's TSO obtained in step 1, then all updates have been replicated downstream.

    * **Method 2**: query Syncpoint from the downstream TiDB.

        If the downstream is a TiDB cluster and the [TiCDC Syncpoint feature](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check) is enabled, you can get the replication progress by querying the Syncpoint in the downstream TiDB.

        > **Note:**
        >
        > The Syncpoint update interval is controlled by the [`sync-point-interval`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check#enable-syncpoint) configuration item. For the most up-to-date replication progress, use method 1.

        Execute the following SQL statement in the downstream TiDB to get the upstream TSO (`primary_ts`) and downstream TSO (`secondary_ts`):

        ```sql
        SELECT * FROM tidb_cdc.syncpoint_v1;
        ```

        The output is as follows:

        ```sql
        +------------------+------------+--------------------+--------------------+---------------------+
        | ticdc_cluster_id | changefeed | primary_ts         | secondary_ts       | created_at          |
        +------------------+------------+--------------------+--------------------+---------------------+
        | default          | syncpoint  | 453879870259200000 | 453879870545461257 | 2024-11-12 20:25:01 |
        | default          | syncpoint  | 453879948902400000 | 453879949214351361 | 2024-11-12 20:30:01 |
        | default          | syncpoint  | 453880027545600000 | 453880027751907329 | 2024-11-12 20:35:00 |
        +------------------+------------+--------------------+--------------------+---------------------+
        ```

        In the output, each row shows the upstream TiDB snapshot at `primary_ts` matches the downstream TiDB snapshot at `secondary_ts`.

        To view the replication progress, convert the latest `primary_ts` to a readable time format:

        ```sql
        SELECT TIDB_PARSE_TSO(453880027545600000);
        ```

        The output is as follows:

        ```sql
        +------------------------------------+
        | TIDB_PARSE_TSO(453880027545600000) |
        +------------------------------------+
        | 2024-11-12 20:35:00                |
        +------------------------------------+
        ```

        If the time corresponding to the latest `primary_ts` is greater than or equal to the upstream TiDB cluster's TSO obtained in step 1, then TiCDC has replicated all updates downstream.
