# Archive Recovery

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Write Ahead Log > Archive Recovery`
- Source Line Ranges: `1734-1892, 2317-2437`
- Chunk ID: `pg16_configuration_0055_b8fd4da050`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ce02e45cdf9997817487d06098f5d924f3f0b81ad6e96ba3393276e78107fd5c`

## Retrieval Guidance

- Use When: 需要配置 standby 或基于归档的目标恢复。
- Retrieval Keywords: standby.signal, recovery.signal, restore_command, archive_cleanup_command, recovery_end_command, pg_archivecleanup
- Follow-up Guidance: 多 standby 共用 archive 时不要过早清理仍被其他 standby 需要的 WAL。
- Classification Note: 定义 standby.signal/recovery.signal、restore_command、archive_cleanup_command、recovery_end_command。

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

### Archive Recovery

This section describes the settings that apply only for the duration of
the recovery.  They must be reset for any subsequent recovery you wish to
perform.

"Recovery" covers using the server as a standby or for
executing a targeted recovery.  Typically, standby mode would be used to
provide high availability and/or read scalability, whereas a targeted
recovery is used to recover from data loss.

To start the server in standby mode, create a file called
`standby.signal`
in the data directory.  The server will enter recovery and will not stop
recovery when the end of archived WAL is reached, but will keep trying to
continue recovery by connecting to the sending server as specified by the
`primary_conninfo` setting and/or by fetching new WAL
segments using `restore_command`.  For this mode, the
parameters from this section and [runtime-config-replication-standby](#runtime-config-replication-standby) are of interest.
Parameters from [runtime-config-wal-recovery-target](#runtime-config-wal-recovery-target) will
also be applied but are typically not useful in this mode.

To start the server in targeted recovery mode, create a file called
`recovery.signal`
in the data directory.  If both `standby.signal` and
`recovery.signal` files are created, standby mode
takes precedence.  Targeted recovery mode ends when the archived WAL is
fully replayed, or when `recovery_target` is reached.
In this mode, the parameters from both this section and [runtime-config-wal-recovery-target](#runtime-config-wal-recovery-target) will be used.

**`restore_command` (`string`)**
: The local shell command to execute to retrieve an archived segment of
the WAL file series. This parameter is required for archive recovery,
but optional for streaming replication.
Any `%f` in the string is
replaced by the name of the file to retrieve from the archive,
and any `%p` is replaced by the copy destination path name
on the server.
(The path name is relative to the current working directory,
i.e., the cluster's data directory.)
Any `%r` is replaced by the name of the file containing the
last valid restart point. That is the earliest file that must be kept
to allow a restore to be restartable, so this information can be used
to truncate the archive to just the minimum required to support
restarting from the current restore. `%r` is typically only
used by warm-standby configurations
(see [warm-standby](#warm-standby)).
Write `%%` to embed an actual `%` character.

It is important for the command to return a zero exit status
only if it succeeds.  The command *will* be asked for file
names that are not present in the archive; it must return nonzero
when so asked.  Examples:

```
restore_command = 'cp /mnt/server/archivedir/%f "%p"'
restore_command = 'copy "C:\\server\\archivedir\\%f" "%p"'  # Windows
```

An exception is that if the command was terminated by a signal (other
than SIGTERM, which is used as part of a
database server shutdown) or an error by the shell (such as command
not found), then recovery will abort and the server will not start up.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`archive_cleanup_command` (`string`)**
: This optional parameter specifies a shell command that will be executed
at every restartpoint.  The purpose of
`archive_cleanup_command` is to provide a mechanism for
cleaning up old archived WAL files that are no longer needed by the
standby server.
Any `%r` is replaced by the name of the file containing the
last valid restart point.
That is the earliest file that must be *kept* to allow a
restore to be restartable, and so all files earlier than `%r`
may be safely removed.
This information can be used to truncate the archive to just the
minimum required to support restart from the current restore.
The [pgarchivecleanup](#pgarchivecleanup) module
is often used in `archive_cleanup_command` for
single-standby configurations, for example:

```
archive_cleanup_command = 'pg_archivecleanup /mnt/server/archivedir %r'
```

Note however that if multiple standby servers are restoring from the
same archive directory, you will need to ensure that you do not delete
WAL files until they are no longer needed by any of the servers.
`archive_cleanup_command` would typically be used in a
warm-standby configuration (see [warm-standby](#warm-standby)).
Write `%%` to embed an actual `%` character in the
command.

If the command returns a nonzero exit status then a warning log
message will be written.  An exception is that if the command was
terminated by a signal or an error by the shell (such as command not
found), a fatal error will be raised.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`recovery_end_command` (`string`)**
: This parameter specifies a shell command that will be executed once only
at the end of recovery. This parameter is optional. The purpose of the
`recovery_end_command` is to provide a mechanism for cleanup
following replication or recovery.
Any `%r` is replaced by the name of the file containing the
last valid restart point, like in [guc-archive-cleanup-command](#guc-archive-cleanup-command).

If the command returns a nonzero exit status then a warning log
message will be written and the database will proceed to start up
anyway.  An exception is that if the command was terminated by a
signal or an error by the shell (such as command not found), the
database will not proceed with startup.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.
