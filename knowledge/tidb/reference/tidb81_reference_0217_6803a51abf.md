# DM glossary: binlog, checkpoint, processing units, and migration terms

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-glossary.md`
- Source Title: `TiDB Data Migration Glossary`
- Source Heading Path: `TiDB Data Migration Glossary | TiDB Data Migration Glossary > B | TiDB Data Migration Glossary > B > Binlog | TiDB Data Migration Glossary > B > Binlog event | TiDB Data Migration Glossary > B > Binlog event filter | TiDB Data Migration Glossary > B > Binlog position | TiDB Data Migration Glossary > B > Binlog replication processing unit/sync unit | TiDB Data Migration Glossary > B > Block & allow table list | TiDB Data Migration Glossary > C | TiDB Data Migration Glossary > C > Checkpoint | TiDB Data Migration Glossary > D | TiDB Data Migration Glossary > D > Dump processing unit/dump unit | TiDB Data Migration Glossary > G | TiDB Data Migration Glossary > G > GTID | TiDB Data Migration Glossary > L | TiDB Data Migration Glossary > L > Load processing unit/load unit | TiDB Data Migration Glossary > M | TiDB Data Migration Glossary > M > Migrate/migration`
- Source Line Ranges: `5-72`
- Source Scope: `shared`
- Primary Component: `dm`
- Related Components: `shared`
- Topic Tags: `glossary`, `binlog`, `binlog-event`, `binlog-position`, `event-filter`, `block-allow-list`, `checkpoint`, `dump-unit`, `load-unit`, `sync-unit`, `gtid`, `migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0217_6803a51abf`
- Source ID: `tidb-docs-8.1:dm/dm-glossary.md#tidb-data-migration-glossary`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `175c037fac8627a9141e830530e46fa923dac8d7787903e11a0f818757cced31`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-glossary#tidb-data-migration-glossary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-glossary.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs definitions of TiDB Data Migration glossary terms related to binlog concepts, checkpoints, DM-worker processing units, GTID, block & allow table list, and migrate or migration wording.
- Retrieval Keywords: TiDB Data Migration Glossary, Binlog, Binlog event, Binlog event filter, Binlog position, Binlog replication processing unit, sync unit, Block & allow table list, Checkpoint, relay.meta, Dump processing unit, dump unit, GTID, Load processing unit, load unit, import processing unit, Migrate, migration
- Follow-up Guidance: It also points to related documentation and references such as dm-binlog-event-filter, dm-block-allow-table-lists, and external MySQL or MariaDB references for binary logs, binlog events, SHOW BINLOG EVENTS, and GTID.
- Classification Note: The supplied content is reference material because it defines glossary terms used in logs, monitoring, configurations, and documentation of TiDB Data Migration.

## Official Source Content

# TiDB Data Migration Glossary

This document lists the terms used in the logs, monitoring, configurations, and documentation of TiDB Data Migration (DM).
## B
### Binlog

In TiDB DM, binlogs refer to the binary log files generated in the TiDB database. It has the same indications as that in MySQL or MariaDB. Refer to [MySQL Binary Log](https://dev.mysql.com/doc/dev/mysql-server/latest/page_protocol_replication.html) and [MariaDB Binary Log](https://mariadb.com/docs/server/server-management/server-monitoring-logs/binary-log) for details.
### Binlog event

Binlog events are information about data modification made to a MySQL or MariaDB server instance. These binlog events are stored in the binlog files. Refer to [MySQL Binlog Event](https://dev.mysql.com/doc/dev/mysql-server/latest/page_protocol_replication_binlog_event.html) and [MariaDB Binlog Event](https://mariadb.com/docs/server/reference/clientserver-protocol/replication-protocol/1-binlog-events) for details.
### Binlog event filter

[Binlog event filter](https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter) is a more fine-grained filtering feature than the block and allow lists filtering rule. Refer to [binlog event filter](https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter) for details.
### Binlog position

The binlog position is the offset information of a binlog event in a binlog file. Refer to [MySQL `SHOW BINLOG EVENTS`](https://dev.mysql.com/doc/refman/8.0/en/show-binlog-events.html) and [MariaDB `SHOW BINLOG EVENTS`](https://mariadb.com/docs/server/reference/sql-statements/administrative-sql-statements/show/show-binlog-events) for details.
### Binlog replication processing unit/sync unit

Binlog replication processing unit is the processing unit used in DM-worker to read upstream binlogs or local relay logs, and to migrate these logs to the downstream. Each subtask corresponds to a binlog replication processing unit. In the current documentation, the binlog replication processing unit is also referred to as the sync processing unit.
### Block & allow table list

Block & allow table list is the feature that filters or only migrates all operations of some databases or some tables. Refer to [block & allow table lists](https://docs.pingcap.com/tidb/stable/dm/dm-block-allow-table-lists) for details. This feature is similar to [MySQL Replication Filtering](https://dev.mysql.com/doc/refman/8.0/en/replication-rules.html) and [MariaDB Replication Filters](https://mariadb.com/docs/server/ha-and-performance/standard-replication/replication-filters).
## C
### Checkpoint

A checkpoint indicates the position from which a full data import or an incremental replication task is paused and resumed, or is stopped and restarted.

- In a full import task, a checkpoint corresponds to the offset and other information of the successfully imported data in a file that is being imported. A checkpoint is updated synchronously with the data import task.
- In an incremental replication, a checkpoint corresponds to the [binlog position](#binlog-position) and other information of a [binlog event](#binlog-event) that is successfully parsed and migrated to the downstream. A checkpoint is updated after the DDL operation is successfully migrated or 30 seconds after the last update.

In addition, the `relay.meta` information corresponding to a [relay processing unit](#relay-processing-unit) works similarly to a checkpoint. A relay processing unit pulls the [binlog event](#binlog-event) from the upstream and writes this event to the [relay log](#relay-log), and writes the [binlog position](#binlog-position) or the GTID information corresponding to this event to `relay.meta`.
## D
### Dump processing unit/dump unit

The dump processing unit is the processing unit used in DM-worker to export all data from the upstream. Each subtask corresponds to a dump processing unit.
## G
### GTID

The GTID is the global transaction ID of MySQL or MariaDB. With this feature enabled, the GTID information is recorded in the binlog files. Multiple GTIDs form a GTID set. Refer to [MySQL GTID Format and Storage](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids-concepts.html) and [MariaDB Global Transaction ID](https://mariadb.com/docs/server/ha-and-performance/standard-replication/gtid) for details.
## L
### Load processing unit/load unit

The load processing unit is the processing unit used in DM-worker to import the fully exported data to the downstream. Each subtask corresponds to a load processing unit. In the current documentation, the load processing unit is also referred to as the import processing unit.
## M
### Migrate/migration

The process of using the TiDB Data Migration tool to copy the **full data** of the upstream database to the downstream database.

In the case of clearly mentioning "full", not explicitly mentioning "full or incremental", and clearly mentioning "full + incremental", use migrate/migration instead of replicate/replication.
