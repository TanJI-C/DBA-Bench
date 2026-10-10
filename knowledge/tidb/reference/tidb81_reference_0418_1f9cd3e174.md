# TIDB_HOT_REGIONS table schema and column reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tidb-hot-regions.md`
- Source Title: `TIDB_HOT_REGIONS`
- Source Heading Path: `TIDB_HOT_REGIONS`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `sql`
- Topic Tags: `information_schema`, `hot-regions`, `table-schema`, `column-reference`, `region-metadata`, `sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0418_1f9cd3e174`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tidb-hot-regions.md#tidb-hot-regions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `19d45faea6e3b3a4ce1eaf7e815ed383a8fb032be8e60b3651c26c4964e4e266`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-hot-regions#tidb-hot-regions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tidb-hot-regions.md

## Retrieval Guidance

- Use When: Use this when the question asks for the schema, column meanings, or SQL inspection of the information_schema.TIDB_HOT_REGIONS table for current hot Regions.
- Retrieval Keywords: TIDB_HOT_REGIONS, information_schema, DESC tidb_hot_regions, current hot Regions, TIDB_HOT_REGIONS table schema, TABLE_ID, INDEX_ID, DB_NAME, TABLE_NAME, INDEX_NAME, REGION_ID, TYPE, MAX_HOT_DEGREE, REGION_COUNT, FLOW_BYTES, TIDB_HOT_REGIONS_HISTORY
- Follow-up Guidance: For history hot Regions, the source points to TIDB_HOT_REGIONS_HISTORY.
- Classification Note: This is reference content because it defines the TIDB_HOT_REGIONS table, lists its columns, and states that it is only applicable to TiDB Self-Managed and not available on TiDB Cloud.

## Official Source Content

# TIDB_HOT_REGIONS

The `TIDB_HOT_REGIONS` table provides information about the current hot Regions. For information about history hot Regions, see `[TIDB_HOT_REGIONS_HISTORY](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-hot-regions-history)`.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

```sql
USE information_schema;
DESC tidb_hot_regions;
```

```
+----------------+-------------+------+------+---------+-------+
| Field          | Type        | Null | Key  | Default | Extra |
+----------------+-------------+------+------+---------+-------+
| TABLE_ID       | bigint(21)  | YES  |      | NULL    |       |
| INDEX_ID       | bigint(21)  | YES  |      | NULL    |       |
| DB_NAME        | varchar(64) | YES  |      | NULL    |       |
| TABLE_NAME     | varchar(64) | YES  |      | NULL    |       |
| INDEX_NAME     | varchar(64) | YES  |      | NULL    |       |
| REGION_ID      | bigint(21)  | YES  |      | NULL    |       |
| TYPE           | varchar(64) | YES  |      | NULL    |       |
| MAX_HOT_DEGREE | bigint(21)  | YES  |      | NULL    |       |
| REGION_COUNT   | bigint(21)  | YES  |      | NULL    |       |
| FLOW_BYTES     | bigint(21)  | YES  |      | NULL    |       |
+----------------+-------------+------+------+---------+-------+
10 rows in set (0.00 sec)
```

The description of columns in the `TIDB_HOT_REGIONS` table is as follows:

* `TABLE_ID`: The ID of the table in which the hot Region is located.
* `INDEX_ID`: The ID of the index in which the hot Region is located.
* `DB_NAME`: The database name of the object in which the hot Region is located.
* `TABLE_NAME`: The name of the table in which the hot Region is located.
* `INDEX_NAME`: The name of the index in which the hot Region is located.
* `REGION_ID`: The ID of the hot Region.
* `TYPE`: The type of the hot Region.
* `MAX_HOT_DEGREE`: The maximum hot degree of the Region.
* `REGION_COUNT`: The number of hot Regions in the instance. 
* `FLOW_BYTES`: The number of bytes written and read in the Region.
