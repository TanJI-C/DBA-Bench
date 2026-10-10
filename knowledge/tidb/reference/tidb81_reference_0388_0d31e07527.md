# DEADLOCKS table examples and deadlock group interpretation

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-deadlocks.md`
- Source Title: `DEADLOCKS`
- Source Heading Path: `DEADLOCKS > Example 1 | DEADLOCKS > Example 2`
- Source Line Ranges: `138-194`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `information_schema`, `deadlocks`, `transactions`, `locking`, `sql`, `examples`, `deadlock_id`, `key_info`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0388_0d31e07527`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-deadlocks.md#example-1`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ebc2884732fb2d6d225fcba5e7503180e1e1b934eff1d20cc06a8767fa9d650`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks#example-1
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-deadlocks.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting query results from INFORMATION_SCHEMA.DEADLOCKS, especially to understand how rows with the same DEADLOCK_ID represent one deadlock and how TRY_LOCK_TRX_ID and TRX_HOLDING_LOCK show blocking relationships or a waiting cycle.
- Retrieval Keywords: INFORMATION_SCHEMA.DEADLOCKS, SELECT * FROM INFORMATION_SCHEMA.DEADLOCKS;, DEADLOCK_ID, TRY_LOCK_TRX_ID, TRX_HOLDING_LOCK, CURRENT_SQL_DIGEST, CURRENT_SQL_DIGEST_TEXT, KEY, KEY_INFO, mutual blocking, three transactions wait in a cycle, same DEADLOCK_ID belongs to the same deadlock error, update `t` set `v` = ? where `id` = ? ;
- Follow-up Guidance: The examples show that the same DEADLOCK_ID groups rows for one deadlock error, where two rows can indicate mutual blocking and three rows can indicate three transactions waiting in a cycle.
- Classification Note: This is reference content because it explains how to read DEADLOCKS table output fields and grouped example rows rather than defining a procedure.

## Official Source Content

## Example 1

Assume that the table definition and the initial data is as follows:

```sql
CREATE TABLE t (id int primary key, v int);
INSERT INTO t VALUES (1, 10), (2, 20);
```

Two transactions are executed in the following order:

| Transaction 1                               | Transaction 2                               | Description                 |
|--------------------------------------|--------------------------------------|----------------------|
| `BEGIN;`                             |                                      |                      |
|                                      | `BEGIN;`                             |                      |
| `UPDATE t SET v = 11 WHERE id = 1;`  |                                      |                      |
|                                      | `UPDATE t SET v = 21 WHERE id = 2;`  |                      |
| `UPDATE t SET v = 12 WHERE id = 2;`  |                                      | Transaction 1 gets blocked.          |
|                                      | `UPDATE t SET v = 22 WHERE id = 1;`  | Transaction 2 reports a deadlock error.  |

Next, transaction 2 reports a deadlock error. At this time, query the `DEADLOCKS` table:

```sql
SELECT * FROM INFORMATION_SCHEMA.DEADLOCKS;
```

The expected output is as follows:

```sql
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
| DEADLOCK_ID | OCCUR_TIME                 | RETRYABLE | TRY_LOCK_TRX_ID    | CURRENT_SQL_DIGEST                                               | CURRENT_SQL_DIGEST_TEXT                 | KEY                                    | KEY_INFO                                                                                           | TRX_HOLDING_LOCK   |
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
|           1 | 2021-08-05 11:09:03.230341 |         0 | 426812829645406216 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000002 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"2"} | 426812829645406217 |
|           1 | 2021-08-05 11:09:03.230341 |         0 | 426812829645406217 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000001 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"1"} | 426812829645406216 |
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
```

Two rows of data are generated in the `DEADLOCKS` table. The `DEADLOCK_ID` field of both rows is `1`, which means that the information in both rows belongs to the same deadlock error. The first row shows that on the key of `"7480000000000000355F728000000000000002"`, the transaction of the ID `"426812829645406216"` is blocked by the transaction of the ID `"426812829645406217"`. The second row shows that on the key of `"7480000000000000355F728000000000000001"`, the transaction of the ID `"426812829645406217"` is blocked by the transaction of the ID `426812829645406216`, which constitutes mutual blocking and forms a deadlock.
## Example 2

Assume that you query the `DEADLOCKS` table and get the following result:

```sql
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
| DEADLOCK_ID | OCCUR_TIME                 | RETRYABLE | TRY_LOCK_TRX_ID    | CURRENT_SQL_DIGEST                                               | CURRENT_SQL_DIGEST_TEXT                 | KEY                                    | KEY_INFO                                                                                           | TRX_HOLDING_LOCK   |
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
|           1 | 2021-08-05 11:09:03.230341 |         0 | 426812829645406216 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000002 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"2"} | 426812829645406217 |
|           1 | 2021-08-05 11:09:03.230341 |         0 | 426812829645406217 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000001 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"1"} | 426812829645406216 |
|           2 | 2021-08-05 11:09:21.252154 |         0 | 426812832017809412 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000002 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"2"} | 426812832017809413 |
|           2 | 2021-08-05 11:09:21.252154 |         0 | 426812832017809413 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000003 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"3"} | 426812832017809414 |
|           2 | 2021-08-05 11:09:21.252154 |         0 | 426812832017809414 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000001 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"1"} | 426812832017809412 |
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
```

The `DEADLOCK_ID` column in the preceding query result shows that the first two rows together represent the information of a deadlock error, and the two transactions that wait for each other form the deadlock. The next three rows together represent the information of another deadlock error, and the three transactions that wait in a cycle form the deadlock.
