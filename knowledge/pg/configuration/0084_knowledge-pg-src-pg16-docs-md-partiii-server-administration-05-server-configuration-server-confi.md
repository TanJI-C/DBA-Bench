# Error Handling

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Error Handling`
- Source Line Ranges: `6071-6137`
- Chunk ID: `pg16_configuration_0084_febf399d9a`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `03edaaabb4d03af6d8e374bf7067645a9700ddac1a168801973c3c8549809264`

## Retrieval Guidance

- Use When: 需要控制后端错误、崩溃后重启、writeback 失败和 crash recovery 前同步行为。
- Retrieval Keywords: exit_on_error, restart_after_crash, data_sync_retry, recovery_init_sync_method, PANIC, syncfs, fsync
- Follow-up Guidance: data_sync_retry=on 只应在理解 OS writeback failure 语义后使用。
- Classification Note: 定义 exit_on_error、restart_after_crash、data_sync_retry、recovery_init_sync_method 等错误/崩溃处理策略。

## Official Source Content

## Error Handling

**`exit_on_error` (`boolean`)**
: If on, any error will terminate the current session.  By default,
this is set to off, so that only FATAL errors will terminate the
session.

**`restart_after_crash` (`boolean`)**
: When set to on, which is the default, PostgreSQL
will automatically reinitialize after a backend crash.  Leaving this
value set to on is normally the best way to maximize the availability
of the database.  However, in some circumstances, such as when
PostgreSQL is being invoked by clusterware, it may be
useful to disable the restart so that the clusterware can gain
control and take any actions it deems appropriate.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`data_sync_retry` (`boolean`)**
: When set to off, which is the default, PostgreSQL
will raise a PANIC-level error on failure to flush modified data files
to the file system.  This causes the database server to crash.  This
parameter can only be set at server start.

On some operating systems, the status of data in the kernel's page
cache is unknown after a write-back failure.  In some cases it might
have been entirely forgotten, making it unsafe to retry; the second
attempt may be reported as successful, when in fact the data has been
lost.  In these circumstances, the only way to avoid data loss is to
recover from the WAL after any failure is reported, preferably
after investigating the root cause of the failure and replacing any
faulty hardware.

If set to on, PostgreSQL will instead
report an error but continue to run so that the data flushing
operation can be retried in a later checkpoint.  Only set it to on
after investigating the operating system's treatment of buffered data
in case of write-back failure.

**`recovery_init_sync_method` (`enum`)**
: When set to `fsync`, which is the default,
PostgreSQL will recursively open and
synchronize all files in the data directory before crash recovery
begins.  The search for files will follow symbolic links for the WAL
directory and each configured tablespace (but not any other symbolic
links).  This is intended to make sure that all WAL and data files are
durably stored on disk before replaying changes.  This applies whenever
starting a database cluster that did not shut down cleanly, including
copies created with pg_basebackup.

On Linux, `syncfs` may be used instead, to ask the
operating system to synchronize the whole file systems that contain the
data directory, the WAL files and each tablespace (but not any other
file systems that may be reachable through symbolic links).  This may
be a lot faster than the `fsync` setting, because it
doesn't need to open each file one by one.  On the other hand, it may
be slower if a file system is shared by other applications that
modify a lot of files, since those files will also be written to disk.
Furthermore, on versions of Linux before 5.8, I/O errors encountered
while writing data to disk may not be reported to
PostgreSQL, and relevant error messages may
appear only in kernel logs.

This parameter can only be set in the
`postgresql.conf` file or on the server command line.
