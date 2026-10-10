# DDL_JOBS information_schema table reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-ddl-jobs.md`
- Source Title: `DDL_JOBS`
- Source Heading Path: `DDL_JOBS`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `ddl`, `ddl_jobs`, `admin-show-ddl-jobs`, `schema-metadata`, `job-status`, `sql-reference`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0386_eefb5aee98`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-ddl-jobs.md#ddl-jobs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9507e1d2709239d8a4f006bffb22f16b794bbe86f77aa973d5d2dcaaaa2dc95`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-ddl-jobs#ddl-jobs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-ddl-jobs.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the INFORMATION_SCHEMA reference for DDL job history and status, including the SQL interface equivalent to ADMIN SHOW DDL JOBS and the columns exposed by DDL_JOBS.
- Retrieval Keywords: DDL_JOBS, information_schema.ddl_jobs, INFORMATION_SCHEMA, ADMIN SHOW DDL JOBS, DESC ddl_jobs, JOB_ID, DB_NAME, TABLE_NAME, JOB_TYPE, SCHEMA_STATE, SCHEMA_ID, TABLE_ID, ROW_COUNT, START_TIME, END_TIME, STATE, QUERY, DDL operations, job status, DDL statements
- Follow-up Guidance: The source includes example queries using USE information_schema; DESC ddl_jobs; and SELECT * FROM ddl_jobs LIMIT 3\G.
- Classification Note: This is a SQL reference entry because it defines the DDL_JOBS INFORMATION_SCHEMA table, its purpose, and its returned columns with examples.

## Official Source Content

# DDL_JOBS

The `DDL_JOBS` table provides an `INFORMATION_SCHEMA` interface to the [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) command. It provides information about DDL operations in the TiDB cluster, such as the current status, DDL statements, start time, end time, database names, and table names.

```sql
USE information_schema;
DESC ddl_jobs;
```

```sql
+--------------+-------------+------+------+---------+-------+
| Field        | Type        | Null | Key  | Default | Extra |
+--------------+-------------+------+------+---------+-------+
| JOB_ID       | bigint(21)  | YES  |      | NULL    |       |
| DB_NAME      | varchar(64) | YES  |      | NULL    |       |
| TABLE_NAME   | varchar(64) | YES  |      | NULL    |       |
| JOB_TYPE     | varchar(64) | YES  |      | NULL    |       |
| SCHEMA_STATE | varchar(64) | YES  |      | NULL    |       |
| SCHEMA_ID    | bigint(21)  | YES  |      | NULL    |       |
| TABLE_ID     | bigint(21)  | YES  |      | NULL    |       |
| ROW_COUNT    | bigint(21)  | YES  |      | NULL    |       |
| START_TIME   | datetime    | YES  |      | NULL    |       |
| END_TIME     | datetime    | YES  |      | NULL    |       |
| STATE        | varchar(64) | YES  |      | NULL    |       |
| QUERY        | varchar(64) | YES  |      | NULL    |       |
+--------------+-------------+------+------+---------+-------+
12 rows in set (0.00 sec)
```

```sql
SELECT * FROM ddl_jobs LIMIT 3\G
```

```sql
*************************** 1. row ***************************
      JOB_ID: 44
     DB_NAME: mysql
  TABLE_NAME: opt_rule_blacklist
    JOB_TYPE: create table
SCHEMA_STATE: public
   SCHEMA_ID: 3
    TABLE_ID: 43
   ROW_COUNT: 0
  START_TIME: 2020-07-06 15:24:27
    END_TIME: 2020-07-06 15:24:27
       STATE: synced
       QUERY: CREATE TABLE IF NOT EXISTS mysql.opt_rule_blacklist (
        name char(100) NOT NULL
    );
*************************** 2. row ***************************
      JOB_ID: 42
     DB_NAME: mysql
  TABLE_NAME: expr_pushdown_blacklist
    JOB_TYPE: create table
SCHEMA_STATE: public
   SCHEMA_ID: 3
    TABLE_ID: 41
   ROW_COUNT: 0
  START_TIME: 2020-07-06 15:24:27
    END_TIME: 2020-07-06 15:24:27
       STATE: synced
       QUERY: CREATE TABLE IF NOT EXISTS mysql.expr_pushdown_blacklist (
        name char(100) NOT NULL,
        store_type char(100) NOT NULL DEFAULT 'tikv,tiflash,tidb',
        reason varchar(200)
    );
*************************** 3. row ***************************
      JOB_ID: 40
     DB_NAME: mysql
  TABLE_NAME: stats_top_n
    JOB_TYPE: create table
SCHEMA_STATE: public
   SCHEMA_ID: 3
    TABLE_ID: 39
   ROW_COUNT: 0
  START_TIME: 2020-07-06 15:24:26
    END_TIME: 2020-07-06 15:24:27
       STATE: synced
       QUERY: CREATE TABLE if not exists mysql.stats_top_n (
        table_id bigint(64) NOT NULL,
        is_index tinyint(2) NOT NULL,
        hist_id bigint(64) NOT NULL,
        value longblob,
        count bigint(64) UNSIGNED NOT NULL,
        index tbl(table_id, is_index, hist_id)
    );
3 rows in set (0.01 sec)
```
