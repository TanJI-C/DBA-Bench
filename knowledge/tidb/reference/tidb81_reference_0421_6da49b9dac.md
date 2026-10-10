# TIDB_SERVERS_INFO table schema and example query output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tidb-servers-info.md`
- Source Title: `TIDB_SERVERS_INFO`
- Source Heading Path: `TIDB_SERVERS_INFO`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`
- Topic Tags: `information_schema`, `metadata`, `server-info`, `schema`, `sql-query`, `cluster-topology`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0421_6da49b9dac`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tidb-servers-info.md#tidb-servers-info`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c02df011604336a94da4a52bb6f0adaf2e9cf07568b2aef61cf572c375cdd23d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-servers-info#tidb-servers-info
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tidb-servers-info.md

## Retrieval Guidance

- Use When: Use this when looking for the INFORMATION_SCHEMA table that lists TiDB server process metadata, its schema, or example query output for cluster topology details.
- Retrieval Keywords: TIDB_SERVERS_INFO, INFORMATION_SCHEMA, tidb_servers_info, DESC tidb_servers_info, SELECT * FROM TIDB_SERVERS_INFO\G, DDL_ID, IP, PORT, STATUS_PORT, LEASE, VERSION, GIT_HASH, BINLOG_STATUS, LABELS, TiDB servers in the TiDB Cluster, tidb-server processes
- Follow-up Guidance: The content also notes that this table is not available on Starter and Essential clusters.
- Classification Note: This is reference content because it defines the TIDB_SERVERS_INFO table, lists its columns, and shows example SQL query output.

## Official Source Content

# TIDB_SERVERS_INFO

The `TIDB_SERVERS_INFO` table provides information about TiDB servers in the TiDB Cluster (namely, tidb-server processes).

> **Note:**
>
> This table is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

```sql
USE INFORMATION_SCHEMA;
DESC tidb_servers_info;
```

The output is as follows:

```sql
+---------------+--------------+------+------+---------+-------+
| Field         | Type         | Null | Key  | Default | Extra |
+---------------+--------------+------+------+---------+-------+
| DDL_ID        | varchar(64)  | YES  |      | NULL    |       |
| IP            | varchar(64)  | YES  |      | NULL    |       |
| PORT          | bigint(21)   | YES  |      | NULL    |       |
| STATUS_PORT   | bigint(21)   | YES  |      | NULL    |       |
| LEASE         | varchar(64)  | YES  |      | NULL    |       |
| VERSION       | varchar(64)  | YES  |      | NULL    |       |
| GIT_HASH      | varchar(64)  | YES  |      | NULL    |       |
| BINLOG_STATUS | varchar(64)  | YES  |      | NULL    |       |
| LABELS        | varchar(128) | YES  |      | NULL    |       |
+---------------+--------------+------+------+---------+-------+
9 rows in set (0.00 sec)
```

View the `TIDB_SERVERS_INFO` table:

```sql
SELECT * FROM TIDB_SERVERS_INFO\G
```

The output is as follows:

```sql
*************************** 1. row ***************************
       DDL_ID: 771c169d-0a3a-48ea-a93c-a4d6751d3674
           IP: 0.0.0.0
         PORT: 4000
  STATUS_PORT: 10080
        LEASE: 45s
      VERSION: 8.0.11-TiDB-v8.1.2
     GIT_HASH: 827d8ff2d22ac4c93ae1b841b79d468211e1d393
BINLOG_STATUS: Off
       LABELS:
1 row in set (0.006 sec)
```
