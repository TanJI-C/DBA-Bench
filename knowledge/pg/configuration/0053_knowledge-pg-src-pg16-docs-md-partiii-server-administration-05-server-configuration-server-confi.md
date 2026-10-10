# Archiving

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Write Ahead Log > Archiving`
- Source Line Ranges: `1734-1892, 2195-2286`
- Chunk ID: `pg16_configuration_0053_74e79345a7`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c6f93bbd1047bf8e435ef344b75f1736986b3b413cc2a0e1899ef34f50e747c`

## Retrieval Guidance

- Use When: 需要配置 WAL 归档、PITR 或处理归档积压。
- Retrieval Keywords: archive_mode, archive_command, archive_library, archive_timeout, WAL archiving, PITR, archive storage
- Follow-up Guidance: archive_command 必须只在成功归档后返回 0，/bin/true 会破坏恢复链。
- Classification Note: 定义 archive_mode、archive_command、archive_library、archive_timeout 的归档语义和失败影响。

## Official Source Content

## Write Ahead Log

For additional information on tuning these settings,
see [wal-configuration](#wal-configuration).

### Settings

**`wal_level` (`enum`)**
: `wal_level` determines how much information is written to
the WAL. The default value is `replica`, which writes enough
data to support WAL archiving and replication, including running
read-only queries on a standby server. `minimal` removes all
logging except the information required to recover from a crash or
immediate shutdown.  Finally,
`logical` adds information necessary to support logical
decoding.  Each level includes the information logged at all lower
levels.  This parameter can only be set at server start.

The `minimal` level generates the least WAL
volume.  It logs no row information for permanent relations
in transactions that create or
rewrite them.  This can make operations much faster (see
[populate-pitr](#populate-pitr)).  Operations that initiate this
optimization include:

However, minimal WAL does not contain sufficient information for
point-in-time recovery, so `replica` or
higher must be used to enable continuous archiving
([guc-archive-mode](#guc-archive-mode)) and streaming binary replication.
In fact, the server will not even start in this mode if
`max_wal_senders` is non-zero.
Note that changing `wal_level` to
`minimal` makes previous base backups unusable
for point-in-time recovery and standby servers.

In `logical` level, the same information is logged as
with `replica`, plus information needed to
extract logical change sets from the WAL. Using a level of
`logical` will increase the WAL volume, particularly if many
tables are configured for `REPLICA IDENTITY FULL` and
many `UPDATE` and `DELETE` statements are
executed.

In releases prior to 9.6, this parameter also allowed the
values `archive` and `hot_standby`.
These are still accepted but mapped to `replica`.

**`fsync` (`boolean`)**
: If this parameter is on, the PostgreSQL server
will try to make sure that updates are physically written to
disk, by issuing `fsync()` system calls or various
equivalent methods (see [guc-wal-sync-method](#guc-wal-sync-method)).
This ensures that the database cluster can recover to a
consistent state after an operating system or hardware crash.

While turning off `fsync` is often a performance
benefit, this can result in unrecoverable data corruption in
the event of a power failure or system crash.  Thus it
is only advisable to turn off `fsync` if
you can easily recreate your entire database from external
data.

Examples of safe circumstances for turning off
`fsync` include the initial loading of a new
database cluster from a backup file, using a database cluster
for processing a batch of data after which the database
will be thrown away and recreated,
or for a read-only database clone which
gets recreated frequently and is not used for failover.  High
quality hardware alone is not a sufficient justification for
turning off `fsync`.

For reliable recovery when changing `fsync`
off to on, it is necessary to force all modified buffers in the
kernel to durable storage.  This can be done while the cluster
is shutdown or while `fsync` is on by running `initdb
--sync-only`, running `sync`, unmounting the
file system, or rebooting the server.

In many situations, turning off [guc-synchronous-commit](#guc-synchronous-commit)
for noncritical transactions can provide much of the potential
performance benefit of turning off `fsync`, without
the attendant risks of data corruption.

`fsync` can only be set in the `postgresql.conf`
file or on the server command line.
If you turn this parameter off, also consider turning off
[guc-full-page-writes](#guc-full-page-writes).

**`synchronous_commit` (`enum`)**
: Specifies how much WAL processing must complete before
the database server returns a "success"
indication to the client.  Valid values are
`remote_apply`, `on`
(the default), `remote_write`,
`local`, and `off`.

If `synchronous_standby_names` is empty,
the only meaningful settings are `on` and
`off`;  `remote_apply`,
`remote_write` and `local`
all provide the same local synchronization level
as `on`.  The local behavior of all
non-`off` modes is to wait for local flush of WAL
to disk.  In `off` mode, there is no waiting,
so there can be a delay between when success is reported to the
client and when the transaction is later guaranteed to be safe
against a server crash.  (The maximum
delay is three times [guc-wal-writer-delay](#guc-wal-writer-delay).)  Unlike
[guc-fsync](#guc-fsync), setting this parameter to `off`
does not create any risk of database inconsistency: an operating
system or database crash might
result in some recent allegedly-committed transactions being lost, but
the database state will be just the same as if those transactions had
been aborted cleanly.  So, turning `synchronous_commit` off
can be a useful alternative when performance is more important than
exact certainty about the durability of a transaction.  For more
discussion see [wal-async-commit](#wal-async-commit).

If [guc-synchronous-standby-names](#guc-synchronous-standby-names) is non-empty,
`synchronous_commit` also controls whether
transaction commits will wait for their WAL records to be
processed on the standby server(s).

When set to `remote_apply`, commits will wait
until replies from the current synchronous standby(s) indicate they
have received the commit record of the transaction and applied
it, so that it has become visible to queries on the standby(s),
and also written to durable storage on the standbys.  This will
cause much larger commit delays than previous settings since
it waits for WAL replay.  When set to `on`,
commits wait until replies
from the current synchronous standby(s) indicate they have received
the commit record of the transaction and flushed it to durable storage.  This
ensures the transaction will not be lost unless both the primary and
all synchronous standbys suffer corruption of their database storage.
When set to `remote_write`, commits will wait until replies
from the current synchronous standby(s) indicate they have
received the commit record of the transaction and written it to
their file systems. This setting ensures data preservation if a standby instance of
PostgreSQL crashes, but not if the standby
suffers an operating-system-level crash because the data has not
necessarily reached durable storage on the standby.
The setting `local` causes commits to wait for
local flush to disk, but not for replication.  This is usually not
desirable when synchronous replication is in use, but is provided for
completeness.

This parameter can be changed at any time; the behavior for any
one transaction is determined by the setting in effect when it
commits.  It is therefore possible, and useful, to have some
transactions commit synchronously and others asynchronously.
For example, to make a single multistatement transaction commit
asynchronously when the default is the opposite, issue `SET
LOCAL synchronous_commit TO OFF` within the transaction.

[synchronous-commit-matrix](#synchronous-commit-matrix) summarizes the
capabilities of the `synchronous_commit` settings.

### Archiving

**`archive_mode` (`enum`)**
: When `archive_mode` is enabled, completed WAL segments
are sent to archive storage by setting
[guc-archive-command](#guc-archive-command) or
[guc-archive-library](#guc-archive-library). In addition to `off`,
to disable, there are two modes: `on`, and
`always`. During normal operation, there is no
difference between the two modes, but when set to `always`
the WAL archiver is enabled also during archive recovery or standby
mode. In `always` mode, all files restored from the archive
or streamed with streaming replication will be archived (again). See
[continuous-archiving-in-standby](#continuous-archiving-in-standby) for details.

`archive_mode` is a separate setting from
`archive_command` and
`archive_library` so that
`archive_command` and
`archive_library` can be changed without leaving
archiving mode.
This parameter can only be set at server start.
`archive_mode` cannot be enabled when
`wal_level` is set to `minimal`.

**`archive_command` (`string`)**
: The local shell command to execute to archive a completed WAL file
segment.  Any `%p` in the string is
replaced by the path name of the file to archive, and any
`%f` is replaced by only the file name.
(The path name is relative to the working directory of the server,
i.e., the cluster's data directory.)
Use `%%` to embed an actual `%` character in the
command.  It is important for the command to return a zero
exit status only if it succeeds. For more information see
[backup-archiving-wal](#backup-archiving-wal).

This parameter can only be set in the `postgresql.conf`
file or on the server command line.  It is only used if
`archive_mode` was enabled at server start and
`archive_library` is set to an empty string.  If both
`archive_command` and `archive_library`
are set, an error will be raised.
If `archive_command` is an empty string (the default) while
`archive_mode` is enabled (and `archive_library`
is set to an empty string), WAL archiving is temporarily
disabled, but the server continues to accumulate WAL segment files in
the expectation that a command will soon be provided.  Setting
`archive_command` to a command that does nothing but
return true, e.g., `/bin/true` (`REM` on
Windows), effectively disables
archiving, but also breaks the chain of WAL files needed for
archive recovery, so it should only be used in unusual circumstances.

**`archive_library` (`string`)**
: The library to use for archiving completed WAL file segments.  If set to
an empty string (the default), archiving via shell is enabled, and
[guc-archive-command](#guc-archive-command) is used.  If both
`archive_command` and `archive_library`
are set, an error will be raised.  Otherwise, the specified
shared library is used for archiving. The WAL archiver process is
restarted by the postmaster when this parameter changes. For more
information, see [backup-archiving-wal](#backup-archiving-wal) and
[archive-modules](#archive-modules).

This parameter can only be set in the
`postgresql.conf` file or on the server command line.

**`archive_timeout` (`integer`)**
: The [guc-archive-command](#guc-archive-command) or [guc-archive-library](#guc-archive-library) is only invoked for
completed WAL segments. Hence, if your server generates little WAL
traffic (or has slack periods where it does so), there could be a
long delay between the completion of a transaction and its safe
recording in archive storage.  To limit how old unarchived
data can be, you can set `archive_timeout` to force the
server to switch to a new WAL segment file periodically.  When this
parameter is greater than zero, the server will switch to a new
segment file whenever this amount of time has elapsed since the last
segment file switch, and there has been any database activity,
including a single checkpoint (checkpoints are skipped if there is
no database activity).  Note that archived files that are closed
early due to a forced switch are still the same length as completely
full files.  Therefore, it is unwise to use a very short
`archive_timeout` — it will bloat your archive
storage.  `archive_timeout` settings of a minute or so are
usually reasonable.  You should consider using streaming replication,
instead of archiving, if you want data to be copied off the primary
server more quickly than that.
If this value is specified without units, it is taken as seconds.
This parameter can only be set in the
`postgresql.conf` file or on the server command line.
