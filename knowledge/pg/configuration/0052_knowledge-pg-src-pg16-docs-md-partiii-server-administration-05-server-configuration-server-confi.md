# Checkpoints

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Write Ahead Log > Checkpoints`
- Source Line Ranges: `1734-1892, 2112-2194`
- Chunk ID: `pg16_configuration_0052_04fedf7751`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `566533a2e13a40973a96d67144d4a88f00f8f455a47b62450e802f034393505d`

## Retrieval Guidance

- Use When: 日志提示 checkpoint 过频、恢复时间或 checkpoint I/O 延迟需要调优。
- Retrieval Keywords: checkpoint_timeout, checkpoint_completion_target, checkpoint_flush_after, checkpoint_warning, max_wal_size, min_wal_size, checkpoints
- Follow-up Guidance: 提高 max_wal_size/checkpoint_timeout 会增加 crash recovery 时间。
- Classification Note: 定义 checkpoint_timeout、checkpoint_completion_target、checkpoint_flush_after、checkpoint_warning、max_wal_size、min_wal_size。

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

### Checkpoints

**`checkpoint_timeout` (`integer`)**
: Maximum time between automatic WAL checkpoints.
If this value is specified without units, it is taken as seconds.
The valid range is between 30 seconds and one day.
The default is five minutes (`5min`).
Increasing this parameter can increase the amount of time needed
for crash recovery.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`checkpoint_completion_target` (`floating point`)**
: Specifies the target of checkpoint completion, as a fraction of
total time between checkpoints. The default is 0.9, which spreads the
checkpoint across almost all of the available interval, providing fairly
consistent I/O load while also leaving some time for checkpoint
completion overhead.  Reducing this parameter is not recommended because
it causes the checkpoint to complete faster.  This results in a higher
rate of I/O during the checkpoint followed by a period of less I/O between
the checkpoint completion and the next scheduled checkpoint.  This
parameter can only be set in the `postgresql.conf` file
or on the server command line.

**`checkpoint_flush_after` (`integer`)**
: Whenever more than this amount of data has been
written while performing a checkpoint, attempt to force the
OS to issue these writes to the underlying storage.  Doing so will
limit the amount of dirty data in the kernel's page cache, reducing
the likelihood of stalls when an `fsync` is issued at the end of the
checkpoint, or when the OS writes data back in larger batches in the
background.  Often that will result in greatly reduced transaction
latency, but there also are some cases, especially with workloads
that are bigger than [guc-shared-buffers](#guc-shared-buffers), but smaller
than the OS's page cache, where performance might degrade.  This
setting may have no effect on some platforms.
If this value is specified without units, it is taken as blocks,
that is `BLCKSZ` bytes, typically 8kB.
The valid range is
between `0`, which disables forced writeback,
and `2MB`.  The default is `256kB` on
Linux, `0` elsewhere.  (If `BLCKSZ` is not
8kB, the default and maximum values scale proportionally to it.)
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`checkpoint_warning` (`integer`)**
: Write a message to the server log if checkpoints caused by
the filling of WAL segment files happen closer together
than this amount of time (which suggests that
`max_wal_size` ought to be raised).
If this value is specified without units, it is taken as seconds.
The default is 30 seconds (`30s`).
Zero disables the warning.
No warnings will be generated if `checkpoint_timeout`
is less than `checkpoint_warning`.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`max_wal_size` (`integer`)**
: Maximum size to let the WAL grow during automatic
checkpoints. This is a soft limit; WAL size can exceed
`max_wal_size` under special circumstances, such as
heavy load, a failing `archive_command` or `archive_library`, or a high
`wal_keep_size` setting.
If this value is specified without units, it is taken as megabytes.
The default is 1 GB.
Increasing this parameter can increase the amount of time needed for
crash recovery.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`min_wal_size` (`integer`)**
: As long as WAL disk usage stays below this setting, old WAL files are
always recycled for future use at a checkpoint, rather than removed.
This can be used to ensure that enough WAL space is reserved to
handle spikes in WAL usage, for example when running large batch
jobs.
If this value is specified without units, it is taken as megabytes.
The default is 80 MB.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
