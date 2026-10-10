# ALTER RESOURCE GROUP compatibility and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-resource-group.md`
- Source Title: `ALTER RESOURCE GROUP`
- Source Heading Path: `ALTER RESOURCE GROUP > MySQL compatibility | ALTER RESOURCE GROUP > See also`
- Source Line Ranges: `175-183`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `shared`
- Topic Tags: `mysql-compatibility`, `related-statements`, `resource-groups`, `request-unit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0528_cc48b03eff`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-resource-group.md#mysql-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a90f77401476c8f71f3d76f417bd47cf2f12207869fc1db209999ae61d71c528`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-resource-group.md

## Retrieval Guidance

- Use When: Use this chunk when you need the MySQL compatibility note for ALTER RESOURCE GROUP or links to related resource group statements and the Request Unit concept.
- Retrieval Keywords: MySQL compatibility, ALTER RESOURCE GROUP MySQL, acceptable parameters are different, not compatible, DROP RESOURCE GROUP, CREATE RESOURCE GROUP, Request Unit (RU)
- Follow-up Guidance: The source points to DROP RESOURCE GROUP, CREATE RESOURCE GROUP, and Request Unit (RU) as related documentation.
- Classification Note: This is reference content because it states the compatibility status with MySQL and lists related statements and concepts from the official documentation.

## Official Source Content

## MySQL compatibility

MySQL also supports [ALTER RESOURCE GROUP](https://dev.mysql.com/doc/refman/8.0/en/alter-resource-group.html). However, the acceptable parameters are different from that of TiDB so that they are not compatible.
## See also

* [DROP RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group)
* [CREATE RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group)
* [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru)
