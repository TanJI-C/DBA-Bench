# Post-migration users, application testing, and data validation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-mariadb.md`
- Source Title: `Migrate Data from MariaDB to TiDB`
- Source Heading Path: `Migrate Data from MariaDB to TiDB > Export users and grants | Migrate Data from MariaDB to TiDB > Test your application | Migrate Data from MariaDB to TiDB > Validate data`
- Source Line Ranges: `333-345`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ecosystem`, `tidb`
- Topic Tags: `users`, `grants`, `application-testing`, `compatibility`, `performance-testing`, `log-monitoring`, `data-validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0162_cd12d50ac4`
- Source ID: `tidb-docs-8.1:migrate-from-mariadb.md#export-users-and-grants`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e6d638f25af7e3216836fa9d9ab0d8743ec72000cb9eea1b460fe07d501784b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-mariadb#export-users-and-grants
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-mariadb.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to export MariaDB users and grants, test application compatibility and performance on TiDB, and validate migrated data consistency.
- Retrieval Keywords: Export users and grants, pt-show-grants, Percona Toolkit, Test your application, sysbench, temporary copy of your data, application compatibility, performance with TiDB, log files, database driver, MySQL Connector/J, JMeter, Validate data, sync-diff-inspector, MariaDB and TiDB are identical
- Follow-up Guidance: The source mentions testing a copy of the application against a TiDB cluster, monitoring application and TiDB log files for warnings, and using sync-diff-inspector to compare MariaDB and TiDB data.
- Classification Note: This is classified as an operation-oriented shared topic because the content covers post-migration user export, application testing, and data validation rather than a single TiDB component workflow.

## Official Source Content

## Export users and grants

You can use [`pt-show-grants`](https://docs.percona.com/percona-toolkit/pt-show-grants.html). It is part of the Percona Toolkit to export users and grants from MariaDB and load these into TiDB.
## Test your application

While it is possible to use generic tools such as `sysbench` for testing, it is highly recommended to test some specific features of your application. For example, run a copy of your application against a TiDB cluster with a temporary copy of your data.

Such a test makes sure your application compatibility and performance with TiDB is verified. You need to monitor the log files of your application and TiDB to see if there are any warnings that might need to be addressed. Make sure that the database driver that your application is using (for example MySQL Connector/J for Java based applications) is tested. You might want to use an application such as JMeter to put some load on your application if needed.
## Validate data

You can use [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) to validate if the data in MariaDB and TiDB are identical.
