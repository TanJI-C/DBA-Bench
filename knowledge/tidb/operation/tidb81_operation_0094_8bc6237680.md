# DM binlog-schema list, update, and delete examples

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-manage-schema.md`
- Source Title: `Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration`
- Source Heading Path: `Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration > Usage example | Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration > Usage example > Get the table schema | Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration > Usage example > Update the table schema | Manage Table Schemas of Tables to Be Migrated Using TiDB Data Migration > Usage example > Delete the table schema`
- Source Line Ranges: `89-245`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `schema-management`, `list`, `update`, `delete`, `examples`, `checkpoint`, `optimistic-sharding`, `downstream-schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0094_8bc6237680`
- Source ID: `tidb-docs-8.1:dm/dm-manage-schema.md#usage-example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8735f01e32d667fc01f8718e994504160c9f6e65a2baba72400b5d9a55560ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-manage-schema#usage-example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-manage-schema.md

## Retrieval Guidance

- Use When: Use this chunk when you need concrete DM examples for listing, updating, or deleting a table schema and the exact command syntax and recovery sources involved.
- Retrieval Keywords: binlog-schema list, binlog-schema update, binlog-schema delete, dmctl binlog-schema list <task-name> <database> <table>, dmctl binlog-schema update <task-name> <database> <table> [schema-file], dmctl binlog-schema delete <task-name> <database> <table>, --flush, --from-source, --from-target, --sync, mysql-replica-01, task_single, db_single, t1, CREATE TABLE `t1`, table_info field in the checkpoint table, optimistic sharding DDL, downstream TiDB
- Follow-up Guidance: After deletion, DM tries to obtain the table schema in order from the `table_info` field in the checkpoint table, the meta information in the optimistic sharding DDL, and the corresponding table in the downstream TiDB.
- Classification Note: This is classified as an operation chunk because the official content provides command help, example invocations, example output, and the post-deletion schema lookup order for schema management.

## Official Source Content

## Usage example
### Get the table schema

To get the table schema, run the `binlog-schema list` command:

```bash
help binlog-schema list
```

```
show table schema structure

Usage:
  dmctl binlog-schema list <task-name> <database> <table> [flags]

Flags:
  -h, --help   help for list

Global Flags:
  -s, --source strings   MySQL Source ID.
```

If you want to get the table schema of the ``` `db_single`.`t1` ``` table corresponding to the `mysql-replica-01` MySQL source in the `db_single` task, run the following command:

```bash
binlog-schema list -s mysql-replica-01 task_single db_single t1
```

```
{
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "CREATE TABLE `t1` ( `c1` int(11) NOT NULL, `c2` int(11) DEFAULT NULL, PRIMARY KEY (`c1`)) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_bin",
            "source": "mysql-replica-01",
            "worker": "127.0.0.1:8262"
        }
    ]
}
```
### Update the table schema

To update the table schema, run the `binlog-schema update` command:

```bash
help binlog-schema update
```

```
update tables schema structure

Usage:
  dmctl binlog-schema update <task-name> <database> <table> [schema-file] [flags]

Flags:
      --flush         flush the table info and checkpoint immediately (default true)
      --from-source   use the schema from upstream database as the schema of the specified tables
      --from-target   use the schema from downstream database as the schema of the specified tables
  -h, --help          help for update
      --sync          sync the table info to master to resolve shard ddl lock, only for optimistic mode now (default true)

Global Flags:
  -s, --source strings   MySQL Source ID.
```

If you want to set the table schema of the ``` `db_single`.`t1` ``` table corresponding to the `mysql-replica-01` MySQL source in the `db_single` task as follows:

```sql
CREATE TABLE `t1` (
    `c1` int(11) NOT NULL,
    `c2` bigint(11) DEFAULT NULL,
    PRIMARY KEY (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_bin
```

Save the `CREATE TABLE` statement above as a file (for example, `db_single.t1-schema.sql`), and run the following command:

```bash
operate-schema set -s mysql-replica-01 task_single -d db_single -t t1 db_single.t1-schema.sql
```

```
{
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "",
            "source": "mysql-replica-01",
            "worker": "127.0.0.1:8262"
        }
    ]
}
```
### Delete the table schema

To delete the table schema, run the `binlog-schema delete` command:

```bash
help binlog-schema delete
```

```
delete table schema structure

Usage:
  dmctl binlog-schema delete <task-name> <database> <table> [flags]

Flags:
  -h, --help   help for delete

Global Flags:
  -s, --source strings   MySQL Source ID.
```

> **Note:**
>
> After the table schema maintained in DM is deleted, if a DDL/DML statement related to this table needs to be migrated to the downstream, DM will try to get the table schema from the following three sources in an orderly manner:
>
> * The `table_info` field in the checkpoint table
> * The meta information in the optimistic sharding DDL
> * The corresponding table in the downstream TiDB

If you want to delete the table schema of the ``` `db_single`.`t1` ``` table corresponding to the `mysql-replica-01` MySQL source in the `db_single` task, run the following command:

```bash
binlog-schema delete -s mysql-replica-01 task_single db_single t1
```

```
{
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "",
            "source": "mysql-replica-01",
            "worker": "127.0.0.1:8262"
        }
    ]
}
```
