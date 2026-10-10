# MySQL sink UPDATE splitting behavior and thresholdTS

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-split-update-behavior.md`
- Source Title: `TiCDC Behavior in Splitting UPDATE Events`
- Source Heading Path: `TiCDC Behavior in Splitting UPDATE Events | TiCDC Behavior in Splitting UPDATE Events > Split `UPDATE` events for MySQL sinks`
- Source Line Ranges: `5-74`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`
- Topic Tags: `update-events`, `mysql-sink`, `thresholdts`, `event-ordering`, `data-consistency`, `sorter`, `changefeed-restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0069_5095704b07`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-split-update-behavior.md#ticdc-behavior-in-splitting-update-events`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `277dc83e609752c7faa4d4c60e44184acce040316c8089095e2ebb5eb5991b21`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#ticdc-behavior-in-splitting-update-events
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-split-update-behavior.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about how TiCDC MySQL sink decides to split UPDATE events based on thresholdTS, commitTS, Sorter ordering, or changefeed restart behavior.
- Retrieval Keywords: MySQL sink, thresholdTS, commitTS, PD, Sorter module, split UPDATE events, DELETE event, INSERT event, data inconsistency, changefeed restart, primary key conflict, unique key conflict, #10918, #11219
- Follow-up Guidance: The content also notes that in v8.1.0 thresholdTS was fetched from PD at TiCDC startup and that this could cause data inconsistency issues in multi-node scenarios.
- Classification Note: This is classified as architecture because it explains TiCDC event-processing behavior for MySQL sinks, including thresholdTS-based splitting and ordering through the Sorter module.

## Official Source Content

# TiCDC Behavior in Splitting UPDATE Events
## Split `UPDATE` events for MySQL sinks

Starting from v6.5.10, v7.1.6, v7.5.2, and v8.1.1, when using the MySQL sink, any TiCDC node that receives a request for replicating a table will fetch the current timestamp `thresholdTS` from PD before starting the replication to the downstream. Based on the value of this timestamp, TiCDC decides whether to split `UPDATE` events:

- For transactions containing one or multiple `UPDATE` changes, if the transaction `commitTS` is less than `thresholdTS`, TiCDC splits the `UPDATE` event into a `DELETE` event and an `INSERT` event before writing them to the Sorter module.
- For `UPDATE` events with the transaction `commitTS` greater than or equal to `thresholdTS`, TiCDC does not split them. For more information, see GitHub issue [#10918](https://github.com/pingcap/tiflow/issues/10918).

> **Note:**
>
> In v8.1.0, when using MySQL Sink, TiCDC also decides whether to split `UPDATE` events based on the value of `thresholdTS`, but `thresholdTS` is obtained differently. Specifically, in v8.1.0, `thresholdTS` is the current timestamp fetched from PD at TiCDC startup, but this way might cause data inconsistency issues in multi-node scenarios. For more information, see GitHub issue [#11219](https://github.com/pingcap/tiflow/issues/11219).

This behavior change (that is, deciding whether to split `UPDATE` events based on `thresholdTS`) addresses the issue of downstream data inconsistencies caused by the potentially incorrect order of `UPDATE` events received by TiCDC, which can lead to an incorrect order of split `DELETE` and `INSERT` events.

Take the following SQL statements as an example:

```sql
CREATE TABLE t (a INT PRIMARY KEY, b INT);
INSERT INTO t VALUES (1, 1);
INSERT INTO t VALUES (2, 2);

BEGIN;
UPDATE t SET a = 3 WHERE a = 2;
UPDATE t SET a = 2 WHERE a = 1;
COMMIT;
```

In this example, the two `UPDATE` statements within the transaction have a sequential dependency on execution. The primary key `a` is changed from `2` to `3`, and then the primary key `a` is changed from `1` to `2`. After this transaction is executed, the records in the upstream database are `(2, 1)` and `(3, 2)`.

However, the order of `UPDATE` events received by TiCDC might differ from the actual execution order of the upstream transaction. For example:

```sql
UPDATE t SET a = 2 WHERE a = 1;
UPDATE t SET a = 3 WHERE a = 2;
```

- Before this behavior change, TiCDC writes these `UPDATE` events to the Sorter module and then splits them into `DELETE` and `INSERT` events. After the split, the actual execution order of these events in the downstream is as follows:

    ```sql
    BEGIN;
    DELETE FROM t WHERE a = 1;
    REPLACE INTO t VALUES (2, 1);
    DELETE FROM t WHERE a = 2;
    REPLACE INTO t VALUES (3, 2);
    COMMIT;
    ```

    After the downstream executes the transaction, the records in the database are `(3, 2)`, which are different from the records in the upstream database (`(2, 1)` and `(3, 2)`), indicating a data inconsistency issue.

- After this behavior change, if the transaction `commitTS` is less than the `thresholdTS` fetched from PD when TiCDC starts replicating the corresponding table to the downstream, TiCDC splits these `UPDATE` events into `DELETE` and `INSERT` events before writing them to the Sorter module. After the sorting by the Sorter module, the actual execution order of these events in the downstream is as follows:

    ```sql
    BEGIN;
    DELETE FROM t WHERE a = 1;
    DELETE FROM t WHERE a = 2;
    REPLACE INTO t VALUES (2, 1);
    REPLACE INTO t VALUES (3, 2);
    COMMIT;
    ```

    After the downstream executes the transaction, the records in the downstream database are the same as those in the upstream database, which are `(2, 1)` and `(3, 2)`, ensuring data consistency.

As you can see from the preceding example, splitting the `UPDATE` event into `DELETE` and `INSERT` events before writing them to the Sorter module ensures that all `DELETE` events are executed before `INSERT` events after the split, thereby maintaining data consistency regardless of the order of `UPDATE` events received by TiCDC.

> **Note:**
>
> After this behavior change, when using the MySQL sink, TiCDC does not split the `UPDATE` event in most cases. Consequently, there might be primary key or unique key conflicts during changefeed runtime, causing the changefeed to restart automatically. After the restart, TiCDC will split the conflicting `UPDATE` events into `DELETE` and `INSERT` events before writing them to the Sorter module. This ensures that all events within the same transaction are correctly ordered, with all `DELETE` events preceding `INSERT` events, thus correctly completing data replication.
