# MySQL compatibility and related references for Split Region

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-split-region.md`
- Source Title: `Split Region`
- Source Heading Path: `Split Region > MySQL compatibility | Split Region > See also`
- Source Line Ranges: `390-397`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `mysql-compatibility`, `syntax-extension`, `related-statements`, `session-variables`, `region-splitting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0692_acb10b9d0e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-split-region.md#mysql-compatibility`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3abad6d1da19bf9a0a9b3b0e24cc3f11a972bfa882749d80773d105ba651d97e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-split-region.md

## Retrieval Guidance

- Use When: Use this chunk when identifying MySQL compatibility for the SPLIT REGION statement or locating the related TiDB references for region splitting behavior.
- Retrieval Keywords: Split Region, MySQL compatibility, TiDB extension to MySQL syntax, SHOW TABLE REGIONS, tidb_scatter_region, tidb_wait_split_region_finish, tidb_wait_split_region_timeout, session variables, region splitting
- Follow-up Guidance: The source points to SHOW TABLE REGIONS and the session variables tidb_scatter_region, tidb_wait_split_region_finish, and tidb_wait_split_region_timeout as related references.
- Classification Note: The content is classified as reference because it states compatibility information and lists related statements and session variables for Split Region.

## Official Source Content

## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [SHOW TABLE REGIONS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-regions)
* Session variables: [`tidb_scatter_region`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_scatter_region), [`tidb_wait_split_region_finish`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_wait_split_region_finish) and [`tidb_wait_split_region_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_wait_split_region_timeout).
