# TiDB basics, transaction behavior, and application interaction

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-overview.md`
- Source Title: `Developer Guide Overview`
- Source Heading Path: `Developer Guide Overview > TiDB basics | Developer Guide Overview > TiDB transaction mechanisms | Developer Guide Overview > The way applications interact with TiDB | Developer Guide Overview > Read more | Developer Guide Overview > Need help?`
- Source Line Ranges: `191-231`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `cloud`, `sql`, `shared`
- Topic Tags: `transactions`, `pessimistic-transactions`, `optimistic-transactions`, `begin`, `commit`, `rollback`, `mysql-protocol`, `orm-compatibility`, `developer-resources`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0123_c4bbb64888`
- Source ID: `tidb-docs-8.1:develop/dev-guide-overview.md#tidb-basics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e7f7fddebfd38d47ccef4b5fede8f45e99dc320dd37e14281bf3854fb291985`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview#tidb-basics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an overview of TiDB transaction mechanisms, MySQL protocol compatibility, ORM compatibility, and developer follow-up resources.
- Retrieval Keywords: TiDB basics, TiDB transaction mechanisms, optimistic transaction, pessimistic transaction, BEGIN, BEGIN PESSIMISTIC, BEGIN OPTIMISTIC, COMMIT, ROLLBACK, error-codes, atomicity, The way applications interact with TiDB, MySQL protocol, most MySQL syntax and features, MySQL connection libraries, ORMs that support MySQL, TiDB Transaction Overview, Transaction Notes for Application Developers, Choose Driver or ORM, Connect to TiDB, Database Schema Design, Write Data, Read Data, Optimize, Need help, Discord, Slack, support ticket
- Follow-up Guidance: The page links to follow-up resources including Quick Start, Choose Driver or ORM, Connect to TiDB, Database Schema Design, Write Data, Read Data, Transaction, Optimize, Example Applications, and community support channels.
- Classification Note: This is reference content because it summarizes TiDB transaction behavior and application interaction concepts, including SQL transaction statements and compatibility notes, with links for deeper reading.

## Official Source Content

## TiDB basics

Before you start working with TiDB, you need to understand some important mechanisms of how TiDB works:

- Read the [TiDB Transaction Overview](https://docs.pingcap.com/tidb/stable/transaction-overview) to understand how transactions work in TiDB, or check out the [Transaction Notes for Application Developers](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview) to learn about transaction knowledge required for application development.
- Understand [the way applications interact with TiDB](#the-way-applications-interact-with-tidb).
- To learn core components and concepts of building up the distributed database TiDB and TiDB Cloud, refer to the free online course [Introduction to TiDB](https://eng.edu.pingcap.com/catalog/info/id:203/?utm_source=docs-dev-guide).
## TiDB transaction mechanisms

TiDB supports distributed transactions and offers both [optimistic transaction](https://docs.pingcap.com/tidb/stable/optimistic-transaction) and [pessimistic transaction](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) modes. The current version of TiDB uses the **pessimistic transaction** mode by default, which allows you to transact with TiDB as you would with a traditional monolithic database (for example, MySQL).

You can start a transaction using [`BEGIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-begin), explicitly specify a **pessimistic transaction** using `BEGIN PESSIMISTIC`, or explicitly specify an **optimistic transaction** using `BEGIN OPTIMISTIC`. After that, you can either commit ([`COMMIT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-commit)) or roll back ([`ROLLBACK`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback)) the transaction.

TiDB guarantees atomicity for all statements between the start of `BEGIN` and the end of `COMMIT` or `ROLLBACK`, that is, all statements that are executed during this period either succeed or fail as a whole. This is used to ensure data consistency you need for application development.

If you are not sure what an **optimistic transaction** is, do **_NOT_** use it yet. Because **optimistic transactions** require that the application can correctly handle [all errors](https://docs.pingcap.com/tidb/stable/error-codes) returned by the `COMMIT` statement. If you are not sure how your application handles them, use a **pessimistic transaction** instead.
## The way applications interact with TiDB

TiDB is highly compatible with the MySQL protocol and supports [most MySQL syntax and features](https://docs.pingcap.com/tidb/stable/mysql-compatibility), so most MySQL connection libraries are compatible with TiDB. If your application framework or language does not have an official adaptation from PingCAP, it is recommended that you use MySQL's client libraries. More and more third-party libraries are actively supporting TiDB's different features.

Since TiDB is compatible with the MySQL protocol and MySQL syntax, most of the ORMs that support MySQL are also compatible with TiDB.
## Read more

- [Quick Start](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud)
- [Choose Driver or ORM](https://docs.pingcap.com/tidb/stable/develop/dev-guide-choose-driver-or-orm)
- [Connect to TiDB](https://docs.pingcap.com/tidb/stable/develop/dev-guide-connect-to-tidb)
- [Database Schema Design](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview)
- [Write Data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data)
- [Read Data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table)
- [Transaction](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview)
- [Optimize](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview)
- [Example Applications](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-spring-boot)
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).
