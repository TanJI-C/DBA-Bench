# PARTITIONS information schema table and example query

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-partitions.md`
- Source Title: `PARTITIONS`
- Source Heading Path: `PARTITIONS | PARTITIONS > See also`
- Source Line Ranges: `5-121`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `partitions`, `partitioned-tables`, `schema-metadata`, `table-definition`, `example-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0399_4d9e15f4d1`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-partitions.md#partitions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b70a4544cf4ade4f666f59996d6d95dffb06050c81d95f3011cc91df4d19a1a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-partitions#partitions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-partitions.md

## Retrieval Guidance

- Use When: Use this content when looking for schema metadata about partitioned tables in INFORMATION_SCHEMA, including the PARTITIONS table columns and an example query filtered by table_schema and table_name.
- Retrieval Keywords: PARTITIONS, INFORMATION_SCHEMA, DESC partitions, partitioned tables, TABLE_SCHEMA, TABLE_NAME, PARTITION_NAME, PARTITION_METHOD, PARTITION_EXPRESSION, TIDB_PARTITION_ID, TIDB_PLACEMENT_POLICY_NAME, SELECT * FROM PARTITIONS WHERE table_schema='test' AND table_name='t1', CREATE TABLE test.t1 (id INT NOT NULL PRIMARY KEY) PARTITION BY HASH (id) PARTITIONS 2
- Follow-up Guidance: The source also links to "Explain statements using partitions".
- Classification Note: This is reference content because it defines the INFORMATION_SCHEMA.PARTITIONS table structure and shows example SQL output for a partitioned table.

## Official Source Content

# PARTITIONS

The `PARTITIONS` table provides information about [partitioned tables](https://docs.pingcap.com/tidb/stable/partitioned-table).

```sql
USE INFORMATION_SCHEMA;
DESC partitions;
```

The output is as follows:

```sql
+-------------------------------+--------------+------+------+---------+-------+
| Field                         | Type         | Null | Key  | Default | Extra |
+-------------------------------+--------------+------+------+---------+-------+
| TABLE_CATALOG                 | varchar(512) | YES  |      | NULL    |       |
| TABLE_SCHEMA                  | varchar(64)  | YES  |      | NULL    |       |
| TABLE_NAME                    | varchar(64)  | YES  |      | NULL    |       |
| PARTITION_NAME                | varchar(64)  | YES  |      | NULL    |       |
| SUBPARTITION_NAME             | varchar(64)  | YES  |      | NULL    |       |
| PARTITION_ORDINAL_POSITION    | bigint(21)   | YES  |      | NULL    |       |
| SUBPARTITION_ORDINAL_POSITION | bigint(21)   | YES  |      | NULL    |       |
| PARTITION_METHOD              | varchar(18)  | YES  |      | NULL    |       |
| SUBPARTITION_METHOD           | varchar(12)  | YES  |      | NULL    |       |
| PARTITION_EXPRESSION          | longtext     | YES  |      | NULL    |       |
| SUBPARTITION_EXPRESSION       | longtext     | YES  |      | NULL    |       |
| PARTITION_DESCRIPTION         | longtext     | YES  |      | NULL    |       |
| TABLE_ROWS                    | bigint(21)   | YES  |      | NULL    |       |
| AVG_ROW_LENGTH                | bigint(21)   | YES  |      | NULL    |       |
| DATA_LENGTH                   | bigint(21)   | YES  |      | NULL    |       |
| MAX_DATA_LENGTH               | bigint(21)   | YES  |      | NULL    |       |
| INDEX_LENGTH                  | bigint(21)   | YES  |      | NULL    |       |
| DATA_FREE                     | bigint(21)   | YES  |      | NULL    |       |
| CREATE_TIME                   | datetime     | YES  |      | NULL    |       |
| UPDATE_TIME                   | datetime     | YES  |      | NULL    |       |
| CHECK_TIME                    | datetime     | YES  |      | NULL    |       |
| CHECKSUM                      | bigint(21)   | YES  |      | NULL    |       |
| PARTITION_COMMENT             | varchar(80)  | YES  |      | NULL    |       |
| NODEGROUP                     | varchar(12)  | YES  |      | NULL    |       |
| TABLESPACE_NAME               | varchar(64)  | YES  |      | NULL    |       |
| TIDB_PARTITION_ID             | bigint(21)   | YES  |      | NULL    |       |
| TIDB_PLACEMENT_POLICY_NAME    | varchar(64)  | YES  |      | NULL    |       |
+-------------------------------+--------------+------+------+---------+-------+
27 rows in set (0.00 sec)
```

```sql
CREATE TABLE test.t1 (id INT NOT NULL PRIMARY KEY) PARTITION BY HASH (id) PARTITIONS 2;
SELECT * FROM PARTITIONS WHERE table_schema='test' AND table_name='t1'\G
```

The output is as follows:

```sql
*************************** 1. row ***************************
                TABLE_CATALOG: def
                 TABLE_SCHEMA: test
                   TABLE_NAME: t1
               PARTITION_NAME: p0
            SUBPARTITION_NAME: NULL
   PARTITION_ORDINAL_POSITION: 1
SUBPARTITION_ORDINAL_POSITION: NULL
             PARTITION_METHOD: HASH
          SUBPARTITION_METHOD: NULL
         PARTITION_EXPRESSION: `id`
      SUBPARTITION_EXPRESSION: NULL
        PARTITION_DESCRIPTION:
                   TABLE_ROWS: 0
               AVG_ROW_LENGTH: 0
                  DATA_LENGTH: 0
              MAX_DATA_LENGTH: 0
                 INDEX_LENGTH: 0
                    DATA_FREE: 0
                  CREATE_TIME: 2022-12-14 06:09:33
                  UPDATE_TIME: NULL
                   CHECK_TIME: NULL
                     CHECKSUM: NULL
            PARTITION_COMMENT:
                    NODEGROUP: NULL
              TABLESPACE_NAME: NULL
            TIDB_PARTITION_ID: 89
   TIDB_PLACEMENT_POLICY_NAME: NULL
*************************** 2. row ***************************
                TABLE_CATALOG: def
                 TABLE_SCHEMA: test
                   TABLE_NAME: t1
               PARTITION_NAME: p1
            SUBPARTITION_NAME: NULL
   PARTITION_ORDINAL_POSITION: 2
SUBPARTITION_ORDINAL_POSITION: NULL
             PARTITION_METHOD: HASH
          SUBPARTITION_METHOD: NULL
         PARTITION_EXPRESSION: `id`
      SUBPARTITION_EXPRESSION: NULL
        PARTITION_DESCRIPTION:
                   TABLE_ROWS: 0
               AVG_ROW_LENGTH: 0
                  DATA_LENGTH: 0
              MAX_DATA_LENGTH: 0
                 INDEX_LENGTH: 0
                    DATA_FREE: 0
                  CREATE_TIME: 2022-12-14 06:09:33
                  UPDATE_TIME: NULL
                   CHECK_TIME: NULL
                     CHECKSUM: NULL
            PARTITION_COMMENT:
                    NODEGROUP: NULL
              TABLESPACE_NAME: NULL
            TIDB_PARTITION_ID: 90
   TIDB_PLACEMENT_POLICY_NAME: NULL
2 rows in set (0.00 sec)
```
## See also

- [Explain statements using partitions](https://docs.pingcap.com/tidb/stable/explain-partitions)
