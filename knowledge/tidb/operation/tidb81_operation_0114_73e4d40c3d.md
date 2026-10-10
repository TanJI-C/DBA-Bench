# Replace failed DDL in shard merge migration

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/handle-failed-ddl-statements.md`
- Source Title: `Handle Failed DDL Statements in TiDB Data Migration`
- Source Heading Path: `Handle Failed DDL Statements in TiDB Data Migration > Usage examples > Replace DDL if the migration gets interrupted > Shard merge scenario`
- Source Line Ranges: `592-755`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `failed-ddl`, `ddl-replacement`, `query-status`, `binlog-replace`, `migration-interruption`, `shard-merge`, `pessimistic-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0114_73e4d40c3d`
- Source ID: `tidb-docs-8.1:dm/handle-failed-ddl-statements.md#shard-merge-scenario`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e6d71c52c29e0bfc0f17d1368e634cda20956d6e85fec42a09ad341b7d37696`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/handle-failed-ddl-statements#shard-merge-scenario
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/handle-failed-ddl-statements.md

## Retrieval Guidance

- Use When: Use this chunk when a DM shard merge migration in pessimistic mode is interrupted by unsupported `ADD COLUMN ... UNIQUE` DDLs on sharded upstream tables and you need the per-source replacement flow and the subsequent inconsistent DDL sequence errors.
- Retrieval Keywords: Shard merge scenario, pessimistic, query-status, binlog replace test -s mysql-replica-01, binlog replace test -s mysql-replica-02, ALTER TABLE `shard_db_*`.`shard_table_*` ADD COLUMN new_col INT UNIQUE, cannot track DDL, [ddl:8200]unsupported add column 'new_col' constraint UNIQUE KEY, detect inconsistent DDL sequence from source, ALTER TABLE `shard_db_1`.`shard_table_1` ADD COLUMN `new_col` INT;ALTER TABLE `shard_db_1`.`shard_table_1` ADD UNIQUE(`new_col`), ALTER TABLE `shard_db_2`.`shard_table_1` ADD COLUMN `new_col` INT;ALTER TABLE `shard_db_2`.`shard_table_1` ADD UNIQUE(`new_col`), ALTER TABLE `shard_db_1`.`shard_table_2` ADD COLUMN `new_col` INT;ALTER TABLE `shard_db_1`.`shard_table_2` ADD UNIQUE(`new_col`), ALTER TABLE `shard_db_2`.`shard_table_2` ADD COLUMN `new_col` INT;ALTER TABLE `shard_db_2`.`shard_table_2` ADD UNIQUE(`new_col`)
- Follow-up Guidance: After the first replacements, `query-status <task-name>` reports `detect inconsistent DDL sequence from source` for `shard_table_2` on both sources, and the chunk then shows replacing those DDL statements as well before checking status again.
- Classification Note: This is an operation example for DM that covers failed DDL replacement in a self-managed shard merge migration, including source-specific replacements and follow-up errors caused by inconsistent DDL sequences.

## Official Source Content

#### Shard merge scenario

Assume that you need to merge and migrate the following four tables in the upstream to one same table ``` `shard_db`.`shard_table` ``` in the downstream. The task mode is "pessimistic".

- In the MySQL instance 1, there is a schema `shard_db_1`, which has two tables `shard_table_1` and `shard_table_2`.
- In the MySQL instance 2, there is a schema `shard_db_2`, which has two tables `shard_table_1` and `shard_table_2`.

The initial table schema is:

```sql
SHOW CREATE TABLE shard_db.shard_table;
```

```sql
+-------+-----------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                              |
+-------+-----------------------------------------------------------------------------------------------------------+
| tb    | CREATE TABLE `shard_table` (
  `id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_bin |
