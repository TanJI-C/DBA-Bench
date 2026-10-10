# Custom online DDL temporary table matching rules

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-online-ddl.md`
- Source Title: `Migrate from Databases that Use GH-ost/PT-osc`
- Source Heading Path: `Migrate from Databases that Use GH-ost/PT-osc > Other online schema change tools`
- Source Line Ranges: `215-229`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `online-ddl`, `shadow-table-rules`, `trash-table-rules`, `regex`, `customization`, `temporary-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0086_5436ee934e`
- Source ID: `tidb-docs-8.1:dm/feature-online-ddl.md#other-online-schema-change-tools`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `30175abf7026bc00a559c6c256eeebb568efcbc8647ffd90861140989d04737e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl#other-online-schema-change-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-online-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how to configure DM to match customized ghost table and trash table names for modified online schema change tools.
- Retrieval Keywords: Other online schema change tools, online-ddl=true, shadow-table-rules, trash-table-rules, ghost table, trash table, regular expressions, customized pt-osc, ^_(.+)_(?:pcnew)$, ^_(.+)_(?:pcold)$
- Follow-up Guidance: The example shows setting online-ddl: true together with shadow-table-rules and trash-table-rules to match customized temporary table names.
- Classification Note: This chunk is classified as configuration because it provides DM task configuration fields and regex-based matching rules for customized online DDL temporary tables.

## Official Source Content

## Other online schema change tools

In some cases, you might need to change the default behavior of your online schema change tool. For example, you might use customized names for `ghost table` and `trash table`. In other cases, you might want to use other tools instead of gh-ost or pt-osc, with the same working principles and change processes.

To achieve such customized needs, you need to write regular expressions to match the names of the `ghost table` and `trash table`.

Starting from v2.0.7, DM experimentally supports the modified online schema change tools. By setting `online-ddl=true` in the DM task configuration and configuring `shadow-table-rules` and `trash-table-rules`, you can match the modified temporary tables with regular expressions.

For example, if you use a customized pt-osc with the name of `ghost table` being `_{origin_table}_pcnew` and the name of `trash table` being `_{origin_table}_pcold`, you can set the custom rules as follows:

```yaml
online-ddl: true
shadow-table-rules: ["^_(.+)_(?:pcnew)$"]
trash-table-rules: ["^_(.+)_(?:pcold)$"]
```
