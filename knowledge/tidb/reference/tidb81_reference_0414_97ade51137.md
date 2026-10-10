# TABLE_STORAGE_STATS columns and example query output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-table-storage-stats.md`
- Source Title: `TABLE_STORAGE_STATS`
- Source Heading Path: `TABLE_STORAGE_STATS`
- Source Line Ranges: `5-63`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tikv`
- Topic Tags: `information_schema`, `table_storage_stats`, `table-size`, `storage-engine`, `table-metadata`, `regions`, `replicas`, `table-keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0414_97ade51137`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-table-storage-stats.md#table-storage-stats`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0e9a98a268310a71e713662ed34544b816255b86b4fb25f6c271ad26bd2d0101`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-table-storage-stats#table-storage-stats
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-table-storage-stats.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the INFORMATION_SCHEMA.TABLE_STORAGE_STATS table definition, example query output, or the meaning of TiKV-backed table storage size, Region, replica, and key-count fields for a specific table.
- Retrieval Keywords: TABLE_STORAGE_STATS, INFORMATION_SCHEMA, DESC TABLE_STORAGE_STATS, SELECT * FROM TABLE_STORAGE_STATS WHERE table_schema = 'test' AND table_name = 't1', TABLE_SCHEMA, TABLE_NAME, TABLE_ID, PEER_COUNT, REGION_COUNT, EMPTY_REGION_COUNT, TABLE_SIZE, TABLE_KEYS, table sizes as stored by the storage engine (TiKV), The total size of the table, in the unit of MiB, The number of replicas of the table, The number of Regions, The number of Regions that do not contain data in this table, The total number of records in the table
- Follow-up Guidance: The source includes an example that creates test.t1, inserts one row, and queries TABLE_STORAGE_STATS for table_schema = 'test' and table_name = 't1'.
- Classification Note: This is reference content because it defines the TABLE_STORAGE_STATS information schema table, lists its columns, and explains each field with example SQL output.

## Official Source Content

# TABLE_STORAGE_STATS

The `TABLE_STORAGE_STATS` table provides information about table sizes as stored by the storage engine (TiKV).

```sql
USE INFORMATION_SCHEMA;
DESC TABLE_STORAGE_STATS;
```

The output is as follows:

```sql
+--------------------+-------------+------+------+---------+-------+
| Field              | Type        | Null | Key  | Default | Extra |
+--------------------+-------------+------+------+---------+-------+
| TABLE_SCHEMA       | varchar(64) | YES  |      | NULL    |       |
| TABLE_NAME         | varchar(64) | YES  |      | NULL    |       |
| TABLE_ID           | bigint(21)  | YES  |      | NULL    |       |
| PEER_COUNT         | bigint(21)  | YES  |      | NULL    |       |
| REGION_COUNT       | bigint(21)  | YES  |      | NULL    |       |
| EMPTY_REGION_COUNT | bigint(21)  | YES  |      | NULL    |       |
| TABLE_SIZE         | bigint(64)  | YES  |      | NULL    |       |
| TABLE_KEYS         | bigint(64)  | YES  |      | NULL    |       |
+--------------------+-------------+------+------+---------+-------+
8 rows in set (0.00 sec)
```

```sql
CREATE TABLE test.t1 (id INT);
INSERT INTO test.t1 VALUES (1);
SELECT * FROM TABLE_STORAGE_STATS WHERE table_schema = 'test' AND table_name = 't1'\G
```

The output is as follows:

```sql
*************************** 1. row ***************************
      TABLE_SCHEMA: test
        TABLE_NAME: t1
          TABLE_ID: 56
        PEER_COUNT: 1
      REGION_COUNT: 1
EMPTY_REGION_COUNT: 1
        TABLE_SIZE: 1
        TABLE_KEYS: 0
1 row in set (0.00 sec)
```

Fields in the `TABLE_STORAGE_STATS` table are described as follows:

* `TABLE_SCHEMA`: The name of the schema to which the table belongs.
* `TABLE_NAME`: The name of the table.
* `TABLE_ID`: The ID of the table.
* `PEER_COUNT`: The number of replicas of the table.
* `REGION_COUNT`: The number of Regions.
* `EMPTY_REGION_COUNT`: The number of Regions that do not contain data in this table.
* `TABLE_SIZE`: The total size of the table, in the unit of MiB.
* `TABLE_KEYS`: The total number of records in the table.
