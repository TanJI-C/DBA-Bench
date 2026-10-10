# View RU consumption history by resource group

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > View RU consumption > View the RU consumption of resource groups`
- Source Line Ranges: `586-612`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `resource-control`, `resource-groups`, `request-unit`, `ru-consumption`, `system-table`, `historical-records`, `scheduled-task`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0113_cd09a5929c`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#view-the-ru-consumption-of-resource-groups`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6f04454bf25717204451eb4b397957e78dc11cd5bddda95a2d7586458ed62e10`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#view-the-ru-consumption-of-resource-groups
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official system table and query example for viewing historical RU consumption by resource group.
- Retrieval Keywords: mysql.request_unit_by_group, request_unit_by_group, RU consumption history, historical records of the RU consumption, resource group total_ru, SELECT * FROM request_unit_by_group LIMIT 5, start_time end_time resource_group total_ru, TiDB scheduled task, last three months, 92 days
- Follow-up Guidance: The source states that `mysql.request_unit_by_group` is populated automatically by a TiDB scheduled task at the end of each day, omits days with 0 RU consumption, and retains data for the last three months up to 92 days.
- Classification Note: This is classified as observability because the content describes a system table used to inspect historical RU consumption records for resource groups.

## Official Source Content

### View the RU consumption of resource groups

Starting from v7.6.0, TiDB provides the system table [`mysql.request_unit_by_group`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema#system-tables-related-to-resource-control) to store the historical records of the RU consumption of each resource group.

Example:

```sql
SELECT * FROM request_unit_by_group LIMIT 5;
```

```
+----------------------------+----------------------------+----------------+----------+
| start_time                 | end_time                   | resource_group | total_ru |
+----------------------------+----------------------------+----------------+----------+
| 2024-01-01 00:00:00.000000 | 2024-01-02 00:00:00.000000 | default        |   334147 |
| 2024-01-01 00:00:00.000000 | 2024-01-02 00:00:00.000000 | rg1            |     4172 |
| 2024-01-01 00:00:00.000000 | 2024-01-02 00:00:00.000000 | rg2            |    34028 |
| 2024-01-02 00:00:00.000000 | 2024-01-03 00:00:00.000000 | default        |   334088 |
| 2024-01-02 00:00:00.000000 | 2024-01-03 00:00:00.000000 | rg1            |     3850 |
+----------------------------+----------------------------+----------------+----------+
5 rows in set (0.01 sec)
```

> **Note:**
>
> The data of `mysql.request_unit_by_group` is automatically imported by a TiDB scheduled task at the end of each day. If the RU consumption of a resource group is 0 on a certain day, no record is generated. By default, this table stores data for the last three months (up to 92 days). Data that exceeds this period is automatically cleared.
