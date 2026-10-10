# RESOURCE_GROUP whole-query hint

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect in the whole query > RESOURCE_GROUP(resource_group_name)`
- Source Line Ranges: `850-859`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `optimizer-hints`, `resource-control`, `resource-group`, `statement-execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0460_03235f8fac`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#resource-group-resource-group-name`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ff1a1973ea2d455218b75644855e1af4dfb3155803fe698c2a43ae164dd6bb5a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#resource-group-resource-group-name
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how to apply a whole-query optimizer hint that temporarily runs the current statement in a specified resource group for Resource Control.
- Retrieval Keywords: RESOURCE_GROUP(resource_group_name), RESOURCE_GROUP(rg1), Resource Control, resource group, whole-query hint, temporarily executes the current statement, specified resource group, SELECT /*+ RESOURCE_GROUP(rg1) */ * FROM t limit 10;
- Follow-up Guidance: If the specified resource group does not exist, this hint will be ignored.
- Classification Note: This is a reference entry because it defines the RESOURCE_GROUP(resource_group_name) hint syntax, purpose, and example usage from the official content.

## Official Source Content

### RESOURCE_GROUP(resource_group_name)

`RESOURCE_GROUP(resource_group_name)` is used for [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) to isolate resources. This hint temporarily executes the current statement using the specified resource group. If the specified resource group does not exist, this hint will be ignored.

Example:

```sql
SELECT /*+ RESOURCE_GROUP(rg1) */ * FROM t limit 10;
```
