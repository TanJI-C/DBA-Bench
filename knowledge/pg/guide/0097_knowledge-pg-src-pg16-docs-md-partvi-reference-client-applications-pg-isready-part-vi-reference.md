# pg_isready

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/pg_isready.md`
- Source Title: `pg isready`
- Source Heading Path: `Part VI Reference > Client Applications > pg_isready`
- Source Line Ranges: `1-110`
- Chunk ID: `pg16_guide_0097_21ea55471b`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `55b7451f6a3525cce263dfd566674f4fc8585d6b939befbf62c862bc0220915b`

## Retrieval Guidance

- Use When: Use to confirm service readiness, startup state, or connectivity state from scripts/monitoring.
- Retrieval Keywords: pg_isready, connection status, accepting connections, rejecting connections, no response, exit status
- Follow-up Guidance: If not ready, correlate with logs, pg_ctl status, network/socket checks, and authentication behavior.
- Classification Note: Checks server connection readiness and returns distinct exit statuses for accepting, rejecting, no response, or invalid invocation.

## Official Source Content

pg_isready
1
Application

pg_isready
check the connection status of a PostgreSQL server

`pg_isready`
`connection-option`
`option`

## Description

pg_isready is a utility for checking the connection
status of a PostgreSQL database server. The exit
status specifies the result of the connection check.

## Options

**`-d `dbname``**
: Specifies the name of the database to connect to. The
`dbname` can be a [connection string](#libpq-connstring).  If so,
connection string parameters will override any conflicting command
line options.

**`-h `hostname``**
: Specifies the host name of the machine on which the
server is running. If the value begins
with a slash, it is used as the directory for the Unix-domain
socket.

**`-p `port``**
: Specifies the TCP port or the local Unix-domain
socket file extension on which the server is listening for
connections. Defaults to the value of the `PGPORT`
environment variable or, if not set, to the port specified at
compile time, usually 5432.

**`-q`**
: Do not display status message. This is useful when scripting.

**`-t `seconds``**
: The maximum number of seconds to wait when attempting connection before
returning that the server is not responding. Setting to 0 disables. The
default is 3 seconds.

**`-U `username``**
: Connect to the database as the user `username` instead of the default.

**`-V`**
: Print the pg_isready version and exit.

**`-?`**
: Show help about pg_isready command line
arguments, and exit.

## Exit Status

pg_isready returns `0` to the shell if the server
is accepting connections normally, `1` if the server is rejecting
connections (for example during startup), `2` if there was no response to the
connection attempt, and `3` if no attempt was made (for example due to invalid
parameters).

## Environment

`pg_isready`, like most other PostgreSQL
utilities,
also uses the environment variables supported by libpq
(see [libpq-envars](#libpq-envars)).

The environment variable `PG_COLOR` specifies whether to use
color in diagnostic messages. Possible values are
`always`, `auto` and
`never`.

## Notes

It is not necessary to supply correct user name, password, or database
name values to obtain the server status; however, if incorrect values
are provided, the server will log a failed connection attempt.

## Examples

Standard Usage:

```
$ pg_isready
/tmp:5432 - accepting connections
$ echo $?
0
```

Running with connection parameters to a PostgreSQL cluster in startup:

```
$ pg_isready -h localhost -p 5433
localhost:5433 - rejecting connections
$ echo $?
1
```

Running with connection parameters to a non-responsive PostgreSQL cluster:

```
$ pg_isready -h someremotehost
someremotehost:5432 - no response
$ echo $?
2
```
