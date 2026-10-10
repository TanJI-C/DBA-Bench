# TIFLASH_REPLICA table schema and field descriptions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tiflash-replica.md`
- Source Title: `TIFLASH_REPLICA`
- Source Heading Path: `TIFLASH_REPLICA`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `information_schema`, `metadata`, `replica-status`, `availability`, `replication-progress`, `schema-reference`, `query-planning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0424_d4bebd3b8b`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tiflash-replica.md#tiflash-replica`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `20e49bbca3ad0a595f0cb23b19d16330f9cc3b78e8d9b2b6295e918adfafd441`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tiflash-replica#tiflash-replica
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tiflash-replica.md

## Retrieval Guidance

- Use When: Use this when you need the INFORMATION_SCHEMA metadata schema or field meanings for checking TiFlash replica availability, replica count, location labels, or replication progress for a table.
- Retrieval Keywords: TIFLASH_REPLICA, INFORMATION_SCHEMA, DESC TIFLASH_REPLICA, TABLE_SCHEMA, TABLE_NAME, TABLE_ID, REPLICA_COUNT, LOCATION_LABELS, AVAILABLE, PROGRESS, TiFlash replica available, replication progress, query push down to TiFlash, LocationLabelList
- Follow-up Guidance: The content states that when AVAILABLE is 1, the TiDB optimizer can choose to push down queries to TiKV or TiFlash based on query cost, and when AVAILABLE is 1 but PROGRESS is less than 1, queries pushed down to TiFlash will probably fail due to timeout of waiting for data replication.
- Classification Note: This is reference content because it defines the TIFLASH_REPLICA table schema and explains the meaning of each field in INFORMATION_SCHEMA.

## Official Source Content

# TIFLASH_REPLICA

The `TIFLASH_REPLICA` table provides information about TiFlash replicas available.

```sql
USE INFORMATION_SCHEMA;
DESC TIFLASH_REPLICA;
```

The output is as follows:

```sql
+-----------------+-------------+------+------+---------+-------+
| Field           | Type        | Null | Key  | Default | Extra |
+-----------------+-------------+------+------+---------+-------+
| TABLE_SCHEMA    | varchar(64) | YES  |      | NULL    |       |
| TABLE_NAME      | varchar(64) | YES  |      | NULL    |       |
| TABLE_ID        | bigint(21)  | YES  |      | NULL    |       |
| REPLICA_COUNT   | bigint(64)  | YES  |      | NULL    |       |
| LOCATION_LABELS | varchar(64) | YES  |      | NULL    |       |
| AVAILABLE       | tinyint(1)  | YES  |      | NULL    |       |
| PROGRESS        | double      | YES  |      | NULL    |       |
+-----------------+-------------+------+------+---------+-------+
7 rows in set (0.01 sec)
```

Fields in the `TIFLASH_REPLICA` table are described as follows:

- `TABLE_SCHEMA`: the name of the database to which the table belongs.
- `TABLE_NAME`: the name of the table.
- `TABLE_ID`: the internal ID of the table, which is unique within a TiDB cluster.
- `REPLICA_COUNT`: the number of TiFlash replicas.
- `LOCATION_LABELS`: the LocationLabelList that is set when a TiFlash replica is created.
- `AVAILABLE`: indicates whether the TiFlash replica of the table is available. When the value is `1` (available), the TiDB optimizer can intelligently choose to push down queries to TiKV or TiFlash based on query cost. When the value is `0` (unavailable), TiDB will not push down queries to TiFlash. Once the value of this field becomes `1` (available), it will not change anymore.
- `PROGRESS`: the replication progress of TiFlash replicas, with the accuracy to two decimal places and at the minute level. The scope of this field is `[0, 1]`. When the `AVAILABLE` field is `1` and `PROGRESS` is less than 1, the TiFlash replica is far behind TiKV, and the queries pushed down to TiFlash will probably fail due to timeout of waiting for data replication.
