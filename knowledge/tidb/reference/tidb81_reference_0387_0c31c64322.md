# DEADLOCKS table schema and KEY_INFO fields

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-deadlocks.md`
- Source Title: `DEADLOCKS`
- Source Heading Path: `DEADLOCKS | DEADLOCKS > `KEY_INFO``
- Source Line Ranges: `5-88`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `information_schema`, `deadlocks`, `table-schema`, `key_info`, `sql-digest`, `process-privilege`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0387_0c31c64322`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-deadlocks.md#deadlocks`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d493a6e358bbd7fdac6d9e632c6ec741a8a73660d3263820f3af83c9a6b99c9e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks#deadlocks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-deadlocks.md

## Retrieval Guidance

- Use When: Use this content when retrieving the schema, column meanings, row grouping behavior, access restriction, or KEY_INFO JSON fields of the INFORMATION_SCHEMA.DEADLOCKS table on the current TiDB node.
- Retrieval Keywords: INFORMATION_SCHEMA.DEADLOCKS, DESC deadlocks, DEADLOCK_ID, OCCUR_TIME, RETRYABLE, TRY_LOCK_TRX_ID, CURRENT_SQL_DIGEST, CURRENT_SQL_DIGEST_TEXT, KEY, KEY_INFO, TRX_HOLDING_LOCK, KEY_INFO JSON, db_id, db_name, table_id, table_name, partition_id, partition_name, handle_type, handle_value, index_id, index_name, index_values, PROCESS privilege, pessimistic-txn.deadlock-history-capacity, deadlock history capacity, current TiDB node, deadlock event rows, SQL digest, statement summary tables
- Follow-up Guidance: The source also states that DEADLOCK_ID only identifies the same deadlock event within the same result set and is not globally unique or persisted, and that unavailable KEY_INFO fields are omitted from the JSON result.
- Classification Note: This is reference content because it defines the DEADLOCKS table schema, explains each column and KEY_INFO field, and documents related configuration and privilege details from the official table description.

## Official Source Content

# DEADLOCKS

The `DEADLOCKS` table shows the information of the several deadlock errors that have occurred recently on the current TiDB node.

```sql
USE INFORMATION_SCHEMA;
DESC deadlocks;
```

The output is as follows:

```sql
+-------------------------+---------------------+------+------+---------+-------+
| Field                   | Type                | Null | Key  | Default | Extra |
+-------------------------+---------------------+------+------+---------+-------+
| DEADLOCK_ID             | bigint(21)          | NO   |      | NULL    |       |
| OCCUR_TIME              | timestamp(6)        | YES  |      | NULL    |       |
| RETRYABLE               | tinyint(1)          | NO   |      | NULL    |       |
| TRY_LOCK_TRX_ID         | bigint(21) unsigned | NO   |      | NULL    |       |
| CURRENT_SQL_DIGEST      | varchar(64)         | YES  |      | NULL    |       |
| CURRENT_SQL_DIGEST_TEXT | text                | YES  |      | NULL    |       |
| KEY                     | text                | YES  |      | NULL    |       |
| KEY_INFO                | text                | YES  |      | NULL    |       |
| TRX_HOLDING_LOCK        | bigint(21) unsigned | NO   |      | NULL    |       |
+-------------------------+---------------------+------+------+---------+-------+
```

The `DEADLOCKS` table uses multiple rows to show the same deadlock event, and each row displays the information about one of the transactions involved in the deadlock event. If the TiDB node records multiple deadlock errors, each error is distinguished using the `DEADLOCK_ID` column. The same `DEADLOCK_ID` indicates the same deadlock event. Note that `DEADLOCK_ID` **does not guarantee global uniqueness and will not be persisted**. It only shows the same deadlock event in the same result set.

The meaning of each column field in the `DEADLOCKS` table is as follows:

