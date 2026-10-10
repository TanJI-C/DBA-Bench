# init/start/reload/register/options/environment

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/pg_ctl-ref.md`
- Source Title: `pg ctl-ref`
- Source Heading Path: `Part VI Reference > Client Applications > pg_ctl > init/start/reload/register/options/environment`
- Source Line Ranges: `197-336, 337-352, 369-384, 400-418`
- Chunk ID: `pg16_configuration_0228_e6c125b3d3`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4f6be6dbf459a875f4513d1f8e83f4a4651bf7bbcef6b24027225306cd05473d`

## Retrieval Guidance

- Use When: Use when configuring how an instance is initialized, started, reloaded, or registered as a service.
- Retrieval Keywords: pg_ctl, pg_ctl start, pg_ctl reload, PGDATA, PGCTLTIMEOUT, postgres options, service register
- Follow-up Guidance: Verify effective server options with pg_ctl status, postgres command line, SHOW, or logs.
- Classification Note: Controls initialization/start options, data directory, postgres/initdb options, reload of configuration files, Windows service registration, and environment defaults.

## Official Source Content

## Options

**`-c`**
: Attempt to allow server crashes to produce core files, on platforms
where this is possible, by lifting any soft resource limit placed on
core files.
This is useful in debugging or diagnosing problems by allowing a
stack trace to be obtained from a failed server process.

**`-D `datadir``**
: Specifies the file system location of the database configuration files.  If
this option is omitted, the environment variable
`PGDATA` is used.

**`-l `filename``**
: Append the server log output to
`filename`.  If the file does not
exist, it is created.  By default, only the cluster owner can
access the log file.  If group access is enabled in the cluster,
users in the same group as the cluster owner can also read it.

**`-m `mode``**
: Specifies the shutdown mode.  `mode`
can be `smart`, `fast`, or
`immediate`, or the first letter of one of
these three.  If this option is omitted, `fast` is
the default.

**`-o `options``**
: Specifies options to be passed directly to the
`postgres` command.
`-o` can be specified multiple times, with all the given
options being passed through.

The `options` should usually be surrounded by single or
double quotes to ensure that they are passed through as a group.

**`-o `initdb-options``**
: Specifies options to be passed directly to the
`initdb` command.
`-o` can be specified multiple times, with all the given
options being passed through.

The `initdb-options` should usually be surrounded by single or
double quotes to ensure that they are passed through as a group.

**`-p `path``**
: Specifies the location of the `postgres`
executable.  By default the `postgres` executable is taken from the same
directory as `pg_ctl`, or failing that, the hard-wired
installation directory.  It is not necessary to use this
option unless you are doing something unusual and get errors
that the `postgres` executable was not found.

In `init` mode, this option analogously
specifies the location of the `initdb`
executable.

**`-s`**
: Print only errors, no informational messages.

**`-t `seconds``**
: Specifies the maximum number of seconds to wait when waiting for an
operation to complete (see option `-w`).  Defaults to
the value of the `PGCTLTIMEOUT` environment variable or, if
not set, to 60 seconds.

**`-V`**
: Print the pg_ctl version and exit.

**`-w`**
: Wait for the operation to complete.  This is supported for the
modes `start`, `stop`,
`restart`, `promote`,
and `register`, and is the default for those modes.

When waiting, `pg_ctl` repeatedly checks the
server's PID file, sleeping for a short amount
of time between checks.  Startup is considered complete when
the PID file indicates that the server is ready to
accept connections.  Shutdown is considered complete when the server
removes the PID file.
`pg_ctl` returns an exit code based on the
success of the startup or shutdown.

If the operation does not complete within the timeout (see
option `-t`), then `pg_ctl` exits with
a nonzero exit status.  But note that the operation might continue in
the background and eventually succeed.

**`-W`**
: Do not wait for the operation to complete.  This is the opposite of
the option `-w`.

If waiting is disabled, the requested action is triggered, but there
is no feedback about its success.  In that case, the server log file
or an external monitoring system would have to be used to check the
progress and success of the operation.

In prior releases of PostgreSQL, this was the default except for
the `stop` mode.

**`-?`**
: Show help about pg_ctl command line
arguments, and exit.

If an option is specified that is valid, but not relevant to the selected
operating mode, pg_ctl ignores it.

### Options for Windows

**`-e `source``**
: Name of the event source for pg_ctl to use
for logging to the event log when running as a Windows service.  The
default is `PostgreSQL`.  Note that this only controls
messages sent from pg_ctl itself; once
started, the server will use the event source specified
by its [guc-event-source](#guc-event-source) parameter.  Should the server
fail very early in startup, before that parameter has been set,
it might also log using the default event
source name `PostgreSQL`.

**`-N `servicename``**
: Name of the system service to register. This name will be used
as both the service name and the display name.
The default is `PostgreSQL`.

**`-P `password``**
: Password for the user to run the service as.

**`-S `start-type``**
: Start type of the system service.  `start-type` can
be `auto`, or `demand`, or
the first letter of one of these two. If this option is omitted,
`auto` is the default.

**`-U `username``**
: User name for the user to run the service as. For domain users, use the
format `DOMAIN\username`.

## Environment

**`PGCTLTIMEOUT`**
: Default limit on the number of seconds to wait when waiting for startup
or shutdown to complete.  If not set, the default is 60 seconds.

**`PGDATA`**
: Default data directory location.

Most `pg_ctl` modes require knowing the data directory
location; therefore, the `-D` option is required
unless `PGDATA` is set.

For additional variables that affect the server,
see [app-postgres](#app-postgres).

### Starting the Server

To start the server, waiting until the server is
accepting connections:

```
$ pg_ctl start
```

To start the server using port 5433, and
running without `fsync`, use:

```
$ pg_ctl -o "-F -p 5433" start
```

### Restarting the Server

Restarting the server is almost equivalent to stopping the
server and starting it again, except that by default,
`pg_ctl` saves and reuses the command line options that
were passed to the previously-running instance.  To restart
the server using the same options as before, use:

```
$ pg_ctl restart
```

But if `-o` is specified, that replaces any previous options.
To restart using port 5433, disabling `fsync` upon restart:

```
$ pg_ctl -o "-F -p 5433" restart
```
