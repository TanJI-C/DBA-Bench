# SELECT MySQL compatibility and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-select.md`
- Source Title: `SELECT | TiDB SQL Statement Reference`
- Source Heading Path: `SELECT > MySQL compatibility | SELECT > See also`
- Source Line Ranges: `200-212`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `mysql-compatibility`, `syntax-support`, `group-by-ordering`, `tablesample`, `related-statements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0632_309c3e0fe3`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-select.md#mysql-compatibility`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad120b3449b8899e04562d68c84ceb637b3219ba1a1c47b17cd53cfba3e66e1e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-select.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB SELECT statement compatibility differences from MySQL, especially unsupported INTO forms, GROUP BY ordering behavior, or TABLESAMPLE syntax support.
- Retrieval Keywords: SELECT ... INTO @variable, SELECT ... INTO DUMPFILE, SELECT .. GROUP BY expr, GROUP BY expr ORDER BY expr, MySQL 5.7, MySQL 8.0, SELECT ... TABLESAMPLE ..., TiDB extension, ISO/IEC 9075-2, SELECT MySQL compatibility, INSERT, DELETE, UPDATE, REPLACE
- Follow-up Guidance: The source also points to related SQL statements: INSERT, DELETE, UPDATE, and REPLACE.
- Classification Note: This is reference content because it lists specific SELECT compatibility behaviors and related statements from the official SQL statement documentation.

## Official Source Content

## MySQL compatibility

- The syntax `SELECT ... INTO @variable` is not supported.
- The syntax `SELECT ... INTO DUMPFILE` is not supported.
- The syntax `SELECT .. GROUP BY expr` does not imply `GROUP BY expr ORDER BY expr` as it does in MySQL 5.7. TiDB instead matches the behavior of MySQL 8.0 and does not imply a default order.
- The syntax `SELECT ... TABLESAMPLE ...` is a TiDB extension designed for compatibility with other database systems and the [ISO/IEC 9075-2](https://standards.iso.org/iso-iec/9075/-2/ed-6/en/) standard, but currently it is not supported by MySQL.
## See also

* [INSERT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert)
* [DELETE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete)
* [UPDATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update)
* [REPLACE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-replace)