+-------+-----------------------------------------------------------------------------------------------------------+
```

Now, perform the following DDL operation to all upstream sharded tables to add a new column with the UNIQUE constraint:

```sql
ALTER TABLE `shard_db_*`.`shard_table_*` ADD COLUMN new_col INT UNIQUE;
```

Because this DDL statement is not supported by TiDB, the migration task gets interrupted. Execute the `query-status` command, and you can see the following errors reported by the `shard_db_1`.`shard_table_1` table in MySQL instance 1 and the `shard_db_2`.`shard_table_1` table in MySQL instance 2:

```
{
    "Message": "cannot track DDL: ALTER TABLE `shard_db_1`.`shard_table_1` ADD COLUMN `new_col` INT UNIQUE KEY",
    "RawCause": "[ddl:8200]unsupported add column 'new_col' constraint UNIQUE KEY when altering 'shard_db_1.shard_table_1'",
}
```

```
{
    "Message": "cannot track DDL: ALTER TABLE `shard_db_2`.`shard_table_1` ADD COLUMN `new_col` INT UNIQUE KEY",
    "RawCause": "[ddl:8200]unsupported add column 'new_col' constraint UNIQUE KEY when altering 'shard_db_2.shard_table_1'",
}
```

You can replace this DDL statement with two equivalent DDL statements. The steps are as follows:

1. Replace the wrong DDL statements respectively in MySQL instance 1 and MySQL instance 2 by the following commands:

    ```bash
    » binlog replace test -s mysql-replica-01 "ALTER TABLE `shard_db_1`.`shard_table_1` ADD COLUMN `new_col` INT;ALTER TABLE `shard_db_1`.`shard_table_1` ADD UNIQUE(`new_col`)";
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
                "worker": "worker1"
            }
        ]
    }
    ```

    ```bash
    » binlog replace test -s mysql-replica-02 "ALTER TABLE `shard_db_2`.`shard_table_1` ADD COLUMN `new_col` INT;ALTER TABLE `shard_db_2`.`shard_table_1` ADD UNIQUE(`new_col`)";
    ```

    ```
    {
        "result": true,
        "msg": "",
        "sources": [
            {
                "result": true,
                "msg": "",
                "source": "mysql-replica-02",
                "worker": "worker2"
            }
        ]
    }
    ```

2. Use `query-status <task-name>` to view the task status, and you can see the following errors reported by the `shard_db_1`.`shard_table_2` table in MySQL instance 1 and the `shard_db_2`.`shard_table_2` table in MySQL instance 2:

    ```
    {
        "Message": "detect inconsistent DDL sequence from source ... ddls: [ALTER TABLE `shard_db`.`tb` ADD COLUMN `new_col` INT UNIQUE KEY] source: `shard_db_1`.`shard_table_2`], right DDL sequence should be ..."
    }
    ```

    ```
    {
        "Message": "detect inconsistent DDL sequence from source ... ddls: [ALTER TABLE `shard_db`.`tb` ADD COLUMN `new_col` INT UNIQUE KEY] source: `shard_db_2`.`shard_table_2`], right DDL sequence should be ..."
    }
    ```

3. Execute `handle-error <task-name> replace` again to replace the wrong DDL statements in MySQL instance 1 and 2:

    ```bash
    » binlog replace test -s mysql-replica-01 "ALTER TABLE `shard_db_1`.`shard_table_2` ADD COLUMN `new_col` INT;ALTER TABLE `shard_db_1`.`shard_table_2` ADD UNIQUE(`new_col`)";
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
                "worker": "worker1"
            }
        ]
    }
    ```

    ```bash
    » binlog replace test -s mysql-replica-02 "ALTER TABLE `shard_db_2`.`shard_table_2` ADD COLUMN `new_col` INT;ALTER TABLE `shard_db_2`.`shard_table_2` ADD UNIQUE(`new_col`)";
    ```

    ```
    {
        "result": true,
        "msg": "",
        "sources": [
            {
                "result": true,
                "msg": "",
                "source": "mysql-replica-02",
                "worker": "worker2"
            }
        ]
    }
    ```

4. Use `query-status <task-name>` to view the task status:

    ```bash
    » query-status test
    ```

    <details><summary> See the execution result.</summary>
