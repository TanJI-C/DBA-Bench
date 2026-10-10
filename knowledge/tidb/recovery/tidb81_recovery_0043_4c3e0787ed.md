# RESTORE statement syntax, requirements, options, and examples

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-restore.md`
- Source Title: `RESTORE | TiDB SQL Statement Reference`
- Source Heading Path: `RESTORE | RESTORE > Synopsis | RESTORE > Examples | RESTORE > Examples > Restore from backup archive | RESTORE > Examples > Partial restore | RESTORE > Examples > External storages | RESTORE > Examples > Performance fine-tuning | RESTORE > Examples > Incremental restore | RESTORE > MySQL compatibility | RESTORE > See also`
- Source Line Ranges: `5-163`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `br`, `tidb`, `tikv`
- Topic Tags: `restore`, `backup-archive`, `syntax`, `privileges`, `offline-cluster`, `external-storage`, `s3`, `gcs`, `checksum`, `rate-limit`, `concurrency`, `incremental-restore`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0043_4c3e0787ed`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-restore.md#restore`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dbd581ce424ff114ab1489d2a31a86632a1c817e5532948b99460462c8dc9318`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-restore#restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-restore.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB SQL RESTORE syntax, prerequisites, privileges, options, examples, or restore behavior from backup archives and external storage.
- Retrieval Keywords: RESTORE statement, RESTORE DATABASE * FROM, RESTORE TABLE, RESTORE_ADMIN, SUPER privilege, KILL TIDB QUERY, SHOW RESTORES, BACKUP statement, BR tool, offline cluster, only one BACKUP and RESTORE task can be executed at a time, tikv storage engine, unistore, RATE_LIMIT, CONCURRENCY, CHECKSUM, SEND_CREDENTIALS_TO_TIKV, S3, GCS, external storage URI, incremental restore, LAST_BACKUP, partial restore, MySQL compatibility
- Follow-up Guidance: The source also points to related statements and topics including BACKUP, SHOW RESTORES, KILL TIDB QUERY, and URI Formats of External Storage Services.
- Classification Note: This is classified as recovery for the SQL component because the content defines the RESTORE SQL statement used to restore data from backup archives with BR-based restore behavior and options.

## Official Source Content

# RESTORE

This statement performs a distributed restore from a backup archive previously produced by a [`BACKUP` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup).

> **Warning:**
>
> - This feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
> - This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

The `RESTORE` statement uses the same engine as the [BR tool](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview), except that the restore process is driven by TiDB itself rather than a separate BR tool. All benefits and caveats of BR also apply here. In particular, **`RESTORE` is currently not ACID-compliant**. Before running `RESTORE`, ensure that the following requirements are met:

* The cluster is "offline", and the current TiDB session is the only active SQL connection to access all tables being restored.
* When a full restore is being performed, the tables being restored should not already exist, because existing data might be overridden and causes inconsistency between the data and indices.
* When an incremental restore is being performed, the tables should be at the exact same state as the `LAST_BACKUP` timestamp when the backup is created.

Running `RESTORE` requires either the `RESTORE_ADMIN` or `SUPER` privilege. Additionally, both the TiDB node executing the restore and all TiKV nodes in the cluster must have read permission from the destination.

