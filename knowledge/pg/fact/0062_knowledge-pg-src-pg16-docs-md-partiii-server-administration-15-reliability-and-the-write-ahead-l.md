# Write-Ahead Logging (WAL)

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/15_reliability_and_the_write-ahead_log.md`
- Source Title: `Reliability and the Write-Ahead Log`
- Source Heading Path: `Reliability and the Write-Ahead Log > Write-Ahead Logging (WAL)`
- Source Line Ranges: `187-237`
- Chunk ID: `pg16_fact_0062_18bb150994`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `24729da5e5f72826f2945ed27bd1dc29ddb0cf5073a8f4e6fa90d4f2d3f96f53`

## Retrieval Guidance

- Use When: 需要基础解释为什么 WAL 能保证崩溃恢复和物理备份。
- Retrieval Keywords: WAL, write-ahead logging, REDO, crash recovery, online backup, PITR
- Follow-up Guidance: none
- Classification Note: 解释 WAL 先写日志、REDO、减少同步写和支持在线备份/PITR 的机制。

## Official Source Content

## Write-Ahead Logging (WAL)

*Write-Ahead Logging* (WAL)
is a standard method for ensuring data integrity.  A detailed
description can be found in most (if not all) books about
transaction processing. Briefly, WAL's central
concept is that changes to data files (where tables and indexes
reside) must be written only after those changes have been logged,
that is, after WAL records describing the changes have been flushed
to permanent storage. If we follow this procedure, we do not need
to flush data pages to disk on every transaction commit, because we
know that in the event of a crash we will be able to recover the
database using the log: any changes that have not been applied to
the data pages can be redone from the WAL records.  (This is
roll-forward recovery, also known as REDO.)

> **Tip:**

> Because WAL restores database file
> contents after a crash, journaled file systems are not necessary for
> reliable storage of the data files or WAL files.  In fact, journaling
> overhead can reduce performance, especially if journaling
> causes file system *data* to be flushed
> to disk.  Fortunately, data flushing during journaling can
> often be disabled with a file system mount option, e.g.,
> `data=writeback` on a Linux ext3 file system.
> Journaled file systems do improve boot speed after a crash.
>

Using WAL results in a
significantly reduced number of disk writes, because only the WAL
file needs to be flushed to disk to guarantee that a transaction is
committed, rather than every data file changed by the transaction.
The WAL file is written sequentially,
and so the cost of syncing the WAL is much less than the cost of
flushing the data pages.  This is especially true for servers
handling many small transactions touching different parts of the data
store.  Furthermore, when the server is processing many small concurrent
transactions, one `fsync` of the WAL file may
suffice to commit many transactions.

WAL also makes it possible to support on-line
backup and point-in-time recovery, as described in [continuous-archiving](#continuous-archiving).  By archiving the WAL data we can support
reverting to any time instant covered by the available WAL data:
we simply install a prior physical backup of the database, and
replay the WAL just as far as the desired time.  What's more,
the physical backup doesn't have to be an instantaneous snapshot
of the database state — if it is made over some period of time,
then replaying the WAL for that period will fix any internal
inconsistencies.
