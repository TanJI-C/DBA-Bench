# wal_compression, wal_init_zero, wal_recycle, wal_buffers, wal_writer_delay, wal_writer_flush_after, wal_skip_threshold, commit_delay, commit_siblings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Write Ahead Log > Settings > wal_compression, wal_init_zero, wal_recycle, wal_buffers, wal_writer_delay, wal_writer_flush_after, wal_skip_threshold, commit_delay, commit_siblings`
- Source Line Ranges: `431-602, 603-674, 1734-1892`
- Chunk ID: `pg16_configuration_0051_e190a91d5d`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2fe69faba2a3e098a02bc16e979f7dc6f181de5af301d2a3022801f513fc150c`

## Retrieval Guidance

- Use When: 需要调优 WAL 写入吞吐、延迟、空间或 COW 文件系统行为。
- Retrieval Keywords: wal_compression, wal_init_zero, wal_recycle, wal_buffers, wal_writer_delay, wal_writer_flush_after, wal_skip_threshold, commit_delay, commit_siblings
- Follow-up Guidance: commit_delay 只在高并发且 fsync 开启时可能收益。
- Classification Note: 定义 WAL 体积、预分配/回收、WAL buffer、WAL writer 和 group commit 行为。

## Official Source Content

### Connection Settings

**`listen_addresses` (`string`)**
: Specifies the TCP/IP address(es) on which the server is
to listen for connections from client applications.
The value takes the form of a comma-separated list of host names
and/or numeric IP addresses.  The special entry `*`
corresponds to all available IP interfaces.  The entry
`0.0.0.0` allows listening for all IPv4 addresses and
`::` allows listening for all IPv6 addresses.
If the list is empty, the server does not listen on any IP interface
at all, in which case only Unix-domain sockets can be used to connect
to it.  If the list is not empty, the server will start if it
can listen on at least one TCP/IP address.  A warning will be
emitted for any TCP/IP address which cannot be opened.
The default value is localhost,
which allows only local TCP/IP "loopback" connections to be
made.

While client authentication ([client-authentication](#client-authentication)) allows fine-grained control
over who can access the server, `listen_addresses`
controls which interfaces accept connection attempts, which
can help prevent repeated malicious connection requests on
insecure network interfaces.  This parameter can only be set
at server start.

**`port` (`integer`)**
: The TCP port the server listens on; 5432 by default.  Note that the
same port number is used for all IP addresses the server listens on.
This parameter can only be set at server start.

**`max_connections` (`integer`)**
: Determines the maximum number of concurrent connections to the
database server. The default is typically 100 connections, but
might be less if your kernel settings will not support it (as
determined during initdb).  This parameter can
only be set at server start.

When running a standby server, you must set this parameter to the
same or higher value than on the primary server. Otherwise, queries
will not be allowed in the standby server.

**`reserved_connections` (`integer`)**
: Determines the number of connection "slots" that are
reserved for connections by roles with privileges of the
[`pg_use_reserved_connections`](#predefined-roles-table)
role.  Whenever the number of free connection slots is greater than
[guc-superuser-reserved-connections](#guc-superuser-reserved-connections) but less than or
equal to the sum of `superuser_reserved_connections`
and `reserved_connections`, new connections will be
accepted only for superusers and roles with privileges of
`pg_use_reserved_connections`.  If
`superuser_reserved_connections` or fewer connection
slots are available, new connections will be accepted only for
superusers.

The default value is zero connections.  The value must be less than
`max_connections` minus
`superuser_reserved_connections`.  This parameter can
only be set at server start.

**`superuser_reserved_connections`
(`integer`)**
: Determines the number of connection "slots" that
are reserved for connections by PostgreSQL
superusers.  At most [guc-max-connections](#guc-max-connections)
connections can ever be active simultaneously.  Whenever the
number of active concurrent connections is at least
`max_connections` minus
`superuser_reserved_connections`, new
connections will be accepted only for superusers.  The connection slots
reserved by this parameter are intended as final reserve for emergency
use after the slots reserved by
[guc-reserved-connections](#guc-reserved-connections) have been exhausted.

The default value is three connections. The value must be less
than `max_connections` minus
`reserved_connections`.
This parameter can only be set at server start.

**`unix_socket_directories` (`string`)**
: Specifies the directory of the Unix-domain socket(s) on which the
server is to listen for connections from client applications.
Multiple sockets can be created by listing multiple directories
separated by commas.  Whitespace between entries is
ignored; surround a directory name with double quotes if you need
to include whitespace or commas in the name.
An empty value
specifies not listening on any Unix-domain sockets, in which case
only TCP/IP sockets can be used to connect to the server.

A value that starts with `@` specifies that a
Unix-domain socket in the abstract namespace should be created
(currently supported on Linux only).  In that case, this value
does not specify a "directory" but a prefix from which
the actual socket name is computed in the same manner as for the
file-system namespace.  While the abstract socket name prefix can be
chosen freely, since it is not a file-system location, the convention
is to nonetheless use file-system-like values such as
`@/tmp`.

The default value is normally
`/tmp`, but that can be changed at build time.
On Windows, the default is empty, which means no Unix-domain socket is
created by default.
This parameter can only be set at server start.

In addition to the socket file itself, which is named
`.s.PGSQL.`nnnn`` where
`nnnn` is the server's port number, an ordinary file
named `.s.PGSQL.`nnnn`.lock` will be
created in each of the `unix_socket_directories` directories.
Neither file should ever be removed manually.
For sockets in the abstract namespace, no lock file is created.

**`unix_socket_group` (`string`)**
: Sets the owning group of the Unix-domain socket(s).  (The owning
user of the sockets is always the user that starts the
server.)  In combination with the parameter
`unix_socket_permissions` this can be used as
an additional access control mechanism for Unix-domain connections.
By default this is the empty string, which uses the default
group of the server user.  This parameter can only be set at
server start.

This parameter is not supported on Windows.  Any setting will be
ignored.  Also, sockets in the abstract namespace have no file owner,
so this setting is also ignored in that case.

**`unix_socket_permissions` (`integer`)**
: Sets the access permissions of the Unix-domain socket(s).  Unix-domain
sockets use the usual Unix file system permission set.
The parameter value is expected to be a numeric mode
specified in the format accepted by the
`chmod` and `umask`
system calls.  (To use the customary octal format the number
must start with a `0` (zero).)

The default permissions are `0777`, meaning
anyone can connect. Reasonable alternatives are
`0770` (only user and group, see also
`unix_socket_group`) and `0700`
(only user). (Note that for a Unix-domain socket, only write
permission matters, so there is no point in setting or revoking
read or execute permissions.)

This access control mechanism is independent of the one
described in [client-authentication](#client-authentication).

This parameter can only be set at server start.

This parameter is irrelevant on systems, notably Solaris as of Solaris
10, that ignore socket permissions entirely.  There, one can achieve a
similar effect by pointing `unix_socket_directories` to a
directory having search permission limited to the desired audience.

Sockets in the abstract namespace have no file permissions, so this
setting is also ignored in that case.

**`bonjour` (`boolean`)**
: Enables advertising the server's existence via
Bonjour.  The default is off.
This parameter can only be set at server start.

**`bonjour_name` (`string`)**
: Specifies the Bonjour service
name.  The computer name is used if this parameter is set to the
empty string `''` (which is the default).  This parameter is
ignored if the server was not compiled with
Bonjour support.
This parameter can only be set at server start.

### TCP Settings

**`tcp_keepalives_idle` (`integer`)**
: Specifies the amount of time with no network activity after which
the operating system should send a TCP keepalive message to the client.
If this value is specified without units, it is taken as seconds.
A value of 0 (the default) selects the operating system's default.
On Windows, setting a value of 0 will set this parameter to 2 hours,
since Windows does not provide a way to read the system default value.
This parameter is supported only on systems that support
`TCP_KEEPIDLE` or an equivalent socket option, and on
Windows; on other systems, it must be zero.
In sessions connected via a Unix-domain socket, this parameter is
ignored and always reads as zero.

**`tcp_keepalives_interval` (`integer`)**
: Specifies the amount of time after which a TCP keepalive message
that has not been acknowledged by the client should be retransmitted.
If this value is specified without units, it is taken as seconds.
A value of 0 (the default) selects the operating system's default.
On Windows, setting a value of 0 will set this parameter to 1 second,
since Windows does not provide a way to read the system default value.
This parameter is supported only on systems that support
`TCP_KEEPINTVL` or an equivalent socket option, and on
Windows; on other systems, it must be zero.
In sessions connected via a Unix-domain socket, this parameter is
ignored and always reads as zero.

**`tcp_keepalives_count` (`integer`)**
: Specifies the number of TCP keepalive messages that can be lost before
the server's connection to the client is considered dead.
A value of 0 (the default) selects the operating system's default.
This parameter is supported only on systems that support
`TCP_KEEPCNT` or an equivalent socket option (which does not include Windows);
on other systems, it must be zero.
In sessions connected via a Unix-domain socket, this parameter is
ignored and always reads as zero.

**`tcp_user_timeout` (`integer`)**
: Specifies the amount of time that transmitted data may
remain unacknowledged before the TCP connection is forcibly closed.
If this value is specified without units, it is taken as milliseconds.
A value of 0 (the default) selects the operating system's default.
This parameter is supported only on systems that support
`TCP_USER_TIMEOUT` (which does not include Windows); on other systems, it must be zero.
In sessions connected via a Unix-domain socket, this parameter is
ignored and always reads as zero.

**`client_connection_check_interval` (`integer`)**
: Sets the time interval between optional checks that the client is still
connected, while running queries.  The check is performed by polling
the socket, and allows long running queries to be aborted sooner if
the kernel reports that the connection is closed.

This option relies on kernel events exposed by Linux, macOS, illumos
and the BSD family of operating systems, and is not currently available
on other systems.

If the value is specified without units, it is taken as milliseconds.
The default value is `0`, which disables connection
checks.  Without connection checks, the server will detect the loss of
the connection only at the next interaction with the socket, when it
waits for, receives or sends data.

For the kernel itself to detect lost TCP connections reliably and within
a known timeframe in all scenarios including network failure, it may
also be necessary to adjust the TCP keepalive settings of the operating
system, or the [guc-tcp-keepalives-idle](#guc-tcp-keepalives-idle),
[guc-tcp-keepalives-interval](#guc-tcp-keepalives-interval) and
[guc-tcp-keepalives-count](#guc-tcp-keepalives-count) settings of
PostgreSQL.

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
