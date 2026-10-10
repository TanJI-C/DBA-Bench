# information_schema.TABLES columns and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tables.md`
- Source Title: `TABLES`
- Source Heading Path: `TABLES`
- Source Line Ranges: `5-126`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`, `tikv`
- Topic Tags: `information_schema`, `tables`, `metadata`, `schema`, `columns`, `show tables`, `table statistics`, `auto_increment`, `collation`, `table id`, `row id sharding`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0415_0e38ea748c`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tables.md#tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9984a9b1b926f61c43a63cd65a3423996f0d5d4addcd99ad89f3cba3a426cbe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tables#tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tables.md

## Retrieval Guidance

- Use When: Use this chunk when you need the column definitions, example output, or SQL equivalence for querying table metadata from INFORMATION_SCHEMA.TABLES.
- Retrieval Keywords: INFORMATION_SCHEMA.TABLES, information_schema.TABLES, DESC tables, SELECT * FROM tables WHERE table_schema='mysql' AND table_name='user', SHOW TABLES FROM db_name [LIKE 'wild'], SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'db_name', TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE, ENGINE, VERSION, ROW_FORMAT, TABLE_ROWS, AVG_ROW_LENGTH, DATA_LENGTH, MAX_DATA_LENGTH, INDEX_LENGTH, DATA_FREE, AUTO_INCREMENT, CREATE_TIME, UPDATE_TIME, CHECK_TIME, TABLE_COLLATION, CHECKSUM, CREATE_OPTIONS, TABLE_COMMENT, TIDB_TABLE_ID, TIDB_ROW_ID_SHARDING_INFO, NOT_SHARDED, NOT_SHARDED(PK_IS_HANDLE), PK_AUTO_RANDOM_BITS={bit_number}, SHARD_BITS={bit_number}, table metadata, table statistics, table id, row id sharding
- Follow-up Guidance: The source also lists the meanings of all TABLES columns, including the TiDB-specific TIDB_TABLE_ID and TIDB_ROW_ID_SHARDING_INFO values.
- Classification Note: This is reference content because it enumerates INFORMATION_SCHEMA.TABLES columns, shows example queries and results, and defines each field's meaning.

## Official Source Content

# TABLES

The `TABLES` table provides information about tables in databases:

```sql
USE information_schema;
DESC tables;
```

```sql
+---------------------------+---------------+------+------+----------+-------+
| Field                     | Type          | Null | Key  | Default  | Extra |
+---------------------------+---------------+------+------+----------+-------+
| TABLE_CATALOG             | varchar(512)  | YES  |      | NULL     |       |
| TABLE_SCHEMA              | varchar(64)   | YES  |      | NULL     |       |
| TABLE_NAME                | varchar(64)   | YES  |      | NULL     |       |
| TABLE_TYPE                | varchar(64)   | YES  |      | NULL     |       |
| ENGINE                    | varchar(64)   | YES  |      | NULL     |       |
| VERSION                   | bigint(21)    | YES  |      | NULL     |       |
| ROW_FORMAT                | varchar(10)   | YES  |      | NULL     |       |
| TABLE_ROWS                | bigint(21)    | YES  |      | NULL     |       |
| AVG_ROW_LENGTH            | bigint(21)    | YES  |      | NULL     |       |
| DATA_LENGTH               | bigint(21)    | YES  |      | NULL     |       |
| MAX_DATA_LENGTH           | bigint(21)    | YES  |      | NULL     |       |
| INDEX_LENGTH              | bigint(21)    | YES  |      | NULL     |       |
| DATA_FREE                 | bigint(21)    | YES  |      | NULL     |       |
| AUTO_INCREMENT            | bigint(21)    | YES  |      | NULL     |       |
| CREATE_TIME               | datetime      | YES  |      | NULL     |       |
| UPDATE_TIME               | datetime      | YES  |      | NULL     |       |
| CHECK_TIME                | datetime      | YES  |      | NULL     |       |
| TABLE_COLLATION           | varchar(32)   | NO   |      | utf8_bin |       |
| CHECKSUM                  | bigint(21)    | YES  |      | NULL     |       |
| CREATE_OPTIONS            | varchar(255)  | YES  |      | NULL     |       |
| TABLE_COMMENT             | varchar(2048) | YES  |      | NULL     |       |
| TIDB_TABLE_ID             | bigint(21)    | YES  |      | NULL     |       |
| TIDB_ROW_ID_SHARDING_INFO | varchar(255)  | YES  |      | NULL     |       |
+---------------------------+---------------+------+------+----------+-------+
23 rows in set (0.00 sec)
```

