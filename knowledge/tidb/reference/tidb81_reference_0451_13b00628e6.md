# MySQL compatibility and related references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/non-transactional-dml.md`
- Source Title: `Non-Transactional DML Statements`
- Source Heading Path: `Non-Transactional DML Statements > MySQL compatibility | Non-Transactional DML Statements > See also`
- Source Line Ranges: `423-430`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `mysql-compatibility`, `batch-syntax`, `system-variable`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0451_13b00628e6`
- Source ID: `tidb-docs-8.1:non-transactional-dml.md#mysql-compatibility`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6274bbd66fd37e3072a064fdab66dc5ede1b923b125ff798aa27413bbc33798`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/non-transactional-dml#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/non-transactional-dml.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether non-transactional statements are compatible with MySQL or when looking for related references to BATCH syntax and tidb_nontransactional_ignore_error.
- Retrieval Keywords: MySQL compatibility, not compatible with MySQL, TiDB-specific, BATCH syntax, tidb_nontransactional_ignore_error, See also, non-transactional statements
- Follow-up Guidance: The related references are the BATCH syntax and the tidb_nontransactional_ignore_error system variable.
- Classification Note: This is reference content because it states the MySQL compatibility status of non-transactional statements and provides links to related syntax and system variable documentation.

## Official Source Content

## MySQL compatibility

Non-transactional statements are TiDB-specific and are not compatible with MySQL.
## See also

* The [`BATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-batch) syntax
* [`tidb_nontransactional_ignore_error`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_nontransactional_ignore_error-new-in-v610)
