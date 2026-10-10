# Failed DDL handling restrictions, supported scenarios, and dmctl commands

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/handle-failed-ddl-statements.md`
- Source Title: `Handle Failed DDL Statements in TiDB Data Migration`
- Source Heading Path: `Handle Failed DDL Statements in TiDB Data Migration | Handle Failed DDL Statements in TiDB Data Migration > Restrictions | Handle Failed DDL Statements in TiDB Data Migration > Supported scenarios | Handle Failed DDL Statements in TiDB Data Migration > Commands | Handle Failed DDL Statements in TiDB Data Migration > Commands > query-status | Handle Failed DDL Statements in TiDB Data Migration > Commands > binlog | Handle Failed DDL Statements in TiDB Data Migration > Usage examples | Handle Failed DDL Statements in TiDB Data Migration > Usage examples > Skip DDL if the migration gets interrupted`
- Source Line Ranges: `5-114`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `failed-ddl`, `migration-interruption`, `binlog-operations`, `query-status`, `skip`, `replace`, `inject`, `revert`, `restrictions`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0110_53d792baf4`
- Source ID: `tidb-docs-8.1:dm/handle-failed-ddl-statements.md#handle-failed-ddl-statements-in-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6dd93302f08b345c2ccc3cf0e795faf21340d180b9d18ae574babce25eb3e52c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements#handle-failed-ddl-statements-in-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/handle-failed-ddl-statements.md

## Retrieval Guidance

- Use When: Use this chunk when handling a DM migration interruption caused by an upstream DDL unsupported by TiDB and you need the restrictions, supported scenarios, or dmctl commands such as query-status and binlog.
- Retrieval Keywords: TiDB Data Migration failed DDL, DM unsupported DDL migration interrupted, dmctl query-status, dmctl binlog, binlog skip <task-name>, binlog replace <task-name>, binlog inject <task-name>, binlog revert, binlog list, --binlog-pos, mysql-bin|000001.000003:3270, startLocation position, SHOW BINLOG EVENTS, handle-error command, DM v6.0 and later
- Follow-up Guidance: The source says the binlog position can be obtained from position in startLocation returned by query-status after an error, or from SHOW BINLOG EVENTS in the upstream MySQL instance before an error.
- Classification Note: This is classified as an operation chunk because the content explains when failed DDL can be manually handled in DM and documents the dmctl query-status and binlog commands, flags, and restrictions.

## Official Source Content

# Handle Failed DDL Statements in TiDB Data Migration

This document introduces how to handle failed DDL statements when you're using the TiDB Data Migration (DM) tool to migrate data.

Currently, TiDB is not completely compatible with all MySQL syntax (see [the DDL statements supported by TiDB](https://docs.pingcap.com/tidb/stable/mysql-compatibility#ddl-operations)). Therefore, when DM is migrating data from MySQL to TiDB and TiDB does not support the corresponding DDL statement, an error might occur and break the migration process. In this case, you can use the `binlog` command of DM to resume the migration.
## Restrictions

Do not use this command in the following situations:

* It is unacceptable in the actual production environment that the failed DDL statement is skipped in the downstream TiDB.
* The failed DDL statement cannot be replaced with other DDL statements.
* Other DDL statements must not be injected into the downstream TiDB.

For example, `DROP PRIMARY KEY`. In this scenario, you can only create a new table in the downstream with the new table schema (after executing the DDL statement), and re-import all the data into this new table.
## Supported scenarios

During the migration, the DDL statement unsupported by TiDB is executed in the upstream and migrated to the downstream, and as a result, the migration task gets interrupted.

- If it is acceptable that this DDL statement is skipped in the downstream TiDB, then you can use `binlog skip <task-name>` to skip migrating this DDL statement and resume the migration.
- If it is acceptable that this DDL statement is replaced with other DDL statements, then you can use `binlog replace <task-name>` to replace this DDL statement and resume the migration.
- If it is acceptable that other DDL statements are injected to the downstream TiDB, then you can use `binlog inject <task-name>` to inject other DDL statements and resume the migration.
## Commands

When you use dmctl to manually handle the failed DDL statements, the commonly used commands include `query-status` and `binlog`.
### query-status

The `query-status` command is used to query the current status of items such as the subtask and the relay unit in each MySQL instance. For details, see [query status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status).
### binlog

The `binlog` command is used to manage and show binlog operations. This command is only supported in DM v6.0 and later versions. For earlier versions, use the `handle-error` command.

The usage of `binlog` is as follows:

```bash
binlog -h
```

```
manage or show binlog operations

Usage:
  dmctl binlog [command]

Available Commands:
  inject      inject the current error event or a specific binlog position (binlog-pos) with some ddls
  list        list error handle command at binlog position (binlog-pos) or after binlog position (binlog-pos)
  replace     replace the current error event or a specific binlog position (binlog-pos) with some ddls
  revert      revert the current binlog operation or a specific binlog position (binlog-pos) operation
  skip        skip the current error event or a specific binlog position (binlog-pos) event

Flags:
  -b, --binlog-pos string   position used to match binlog event if matched the binlog operation will be applied. The format like "mysql-bin|000001.000003:3270"
  -h, --help                help for binlog

Global Flags:
  -s, --source strings   MySQL Source ID.

Use "dmctl binlog [command] --help" for more information about a command.
```

`binlog` supports the following sub-commands:

* `inject`: injects DDL statements into the current error event or a specific binlog position. To specify the binlog position, refer to `-b, --binlog-pos`.
* `list`: lists all valid `inject`, `skip`, and `replace` operations at the current binlog position or after the current binlog position. To specify the binlog position, refer to `-b, --binlog-pos`.
* `replace`: replaces the DDL statement at a specific binlog position with another DDL statement. To specify the binlog position, refer to `-b, --binlog-pos`.
* `revert`: reverts the `inject`, `skip` or `replace` operation at a specified binlog operation, only if the previous operation does not take effect. To specify the binlog position, refer to `-b, --binlog-pos`.
* `skip`: skips the DDL statement at a specific binlog position. To specify the binlog position, refer to `-b, --binlog-pos`.

`binlog` supports the following flags:

+ `-b, --binlog-pos`:
    - Type: string.
    - Specifies a binlog position. When the position of the binlog event matches `binlog-pos`, the operation is executed. If it is not specified, DM automatically sets `binlog-pos` to the currently failed DDL statement.
    - Format: `binlog-filename:binlog-pos`, for example, `mysql-bin|000001.000003:3270`.
    - After the migration returns an error, the binlog position can be obtained from `position` in `startLocation` returned by `query-status`. Before the migration returns an error, the binlog position can be obtained by using [`SHOW BINLOG EVENTS`](https://dev.mysql.com/doc/refman/8.0/en/show-binlog-events.html) in the upstream MySQL instance.

+ `-s, --source`:
    - Type: string.
    - Specifies the MySQL instance in which the preset operation is to be executed.
## Usage examples
### Skip DDL if the migration gets interrupted

If you need to skip the DDL statement when the migration gets interrupted, run the `binlog skip` command:

```bash
binlog skip -h
```

```
skip the current error event or a specific binlog position (binlog-pos) event

Usage:
  dmctl binlog skip <task-name> [flags]

Flags:
  -h, --help   help for skip

Global Flags:
  -b, --binlog-pos string   position used to match binlog event if matched the binlog operation will be applied. The format like "mysql-bin|000001.000003:3270"
  -s, --source strings      MySQL Source ID.
```