```sql
SELECT * FROM tables WHERE table_schema='mysql' AND table_name='user'\G
```

```sql
*************************** 1. row ***************************
            TABLE_CATALOG: def
             TABLE_SCHEMA: mysql
               TABLE_NAME: user
               TABLE_TYPE: BASE TABLE
                   ENGINE: InnoDB
                  VERSION: 10
               ROW_FORMAT: Compact
               TABLE_ROWS: 0
           AVG_ROW_LENGTH: 0
              DATA_LENGTH: 0
          MAX_DATA_LENGTH: 0
             INDEX_LENGTH: 0
                DATA_FREE: 0
           AUTO_INCREMENT: NULL
              CREATE_TIME: 2020-07-05 09:25:51
              UPDATE_TIME: NULL
               CHECK_TIME: NULL
          TABLE_COLLATION: utf8mb4_bin
                 CHECKSUM: NULL
           CREATE_OPTIONS: 
            TABLE_COMMENT: 
            TIDB_TABLE_ID: 5
TIDB_ROW_ID_SHARDING_INFO: NULL
1 row in set (0.00 sec)
```

The following statements are equivalent:

```sql
SELECT table_name FROM INFORMATION_SCHEMA.TABLES
  WHERE table_schema = 'db_name'
  [AND table_name LIKE 'wild']

SHOW TABLES
  FROM db_name
  [LIKE 'wild']
```

The description of columns in the `TABLES` table is as follows:

* `TABLE_CATALOG`: The name of the catalog which the table belongs to. The value is always `def`.
* `TABLE_SCHEMA`: The name of the schema which the table belongs to.
* `TABLE_NAME`: The name of the table.
* `TABLE_TYPE`: The type of the table.
* `ENGINE`: The type of the storage engine. The value is currently `InnoDB`.
* `VERSION`: Version. The value is `10` by default.
* `ROW_FORMAT`: The row format. The value is currently `Compact`.
* `TABLE_ROWS`: The number of rows in the table in statistics.
* `AVG_ROW_LENGTH`: The average row length of the table. `AVG_ROW_LENGTH` = `DATA_LENGTH` / `TABLE_ROWS`.
* `DATA_LENGTH`: Data length. `DATA_LENGTH` = `TABLE_ROWS` \* the sum of storage lengths of the columns in the tuple. The replicas of TiKV are not taken into account.
* `MAX_DATA_LENGTH`: The maximum data length. The value is currently `0`, which means the data length has no upper limit.
* `INDEX_LENGTH`: The index length. `INDEX_LENGTH` = `TABLE_ROWS` \* the sum of lengths of the columns in the index tuple. The replicas of TiKV are not taken into account.
* `DATA_FREE`: Data fragment. The value is currently `0`.
* `AUTO_INCREMENT`: The current step of the auto-increment primary key.
* `CREATE_TIME`: The time at which the table is created.
* `UPDATE_TIME`: The time at which the table is updated.
* `CHECK_TIME`: The time at which the table is checked.
* `TABLE_COLLATION`: The collation of strings in the table.
* `CHECKSUM`: Checksum.
* `CREATE_OPTIONS`: Creates options.
* `TABLE_COMMENT`: The comments and notes of the table.

Most of the information in the table is the same as MySQL. Only two columns are newly defined by TiDB:

* `TIDB_TABLE_ID`: to indicate the internal ID of a table. This ID is unique in a TiDB cluster.
* `TIDB_ROW_ID_SHARDING_INFO`: to indicate the sharding type of a table. The possible values are as follows:
    - `"NOT_SHARDED"`: the table is not sharded.
    - `"NOT_SHARDED(PK_IS_HANDLE)"`: the table that defines an integer Primary Key as its row id is not sharded.
    - `"PK_AUTO_RANDOM_BITS={bit_number}"`: the table that defines an integer Primary Key as its row id is sharded because the Primary Key is assigned with `AUTO_RANDOM` attribute.
    - `"SHARD_BITS={bit_number}"`: the table is sharded using `SHARD_ROW_ID_BITS={bit_number}`.
    - NULL: the table is a system table or view, and thus cannot be sharded.
