# Recovery Target

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Write Ahead Log > Recovery Target`
- Source Line Ranges: `1734-1892, 2438-2567`
- Chunk ID: `pg16_configuration_0056_0232a20b03`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `70f49058ee3fc14fea0abba14e12b8aaf88734760cc34b116fa51ac85a6f8a6b`

## Retrieval Guidance

- Use When: 需要设置 PITR 停止点或到达目标后的 pause/promote/shutdown 行为。
- Retrieval Keywords: recovery_target, recovery_target_time, recovery_target_xid, recovery_target_lsn, recovery_target_inclusive, recovery_target_timeline, recovery_target_action, PITR
- Follow-up Guidance: 同一配置最多设置一个 recovery target；pause 后用 pg_wal_replay_resume。
- Classification Note: 定义 recovery_target、target name/time/xid/lsn、inclusive、timeline、target_action。

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

### Recovery Target

By default, recovery will recover to the end of the WAL log. The
following parameters can be used to specify an earlier stopping point.
At most one of `recovery_target`,
`recovery_target_lsn`, `recovery_target_name`,
`recovery_target_time`, or `recovery_target_xid`
can be used; if more than one of these is specified in the configuration
file, an error will be raised.
These parameters can only be set at server start.

**`recovery_target`` = 'immediate'`**
: This parameter specifies that recovery should end as soon as a
consistent state is reached, i.e., as early as possible. When restoring
from an online backup, this means the point where taking the backup
ended.

Technically, this is a string parameter, but `'immediate'`
is currently the only allowed value.

**`recovery_target_name` (`string`)**
: This parameter specifies the named restore point (created with
`pg_create_restore_point()`) to which recovery will proceed.

**`recovery_target_time` (`timestamp`)**
: This parameter specifies the time stamp up to which recovery
will proceed.
The precise stopping point is also influenced by
[guc-recovery-target-inclusive](#guc-recovery-target-inclusive).

The value of this parameter is a time stamp in the same format
accepted by the `timestamp with time zone` data type,
except that you cannot use a time zone abbreviation (unless the
[guc-timezone-abbreviations](#guc-timezone-abbreviations) variable has been set
earlier in the configuration file).  Preferred style is to use a
numeric offset from UTC, or you can write a full time zone name,
e.g., `Europe/Helsinki` not `EEST`.

**`recovery_target_xid` (`string`)**
: This parameter specifies the transaction ID up to which recovery
will proceed. Keep in mind
that while transaction IDs are assigned sequentially at transaction
start, transactions can complete in a different numeric order.
The transactions that will be recovered are those that committed
before (and optionally including) the specified one.
The precise stopping point is also influenced by
[guc-recovery-target-inclusive](#guc-recovery-target-inclusive).

**`recovery_target_lsn` (`pg_lsn`)**
: This parameter specifies the LSN of the write-ahead log location up
to which recovery will proceed. The precise stopping point is also
influenced by [guc-recovery-target-inclusive](#guc-recovery-target-inclusive). This
parameter is parsed using the system data type
[`pg_lsn`](#datatype-pg-lsn).

The following options further specify the recovery target, and affect
what happens when the target is reached:

**`recovery_target_inclusive` (`boolean`)**
: Specifies whether to stop just after the specified recovery target
(`on`), or just before the recovery target
(`off`).
Applies when [guc-recovery-target-lsn](#guc-recovery-target-lsn),
[guc-recovery-target-time](#guc-recovery-target-time), or
[guc-recovery-target-xid](#guc-recovery-target-xid) is specified.
This setting controls whether transactions
having exactly the target WAL location (LSN), commit time, or transaction ID, respectively, will
be included in the recovery.  Default is `on`.

**`recovery_target_timeline` (`string`)**
: Specifies recovering into a particular timeline.  The value can be a
numeric timeline ID or a special value.  The value
`current` recovers along the same timeline that was
current when the base backup was taken.  The
value `latest` recovers
to the latest timeline found in the archive, which is useful in
a standby server.  `latest` is the default.

To specify a timeline ID in hexadecimal (for example, if extracted
from a WAL file name or history file), prefix it with a
`0x`.  For instance, if the WAL file name is
`00000011000000A10000004F`, then the timeline ID is
`0x11` (or 17 decimal).

You usually only need to set this parameter
in complex re-recovery situations, where you need to return to
a state that itself was reached after a point-in-time recovery.
See [backup-timelines](#backup-timelines) for discussion.

**`recovery_target_action` (`enum`)**
: Specifies what action the server should take once the recovery target is
reached. The default is `pause`, which means recovery will
be paused. `promote` means the recovery process will finish
and the server will start to accept connections.
Finally `shutdown` will stop the server after reaching the
recovery target.

The intended use of the `pause` setting is to allow queries
to be executed against the database to check if this recovery target
is the most desirable point for recovery.
The paused state can be resumed by
using `pg_wal_replay_resume()` (see
[functions-recovery-control-table](#functions-recovery-control-table)), which then
causes recovery to end. If this recovery target is not the
desired stopping point, then shut down the server, change the
recovery target settings to a later target and restart to
continue recovery.

The `shutdown` setting is useful to have the instance ready
at the exact replay point desired.  The instance will still be able to
replay more WAL records (and in fact will have to replay WAL records
since the last checkpoint next time it is started).

Note that because `recovery.signal` will not be
removed when `recovery_target_action` is set to `shutdown`,
any subsequent start will end with immediate shutdown unless the
configuration is changed or the `recovery.signal`
file is removed manually.

This setting has no effect if no recovery target is set.
If [guc-hot-standby](#guc-hot-standby) is not enabled, a setting of
`pause` will act the same as `shutdown`.
If the recovery target is reached while a promotion is ongoing,
a setting of `pause` will act the same as
`promote`.

In any case, if a recovery target is configured but the archive
recovery ends before the target is reached, the server will shut down
with a fatal error.
