# CLUSTER_LOAD table schema and CPU load query example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-cluster-load.md`
- Source Title: `CLUSTER_LOAD`
- Source Heading Path: `CLUSTER_LOAD`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `information_schema`, `cluster_load`, `schema`, `fields`, `cpu`, `load`, `query`, `instances`, `hardware-metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0379_be99496313`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-cluster-load.md#cluster-load`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ebdfae2ae65dc273c3c169e98a1530ed8dc149c57f555a1b358eb9759b11eac2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-load#cluster-load
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-cluster-load.md

## Retrieval Guidance

- Use When: Use this chunk when you need the schema, field meanings, or a sample query for the information_schema.CLUSTER_LOAD table that shows current hardware load for TiDB, PD, and TiKV instances.
- Retrieval Keywords: CLUSTER_LOAD, information_schema.cluster_load, DESC cluster_load, TYPE, INSTANCE, DEVICE_TYPE, DEVICE_NAME, NAME, VALUE, cluster_info, tidb, pd, tikv, cpu, memory, disk, net, load1, load5, load15, SELECT * FROM cluster_load WHERE device_type='cpu' AND device_name='cpu'
- Follow-up Guidance: It also points to the relationship of TYPE and INSTANCE with the information_schema.cluster_info table and notes that the table is only applicable to TiDB Self-Managed and not available on TiDB Cloud.
- Classification Note: This is reference content because it defines the CLUSTER_LOAD table schema, explains each field, and includes an example SQL query with result output.

## Official Source Content

# CLUSTER_LOAD

The `CLUSTER_LOAD` cluster load table provides the current load information of the server where each instance of the TiDB cluster is located.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

```sql
USE information_schema;
DESC cluster_load;
```

```sql
+-------------+--------------+------+------+---------+-------+
| Field       | Type         | Null | Key  | Default | Extra |
+-------------+--------------+------+------+---------+-------+
| TYPE        | varchar(64)  | YES  |      | NULL    |       |
| INSTANCE    | varchar(64)  | YES  |      | NULL    |       |
| DEVICE_TYPE | varchar(64)  | YES  |      | NULL    |       |
| DEVICE_NAME | varchar(64)  | YES  |      | NULL    |       |
| NAME        | varchar(256) | YES  |      | NULL    |       |
| VALUE       | varchar(128) | YES  |      | NULL    |       |
+-------------+--------------+------+------+---------+-------+
6 rows in set (0.00 sec)
```

Field description:

* `TYPE`: Corresponds to the `TYPE` field in the [`information_schema.cluster_info`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info) table. The optional values are `tidb`, `pd`, and `tikv`.
* `INSTANCE`: Corresponds to the `INSTANCE` field in the [`information_schema.cluster_info`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info) cluster information table.
* `DEVICE_TYPE`: Hardware type. Currently, you can query the `cpu`, `memory`, `disk`, and `net` types.
* `DEVICE_NAME`: Hardware name. The value of `DEVICE_NAME` varies with `DEVICE_TYPE`.
    * `cpu`: The hardware name is cpu.
    * `disk`: The disk name.
    * `net`: The network card name.
    * `memory`: The hardware name is memory.
* `NAME`: Different load types. For example, cpu has three load types: `load1`, `load5`, and `load15`, which respectively mean the average load of cpu within 1 minute, 5 minutes, and 15 minutes.
* `VALUE`: The value of the hardware load. For example, `1min`, `5min`, and `15min` respectively mean the average load of the hardware within 1 minute, 5 minutes, and 15 minutes.

The following example shows how to query the current load information of cpu using the `CLUSTER_LOAD` table:

```sql
SELECT * FROM cluster_load WHERE device_type='cpu' AND device_name='cpu';
```

```sql
+------+-----------------+-------------+-------------+--------+-------+
| TYPE | INSTANCE        | DEVICE_TYPE | DEVICE_NAME | NAME   | VALUE |
+------+-----------------+-------------+-------------+--------+-------+
| tidb | 0.0.0.0:4000    | cpu         | cpu         | load1  | 0.13  |
| tidb | 0.0.0.0:4000    | cpu         | cpu         | load5  | 0.25  |
| tidb | 0.0.0.0:4000    | cpu         | cpu         | load15 | 0.31  |
| pd   | 127.0.0.1:2379  | cpu         | cpu         | load1  | 0.13  |
| pd   | 127.0.0.1:2379  | cpu         | cpu         | load5  | 0.25  |
| pd   | 127.0.0.1:2379  | cpu         | cpu         | load15 | 0.31  |
| tikv | 127.0.0.1:20165 | cpu         | cpu         | load1  | 0.13  |
| tikv | 127.0.0.1:20165 | cpu         | cpu         | load5  | 0.25  |
| tikv | 127.0.0.1:20165 | cpu         | cpu         | load15 | 0.31  |
+------+-----------------+-------------+-------------+--------+-------+
9 rows in set (1.50 sec)
```
