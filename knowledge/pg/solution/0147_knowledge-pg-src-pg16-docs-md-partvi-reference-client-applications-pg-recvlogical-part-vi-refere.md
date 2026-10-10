# pg_recvlogical

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/pg_recvlogical.md`
- Source Title: `pg recvlogical`
- Source Heading Path: `Part VI Reference > Client Applications > pg_recvlogical`
- Source Line Ranges: `1-232`
- Chunk ID: `pg16_solution_0147_99aac9dd7e`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `43cae1a059c542345f192940bcb00b8a35925091d435eba1d15ecdd942239274`

## Retrieval Guidance

- Use When: Use when controlling logical decoding streams or slots after deciding replication/decoding action is required.
- Retrieval Keywords: pg_recvlogical, logical decoding, replication slot, create-slot, drop-slot, start streaming
- Follow-up Guidance: Verify slot retention, output plugin options, LSN boundaries, and downstream consumption.
- Classification Note: Creates/drops logical replication slots and streams decoded changes; operational action for logical decoding pipelines.

## Official Source Content

pg_recvlogical
1
Application

pg_recvlogical
control PostgreSQL logical decoding streams

`pg_recvlogical`
`option`

## Description

`pg_recvlogical` controls logical decoding replication
slots and streams data from such replication slots.

It creates a replication-mode connection, so it is subject to the same
constraints as [app-pgreceivewal](#app-pgreceivewal), plus those for logical
replication (see [logicaldecoding](#logicaldecoding)).

`pg_recvlogical` has no equivalent to the logical decoding
SQL interface's peek and get modes. It sends replay confirmations for
data lazily as it receives it and on clean exit. To examine pending data on
a slot without consuming it, use
[`pg_logical_slot_peek_changes`](#functions-replication).

In the absence of fatal errors, pg_recvlogical
will run until terminated by the SIGINT
(ControlC)
or SIGTERM signal.

When pg_recvlogical receives
a SIGHUP signal, it closes the current output file
and opens a new one using the filename specified by
the `--file` option.  This allows us to rotate
the output file by first renaming the current file and then sending
a SIGHUP signal to
pg_recvlogical.

## Options

At least one of the following options must be specified to select an action:

**`--create-slot`**
: Create a new logical replication slot with the name specified by
`--slot`, using the output plugin specified by
`--plugin`, for the database specified
by `--dbname`.

The `--two-phase` can be specified with
`--create-slot` to enable decoding of prepared transactions.

**`--drop-slot`**
: Drop the replication slot with the name specified
by `--slot`, then exit.

**`--start`**
: Begin streaming changes from the logical replication slot specified
by `--slot`, continuing until terminated by a
signal. If the server side change stream ends with a server shutdown
or disconnect, retry in a loop unless
`--no-loop` is specified.

The stream format is determined by the output plugin specified when
the slot was created.

The connection must be to the same database used to create the slot.

`--create-slot` and `--start` can be
specified together.  `--drop-slot` cannot be combined with
another action.

The following command-line options control the location and format of the
output and other replication behavior:

**`-E `lsn``**
: In `--start` mode, automatically stop replication
and exit with normal exit status 0 when receiving reaches the
specified LSN.  If specified when not in `--start`
mode, an error is raised.

If there's a record with LSN exactly equal to `lsn`,
the record will be output.

The `--endpos` option is not aware of transaction
boundaries and may truncate output partway through a transaction.
Any partially output transaction will not be consumed and will be
replayed again when the slot is next read from. Individual messages
are never truncated.

**`-f `filename``**
: Write received and decoded transaction data into this
file. Use `-` for stdout.

**`-F `interval_seconds``**
: Specifies how often pg_recvlogical should
issue `fsync()` calls to ensure the output file is
safely flushed to disk.

The server will occasionally request the client to perform a flush and
report the flush position to the server.  This setting is in addition
to that, to perform flushes more frequently.

Specifying an interval of `0` disables
issuing `fsync()` calls altogether, while still
reporting progress to the server.  In this case, data could be lost in
the event of a crash.

**`-I `lsn``**
: In `--start` mode, start replication from the given
LSN.  For details on the effect of this, see the documentation
in [logicaldecoding](#logicaldecoding)
and [protocol-replication](#protocol-replication). Ignored in other modes.

**`--if-not-exists`**
: Do not error out when `--create-slot` is specified
and a slot with the specified name already exists.

**`-n`**
: When the connection to the server is lost, do not retry in a loop, just exit.

**`-o `name`[=`value`]`**
: Pass the option `name` to the output plugin with,
if specified, the option value `value`. Which
options exist and their effects depends on the used output plugin.

**`-P `plugin``**
: When creating a slot, use the specified logical decoding output
plugin. See [logicaldecoding](#logicaldecoding). This option has no
effect if the slot already exists.

**`-s `interval_seconds``**
: This option has the same effect as the option of the same name
in [app-pgreceivewal](#app-pgreceivewal).  See the description there.

**`-S `slot_name``**
: In `--start` mode, use the existing logical replication slot named
`slot_name`. In `--create-slot`
mode, create the slot with this name. In `--drop-slot`
mode, delete the slot with this name.

**`-t`**
: Enables decoding of prepared transactions. This option may only be specified with
`--create-slot`

**`-v`**
: Enables verbose mode.

The following command-line options control the database connection parameters.

**`-d `dbname``**
: The database to connect to.  See the description
of the actions for what this means in detail.
The `dbname` can be a [connection string](#libpq-connstring).  If so,
connection string parameters will override any conflicting
command line options.  Defaults to the user name.

**`-h `hostname-or-ip``**
: Specifies the host name of the machine on which the server is
running.  If the value begins with a slash, it is used as the
directory for the Unix domain socket. The default is taken
from the `PGHOST` environment variable, if set,
else a Unix domain socket connection is attempted.

**`-p `port``**
: Specifies the TCP port or local Unix domain socket file
extension on which the server is listening for connections.
Defaults to the `PGPORT` environment variable, if
set, or a compiled-in default.

**`-U `user``**
: User name to connect as.  Defaults to current operating system user
name.

**`-w`**
: Never issue a password prompt.  If the server requires
password authentication and a password is not available by
other means such as a `.pgpass` file, the
connection attempt will fail.  This option can be useful in
batch jobs and scripts where no user is present to enter a
password.

**`-W`**
: Force pg_recvlogical to prompt for a
password before connecting to a database.

This option is never essential, since
pg_recvlogical will automatically prompt
for a password if the server demands password authentication.
However, pg_recvlogical will waste a
connection attempt finding out that the server wants a password.
In some cases it is worth typing `-W` to avoid the extra
connection attempt.

The following additional options are available:

**`-V`**
: Print the pg_recvlogical version and exit.

**`-?`**
: Show help about pg_recvlogical command line
arguments, and exit.

## Exit Status

pg_recvlogical will exit with status 0 when
terminated by the SIGINT or
SIGTERM signal.  (That is the
normal way to end it.  Hence it is not an error.)  For fatal errors or
other signals, the exit status will be nonzero.

## Environment

This utility, like most other PostgreSQL utilities,
uses the environment variables supported by libpq
(see [libpq-envars](#libpq-envars)).

The environment variable `PG_COLOR` specifies whether to use
color in diagnostic messages. Possible values are
`always`, `auto` and
`never`.

## Notes

pg_recvlogical will preserve group permissions on
the output files if group permissions are enabled on the source
cluster.

## Examples

See [logicaldecoding-example](#logicaldecoding-example) for an example.

## See Also
