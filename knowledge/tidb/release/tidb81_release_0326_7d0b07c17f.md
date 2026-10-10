# SQL compatibility features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > New features > MySQL compatibility`
- Source Line Ranges: `163-176`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `alter table`, `savepoint`, `transaction`, `ddl`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0326_7d0b07c17f`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#mysql-compatibility`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `07e445df8220f0f87d2c4ce6b8eb4079fb0cb6b96973831c7ef2c4f85e121900`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.2.0 MySQL compatibility changes around multi-object ALTER TABLE support or transaction savepoints.
- Retrieval Keywords: MySQL compatibility, ALTER TABLE, modifying multiple columns or indexes in a single ALTER TABLE statement, single DDL changes, heterogeneous databases, ORM framework, SQL incompatibility, savepoint, setting savepoints in transactions, sql-statement-alter-table, sql-statement-savepoint
- Follow-up Guidance: The source points to the user documents for `ALTER TABLE` and `SAVEPOINT` SQL statements.
- Classification Note: This is classified under the SQL component because the content introduces SQL compatibility features for DDL statements and transaction savepoints.

## Official Source Content

### MySQL compatibility

* TiDB supports modifying multiple columns or indexes in a single `ALTER TABLE` statement

    Before v6.2.0, TiDB only supports single DDL changes, which leads to incompatible DDL operations when migrating heterogeneous databases, and it takes extra effort to modify a complex DDL statement into multiple TiDB-supported simple DDL statements. In addition, some users rely on the ORM framework to create assembly in SQL, thus causing SQL incompatibility. Since v6.2.0, TiDB supports modifying multiple schema objects in a single SQL statement, which is convenient for users to implement SQL and improves usability.

    [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table) [#14766](https://github.com/pingcap/tidb/issues/14766) @[tangenta](https://github.com/tangenta)

* Support setting savepoints in transactions

    A transaction is a logical collection of a series of consecutive operations with which the database guarantees ACID properties. In some complex application scenarios, you might need to manage many operations in a transaction, and sometimes you might need to roll back some operations in the transaction. "Savepoint" is a nameable mechanism for the internal implementation of transactions. With this mechanism, you can flexibly control the rollback points within a transaction, thereby managing the more complex transactions and having more freedom in designing diverse applications.

    [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-savepoint) [#6840](https://github.com/pingcap/tidb/issues/6840) @[crazycs520](https://github.com/crazycs520)
