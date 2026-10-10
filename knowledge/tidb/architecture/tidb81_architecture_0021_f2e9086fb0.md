# DM overview, features, installation, and usage restrictions

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-overview.md`
- Source Title: `TiDB Data Migration Overview`
- Source Heading Path: `TiDB Data Migration Overview | TiDB Data Migration Overview > Basic features | TiDB Data Migration Overview > Quick installation | TiDB Data Migration Overview > Usage restrictions`
- Source Line Ranges: `5-68`
- Source Scope: `shared`
- Primary Component: `dm`
- Related Components: `tiup`, `tidb`
- Topic Tags: `overview`, `features`, `installation`, `compatibility`, `ddl`, `binlog`, `restrictions`, `migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0021_f2e9086fb0`
- Source ID: `tidb-docs-8.1:dm/dm-overview.md#tidb-data-migration-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `978ba42b04b2dba24124548427f443e9dff80fbf522ba7e689970aec73e1be9b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-overview#tidb-data-migration-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what DM supports, how to install dm and dmctl with TiUP, or the documented migration restrictions for DDL, binlog, character set, and upstream database versions.
- Retrieval Keywords: TiDB Data Migration Overview, DM basic features, full data migration, incremental data replication, MySQL-compatible databases, MySQL MariaDB Aurora MySQL, replicating DML and DDL events, MySQL binlog, migrating and merging MySQL shards, customizing replication rules, gh-ost, pt-osc, online-ddl, high availability, tiup install dm dmctl, curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh, MySQL version 5.6 ~ 8.0, MariaDB version >= 10.1.2, primary-secondary migration structure, MySQL version > 5.7.1, MariaDB version >= 10.1.3, DDL syntax compatibility, TiDB parser, MySQL Compatibility, Skip or replace abnormal SQL statements, dmctl, view-related DDL statements, charset=GBK, TiDB clusters earlier than v5.4.0, Transaction_payload_event, binary log transaction compression
- Follow-up Guidance: If DM encounters an incompatible DDL statement, the source says to manually handle it using dmctl by skipping the DDL statement or replacing it with specified DDL statements.
- Classification Note: This chunk is classified as architecture because it defines DM as an integrated data migration task management platform and summarizes its core features, installation entry point, and usage restrictions.

## Official Source Content

# TiDB Data Migration Overview

<!--
![star](https://img.shields.io/github/stars/pingcap/tiflow?style=for-the-badge&logo=github) ![license](https://img.shields.io/github/license/pingcap/tiflow?style=for-the-badge) ![forks](https://img.shields.io/github/forks/pingcap/tiflow?style=for-the-badge)
-->

[TiDB Data Migration](https://github.com/pingcap/tiflow/tree/release-8.1/dm) (DM) is an integrated data migration task management platform, which supports the full data migration and the incremental data replication from MySQL-compatible databases (such as MySQL, MariaDB, and Aurora MySQL) into TiDB. It can help to reduce the operation cost of data migration and simplify the troubleshooting process.
## Basic features

- **Compatibility with MySQL.** DM is compatible with the MySQL protocol and most of the features and syntax of MySQL 5.7 and MySQL 8.0.
- **Replicating DML and DDL events.** It supports parsing and replicating DML and DDL events in MySQL binlog.
- **Migrating and merging MySQL shards.** DM supports migrating and merging multiple MySQL database instances upstream to one TiDB database downstream. It supports customizing replication rules for different migration scenarios. It can automatically detect and handle DDL changes of upstream MySQL shards, which greatly reduces the operational cost.
- **Various types of filters.** You can predefine event types, regular expressions, and SQL expressions to filter out MySQL binlog events during the data migration process.
- **Centralized management.** DM supports thousands of nodes in a cluster. It can run and manage a large number of data migration tasks concurrently.
- **Optimization of the third-party Online Schema Change process.** In the MySQL ecosystem, tools such as gh-ost and pt-osc are widely used. DM optimizes its change process to avoid unnecessary migration of intermediate data. For details, see [online-ddl](https://docs.pingcap.com/tidb/stable/dm/dm-online-ddl-tool-support).
- **High availability.** DM supports data migration tasks to be scheduled freely on different nodes. The running tasks are not affected when a small number of nodes crash.
## Quick installation

Run the following command to install DM:

```shell
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
tiup install dm dmctl
```
## Usage restrictions

Before using the DM tool, note the following restrictions:

+ Database version requirements

    - MySQL version 5.6 ~ 8.0
    - MariaDB version >= 10.1.2 (experimental features)

    > **Note:**
    >
    > If there is a primary-secondary migration structure between the upstream MySQL/MariaDB servers, then choose the following version.
    >
    > - MySQL version > 5.7.1
    > - MariaDB version >= 10.1.3

+ DDL syntax compatibility

    - Currently, TiDB is not compatible with all the DDL statements that MySQL supports. Because DM uses the TiDB parser to process DDL statements, it only supports the DDL syntax supported by the TiDB parser. For details, see [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility#ddl-operations).

    - DM reports an error when it encounters an incompatible DDL statement. To solve this error, you need to manually handle it using dmctl, either skipping this DDL statement or replacing it with specified DDL statements. For details, see [Skip or replace abnormal SQL statements](https://docs.pingcap.com/tidb/stable/dm/dm-faq#how-to-handle-incompatible-ddl-statements).

    - DM does not replicate view-related DDL statements and DML statements to the downstream TiDB cluster. It is recommended that you create the view in the downstream TiDB cluster manually.

+ GBK character set compatibility

    - DM does not support migrating `charset=GBK` tables to TiDB clusters earlier than v5.4.0.

+ Binlog compatibility

    - DM does not support the MySQL 8.0 new feature binlog [Transaction_payload_event](https://dev.mysql.com/doc/refman/8.0/en/binary-log-transaction-compression.html). Using binlog Transaction_payload_event might result in data inconsistency between upstream and downstream.
