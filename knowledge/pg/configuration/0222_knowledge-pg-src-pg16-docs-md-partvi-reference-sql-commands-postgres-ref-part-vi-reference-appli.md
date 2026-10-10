# Options / Environment / Examples

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/postgres-ref.md`
- Source Title: `postgres-ref`
- Source Heading Path: `Part VI Reference > Applications > postgres > Options / Environment / Examples`
- Source Line Ranges: `56-297, 298-314, 448-491`
- Chunk ID: `pg16_configuration_0222_66e0916d1f`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2b2f9d6fe66f0e7aacbcc6b3c9ff5f96536c9699a90d800b2f9175a60a3f7e2`

## Retrieval Guidance

- Use When: Use when configuring how the PostgreSQL server process starts or which runtime parameters are supplied at launch.
- Retrieval Keywords: postgres, server options, -D, -c name=value, PGDATA, listen_addresses, shared_buffers
- Follow-up Guidance: Prefer persistent postgresql.conf/ALTER SYSTEM for durable settings unless process launch options are intended.
- Classification Note: postgres server command-line options and environment variables set data directory, ports, listen addresses, buffers, runtime parameters, logging, SSL, and other server configuration.

## Official Source Content

## Options

`postgres` accepts the following command-line
arguments.  For a detailed discussion of the options consult [runtime-config](#runtime-config).  You can save typing most of these
options by setting up a configuration file.  Some (safe) options
can also be set from the connecting client in an
application-dependent way to apply only for that session.  For
example, if the environment variable `PGOPTIONS` is
set, then libpq-based clients will pass that
string to the server, which will interpret it as
`postgres` command-line options.

### General Purpose

**`-B `nbuffers``**
: Sets the number of shared buffers for use by the server
processes.  The default value of this parameter is chosen
automatically by initdb.
Specifying this option is equivalent to setting the
[guc-shared-buffers](#guc-shared-buffers) configuration parameter.

**`-c `name`=`value``**
: Sets a named run-time parameter. The configuration parameters
supported by PostgreSQL are
described in [runtime-config](#runtime-config). Most of the
other command line options are in fact short forms of such a
parameter assignment.  `-c` can appear multiple times
to set multiple parameters.

**`-C `name``**
: Prints the value of the named run-time parameter, and exits.
(See the `-c` option above for details.)  This
returns values from
`postgresql.conf`, modified by any parameters
supplied in this invocation.  It does not reflect parameters
supplied when the cluster was started.

This can be used on a running server for most parameters.  However,
the server must be shut down for some runtime-computed parameters
(e.g., [guc-shared-memory-size](#guc-shared-memory-size),
[guc-shared-memory-size-in-huge-pages](#guc-shared-memory-size-in-huge-pages), and
[guc-wal-segment-size](#guc-wal-segment-size)).

This option is meant for other programs that interact with a server
instance, such as [app-pg-ctl](#app-pg-ctl), to query configuration
parameter values.  User-facing applications should instead use [`SHOW`](#sql-show) or the `pg_settings` view.

**`-d `debug-level``**
: Sets the debug level.  The higher this value is set, the more
debugging output is written to the server log.  Values are
from 1 to 5.  It is also possible to pass `-d
0` for a specific session, which will prevent the
server log level of the parent `postgres` process from being
propagated to this session.

**`-D `datadir``**
: Specifies the file system location of the database
configuration files.  See
[runtime-config-file-locations](#runtime-config-file-locations) for details.

**`-e`**
: Sets the default date style to "European", that is
`DMY` ordering of input date fields.  This also causes
the day to be printed before the month in certain date output formats.
See [datatype-datetime](#datatype-datetime) for more information.

**`-F`**
: Disables `fsync` calls for improved
performance, at the risk of data corruption in the event of a
system crash.  Specifying this option is equivalent to
disabling the [guc-fsync](#guc-fsync) configuration
parameter. Read the detailed documentation before using this!

**`-h `hostname``**
: Specifies the IP host name or address on which
`postgres` is to listen for TCP/IP
connections from client applications.  The value can also be a
comma-separated list of addresses, or `*` to specify
listening on all available interfaces.  An empty value
specifies not listening on any IP addresses, in which case
only Unix-domain sockets can be used to connect to the
server.  Defaults to listening only on
localhost.
Specifying this option is equivalent to setting the [guc-listen-addresses](#guc-listen-addresses) configuration parameter.

**`-i`**
: Allows remote clients to connect via TCP/IP (Internet domain)
connections.  Without this option, only local connections are
accepted.  This option is equivalent to setting
`listen_addresses` to `*` in
`postgresql.conf` or via `-h`.

This option is deprecated since it does not allow access to the
full functionality of [guc-listen-addresses](#guc-listen-addresses).
It's usually better to set `listen_addresses` directly.

**`-k `directory``**
: Specifies the directory of the Unix-domain socket on which
`postgres` is to listen for
connections from client applications.  The value can also be a
comma-separated list of directories.  An empty value
specifies not listening on any Unix-domain sockets, in which case
only TCP/IP sockets can be used to connect to the server.
The default value is normally
`/tmp`, but that can be changed at build time.
Specifying this option is equivalent to setting the [guc-unix-socket-directories](#guc-unix-socket-directories) configuration parameter.

**`-l`**
: Enables secure connections using SSL.
PostgreSQL must have been compiled with
support for SSL for this option to be
available. For more information on using SSL,
refer to [ssl-tcp](#ssl-tcp).

**`-N `max-connections``**
: Sets the maximum number of client connections that this
server will accept.  The default value of this parameter is chosen
automatically by initdb.
Specifying this option is equivalent to setting the
[guc-max-connections](#guc-max-connections) configuration parameter.

**`-p `port``**
: Specifies the TCP/IP port or local Unix domain socket file
extension on which `postgres`
is to listen for connections from client applications.
Defaults to the value of the `PGPORT` environment
variable, or if `PGPORT` is not set, then
defaults to the value established during compilation (normally
5432).  If you specify a port other than the default port,
then all client applications must specify the same port using
either command-line options or `PGPORT`.

**`-s`**
: Print time information and other statistics at the end of each command.
This is useful for benchmarking or for use in tuning the number of
buffers.

**`-S` `work-mem`**
: Specifies the base amount of memory to be used by sorts and
hash tables before resorting to temporary disk files.  See the
description of the `work_mem` configuration
parameter in [runtime-config-resource-memory](#runtime-config-resource-memory).

**`-V`**
: Print the postgres version and exit.

**`--`name`=`value``**
: Sets a named run-time parameter; a shorter form of
`-c`.

**`--describe-config`**
: This option dumps out the server's internal configuration variables,
descriptions, and defaults in tab-delimited `COPY` format.
It is designed primarily for use by administration tools.

**`-?`**
: Show help about postgres command line
arguments, and exit.

### Semi-Internal Options

The options described here are used
mainly for debugging purposes, and in some cases to assist with
recovery of severely damaged databases. There should be no reason
to use them in a production database setup.  They are listed
here only for use by PostgreSQL
system developers.  Furthermore, these options might
change or be removed in a future release without notice.

**`-f` `{ s | i | o | b | t | n | m | h }`**
: Forbids the use of particular scan and join methods:
`s` and `i`
disable sequential and index scans respectively,
`o`, `b` and `t`
disable index-only scans, bitmap index scans, and TID scans
respectively, while
`n`, `m`, and `h`
disable nested-loop, merge and hash joins respectively.

Neither sequential scans nor nested-loop joins can be disabled
completely; the `-fs` and
`-fn` options simply discourage the optimizer
from using those plan types if it has any other alternative.

**`-O`**
: Allows the structure of system tables to be modified.  This is
used by `initdb`.

**`-P`**
: Ignore system indexes when reading system tables, but still update
the indexes when modifying the tables.  This is useful when
recovering from damaged system indexes.

**`-t` `pa[rser] | pl[anner] | e[xecutor]`**
: Print timing statistics for each query relating to each of the
major system modules.  This option cannot be used together
with the `-s` option.

**`-T`**
: This option is for debugging problems that cause a server
process to die abnormally.  The ordinary strategy in this
situation is to notify all other server processes that they
must terminate, by sending them SIGQUIT
signals.  With this option, SIGABRT
will be sent instead, resulting in production of core dump files.

**`-v` `protocol`**
: Specifies the version number of the frontend/backend protocol
to be used for a particular session.  This option is for
internal use only.

**`-W` `seconds`**
: A delay of this many seconds occurs when a new server process
is started, after it conducts the authentication procedure.
This is intended to give an opportunity to attach to the
server process with a debugger.

### Options for Single-User Mode

The following options only apply to the single-user mode
(see [app-postgres-single-user](#app-postgres-single-user) below).

**`--single`**
: Selects the single-user mode.  This must be the first argument
on the command line.

**`database`**
: Specifies the name of the database to be accessed.  This must be
the last argument on the command line.  If it is
omitted it defaults to the user name.

**`-E`**
: Echo all commands to standard output before executing them.

**`-j`**
: Use semicolon followed by two newlines, rather than just newline,
as the command entry terminator.

**`-r` `filename`**
: Send all server log output to `filename`.  This option is only
honored when supplied as a command-line option.

## Environment

**`PGCLIENTENCODING`**
: Default character encoding used by clients.  (The clients can
override this individually.)  This value can also be set in the
configuration file.

**`PGDATA`**
: Default data directory location

**`PGDATESTYLE`**
: Default value of the [guc-datestyle](#guc-datestyle) run-time
parameter.  (The use of this environment variable is deprecated.)

**`PGPORT`**
: Default port number (preferably set in the configuration file)

## Examples

To start `postgres` in the background
using default values, type:

```
$ nohup postgres >logfile 2>&1 </dev/null &
```

To start `postgres` with a specific
port, e.g., 1234:

```
$ postgres -p 1234
```

To connect to this server using psql, specify this port with the -p option:

```
$ psql -p 1234
```

or set the environment variable `PGPORT`:

```
$ export PGPORT=1234
$ psql
```

Named run-time parameters can be set in either of these styles:

```
$ postgres -c work_mem=1234
$ postgres --work-mem=1234
```

Either form overrides whatever setting might exist for
`work_mem` in `postgresql.conf`.  Notice that
underscores in parameter names can be written as either underscore
or dash on the command line.  Except for short-term experiments,
it's probably better practice to edit the setting in
`postgresql.conf` than to rely on a command-line switch
to set a parameter.
