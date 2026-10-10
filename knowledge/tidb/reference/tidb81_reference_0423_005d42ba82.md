# CLUSTER_TIDB_TRX table scope and schema

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tidb-trx.md`
- Source Title: `TIDB_TRX`
- Source Heading Path: `TIDB_TRX > CLUSTER_TIDB_TRX`
- Source Line Ranges: `126-157`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `information_schema`, `cluster-wide transactions`, `table schema`, `sql query`, `instance field`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0423_005d42ba82`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tidb-trx.md#cluster-tidb-trx`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e04917ab55fbcab81c74628d47507343ce486005084d72c5485c7a4172278290`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-trx#cluster-tidb-trx
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tidb-trx.md

## Retrieval Guidance

- Use When: Use this chunk when you need the schema and scope of INFORMATION_SCHEMA.CLUSTER_TIDB_TRX for viewing transactions running on all TiDB nodes in a cluster and understanding the extra INSTANCE field compared with TIDB_TRX.
- Retrieval Keywords: CLUSTER_TIDB_TRX, TIDB_TRX, INFORMATION_SCHEMA, DESC CLUSTER_TIDB_TRX, INSTANCE, cluster-wide transactions, single TiDB node, IP address and port, CURRENT_SQL_DIGEST, CURRENT_SQL_DIGEST_TEXT, STATE, WAITING_START_TIME, MEM_BUFFER_KEYS, MEM_BUFFER_BYTES, SESSION_ID, ALL_SQL_DIGESTS, RELATED_TABLE_IDS
- Follow-up Guidance: The source shows that querying DESC CLUSTER_TIDB_TRX in INFORMATION_SCHEMA returns the table schema including INSTANCE, ID, START_TIME, CURRENT_SQL_DIGEST, CURRENT_SQL_DIGEST_TEXT, STATE, WAITING_START_TIME, MEM_BUFFER_KEYS, MEM_BUFFER_BYTES, SESSION_ID, USER, DB, ALL_SQL_DIGESTS, and RELATED_TABLE_IDS.
- Classification Note: This is reference content because it defines the scope difference between TIDB_TRX and CLUSTER_TIDB_TRX and lists the exact table fields and types from the official schema output.

## Official Source Content

## CLUSTER_TIDB_TRX

The `TIDB_TRX` table only provides information about the transactions that are being executed on a single TiDB node. If you want to view the information of the transactions that are being executed on all TiDB nodes in the entire cluster, you need to query the `CLUSTER_TIDB_TRX` table. Compared with the query result of the `TIDB_TRX` table, the query result of the `CLUSTER_TIDB_TRX` table includes an extra `INSTANCE` field. The `INSTANCE` field displays the IP address and port of each node in the cluster, which is used to distinguish the TiDB nodes where the transactions are located.

```sql
USE INFORMATION_SCHEMA;
DESC CLUSTER_TIDB_TRX;
```

The output is as follows:

```sql
+-------------------------+-----------------------------------------------------------------+------+------+---------+-------+
| Field                   | Type                                                            | Null | Key  | Default | Extra |
+-------------------------+-----------------------------------------------------------------+------+------+---------+-------+
| INSTANCE                | varchar(64)                                                     | YES  |      | NULL    |       |
| ID                      | bigint(21) unsigned                                             | NO   | PRI  | NULL    |       |
| START_TIME              | timestamp(6)                                                    | YES  |      | NULL    |       |
| CURRENT_SQL_DIGEST      | varchar(64)                                                     | YES  |      | NULL    |       |
| CURRENT_SQL_DIGEST_TEXT | text                                                            | YES  |      | NULL    |       |
| STATE                   | enum('Idle','Running','LockWaiting','Committing','RollingBack') | YES  |      | NULL    |       |
| WAITING_START_TIME      | timestamp(6)                                                    | YES  |      | NULL    |       |
| MEM_BUFFER_KEYS         | bigint(64)                                                      | YES  |      | NULL    |       |
| MEM_BUFFER_BYTES        | bigint(64)                                                      | YES  |      | NULL    |       |
| SESSION_ID              | bigint(21) unsigned                                             | YES  |      | NULL    |       |
| USER                    | varchar(16)                                                     | YES  |      | NULL    |       |
| DB                      | varchar(64)                                                     | YES  |      | NULL    |       |
| ALL_SQL_DIGESTS         | text                                                            | YES  |      | NULL    |       |
| RELATED_TABLE_IDS       | text                                                            | YES  |      | NULL    |       |
+-------------------------+-----------------------------------------------------------------+------+------+---------+-------+
14 rows in set (0.00 sec)
```
