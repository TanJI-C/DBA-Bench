# Setting Up a Standby Server

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/12_high_availability,_load_balancing,_and_replication.md`
- Source Title: `High Availability, Load Balancing, and Replication`
- Source Heading Path: `High Availability, Load Balancing, and Replication > Log-Shipping Standby Servers > Setting Up a Standby Server`
- Source Line Ranges: `218-481`
- Chunk ID: `pg16_solution_0059_6812600b9c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `86c9fcd428410d0f8eb6fb1eff6d3122902bda98637943351afa1b04f81aa1f4`

## Retrieval Guidance

- Use When: 需要实际搭建物理 standby 或修复 standby 初始化步骤。
- Retrieval Keywords: set up standby, standby.signal, restore_command, primary_conninfo, archive_cleanup_command, pg_archivecleanup
- Follow-up Guidance: 确认 WAL archive 可达、primary_conninfo 凭据正确、recovery_target_timeline 为 latest。
- Classification Note: 给出恢复 base backup、创建 standby.signal 和设置连接/归档的操作。

## Official Source Content

## Log-Shipping Standby Servers

Continuous archiving can be used to create a *high
availability* (HA) cluster configuration with one or more
*standby servers* ready to take over operations if the
primary server fails. This capability is widely referred to as
*warm standby* or *log shipping*.

The primary and standby server work together to provide this capability,
though the servers are only loosely coupled. The primary server operates
in continuous archiving mode, while each standby server operates in
continuous recovery mode, reading the WAL files from the primary. No
changes to the database tables are required to enable this capability,
so it offers low administration overhead compared to some other
replication solutions. This configuration also has relatively low
performance impact on the primary server.

