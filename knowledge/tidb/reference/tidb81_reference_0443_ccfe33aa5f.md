# MySQL compatibility overview and unsupported features

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/mysql-compatibility.md`
- Source Title: `MySQL Compatibility`
- Source Heading Path: `MySQL Compatibility | MySQL Compatibility > Unsupported features | MySQL Compatibility > Differences from MySQL`
- Source Line Ranges: `5-77`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `dm`, `ticdc`, `ecosystem`, `cloud`, `sql`
- Topic Tags: `mysql-compatibility`, `unsupported-features`, `protocol-compatibility`, `replication`, `tooling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0443_ccfe33aa5f`
- Source ID: `tidb-docs-8.1:mysql-compatibility.md#mysql-compatibility`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43848da425fdb0fae1e68f4fd41b99aba901f5a25dfd677e2da99c9f5940dd30`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/mysql-compatibility#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/mysql-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB MySQL compatibility, unsupported MySQL features, or whether MySQL replication protocol and common MySQL tools apply to TiDB.
- Retrieval Keywords: MySQL Compatibility, Unsupported features, MySQL 5.7, MySQL 8.0, MySQL protocol, MySQL client, PHPMyAdmin, Navicat, MySQL Workbench, DBeaver, does not support the MySQL replication protocol, TiDB Data Migration, DM, TiCDC, MySQL sink, stored procedures and functions, Triggers, Events, User-defined functions, FULLTEXT, SPATIAL, GIS, GEOMETRY, optimizer trace, XML Functions, X-Protocol, column-level privileges, XA syntax, CREATE TABLE AS SELECT, CHECK TABLE, CHECKSUM TABLE, REPAIR TABLE, OPTIMIZE TABLE, HANDLER, CREATE TABLESPACE, Descending Index, SKIP LOCKED, Lateral derived tables, JOIN ON subquery
- Follow-up Guidance: The source points to dedicated pages for Security, Pessimistic Transaction Mode, DM, and TiCDC when the question is specifically about those compatibility areas.
- Classification Note: This is a reference chunk because it lists TiDB compatibility scope, unsupported MySQL features, and replication-related differences without presenting a procedural workflow.

## Official Source Content

# MySQL Compatibility

TiDB is highly compatible with the MySQL protocol and the common features and syntax of MySQL 5.7 and MySQL 8.0. The ecosystem tools for MySQL (PHPMyAdmin, Navicat, MySQL Workbench, DBeaver and [more](https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-support#gui)) and the MySQL client can be used for TiDB.

TiDB is highly compatible with the MySQL protocol and the common features and syntax of MySQL 5.7 and MySQL 8.0. The ecosystem tools for MySQL (PHPMyAdmin, Navicat, MySQL Workbench, DBeaver and [more](https://docs.pingcap.com/tidb/v7.2/dev-guide-third-party-support#gui)) and the MySQL client can be used for TiDB.

However, some features of MySQL are not supported in TiDB. This could be because there is now a better way to solve the problem (such as the use of JSON instead of XML functions) or a lack of current demand versus effort required (such as stored procedures and functions). Additionally, some features might be difficult to implement in a distributed system.

It's important to note that TiDB does not support the MySQL replication protocol. Instead, specific tools are provided to replicate data with MySQL:

- Replicate data from MySQL: [TiDB Data Migration (DM)](https://docs.pingcap.com/tidb/stable/dm/dm-overview) is a tool that supports full data migration and incremental data replication from MySQL or MariaDB into TiDB.
- Replicate data to MySQL: [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) is a tool for replicating the incremental data of TiDB by pulling TiKV change logs. TiCDC uses the [MySQL sink](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#replication-consistency) to replicate the incremental data of TiDB to MySQL.

> **Note:**
>
> This page describes general differences between MySQL and TiDB. For more information on compatibility with MySQL in the areas of security and pessimistic transaction mode, refer to the dedicated pages on [Security](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql) and [Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction#difference-with-mysql-innodb).

> **Note:**
>
> For information about transaction differences between MySQL and TiDB, see [Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction#difference-with-mysql-innodb).

You can try out TiDB features on [TiDB Playground](https://play.tidbcloud.com/?utm_source=docs&utm_medium=mysql_compatibility).
## Unsupported features

+ Stored procedures and functions
+ Triggers
+ Events
+ User-defined functions
+ `FULLTEXT` syntax and indexes [#1793](https://github.com/pingcap/tidb/issues/1793)
+ `SPATIAL` (also known as `GIS`/`GEOMETRY`) functions, data types and indexes [#6347](https://github.com/pingcap/tidb/issues/6347)
+ Character sets other than `ascii`, `latin1`, `binary`, `utf8`, `utf8mb4`, and `gbk`.
+ Optimizer trace
+ XML Functions
+ X-Protocol [#1109](https://github.com/pingcap/tidb/issues/1109)
+ Column-level privileges [#9766](https://github.com/pingcap/tidb/issues/9766)
+ `XA` syntax (TiDB uses a two-phase commit internally, but this is not exposed via an SQL interface)
+ `CREATE TABLE tblName AS SELECT stmt` syntax [#4754](https://github.com/pingcap/tidb/issues/4754)
+ `CHECK TABLE` syntax [#4673](https://github.com/pingcap/tidb/issues/4673)
+ `CHECKSUM TABLE` syntax [#1895](https://github.com/pingcap/tidb/issues/1895)
+ `REPAIR TABLE` syntax
+ `OPTIMIZE TABLE` syntax
+ `HANDLER` statement
+ `CREATE TABLESPACE` statement
+ "Session Tracker: Add GTIDs context to the OK packet"
+ Descending Index [#2519](https://github.com/pingcap/tidb/issues/2519)
+ `SKIP LOCKED` syntax [#18207](https://github.com/pingcap/tidb/issues/18207)
+ Lateral derived tables [#40328](https://github.com/pingcap/tidb/issues/40328)
+ JOIN ON subquery [#11414](https://github.com/pingcap/tidb/issues/11414)
## Differences from MySQL
