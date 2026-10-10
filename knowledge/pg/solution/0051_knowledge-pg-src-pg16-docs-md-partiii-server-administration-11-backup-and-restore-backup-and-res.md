# File System Level Backup

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/11_backup_and_restore.md`
- Source Title: `Backup and Restore`
- Source Heading Path: `Backup and Restore > File System Level Backup`
- Source Line Ranges: `244-331`
- Chunk ID: `pg16_solution_0051_c8a4db1d16`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7d530feb69775343ec68cbe7bd6edbe68a96d7ca22dda245b8df31fef0b2e26f`

## Retrieval Guidance

- Use When: 需要做物理文件级备份或解释为什么不能只恢复单表文件。
- Retrieval Keywords: file system backup, consistent snapshot, rsync --checksum, shutdown backup, tablespaces, pg_xact
- Follow-up Guidance: 确认全量集群一致性、WAL 文件包含策略和多文件系统快照一致性。
- Classification Note: 说明文件系统备份要求、停机/快照/rsync 方法和限制。

## Official Source Content

## File System Level Backup

An alternative backup strategy is to directly copy the files that
PostgreSQL uses to store the data in the database;
[creating-cluster](#creating-cluster) explains where these files
are located.  You can use whatever method you prefer
for doing file system backups; for example:

```
tar -cf backup.tar /usr/local/pgsql/data
```

There are two restrictions, however, which make this method
impractical, or at least inferior to the pg_dump
method:

1. The database server *must* be shut down in order to
get a usable backup. Half-way measures such as disallowing all
connections will *not* work
(in part because `tar` and similar tools do not take
an atomic snapshot of the state of the file system,
but also because of internal buffering within the server).
Information about stopping the server can be found in
[server-shutdown](#server-shutdown).  Needless to say, you
also need to shut down the server before restoring the data.
2. If you have dug into the details of the file system layout of the
database, you might be tempted to try to back up or restore only certain
individual tables or databases from their respective files or
directories. This will *not* work because the
information contained in these files is not usable without
the commit log files,
`pg_xact/*`, which contain the commit status of
all transactions. A table file is only usable with this
information. Of course it is also impossible to restore only a
table and the associated `pg_xact` data
because that would render all other tables in the database
cluster useless.  So file system backups only work for complete
backup and restoration of an entire database cluster.

An alternative file-system backup approach is to make a
"consistent snapshot" of the data directory, if the
file system supports that functionality (and you are willing to
trust that it is implemented correctly).  The typical procedure is
to make a "frozen snapshot" of the volume containing the
database, then copy the whole data directory (not just parts, see
above) from the snapshot to a backup device, then release the frozen
snapshot.  This will work even while the database server is running.
However, a backup created in this way saves
the database files in a state as if the database server was not
properly shut down; therefore, when you start the database server
on the backed-up data, it will think the previous server instance
crashed and will replay the WAL log.  This is not a problem; just
be aware of it (and be sure to include the WAL files in your backup).
You can perform a `CHECKPOINT` before taking the
snapshot to reduce recovery time.

If your database is spread across multiple file systems, there might not
be any way to obtain exactly-simultaneous frozen snapshots of all
the volumes.  For example, if your data files and WAL log are on different
disks, or if tablespaces are on different file systems, it might
not be possible to use snapshot backup because the snapshots
*must* be simultaneous.
Read your file system documentation very carefully before trusting
the consistent-snapshot technique in such situations.

If simultaneous snapshots are not possible, one option is to shut down
the database server long enough to establish all the frozen snapshots.
Another option is to perform a continuous archiving base backup ([backup-base-backup](#backup-base-backup)) because such backups are immune to file
system changes during the backup.  This requires enabling continuous
archiving just during the backup process; restore is done using
continuous archive recovery ([backup-pitr-recovery](#backup-pitr-recovery)).

Another option is to use rsync to perform a file
system backup.  This is done by first running rsync
while the database server is running, then shutting down the database
server long enough to do an `rsync --checksum`.
(`--checksum` is necessary because `rsync` only
has file modification-time granularity of one second.)  The
second rsync will be quicker than the first,
because it has relatively little data to transfer, and the end result
will be consistent because the server was down.  This method
allows a file system backup to be performed with minimal downtime.

Note that a file system backup will typically be larger
than an SQL dump. (pg_dump does not need to dump
the contents of indexes for example, just the commands to recreate
them.)  However, taking a file system backup might be faster.
