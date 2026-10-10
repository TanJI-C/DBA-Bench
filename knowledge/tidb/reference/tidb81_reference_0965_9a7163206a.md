# Supported connectors and TiProxy resources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-overview.md`
- Source Title: `TiProxy Overview`
- Source Heading Path: `TiProxy Overview > Supported connectors | TiProxy Overview > TiProxy resources`
- Source Line Ranges: `186-209`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `connectors`, `authentication-plugins`, `version-support`, `resources`, `release-notes`, `issues`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0965_9a7163206a`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-overview.md#supported-connectors`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `529084c6bae52cc227fdebcc8a917a056b0664b0ed225bbaba31bb7dee8f8f84`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview#supported-connectors
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks which client connectors and minimum versions TiProxy supports, or where to find TiProxy release notes and issue tracking resources.
- Retrieval Keywords: Supported connectors, authentication plugins, pluggable authentication, MySQL Connector/J 5.1.19, libmysqlclient 5.5.7, Go SQL Driver 1.4.0, MySQL Connector/Node.js 1.0.2, mysqljs/mysql 2.15.0, node-mysql2 1.0.0-rc-6, mysqlnd 5.4, MySQL Connector/Python 1.0.7, PyMySQL 0.7, MySQL/Ruby uses libmysqlclient, TiProxy Release Notes, TiProxy Issues
- Follow-up Guidance: The content notes that some connectors use a common library and gives MySQL/Ruby using `libmysqlclient` as an example for version requirements.
- Classification Note: This is reference content because it provides a compatibility table of supported connectors with minimum versions and links to official TiProxy resources.

## Official Source Content

## Supported connectors

TiProxy requires that the connector used by the client supports [authentication plugins](https://dev.mysql.com/doc/refman/8.0/en/pluggable-authentication.html). Otherwise, the connection might fail.

The following table lists some supported connectors:

| Language   | Connector              | The minimum supported version |
|------------|------------------------|------------------------------|
| Java       | MySQL Connector/J      | 5.1.19                       |
| C          | libmysqlclient         | 5.5.7                        |
| Go         | Go SQL Driver          | 1.4.0                        |
| JavaScript | MySQL Connector/Node.js | 1.0.2                        |
| JavaScript | mysqljs/mysql          | 2.15.0                       |
| JavaScript | node-mysql2            | 1.0.0-rc-6                   |
| PHP        | mysqlnd                | 5.4                          |
| Python     | MySQL Connector/Python | 1.0.7                        |
| Python     | PyMySQL                | 0.7                          |

Note that some connectors call the common library to connect to the database, and these connectors are not listed in the table. You can refer to the above table for the required version of the corresponding library. For example, MySQL/Ruby uses libmysqlclient to connect to the database, so it requires that the libmysqlclient used by MySQL/Ruby is version 5.5.7 or later.
## TiProxy resources

- [TiProxy Release Notes](https://github.com/pingcap/tiproxy/releases)
- [TiProxy Issues](https://github.com/pingcap/tiproxy/issues): Lists TiProxy GitHub issues
