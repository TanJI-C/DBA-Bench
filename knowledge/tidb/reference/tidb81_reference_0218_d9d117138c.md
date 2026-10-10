# DM glossary: relay, replication, sharding, subtasks, and task terms

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-glossary.md`
- Source Title: `TiDB Data Migration Glossary`
- Source Heading Path: `TiDB Data Migration Glossary > R | TiDB Data Migration Glossary > R > Relay log | TiDB Data Migration Glossary > R > Relay processing unit | TiDB Data Migration Glossary > R > Replicate/replication | TiDB Data Migration Glossary > S | TiDB Data Migration Glossary > S > Safe mode | TiDB Data Migration Glossary > S > Shard DDL | TiDB Data Migration Glossary > S > Shard DDL lock | TiDB Data Migration Glossary > S > Shard group | TiDB Data Migration Glossary > S > Subtask | TiDB Data Migration Glossary > S > Subtask status | TiDB Data Migration Glossary > T | TiDB Data Migration Glossary > T > Table routing | TiDB Data Migration Glossary > T > Task | TiDB Data Migration Glossary > T > Task status`
- Source Line Ranges: `73-136`
- Source Scope: `shared`
- Primary Component: `dm`
- Related Components: `shared`
- Topic Tags: `glossary`, `relay-log`, `relay-unit`, `replication`, `safe-mode`, `shard-ddl`, `shard-ddl-lock`, `shard-group`, `subtask`, `subtask-status`, `table-routing`, `task`, `task-status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0218_d9d117138c`
- Source ID: `tidb-docs-8.1:dm/dm-glossary.md#r`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a4a068f50c27fc6f7a747c4036e58a5825c17a8262266d683fc4fe546b9c0e7b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-glossary#r
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-glossary.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs glossary definitions for relay logs, relay processing unit, incremental replication terminology, safe mode behavior, sharding terms, subtasks, table routing, task, or task status in TiDB Data Migration.
- Retrieval Keywords: Relay log, Relay processing unit, Replicate, replication, Safe mode, safe-mode, INSERT, REPLACE, UPDATE, DELETE, Shard DDL, sharding DDL, Shard DDL lock, sharding DDL lock, Shard group, sharding group, Subtask, Subtask status, New, Running, Paused, Stopped, Finished, Table routing, Task, start-task, Task status, mysqlbinlog
- Follow-up Guidance: It also links to related documents for relay log details, shard merge principles in the pessimistic mode, subtask status, and table routing.
- Classification Note: The supplied content is reference material because it provides glossary-style definitions and status terms for DM components, replication concepts, and task terminology.

## Official Source Content

## R
### Relay log

The relay log refers to the binlog files that DM-worker pulls from the upstream MySQL or MariaDB, and stores in the local disk. The format of the relay log is the standard binlog file, which can be parsed by tools such as [mysqlbinlog](https://dev.mysql.com/doc/refman/8.0/en/mysqlbinlog.html) of a compatible version. Its role is similar to [MySQL Relay Log](https://dev.mysql.com/doc/refman/8.0/en/replica-logs-relaylog.html) and [MariaDB Relay Log](https://mariadb.com/docs/server/server-management/server-monitoring-logs/binary-log/relay-log).

For more details such as the relay log's directory structure, initial migration rules, and data purge in TiDB DM, see [TiDB DM relay log](https://docs.pingcap.com/tidb/stable/dm/relay-log).
### Relay processing unit

The relay processing unit is the processing unit used in DM-worker to pull binlog files from the upstream and write data into relay logs. Each DM-worker instance has only one relay processing unit.
### Replicate/replication

The process of using the TiDB Data Migration tool to copy the **incremental data** of the upstream database to the downstream database.

In the case of clearly mentioning "incremental", use replicate/replication instead of migrate/migration.
## S
### Safe mode

Safe mode is the mode in which DML statements can be imported more than once when the primary key or unique index exists in the table schema. In this mode, some statements from the upstream are migrated to the downstream only after they are re-written. The `INSERT` statement is re-written as `REPLACE`; the `UPDATE` statement is re-written as `DELETE` and `REPLACE`.

This mode is enabled in any of the following situations:

- The safe mode remains enabled when the `safe-mode` parameter in the task configuration file is set to `true`.
- In shard merge scenarios, the safe mode remains enabled before DDL statements are replicated in all sharded tables.
- If the argument `--consistency none` is configured for the dump processing unit of a full migration task, it cannot be determined whether the binlog changes at the beginning of the export affect the exported data or not. Therefore, the safe mode remains enabled for the incremental replication of these binlog changes.
- If the task is paused by error and then resumed, the operations on some data might be executed twice.
### Shard DDL

The shard DDL is the DDL statement that is executed on the upstream sharded tables. It needs to be coordinated and migrated by TiDB DM in the process of merging the sharded tables. In the current documentation, the shard DDL is also referred to as the sharding DDL.
### Shard DDL lock

The shard DDL lock is the lock mechanism that coordinates the migration of shard DDL. Refer to [the implementation principles of merging and migrating data from sharded tables in the pessimistic mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#principles) for details. In the current documentation, the shard DDL lock is also referred to as the sharding DDL lock.
### Shard group

A shard group is all the upstream sharded tables to be merged and migrated to the same table in the downstream. Two-level shard groups are used for implementation of TiDB DM. Refer to [the implementation principles of merging and migrating data from sharded tables in the pessimistic mode](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#principles) for details. In the current documentation, the shard group is also referred to as the sharding group.
### Subtask

The subtask is a part of a data migration task that is running on each DM-worker instance. In different task configurations, a single data migration task might have one subtask or multiple subtasks.
### Subtask status

The subtask status is the status of a data migration subtask. The current status options include `New`, `Running`, `Paused`, `Stopped`, and `Finished`. Refer to [subtask status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status#subtask-status) for more details about the status of a data migration task or subtask.
## T
### Table routing

The table routing feature enables DM to migrate a certain table of the upstream MySQL or MariaDB instance to the specified table in the downstream, which can be used to merge and migrate sharded tables. Refer to [table routing](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing) for details.
### Task

The data migration task, which is started after you successfully execute a `start-task` command. In different task configurations, a single migration task can run on a single DM-worker instance or on multiple DM-worker instances at the same time.
### Task status

The task status refers to the status of a data migration task. The task status depends on the statuses of all its subtasks. Refer to [subtask status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status#subtask-status) for details.
