# Non-MySQL sink splitting for single and multiple UPDATE changes

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-split-update-behavior.md`
- Source Title: `TiCDC Behavior in Splitting UPDATE Events`
- Source Heading Path: `TiCDC Behavior in Splitting UPDATE Events > Split primary or unique key `UPDATE` events for non-MySQL sinks | TiCDC Behavior in Splitting UPDATE Events > Split primary or unique key `UPDATE` events for non-MySQL sinks > Transactions containing a single `UPDATE` change | TiCDC Behavior in Splitting UPDATE Events > Split primary or unique key `UPDATE` events for non-MySQL sinks > Transactions containing multiple `UPDATE` changes`
- Source Line Ranges: `75-114`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `non-mysql-sinks`, `update-events`, `primary-key`, `unique-index`, `delete-insert-splitting`, `consumer-behavior`, `event-ordering`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0070_b38b613223`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-split-update-behavior.md#split-primary-or-unique-key-update-events-for-non-mysql-sinks`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5992c606303dcf5e9d32faca16f655bc21ae22095fe4bbaf0e034491d0551a08`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#split-primary-or-unique-key-update-events-for-non-mysql-sinks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-split-update-behavior.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about how non-MySQL sinks handle UPDATE events that modify a primary key or non-null unique index in single-change or multi-change transactions.
- Retrieval Keywords: non-MySQL sink, primary key, non-null unique index, split UPDATE into DELETE and INSERT, CSV protocol, AVRO protocol, Kafka sink, single UPDATE change, multiple UPDATE changes, DELETE events preceding INSERT events, primary key conflict, unique key conflict, #9086, #9430
- Follow-up Guidance: The content distinguishes single-update transactions from transactions containing multiple changes and explains why splitting helps consumers and downstream relational databases.
- Classification Note: This is classified as architecture because it describes TiCDC event transformation and ordering behavior for non-MySQL sinks rather than a tunable setting.

## Official Source Content

## Split primary or unique key `UPDATE` events for non-MySQL sinks
### Transactions containing a single `UPDATE` change

Starting from v6.5.3, v7.1.1, and v7.2.0, when using a non-MySQL sink, for transactions that only contain a single update change, if the primary key or non-null unique index value is modified in an `UPDATE` event, TiCDC splits this event into `DELETE` and `INSERT` events. For more information, see GitHub issue [#9086](https://github.com/pingcap/tiflow/issues/9086).

This change primarily addresses the issue that TiCDC only outputs the new value without the old value by default when using the CSV and AVRO protocols. Due to this issue, when the primary key or non-null unique index value changes, the consumer can only receive the new value, making it impossible to process the value before the change (for example, delete the old value). Take the following SQL as an example:

```sql
CREATE TABLE t (a INT PRIMARY KEY, b INT);
INSERT INTO t VALUES (1, 1);
UPDATE t SET a = 2 WHERE a = 1;
```

In this example, the primary key `a` is updated from `1` to `2`. If the `UPDATE` event is not split, the consumer can only obtain the new value `a = 2` and cannot obtain the old value `a = 1` when using the CSV and AVRO protocols. This might cause the downstream consumer to only insert the new value `2` without deleting the old value `1`.
### Transactions containing multiple `UPDATE` changes

Starting from v6.5.4, v7.1.2, and v7.4.0, for transactions containing multiple changes, if the primary key or non-null unique index value is modified in the `UPDATE` event, TiCDC splits the event into `DELETE` and `INSERT` events and ensures that all events follow the sequence of `DELETE` events preceding `INSERT` events. For more information, see GitHub issue [#9430](https://github.com/pingcap/tiflow/issues/9430).

This change primarily addresses the potential issue of primary key or unique key conflicts that consumers might encounter when writing data changes from the Kafka sink or other sinks to a relational database or performing a similar operation. This issue is caused by the potentially incorrect order of `UPDATE` events received by TiCDC.

Take the following SQL as an example:

```sql
CREATE TABLE t (a INT PRIMARY KEY, b INT);
INSERT INTO t VALUES (1, 1);
INSERT INTO t VALUES (2, 2);

BEGIN;
UPDATE t SET a = 3 WHERE a = 1;
UPDATE t SET a = 1 WHERE a = 2;
UPDATE t SET a = 2 WHERE a = 3;
COMMIT;
```

In this example, by executing three SQL statements to swap the primary keys of two rows, TiCDC only receives two update change events, that is, changing the primary key `a` from `1` to `2` and changing the primary key `a` from `2` to `1`. If consumers directly write these two `UPDATE` events to the downstream, a primary key conflict will occur, leading to changefeed errors.

Therefore, TiCDC splits these two events into four events, that is, deleting records `(1, 1)` and `(2, 2)` and writing records `(2, 1)` and `(1, 2)`.
