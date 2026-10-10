# RESOURCE_GROUPS table schema and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-resource-groups.md`
- Source Title: `RESOURCE_GROUPS`
- Source Heading Path: `RESOURCE_GROUPS | RESOURCE_GROUPS > Examples`
- Source Line Ranges: `5-88`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `cloud`
- Topic Tags: `information_schema`, `resource-groups`, `resource-control`, `request-unit`, `priority`, `burstable`, `schema`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0403_2d6835ffce`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-resource-groups.md#resource-groups`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `621f60989430446fefd1b2ec5f9c4ddd2c950a91a0464d4ec1933008aa8fba3d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-resource-groups#resource-groups
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-resource-groups.md

## Retrieval Guidance

- Use When: Use this chunk when you need the INFORMATION_SCHEMA `RESOURCE_GROUPS` table schema, example queries, or the meanings of `NAME`, `RU_PER_SEC`, `PRIORITY`, and `BURSTABLE` for resource groups.
- Retrieval Keywords: RESOURCE_GROUPS, information_schema.resource_groups, DESC resource_groups, SELECT * FROM information_schema.resource_groups, SHOW CREATE RESOURCE GROUP rg1, CREATE RESOURCE GROUP rg1 RU_PER_SEC=1000, NAME, RU_PER_SEC, PRIORITY, BURSTABLE, default resource group, UNLIMITED, MEDIUM, Request Unit, resource control, resource isolation
- Follow-up Guidance: The source also points to "Use Resource Control to Achieve Resource Isolation" for more information and notes that this table is not available on Starter and Essential clusters.
- Classification Note: This is reference content because it defines the `RESOURCE_GROUPS` table, shows its schema and example SQL output, and explains each column from the official documentation.

## Official Source Content

# RESOURCE_GROUPS

The `RESOURCE_GROUPS` table shows the information about all resource groups. For more information, see [Use Resource Control to Achieve Resource Isolation](https://docs.pingcap.com/tidb/stable/tidb-resource-control).

> **Note:**
>
> This table is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

```sql
USE information_schema;
DESC resource_groups;
```

```sql
+------------+-------------+------+------+---------+-------+
| Field      | Type        | Null | Key  | Default | Extra |
+------------+-------------+------+------+---------+-------+
| NAME       | varchar(32) | NO   |      | NULL    |       |
| RU_PER_SEC | bigint(21)  | YES  |      | NULL    |       |
| PRIORITY   | varchar(6)  | YES  |      | NULL    |       |
| BURSTABLE  | varchar(3)  | YES  |      | NULL    |       |
+------------+-------------+------+------+---------+-------+
3 rows in set (0.00 sec)
```
## Examples

```sql
SELECT * FROM information_schema.resource_groups; -- View all resource groups. TiDB has a `default` resource group.
```

```sql
+---------+------------+----------+-----------+
| NAME    | RU_PER_SEC | PRIORITY | BURSTABLE |
+---------+------------+----------+-----------+
| default | UNLIMITED  | MEDIUM   | YES       |
+---------+------------+----------+-----------+
```

```sql
CREATE RESOURCE GROUP rg1 RU_PER_SEC=1000; -- Create a resource group `rg1`
```

```sql
Query OK, 0 rows affected (0.34 sec)
```

```sql
SHOW CREATE RESOURCE GROUP rg1; -- Show the definition of the `rg1` resource group
```

```sql
+----------------+---------------------------------------------------------------+
| Resource_Group | Create Resource Group                                         |
+----------------+---------------------------------------------------------------+
| rg1            | CREATE RESOURCE GROUP `rg1` RU_PER_SEC=1000 PRIORITY="MEDIUM" |
+----------------+---------------------------------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT * FROM information_schema.resource_groups WHERE NAME = 'rg1'; -- View the resource groups `rg1`
```

```sql
+------+------------+----------+-----------+-------------+
| NAME | RU_PER_SEC | PRIORITY | BURSTABLE | QUERY_LIMIT |
+------+------------+----------+-----------+-------------+
| rg1  | 1000       | MEDIUM   | NO        | NULL        |
+------+------------+----------+-----------+-------------+
1 row in set (0.00 sec)
```

The descriptions of the columns in the `RESOURCE_GROUPS` table are as follows:

* `NAME`: the name of the resource group.
* `RU_PER_SEC`: the backfilling speed of the resource group. The unit is RU/second, in which RU means [Request Unit](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru).
* `PRIORITY`: the absolute priority of tasks to be processed on TiKV. Different resources are scheduled according to the `PRIORITY` setting. Tasks with high `PRIORITY` are scheduled first. For resource groups with the same `PRIORITY`, tasks will be scheduled proportionally according to the `RU_PER_SEC` configuration. If `PRIORITY` is not specified, the default priority is `MEDIUM`.
* `BURSTABLE`: whether to allow the resource group to overuse the available system resources.

> **Note:**
>
> TiDB automatically creates a `default` resource group during cluster initialization. For this resource group, the default value of `RU_PER_SEC` is `UNLIMITED` (equivalent to the maximum value of the `INT` type, that is, `2147483647`) and it is in `BURSTABLE` mode. All requests that are not bound to any resource group are automatically bound to this `default` resource group. When you create a new configuration for another resource group, it is recommended to modify the `default` resource group configuration as needed.
