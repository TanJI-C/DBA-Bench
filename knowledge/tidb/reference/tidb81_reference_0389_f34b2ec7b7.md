# CLUSTER_DEADLOCKS table structure and uniqueness notes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-deadlocks.md`
- Source Title: `DEADLOCKS`
- Source Heading Path: `DEADLOCKS > CLUSTER_DEADLOCKS`
- Source Line Ranges: `195-223`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `information_schema`, `deadlocks`, `cluster_deadlocks`, `schema`, `instance`, `deadlock_id`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0389_f34b2ec7b7`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-deadlocks.md#cluster-deadlocks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ba290867dcb0fd0dd1ed488a996d64f6bfc3d12f5de39d0bffc65f2d1233e0de`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks#cluster-deadlocks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-deadlocks.md

## Retrieval Guidance

- Use When: Use this chunk when identifying the schema of INFORMATION_SCHEMA.CLUSTER_DEADLOCKS or clarifying how to distinguish deadlock records across TiDB nodes.
- Retrieval Keywords: INFORMATION_SCHEMA.CLUSTER_DEADLOCKS, CLUSTER_DEADLOCKS, DEADLOCKS table on each node, INSTANCE column, DEADLOCK_ID, INSTANCE and DEADLOCK_ID together, DESC CLUSTER_DEADLOCKS, recent deadlock errors, TiDB node IP address and port, CURRENT_SQL_DIGEST, CURRENT_SQL_DIGEST_TEXT, TRY_LOCK_TRX_ID, TRX_HOLDING_LOCK, KEY_INFO
- Follow-up Guidance: The source shows that `CLUSTER_DEADLOCKS` is the combined information of the `DEADLOCKS` table on each TiDB node and adds the `INSTANCE` column to distinguish nodes.
- Classification Note: This is reference content because it defines the `CLUSTER_DEADLOCKS` table structure and notes that `DEADLOCK_ID` is not globally unique, so `INSTANCE` and `DEADLOCK_ID` must be used together in results.

## Official Source Content

## CLUSTER_DEADLOCKS

The `CLUSTER_DEADLOCKS` table returns information about the recent deadlock errors on each TiDB node in the entire cluster, which is the combined information of the `DEADLOCKS` table on each node. `CLUSTER_DEADLOCKS` also includes an additional `INSTANCE` column to display the IP address and port of the node to distinguish between different TiDB nodes.

Note that, because `DEADLOCK_ID` does not guarantee global uniqueness, in the query result of the `CLUSTER_DEADLOCKS` table, you need to use the `INSTANCE` and `DEADLOCK_ID` together to distinguish the information of different deadlock errors in the result set.

```sql
USE INFORMATION_SCHEMA;
DESC CLUSTER_DEADLOCKS;
```

The output is as follows:

```sql
+-------------------------+---------------------+------+------+---------+-------+
| Field                   | Type                | Null | Key  | Default | Extra |
+-------------------------+---------------------+------+------+---------+-------+
| INSTANCE                | varchar(64)         | YES  |      | NULL    |       |
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