* `DEADLOCK_ID`: The ID of the deadlock event. When multiple deadlock errors exist in the table, you can use this column to distinguish rows that belong to different deadlock errors.
* `OCCUR_TIME`: The time when the deadlock error occurs.
* `RETRYABLE`: Whether the deadlock error can be retried. For the description of retryable deadlock errors, see the [Retryable deadlock errors](#retryable-deadlock-errors) section.
* `TRY_LOCK_TRX_ID`: The ID of the transaction that tries to acquire lock. This ID is also the `start_ts` of the transaction.
* `CURRENT_SQL_DIGEST`: The digest of the SQL statement currently being executed in the lock-acquiring transaction.
* `CURRENT_SQL_DIGEST_TEXT`: The normalized form of the SQL statement that is currently being executed in the lock-acquiring transaction.
* `KEY`: The blocked key that the transaction tries to lock. The value of this field is displayed in the form of hexadecimal string.
* `KEY_INFO`: The detailed information of `KEY`. See the [`KEY_INFO`](#key_info) section.
* `TRX_HOLDING_LOCK`: The ID of the transaction that currently holds the lock on the key and causes blocking. This ID is also the `start_ts` of the transaction.

To adjust the maximum number of deadlock events that can be recorded in the `DEADLOCKS` table, adjust the [`pessimistic-txn.deadlock-history-capacity`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#deadlock-history-capacity) configuration in the TiDB configuration file. By default, the information of the recent 10 deadlock events is recorded in the table.

The information of the recent 10 deadlock events is recorded in the `DEADLOCKS` table.

> **Warning:**
>
> * Only users with the [PROCESS](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html#priv_process) privilege can query this table.
> * The information (SQL digest) in the `CURRENT_SQL_DIGEST` column is the hash value calculated from the normalized SQL statement. The information in the `CURRENT_SQL_DIGEST_TEXT` column is internally queried from statements summary tables, so it is possible that the corresponding statement cannot be found internally. For the detailed description of SQL digests and the statements summary tables, see [Statement Summary Tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables).
## `KEY_INFO`

The `KEY_INFO` column shows the detailed information of the `KEY` column. The information is shown in the JSON format. The description of each field is as follows:

* `"db_id"`: The ID of the schema to which the key belongs.
* `"db_name"`: The name of the schema to which the key belongs.
* `"table_id"`: The ID of the table to which the key belongs.
* `"table_name"`: The name of the table to which the key belongs.
* `"partition_id"`: The ID of the partition where the key is located.
* `"partition_name"`: The name of the partition where the key is located.
* `"handle_type"`: The handle type of the row key (that is, the key that stores a row of data). The possible values ​​are as follows:
    * `"int"`: The handle type is int, which means that the handle is the row ID.
    * `"common"`: The handle type is not int64. This type is shown in the non-int primary key when clustered index is enabled.
    * `"unknown"`: The handle type is currently not supported.
* `"handle_value"`: The handle value.
* `"index_id"`: The index ID to which the index key (the key that stores the index) belongs.
* `"index_name"`: The name of the index to which the index key belongs.
* `"index_values"`: The index value in the index key.

In the above fields, if the information of a field is not applicable or currently unavailable, the field is omitted in the query result. For example, the row key information does not contain `index_id`, `index_name`, and `index_values`; the index key does not contain `handle_type` and `handle_value`; non-partitioned tables do not display `partition_id` and `partition_name`; the key information in the deleted table cannot obtain schema information such as `table_name`, `db_id`, `db_name`, and `index_name`, and it is unable to distinguish whether the table is a partitioned table.

> **Note:**
>
> If a key comes from a table with partitioning enabled, and the information of the schema to which the key belongs cannot be queried due to some reasons (for example, the table to which the key belongs has been deleted) during the query, the ID of the partition to which the key belongs might be appear in the `table_id` field. This is because TiDB encodes the keys of different partitions in the same way as it encodes the keys of several independent tables. Therefore, when the schema information is missing, TiDB cannot confirm whether the key belongs to an unpartitioned table or to one partition of a table.
