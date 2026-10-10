# METRICS_TABLES system table definition and example query output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-metrics-tables.md`
- Source Title: `METRICS_TABLES`
- Source Heading Path: `METRICS_TABLES`
- Source Line Ranges: `5-79`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `metrics_schema`, `metrics_tables`, `promql`, `prometheus`, `system-table`, `schema-reference`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0398_7ffcf18253`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-metrics-tables.md#metrics-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dcd4dfb7f460aedf89eefe3373b0fd68fa4d55ee7a66dd6ab9fe319ccc8ace75`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-metrics-tables#metrics-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-metrics-tables.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks what INFORMATION_SCHEMA.METRICS_TABLES contains, how METRICS_SCHEMA views map to PromQL, or wants the table definition and example rows for metrics_tables.
- Retrieval Keywords: METRICS_TABLES, INFORMATION_SCHEMA, METRICS_SCHEMA, PromQL, Prometheus Query Language, DESC METRICS_TABLES, SELECT * FROM metrics_tables LIMIT 5, TABLE_NAME, PROMQL, LABELS, QUANTILE, COMMENT, abnormal_stores, etcd_disk_wal_fsync_rate, etcd_wal_fsync_duration
- Follow-up Guidance: The content includes example SQL statements `USE INFORMATION_SCHEMA;`, `DESC METRICS_TABLES;`, and `SELECT * FROM metrics_tables LIMIT 5\G` with sample output rows.
- Classification Note: This is reference content because it defines the METRICS_TABLES system table schema, explains each field, and shows example query output for the SQL component in TiDB Self-Managed.

## Official Source Content

# METRICS_TABLES

The `METRICS_TABLES` table provides the PromQL (Prometheus Query Language) definition for each of the views in the [`METRICS_SCHEMA`](https://docs.pingcap.com/tidb/stable/metrics-schema) database.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

```sql
USE INFORMATION_SCHEMA;
DESC METRICS_TABLES;
```

The output is as follows:

```sql
+------------+--------------+------+------+---------+-------+
| Field      | Type         | Null | Key  | Default | Extra |
+------------+--------------+------+------+---------+-------+
| TABLE_NAME | varchar(64)  | YES  |      | NULL    |       |
| PROMQL     | varchar(64)  | YES  |      | NULL    |       |
| LABELS     | varchar(64)  | YES  |      | NULL    |       |
| QUANTILE   | double       | YES  |      | NULL    |       |
| COMMENT    | varchar(256) | YES  |      | NULL    |       |
+------------+--------------+------+------+---------+-------+
```

Field description:

* `TABLE_NAME`: Corresponds to the table name in `METRICS_SCHEMA`.
* `PROMQL`: The working principle of the monitoring table is to map SQL statements to `PromQL` and convert Prometheus results into SQL query results. This field is the expression template of `PromQL`. When you query the data of the monitoring table, the query conditions are used to rewrite the variables in this template to generate the final query expression.
* `LABELS`: The label for the monitoring item. Each label corresponds to a column in the monitoring table. If the SQL statement contains the filter of the corresponding column, the corresponding `PromQL` changes accordingly.
* `QUANTILE`: The percentile. For monitoring data of the histogram type, a default percentile is specified. If the value of this field is `0`, it means that the monitoring item corresponding to the monitoring table is not a histogram.
* `COMMENT`: The comment about the monitoring table.

```sql
SELECT * FROM metrics_tables LIMIT 5\G
```

The output is as follows:

```sql
*************************** 1. row ***************************
TABLE_NAME: abnormal_stores
    PROMQL: sum(pd_cluster_status{ type=~"store_disconnected_count|store_unhealth_count|store_low_space_count|store_down_count|store_offline_count|store_tombstone_count"})
    LABELS: instance,type
  QUANTILE: 0
   COMMENT:
*************************** 2. row ***************************
TABLE_NAME: etcd_disk_wal_fsync_rate
    PROMQL: delta(etcd_disk_wal_fsync_duration_seconds_count{$LABEL_CONDITIONS}[$RANGE_DURATION])
    LABELS: instance
  QUANTILE: 0
   COMMENT: The rate of writing WAL into the persistent storage
*************************** 3. row ***************************
TABLE_NAME: etcd_wal_fsync_duration
    PROMQL: histogram_quantile($QUANTILE, sum(rate(etcd_disk_wal_fsync_duration_seconds_bucket{$LABEL_CONDITIONS}[$RANGE_DURATION])) by (le,instance))
    LABELS: instance
  QUANTILE: 0.99
   COMMENT: The quantile time consumed of writing WAL into the persistent storage
*************************** 4. row ***************************
TABLE_NAME: etcd_wal_fsync_total_count
    PROMQL: sum(increase(etcd_disk_wal_fsync_duration_seconds_count{$LABEL_CONDITIONS}[$RANGE_DURATION])) by (instance)
    LABELS: instance
  QUANTILE: 0
   COMMENT: The total count of writing WAL into the persistent storage
*************************** 5. row ***************************
TABLE_NAME: etcd_wal_fsync_total_time
    PROMQL: sum(increase(etcd_disk_wal_fsync_duration_seconds_sum{$LABEL_CONDITIONS}[$RANGE_DURATION])) by (instance)
    LABELS: instance
  QUANTILE: 0
   COMMENT: The total time of writing WAL into the persistent storage
5 rows in set (0.00 sec)
```
