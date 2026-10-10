# Resource control FAQ and related SQL references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > FAQ | Use Resource Control to Achieve Resource Isolation > See also`
- Source Line Ranges: `641-660`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `resource-control`, `resource-groups`, `default-group`, `session-binding`, `statement-binding`, `ru-per-sec`, `priority`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0945_44e3f344da`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#faq`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5e4f725c151d3bd7c0fcd5adc60e2cabbd6c592a8cc12bd4fe49033c5d9a03e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need FAQ answers about default resource group behavior, binding users or sessions to resource groups, or how TiDB handles `RU_PER_SEC` allocation when total demand exceeds system capacity.
- Retrieval Keywords: default resource group unlimited resources, disable resource control, SET RESOURCE GROUP, RESOURCE_GROUP(), optimizer hint RESOURCE_GROUP, database user bound to one resource group, session runtime resource group, statement resource group, RU_PER_SEC, higher priority resource groups, allocates resources proportionally, CREATE RESOURCE GROUP, ALTER RESOURCE GROUP, DROP RESOURCE GROUP
- Follow-up Guidance: The source points to the related SQL references `CREATE RESOURCE GROUP`, `ALTER RESOURCE GROUP`, `DROP RESOURCE GROUP`, and the `SET RESOURCE GROUP` statement and `RESOURCE_GROUP()` optimizer hint mentioned in the FAQ.
- Classification Note: This is classified as reference because the content is an FAQ and pointer list for resource group semantics, SQL statements, and allocation behavior.

## Official Source Content

## FAQ

1. Do I have to disable resource control if I don't want to use resource groups?

    No. Users who do not specify any resource groups will be bound to the `default` resource group that has unlimited resources. When all users belong to the `default` resource group, the resource allocation method is the same as when the resource control is disabled.

2. Can a database user be bound to several resource groups?

    No. A database user can only be bound to one resource group. However, during the session runtime, you can use [`SET RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-resource-group) to set the resource group used by the current session. You can also use the optimizer hint [`RESOURCE_GROUP()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#resource_groupresource_group_name) to set the resource group for the running statement.

3. What happens when the total resource allocation (`RU_PER_SEC`) of all resource groups exceeds the system capacity?

    TiDB does not verify the capacity when you create a resource group. As long as the system has enough available resources, TiDB can meet the resource requirements of each resource group. When the system resources exceed the limit, TiDB prioritizes satisfying requests from resource groups with higher priority. If requests with the same priority cannot all be met, TiDB allocates resources proportionally according to the resource allocation (`RU_PER_SEC`).
## See also

* [CREATE RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group)
* [ALTER RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group)
* [DROP RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group)
* [RESOURCE GROUP RFC](https://github.com/pingcap/tidb/blob/release-8.1/docs/design/2022-11-25-global-resource-control.md)
