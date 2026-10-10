# CLUSTER_HARDWARE table schema and CPU query example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-cluster-hardware.md`
- Source Title: `CLUSTER_HARDWARE`
- Source Heading Path: `CLUSTER_HARDWARE`
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`, `tikv`, `shared`
- Topic Tags: `information_schema`, `system-table`, `cluster-metadata`, `hardware-inventory`, `cpu`, `memory`, `disk`, `network`, `schema`, `query-example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0377_416b7516d1`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-cluster-hardware.md#cluster-hardware`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `41e20b1be305a448bf653b7e4582803f336fd24ced007feed304591f80594c98`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-hardware#cluster-hardware
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-cluster-hardware.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the schema, field meanings, supported hardware types, or example SQL for the information_schema.CLUSTER_HARDWARE system table.
- Retrieval Keywords: CLUSTER_HARDWARE, information_schema.cluster_hardware, DESC cluster_hardware, TYPE, INSTANCE, DEVICE_TYPE, DEVICE_NAME, NAME, VALUE, cpu, memory, disk, net, information_schema.cluster_info, cpu-logical-cores, cpu-physical-cores, SELECT * FROM cluster_hardware WHERE device_type='cpu' AND device_name='cpu' AND name LIKE '%cores'
- Follow-up Guidance: The content includes an example query that filters CLUSTER_HARDWARE by device_type='cpu', device_name='cpu', and name LIKE '%cores' to return CPU logical and physical core counts for tidb, pd, and tikv instances.
- Classification Note: This is a self-managed SQL reference for the information_schema CLUSTER_HARDWARE table, including table schema, field descriptions, supported hardware inventory categories, and a CPU query example.

## Official Source Content

# CLUSTER_HARDWARE

The `CLUSTER_HARDWARE` hardware system table provides the hardware information of the server where each instance of the cluster is located.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

```sql
USE information_schema;
DESC cluster_hardware;
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
    * `memory`: The hardware name is memory.
    * `disk`: The disk name.
    * `net`: The network card name.
* `NAME`: The different information names of the hardware. For example, cpu has two information names: `cpu-logical-cores` and `cpu-physical-cores`, which respectively mean logical core numbers and physical core numbers.
* `VALUE`: The value of the corresponding hardware information, such as the disk volume and CPU core numbers.

The following example shows how to query the CPU information using the `CLUSTER_HARDWARE` table:

```sql
SELECT * FROM cluster_hardware WHERE device_type='cpu' AND device_name='cpu' AND name LIKE '%cores';
```

```sql
+------+-----------------+-------------+-------------+--------------------+-------+
| TYPE | INSTANCE        | DEVICE_TYPE | DEVICE_NAME | NAME               | VALUE |
+------+-----------------+-------------+-------------+--------------------+-------+
| tidb | 0.0.0.0:4000    | cpu         | cpu         | cpu-logical-cores  | 16    |
| tidb | 0.0.0.0:4000    | cpu         | cpu         | cpu-physical-cores | 8     |
| pd   | 127.0.0.1:2379  | cpu         | cpu         | cpu-logical-cores  | 16    |
| pd   | 127.0.0.1:2379  | cpu         | cpu         | cpu-physical-cores | 8     |
| tikv | 127.0.0.1:20165 | cpu         | cpu         | cpu-logical-cores  | 16    |
| tikv | 127.0.0.1:20165 | cpu         | cpu         | cpu-physical-cores | 8     |
+------+-----------------+-------------+-------------+--------------------+-------+
6 rows in set (0.03 sec)
```
