# Troubleshooting CSV import source file matching issues

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-csv-files.md`
- Source Title: `Import CSV Files from Cloud Storage into TiDB Cloud Dedicated`
- Source Heading Path: `Import CSV Files from Cloud Storage into TiDB Cloud Dedicated > Troubleshooting > Resolve warnings during data import | Import CSV Files from Cloud Storage into TiDB Cloud Dedicated > Troubleshooting > Zero rows in the imported tables`
- Source Line Ranges: `235-243`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `troubleshooting`, `import`, `csv`, `source-files`, `naming-conventions`, `advanced-settings`, `zero-rows`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0085_61895ec21e`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-csv-files.md#resolve-warnings-during-data-import`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `10fac8afe48d3427b950874642f401ff2f229413feae1f855df4d2a2d977c371`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files#resolve-warnings-during-data-import
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-csv-files.md

## Retrieval Guidance

- Use When: Use this when troubleshooting TiDB Cloud Dedicated CSV import cases where Start Import shows a warning like `can't find the corresponding source files` or the import completes but the imported tables have zero rows.
- Retrieval Keywords: can't find the corresponding source files, Resolve warnings during data import, Zero rows in the imported tables, Bucket URI, source file matching, Naming Conventions for Data Import, Advanced Settings, Completed, import those tables again
- Follow-up Guidance: After resolving the source file or matching issue, import the data again or import those tables again.
- Classification Note: This is classified as diagnosis content because it describes symptoms of source file matching problems during CSV import and identifies the documented resolution context.

## Official Source Content

### Resolve warnings during data import

After clicking **Start Import**, if you see a warning message such as `can't find the corresponding source files`, resolve this by providing the correct source file, renaming the existing one according to [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import), or using **Advanced Settings** to make changes.

After resolving these issues, you need to import the data again.
### Zero rows in the imported tables

After the import progress shows **Completed**, check the imported tables. If the number of rows is zero, it means no data files matched the Bucket URI that you entered. In this case, resolve this issue by providing the correct source file, renaming the existing one according to [Naming Conventions for Data Import](https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import), or using **Advanced Settings** to make changes. After that, import those tables again.