Directly moving WAL records from one database server to another
is typically described as log shipping. PostgreSQL
implements file-based log shipping by transferring WAL records
one file (WAL segment) at a time. WAL files (16MB) can be
shipped easily and cheaply over any distance, whether it be to an
adjacent system, another system at the same site, or another system on
the far side of the globe. The bandwidth required for this technique
varies according to the transaction rate of the primary server.
Record-based log shipping is more granular and streams WAL changes
incrementally over a network connection (see [streaming-replication](#streaming-replication)).

It should be noted that log shipping is asynchronous, i.e., the WAL
records are shipped after transaction commit. As a result, there is a
window for data loss should the primary server suffer a catastrophic
failure; transactions not yet shipped will be lost.  The size of the
data loss window in file-based log shipping can be limited by use of the
`archive_timeout` parameter, which can be set as low
as a few seconds.  However such a low setting will
substantially increase the bandwidth required for file shipping.
Streaming replication (see [streaming-replication](#streaming-replication))
allows a much smaller window of data loss.

Recovery performance is sufficiently good that the standby will
typically be only moments away from full
availability once it has been activated. As a result, this is called
a warm standby configuration which offers high
availability. Restoring a server from an archived base backup and
rollforward will take considerably longer, so that technique only
offers a solution for disaster recovery, not high availability.
A standby server can also be used for read-only queries, in which case
it is called a *hot standby* server. See
[hot-standby](#hot-standby) for more information.

### Planning

It is usually wise to create the primary and standby servers
so that they are as similar as possible, at least from the
perspective of the database server.  In particular, the path names
associated with tablespaces will be passed across unmodified, so both
primary and standby servers must have the same mount paths for
tablespaces if that feature is used.  Keep in mind that if
[sql-createtablespace](#sql-createtablespace)
is executed on the primary, any new mount point needed for it must
be created on the primary and all standby servers before the command
is executed. Hardware need not be exactly the same, but experience shows
that maintaining two identical systems is easier than maintaining two
dissimilar ones over the lifetime of the application and system.
In any case the hardware architecture must be the same — shipping
from, say, a 32-bit to a 64-bit system will not work.

In general, log shipping between servers running different major
PostgreSQL release
levels is not possible. It is the policy of the PostgreSQL Global
Development Group not to make changes to disk formats during minor release
upgrades, so it is likely that running different minor release levels
on primary and standby servers will work successfully. However, no
formal support for that is offered and you are advised to keep primary
and standby servers at the same release level as much as possible.
When updating to a new minor release, the safest policy is to update
the standby servers first — a new minor release is more likely
to be able to read WAL files from a previous minor release than vice
versa.

### Standby Server Operation

A server enters standby mode if a

`standby.signal`

file exists in the data directory when the server is started.

In standby mode, the server continuously applies WAL received from the
primary server. The standby server can read WAL from a WAL archive
(see [guc-restore-command](#guc-restore-command)) or directly from the primary
over a TCP connection (streaming replication). The standby server will
also attempt to restore any WAL found in the standby cluster's
`pg_wal` directory. That typically happens after a server
restart, when the standby replays again WAL that was streamed from the
primary before the restart, but you can also manually copy files to
`pg_wal` at any time to have them replayed.

At startup, the standby begins by restoring all WAL available in the
archive location, calling `restore_command`. Once it
reaches the end of WAL available there and `restore_command`
fails, it tries to restore any WAL available in the `pg_wal` directory.
If that fails, and streaming replication has been configured, the
standby tries to connect to the primary server and start streaming WAL
from the last valid record found in archive or `pg_wal`. If that fails
or streaming replication is not configured, or if the connection is
later disconnected, the standby goes back to step 1 and tries to
restore the file from the archive again. This loop of retries from the
archive, `pg_wal`, and via streaming replication goes on until the server
is stopped or is promoted.

Standby mode is exited and the server switches to normal operation
when `pg_ctl promote` is run, or
`pg_promote()` is called. Before failover,
any WAL immediately available in the archive or in `pg_wal`
will be restored, but no attempt is made to connect to the primary.

### Preparing the Primary for Standby Servers

Set up continuous archiving on the primary to an archive directory
accessible from the standby, as described
in [continuous-archiving](#continuous-archiving). The archive location should be
accessible from the standby even when the primary is down, i.e., it should
reside on the standby server itself or another trusted server, not on
the primary server.

If you want to use streaming replication, set up authentication on the
primary server to allow replication connections from the standby
server(s); that is, create a role and provide a suitable entry or
entries in `pg_hba.conf` with the database field set to
`replication`.  Also ensure `max_wal_senders` is set
to a sufficiently large value in the configuration file of the primary
server. If replication slots will be used,
ensure that `max_replication_slots` is set sufficiently
high as well.

Take a base backup as described in [backup-base-backup](#backup-base-backup)
to bootstrap the standby server.

### Setting Up a Standby Server

To set up the standby server, restore the base backup taken from primary
server (see [backup-pitr-recovery](#backup-pitr-recovery)). Create a file
[`standby.signal`](#file-standby-signal)
in the standby's cluster data
directory. Set [guc-restore-command](#guc-restore-command) to a simple command to copy files from
the WAL archive. If you plan to have multiple standby servers for high
availability purposes, make sure that `recovery_target_timeline` is set to
`latest` (the default), to make the standby server follow the timeline change
that occurs at failover to another standby.

> **Note:**

> [guc-restore-command](#guc-restore-command) should return immediately
> if the file does not exist; the server will retry the command again if
> necessary.
>

If you want to use streaming replication, fill in
[guc-primary-conninfo](#guc-primary-conninfo) with a libpq connection string, including
the host name (or IP address) and any additional details needed to
connect to the primary server. If the primary needs a password for
authentication, the password needs to be specified in
[guc-primary-conninfo](#guc-primary-conninfo) as well.

If you're setting up the standby server for high availability purposes,
set up WAL archiving, connections and authentication like the primary
server, because the standby server will work as a primary server after
failover.

If you're using a WAL archive, its size can be minimized using the [guc-archive-cleanup-command](#guc-archive-cleanup-command) parameter to remove files that are no
longer required by the standby server.
The pg_archivecleanup utility is designed specifically to
be used with `archive_cleanup_command` in typical single-standby
configurations, see [pgarchivecleanup](#pgarchivecleanup).
Note however, that if you're using the archive for backup purposes, you
need to retain files needed to recover from at least the latest base
backup, even if they're no longer needed by the standby.

A simple example of configuration is:

```
primary_conninfo = 'host=192.168.1.50 port=5432 user=foo password=foopass options=''-c wal_sender_timeout=5000'''
restore_command = 'cp /path/to/archive/%f %p'
archive_cleanup_command = 'pg_archivecleanup /path/to/archive %r'
```

You can have any number of standby servers, but if you use streaming
replication, make sure you set `max_wal_senders` high enough in
the primary to allow them to be connected simultaneously.

### Streaming Replication

Streaming replication allows a standby server to stay more up-to-date
than is possible with file-based log shipping. The standby connects
to the primary, which streams WAL records to the standby as they're
generated, without waiting for the WAL file to be filled.

Streaming replication is asynchronous by default
(see [synchronous-replication](#synchronous-replication)), in which case there is
a small delay between committing a transaction in the primary and the
changes becoming visible in the standby. This delay is however much
smaller than with file-based log shipping, typically under one second
assuming the standby is powerful enough to keep up with the load. With
streaming replication, `archive_timeout` is not required to
reduce the data loss window.

If you use streaming replication without file-based continuous
archiving, the server might recycle old WAL segments before the standby
has received them.  If this occurs, the standby will need to be
reinitialized from a new base backup.  You can avoid this by setting
`wal_keep_size` to a value large enough to ensure that
WAL segments are not recycled too early, or by configuring a replication
slot for the standby.  If you set up a WAL archive that's accessible from
the standby, these solutions are not required, since the standby can
always use the archive to catch up provided it retains enough segments.

To use streaming replication, set up a file-based log-shipping standby
server as described in [warm-standby](#warm-standby). The step that
turns a file-based log-shipping standby into streaming replication
standby is setting the `primary_conninfo` setting
to point to the primary server. Set
[guc-listen-addresses](#guc-listen-addresses) and authentication options
(see `pg_hba.conf`) on the primary so that the standby server
can connect to the `replication` pseudo-database on the primary
server (see [streaming-replication-authentication](#streaming-replication-authentication)).

On systems that support the keepalive socket option, setting
[guc-tcp-keepalives-idle](#guc-tcp-keepalives-idle),
[guc-tcp-keepalives-interval](#guc-tcp-keepalives-interval) and
[guc-tcp-keepalives-count](#guc-tcp-keepalives-count) helps the primary promptly
notice a broken connection.

Set the maximum number of concurrent connections from the standby servers
(see [guc-max-wal-senders](#guc-max-wal-senders) for details).

When the standby is started and `primary_conninfo` is set
correctly, the standby will connect to the primary after replaying all
WAL files available in the archive. If the connection is established
successfully, you will see a `walreceiver` in the standby, and
a corresponding `walsender` process in the primary.

#### Authentication

It is very important that the access privileges for replication be set up
so that only trusted users can read the WAL stream, because it is
easy to extract privileged information from it.  Standby servers must
authenticate to the primary as an account that has the
`REPLICATION` privilege or a superuser. It is
recommended to create a dedicated user account with
`REPLICATION` and `LOGIN`
privileges for replication. While `REPLICATION`
privilege gives very high permissions, it does not allow the user to
modify any data on the primary system, which the
`SUPERUSER` privilege does.

Client authentication for replication is controlled by a
`pg_hba.conf` record specifying `replication` in the
`database` field. For example, if the standby is running on
host IP `192.168.1.100` and the account name for replication
is `foo`, the administrator can add the following line to the
`pg_hba.conf` file on the primary:

```
