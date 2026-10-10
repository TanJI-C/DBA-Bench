# WAL Internals

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/15_reliability_and_the_write-ahead_log.md`
- Source Title: `Reliability and the Write-Ahead Log`
- Source Heading Path: `Reliability and the Write-Ahead Log > WAL Internals`
- Source Line Ranges: `635-703`
- Chunk ID: `pg16_fact_0063_1ca344d750`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2fbf09cf3f363b4eb69af6af7cc634f7ea34d10e56ab8981cef787a75c29a4bc`

## Retrieval Guidance

- Use When: 需要理解 WAL 文件命名、LSN 比较或 pg_wal 存储布局。
- Retrieval Keywords: WAL internals, LSN, pg_lsn, pg_wal, WAL segment, --wal-segsize, symbolic link pg_wal
- Follow-up Guidance: 移动 pg_wal 前必须停库并正确创建符号链接。
- Classification Note: 说明 LSN、WAL segment 文件、pg_wal 目录和移动 WAL 目录的基础。

## Official Source Content

## WAL Internals

WAL is automatically enabled; no action is
required from the administrator except ensuring that the
disk-space requirements for the WAL files are met,
and that any necessary tuning is done (see [wal-configuration](#wal-configuration)).

WAL records are appended to the WAL
files as each new record is written. The insert position is described by
a Log Sequence Number (LSN) that is a byte offset into
the WAL, increasing monotonically with each new record.
LSN values are returned as the datatype
[`pg_lsn`](#datatype-pg-lsn). Values can be
compared to calculate the volume of WAL data that
separates them, so they are used to measure the progress of replication
and recovery.

WAL files are stored in the directory
`pg_wal` under the data directory, as a set of
segment files, normally each 16 MB in size (but the size can be changed
by altering the `--wal-segsize` initdb option).  Each segment is
divided into pages, normally 8 kB each (this size can be changed via the
`--with-wal-blocksize` configure option).  The WAL record headers
are described in `access/xlogrecord.h`; the record
content is dependent on the type of event that is being logged.  Segment
files are given ever-increasing numbers as names, starting at
`000000010000000000000001`.  The numbers do not wrap,
but it will take a very, very long time to exhaust the
available stock of numbers.

It is advantageous if the WAL is located on a different disk from the
main database files.  This can be achieved by moving the
`pg_wal` directory to another location (while the server
is shut down, of course) and creating a symbolic link from the
original location in the main data directory to the new location.

The aim of WAL is to ensure that the log is
written before database records are altered, but this can be subverted by
disk drives that falsely report a
successful write to the kernel,
when in fact they have only cached the data and not yet stored it
on the disk.  A power failure in such a situation might lead to
irrecoverable data corruption.  Administrators should try to ensure
that disks holding PostgreSQL's
WAL files do not make such false reports.
(See [wal-reliability](#wal-reliability).)

After a checkpoint has been made and the WAL flushed, the
checkpoint's position is saved in the file
`pg_control`. Therefore, at the start of recovery,
the server first reads `pg_control` and
then the checkpoint record; then it performs the REDO operation by
scanning forward from the WAL location indicated in the checkpoint
record.  Because the entire content of data pages is saved in the
WAL on the first page modification after a checkpoint (assuming
[guc-full-page-writes](#guc-full-page-writes) is not disabled), all pages
changed since the checkpoint will be restored to a consistent
state.

To deal with the case where `pg_control` is
corrupt, we should support the possibility of scanning existing WAL
segments in reverse order — newest to oldest — in order to find the
latest checkpoint.  This has not been implemented yet.
`pg_control` is small enough (less than one disk page)
that it is not subject to partial-write problems, and as of this writing
there have been no reports of database failures due solely to the inability
to read `pg_control` itself.  So while it is
theoretically a weak spot, `pg_control` does not
seem to be a problem in practice.
