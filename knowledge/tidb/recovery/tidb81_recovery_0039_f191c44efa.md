# FLASHBACK CLUSTER execution notes and restrictions

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-flashback-cluster.md`
- Source Title: `FLASHBACK CLUSTER`
- Source Heading Path: `FLASHBACK CLUSTER > Notes`
- Source Line Ranges: `49-79`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `br`, `pd`, `ticdc`, `tidb`
- Topic Tags: `gc`, `safepoint`, `privileges`, `ddl`, `connections`, `backup`, `log-backup`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0039_f191c44efa`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-flashback-cluster.md#notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c81ee356edcbe9eeb3a00d4013d1389db6311ae91d998805d74a71b599e9926e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster#notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-flashback-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when you need operational restrictions, privilege requirements, GC lifetime constraints, or TiCDC and backup interactions for `FLASHBACK CLUSTER`.
- Retrieval Keywords: tikv_gc_safe_point, tidb_gc_life_time, SUPER privilege, ALTER TABLE ATTRIBUTE, ALTER TABLE REPLICA, CREATE PLACEMENT POLICY, BackupTS, log backup, TiCDC changefeed, pause the task manually, disconnect all related connections
- Follow-up Guidance: If metadata rollback affects TiCDC, pause the task, wait for `FLASHBACK CLUSTER` to finish, and recreate the changefeed after the upstream and downstream schema definitions are consistent.
- Classification Note: This chunk is classified as execution notes because it describes restrictions, privilege checks, DDL limitations, connection behavior, backup constraints, and TiCDC handling.

## Official Source Content

## Notes

* The time specified in the `FLASHBACK` statement must be within the Garbage Collection (GC) lifetime. The system variable [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) (default: `10m0s`) defines the retention time of earlier versions of rows. The current `safePoint` of where garbage collection has been performed up to can be obtained with the following query:

    ```sql
    SELECT * FROM mysql.tidb WHERE variable_name = 'tikv_gc_safe_point';
    ```

* Only a user with the `SUPER` privilege can execute the `FLASHBACK CLUSTER` SQL statement.
* `FLASHBACK CLUSTER` does not support rolling back DDL statements that modify PD-related information, such as `ALTER TABLE ATTRIBUTE`, `ALTER TABLE REPLICA`, and `CREATE PLACEMENT POLICY`.
* At the time specified in the `FLASHBACK` statement, there cannot be a DDL statement that is not completely executed. If such a DDL exists, TiDB will reject it.
* Before executing `FLASHBACK CLUSTER`, TiDB disconnects all related connections and prohibits read and write operations on these tables until the `FLASHBACK CLUSTER` statement is completed.
* The `FLASHBACK CLUSTER` statement cannot be canceled after being executed. TiDB will keep retrying until it succeeds.
* During the execution of `FLASHBACK CLUSTER`, if you need to back up data, you can only use [Backup & Restore](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide) and specify a `BackupTS` that is earlier than the start time of `FLASHBACK CLUSTER`. In addition, during the execution of `FLASHBACK CLUSTER`, enabling [log backup](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) will fail. Therefore, try to enable log backup after `FLASHBACK CLUSTER` is completed.
* If the `FLASHBACK CLUSTER` statement causes the rollback of metadata (table structure, database structure), the related modifications will **not** be replicated by TiCDC. Therefore, you need to pause the task manually, wait for the completion of `FLASHBACK CLUSTER`, and manually replicate the schema definitions of the upstream and downstream to make sure that they are consistent. After that, you need to recreate the TiCDC changefeed.

* Only a user with the `SUPER` privilege can execute the `FLASHBACK CLUSTER` SQL statement.
* `FLASHBACK CLUSTER` does not support rolling back DDL statements that modify PD-related information, such as `ALTER TABLE ATTRIBUTE`, `ALTER TABLE REPLICA`, and `CREATE PLACEMENT POLICY`.
* At the time specified in the `FLASHBACK` statement, there cannot be a DDL statement that is not completely executed. If such a DDL exists, TiDB will reject it.
* Before executing `FLASHBACK CLUSTER`, TiDB disconnects all related connections and prohibits read and write operations on these tables until the `FLASHBACK CLUSTER` statement is completed.
* The `FLASHBACK CLUSTER` statement cannot be canceled after being executed. TiDB will keep retrying until it succeeds.
* If the `FLASHBACK CLUSTER` statement causes the rollback of metadata (table structure, database structure), the related modifications will **not** be replicated by TiCDC. Therefore, you need to pause the task manually, wait for the completion of `FLASHBACK CLUSTER`, and manually replicate the schema definitions of the upstream and downstream to make sure that they are consistent. After that, you need to recreate the TiCDC changefeed.
