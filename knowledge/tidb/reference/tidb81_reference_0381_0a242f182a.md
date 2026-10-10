# CLUSTER_SYSTEMINFO table schema and query example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-cluster-systeminfo.md`
- Source Title: `CLUSTER_SYSTEMINFO`
- Source Heading Path: `CLUSTER_SYSTEMINFO`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`, `tikv`, `shared`
- Topic Tags: `information_schema`, `systeminfo`, `cluster`, `sysctl`, `schema`, `field-descriptions`, `kernel-parameters`, `query-example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0381_0a242f182a`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-cluster-systeminfo.md#cluster-systeminfo`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `61816cbe22873f9bc8715f5a96ad4249b22d60b16853bebabb7109cf2c25017f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-systeminfo#cluster-systeminfo
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-cluster-systeminfo.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the schema, field meanings, or example query for the information_schema.CLUSTER_SYSTEMINFO table that returns cluster server sysctl kernel configuration information.
- Retrieval Keywords: CLUSTER_SYSTEMINFO, information_schema.cluster_systeminfo, DESC cluster_systeminfo, TYPE, INSTANCE, SYSTEM_TYPE, SYSTEM_NAME, NAME, VALUE, sysctl, kernel parameter table, kernel configuration information, cluster_info, tidb, pd, tikv, SELECT * FROM cluster_systeminfo WHERE name LIKE '%kernel.osrelease%', kernel.osrelease
- Follow-up Guidance: It includes a query example that uses SELECT * FROM cluster_systeminfo WHERE name LIKE '%kernel.osrelease%' to show the kernel version of all servers in the cluster.
- Classification Note: This is reference content because it defines the CLUSTER_SYSTEMINFO table schema, explains each field, and shows an example query and result.

## Official Source Content

# CLUSTER_SYSTEMINFO

You can use the `CLUSTER_SYSTEMINFO` kernel parameter table to query the kernel configuration information of the server where all instances of the cluster are located. Currently, you can query the information of the `sysctl` system.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

```sql
USE information_schema;
DESC cluster_systeminfo;
```

```sql
+-------------+--------------+------+------+---------+-------+
| Field       | Type         | Null | Key  | Default | Extra |
+-------------+--------------+------+------+---------+-------+
| TYPE        | varchar(64)  | YES  |      | NULL    |       |
| INSTANCE    | varchar(64)  | YES  |      | NULL    |       |
| SYSTEM_TYPE | varchar(64)  | YES  |      | NULL    |       |
| SYSTEM_NAME | varchar(64)  | YES  |      | NULL    |       |
| NAME        | varchar(256) | YES  |      | NULL    |       |
| VALUE       | varchar(128) | YES  |      | NULL    |       |
+-------------+--------------+------+------+---------+-------+
6 rows in set (0.00 sec)
```

Field description:

* `TYPE`: Corresponds to the `TYPE` field in the [`information_schema.cluster_info`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info) table. The optional values are `tidb`, `pd`, and `tikv`.
* `INSTANCE`: Corresponds to the `INSTANCE` field in the [`information_schema.cluster_info`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info) cluster information table.
* `SYSTEM_TYPE`: The system type. Currently, you can query the `system` system type.
* `SYSTEM_NAME`: The system name. Currently, you can query the `sysctl` system name.
* `NAME`: The configuration name corresponding to `sysctl`.
* `VALUE`: The value of the configuration item corresponding to `sysctl`.

The following example shows how to query the kernel version of all servers in the cluster using the `CLUSTER_SYSTEMINFO` system information table.

```sql
SELECT * FROM cluster_systeminfo WHERE name LIKE '%kernel.osrelease%'
```

```sql
+------+-------------------+-------------+-------------+------------------+----------------------------+
| TYPE | INSTANCE          | SYSTEM_TYPE | SYSTEM_NAME | NAME             | VALUE                      |
+------+-------------------+-------------+-------------+------------------+----------------------------+
| tidb | 172.16.5.40:4008  | system      | sysctl      | kernel.osrelease | 3.10.0-862.14.4.el7.x86_64 |
| pd   | 172.16.5.40:20379 | system      | sysctl      | kernel.osrelease | 3.10.0-862.14.4.el7.x86_64 |
| tikv | 172.16.5.40:21150 | system      | sysctl      | kernel.osrelease | 3.10.0-862.14.4.el7.x86_64 |
+------+-------------------+-------------+-------------+------------------+----------------------------+
```