The `RESTORE` statement is blocking, and will finish only after the entire restore task is finished, failed, or canceled. A long-lasting connection should be prepared for running `RESTORE`. The task can be canceled using the [`KILL TIDB QUERY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill) statement.

Only one `BACKUP` and `RESTORE` task can be executed at a time. If a `BACKUP` or `RESTORE` task is already running on the same TiDB server, the new `RESTORE` execution will wait until all previous tasks are done.

`RESTORE` can only be used with "tikv" storage engine. Using `RESTORE` with the "unistore" engine will fail.
## Synopsis

```ebnf+diagram
RestoreStmt ::=
    "RESTORE" BRIETables "FROM" stringLit RestoreOption*

BRIETables ::=
    "DATABASE" ( '*' | DBName (',' DBName)* )
|   "TABLE" TableNameList

RestoreOption ::=
    "RATE_LIMIT" '='? LengthNum "MB" '/' "SECOND"
|   "CONCURRENCY" '='? LengthNum
|   "CHECKSUM" '='? Boolean
|   "SEND_CREDENTIALS_TO_TIKV" '='? Boolean

Boolean ::=
    NUM | "TRUE" | "FALSE"
```
## Examples
### Restore from backup archive

```sql
RESTORE DATABASE * FROM 'local:///mnt/backup/2020/04/';
```

```sql
+------------------------------+-----------+----------+---------------------+---------------------+
| Destination                  | Size      | BackupTS | Queue Time          | Execution Time      |
+------------------------------+-----------+----------+---------------------+---------------------+
| local:///mnt/backup/2020/04/ | 248665063 | 0        | 2020-04-21 17:16:55 | 2020-04-21 17:16:55 |
+------------------------------+-----------+----------+---------------------+---------------------+
1 row in set (28.961 sec)
```

In the example above, all data is restored from a backup archive at the local filesystem. The data is read as SST files from the `/mnt/backup/2020/04/` directories distributed among all TiDB and TiKV nodes.

The first row of the result above is described as follows:

| Column | Description |
| :-------- | :--------- |
| `Destination` | The destination URL to read from |
| `Size` |  The total size of the backup archive, in bytes |
| `BackupTS` | (not used) |
| `Queue Time` | The timestamp (in current time zone) when the `RESTORE` task was queued. |
| `Execution Time` | The timestamp (in current time zone) when the `RESTORE` task starts to run. |
### Partial restore

You can specify which databases or tables to restore. If some databases or tables are missing from the backup archive, they will be ignored, and thus `RESTORE` would complete without doing anything.

```sql
RESTORE DATABASE `test` FROM 'local:///mnt/backup/2020/04/';
```

```sql
RESTORE TABLE `test`.`sbtest01`, `test`.`sbtest02` FROM 'local:///mnt/backup/2020/04/';
```
### External storages

BR supports restoring data from S3 or GCS:

```sql
RESTORE DATABASE * FROM 's3://example-bucket-2020/backup-05/';
```

The URL syntax is further explained in [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

When running on cloud environment where credentials should not be distributed, set the `SEND_CREDENTIALS_TO_TIKV` option to `FALSE`:

```sql
RESTORE DATABASE * FROM 's3://example-bucket-2020/backup-05/'
    SEND_CREDENTIALS_TO_TIKV = FALSE;
```
### Performance fine-tuning

Use `RATE_LIMIT` to limit the average download speed per TiKV node to reduce network bandwidth.

Before the restore is completed, `RESTORE` would perform a checksum against the data in the backup files to verify correctness. If you are confident that this verification is unnecessary, you can disable the check by setting the `CHECKSUM` parameter to `FALSE`.

```sql
RESTORE DATABASE * FROM 's3://example-bucket-2020/backup-06/'
    RATE_LIMIT = 120 MB/SECOND
    CONCURRENCY = 64
    CHECKSUM = FALSE;
```
### Incremental restore

There is no special syntax to perform incremental restore. TiDB will recognize whether the backup archive is full or incremental and take appropriate action. You only need to apply each incremental restore in correct order.

For instance, if a backup task is created as follows:

```sql
BACKUP DATABASE `test` TO 's3://example-bucket/full-backup'  SNAPSHOT = 413612900352000;
BACKUP DATABASE `test` TO 's3://example-bucket/inc-backup-1' SNAPSHOT = 414971854848000 LAST_BACKUP = 413612900352000;
BACKUP DATABASE `test` TO 's3://example-bucket/inc-backup-2' SNAPSHOT = 416353458585600 LAST_BACKUP = 414971854848000;
```

then the same order should be applied in the restore:

```sql
RESTORE DATABASE * FROM 's3://example-bucket/full-backup';
RESTORE DATABASE * FROM 's3://example-bucket/inc-backup-1';
RESTORE DATABASE * FROM 's3://example-bucket/inc-backup-2';
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [BACKUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup)
* [SHOW RESTORES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-backups)
