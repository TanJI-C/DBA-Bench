# DM-worker architecture and required privileges

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-worker-intro.md`
- Source Title: `DM-worker Introduction`
- Source Heading Path: `DM-worker Introduction | DM-worker Introduction > DM-worker processing unit | DM-worker Introduction > DM-worker processing unit > Relay log | DM-worker Introduction > DM-worker processing unit > Dump processing unit | DM-worker Introduction > DM-worker processing unit > Load processing unit | DM-worker Introduction > DM-worker processing unit > Binlog replication/sync processing unit | DM-worker Introduction > Privileges required by DM-worker | DM-worker Introduction > Privileges required by DM-worker > Upstream database user privileges | DM-worker Introduction > Privileges required by DM-worker > Downstream database user privileges | DM-worker Introduction > Privileges required by DM-worker > Minimal privilege required by each processing unit`
- Source Line Ranges: `5-96`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `dm-worker`, `migration`, `processing-units`, `relay-log`, `dump`, `load`, `binlog-replication`, `privileges`, `grant`, `upstream`, `downstream`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0233_d23ca8f38f`
- Source ID: `tidb-docs-8.1:dm/dm-worker-intro.md#dm-worker-introduction`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4b546559a582611122abd5a1b206b9998095454c714aef50ddbedb25a0304cc5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-worker-intro#dm-worker-introduction
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-worker-intro.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about DM-worker architecture, processing units, or the upstream and downstream privileges required for migrating data from MySQL/MariaDB to TiDB.
- Retrieval Keywords: DM-worker Introduction, DM-worker processing unit, relay log, dump processing unit, load processing unit, binlog replication/sync processing unit, Privileges required by DM-worker, Upstream database user privileges, Downstream database user privileges, Minimal privilege required by each processing unit, REPLICATION SLAVE, REPLICATION CLIENT, RELOAD, SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, GRANT RELOAD,REPLICATION SLAVE, REPLICATION CLIENT ON *.*, GRANT SELECT ON db1.*, GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,ALTER,INDEX ON db.table, GRANT ALL ON dm_meta.*, dm_meta
- Follow-up Guidance: The source also lists the minimal upstream, downstream, and system privileges for each processing unit: Relay log, Dump, Load, and Binlog replication.
- Classification Note: This is reference content because it defines what DM-worker does, names its processing units, and enumerates the exact privilege requirements and GRANT statements from the official documentation.

## Official Source Content

# DM-worker Introduction

DM-worker is a tool used to migrate data from MySQL/MariaDB to TiDB.

It has the following features:

- Acts as a secondary database of any MySQL or MariaDB instance
- Reads the binlog events from MySQL/MariaDB and persists them to the local storage
- A single DM-worker supports migrating the data of one MySQL/MariaDB instance to multiple TiDB instances
- Multiple DM-workers support migrating the data of multiple MySQL/MariaDB instances to one TiDB instance
## DM-worker processing unit

A DM-worker task contains multiple logic units, including relay log, the dump processing unit, the load processing unit, and binlog replication.
### Relay log

The relay log persistently stores the binlog data from the upstream MySQL/MariaDB and provides the feature of accessing binlog events for the binlog replication.

Its rationale and features are similar to the relay log of MySQL. For details, see [MySQL Relay Log](https://dev.mysql.com/doc/refman/8.0/en/replica-logs-relaylog.html).
### Dump processing unit

The dump processing unit dumps the full data from the upstream MySQL/MariaDB to the local disk.
### Load processing unit

The load processing unit reads the dumped files of the dump processing unit and then loads these files to the downstream TiDB.
### Binlog replication/sync processing unit

Binlog replication/sync processing unit reads the binlog events of the upstream MySQL/MariaDB or the binlog events of the relay log, transforms these events to SQL statements, and then applies these statements to the downstream TiDB.
## Privileges required by DM-worker

This section describes the upstream and downstream database users' privileges required by DM-worker, and the user privileges required by the respective processing unit.
### Upstream database user privileges

The upstream database (MySQL/MariaDB) user must have the following privileges:

| Privilege | Scope |
|:----|:----|
| `SELECT` | Tables |
| `RELOAD` | Global |
| `REPLICATION SLAVE` | Global |
| `REPLICATION CLIENT` | Global |

If you need to migrate the data from `db1` to TiDB, execute the following `GRANT` statement:

```sql
GRANT RELOAD,REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'your_user'@'your_wildcard_of_host';
GRANT SELECT ON db1.* TO 'your_user'@'your_wildcard_of_host';
```

If you also need to migrate the data from other databases into TiDB, make sure the same privileges are granted to the user of the respective databases.
### Downstream database user privileges

The downstream database (TiDB) user must have the following privileges:

| Privilege | Scope |
|:----|:----|
| `SELECT` | Tables |
| `INSERT` | Tables |
| `UPDATE` | Tables |
| `DELETE` | Tables |
| `CREATE` | Databases, tables |
| `DROP` | Databases, tables |
| `ALTER` | Tables |
| `INDEX` | Tables |

Execute the following `GRANT` statement for the databases or tables that you need to migrate:

```sql
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,ALTER,INDEX ON db.table TO 'your_user'@'your_wildcard_of_host';
GRANT ALL ON dm_meta.* TO 'your_user'@'your_wildcard_of_host';
```
### Minimal privilege required by each processing unit

| Processing unit | Minimal upstream (MySQL/MariaDB) privilege | Minimal downstream (TiDB) privilege | Minimal system privilege |
|:----|:--------------------|:------------|:----|
| Relay log | `REPLICATION SLAVE` (reads the binlog)<br/>`REPLICATION CLIENT` (`show master status`, `show slave status`) | NULL | Read/Write local files |
| Dump | `SELECT`<br/>`RELOAD` (flushes tables with Read lock and unlocks tables）| NULL | Write local files |
| Load | NULL | `SELECT` (Query the checkpoint history)<br/>`CREATE` (creates a database/table)<br/>`DELETE` (deletes checkpoint)<br/>`INSERT` (Inserts the Dump data) | Read/Write local files |
| Binlog replication | `REPLICATION SLAVE` (reads the binlog)<br/>`REPLICATION CLIENT` (`show master status`, `show slave status`) | `SELECT` (shows the index and column)<br/>`INSERT` (DML)<br/>`UPDATE` (DML)<br/>`DELETE` (DML)<br/>`CREATE` (creates a database/table)<br/>`DROP` (drops databases/tables)<br/>`ALTER` (alters a table)<br/>`INDEX` (creates/drops an index)| Read/Write local files |

> **Note:**
>
> These privileges are not immutable and they change as the request changes.
