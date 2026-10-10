# SHOW SCHEMAS alias behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-schemas.md`
- Source Title: `SHOW SCHEMAS | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW SCHEMAS`
- Source Line Ranges: `5-8`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show schemas`, `show databases`, `mysql compatibility`, `sql statement`, `database metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0673_9ea7101e5a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-schemas.md#show-schemas`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5913c007f5a1406b4e958e0c786a8da9dec7cb6b3438c0da971e26f4142572f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-schemas#show-schemas
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-schemas.md

## Retrieval Guidance

- Use When: Use this when looking up whether the SQL statement SHOW SCHEMAS differs from SHOW DATABASES or exists for MySQL compatibility.
- Retrieval Keywords: SHOW SCHEMAS, SHOW DATABASES, alias, MySQL compatibility, sql statement, database metadata
- Follow-up Guidance: The content points to SHOW DATABASES as the equivalent statement.
- Classification Note: This is reference content because it defines SHOW SCHEMAS as an alias of SHOW DATABASES and notes its compatibility purpose.

## Official Source Content

# SHOW SCHEMAS

This statement is an alias to [`SHOW DATABASES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-databases). It is included for compatibility with MySQL.
