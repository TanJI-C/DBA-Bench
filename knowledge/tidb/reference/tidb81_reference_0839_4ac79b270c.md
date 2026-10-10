# Keywords, user-defined variables, and metadata lock

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/sql-concepts.md`
- Source Title: `SQL`
- Source Heading Path: `SQL > Keywords | SQL > User-defined variables | SQL > Metadata lock`
- Source Line Ranges: `70-94`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `keywords`, `reserved-keywords`, `identifiers`, `user-variables`, `session-scope`, `metadata-lock`, `online-schema-change`, `ddl-dml-coordination`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0839_4ac79b270c`
- Source ID: `tidb-docs-8.1:tidb-cloud/sql-concepts.md#keywords`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6eb47b0af35d3f2625f15ba2d3ae4b086b2892c94ad566a07750c476bd87380b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/sql-concepts#keywords
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/sql-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about reserved versus non-reserved SQL keywords, the syntax and scope of user-defined variables, or why TiDB returns the "Information schema is changed" error during online schema changes.
- Retrieval Keywords: Keywords, reserved keywords, non-reserved keywords, identifiers, User-defined variables, @var_name, session-specific, case-insensitive, Metadata lock, online schema changes, Information schema is changed, DML, DDL, table metadata
- Follow-up Guidance: The source points to separate pages for Keywords, User-Defined Variables, and Metadata Lock for more detailed behavior and rules.
- Classification Note: This is reference content because it defines keyword handling, user variable properties, and metadata lock behavior during DDL and DML coordination.

## Official Source Content

## Keywords

Keywords are words that have special meanings in SQL statements, such as `SELECT`, `UPDATE`, and `DELETE`.

- Some of them can be used as identifiers directly, which are called non-reserved keywords.

- Some of them require special treatment before being used as identifiers, which are called reserved keywords.

However, some non-reserved keywords might still require special treatment. It is recommended that you treat them as reserved keywords.

For more information, see [Keywords](https://docs.pingcap.com/tidb/stable/keywords).
## User-defined variables

TiDB lets you set and read the user-defined variables. The format of the user-defined variables is `@var_name`. The characters that compose `var_name` can be any characters that can compose an identifier, including the numbers `0-9`, the letters `a-zA-Z`, the underscore `_`, the dollar sign `$`, and the UTF-8 characters. In addition, it also includes the English period `.`. The user-defined variables are case-insensitive.

The user-defined variables are session-specific, which means a user variable defined by one client connection cannot be seen or used by other client connections.

For more information, see [User-Defined Variables](https://docs.pingcap.com/tidb/stable/user-defined-variables).
## Metadata lock

In TiDB, a metadata lock is a mechanism introduced to manage changes to table metadata during online schema changes. When a transaction begins, it locks onto a snapshot of the current metadata. If the metadata changes during the transaction, TiDB throws an "Information schema is changed" error, preventing the transaction from committing. The metadata lock coordinates Data Manipulation Language (DML) and Data Definition Language (DDL) operations by prioritizing DMLs, ensuring that in-progress DML transactions with outdated metadata commit before applying new DDL changes, thus minimizing errors and maintaining data consistency.

For more information, see [Metadata Lock](https://docs.pingcap.com/tidb/stable/metadata-lock).
