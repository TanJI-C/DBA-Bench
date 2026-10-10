# reindexdb

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/reindexdb.md`
- Source Title: `reindexdb`
- Source Heading Path: `Part VI Reference > Client Applications > reindexdb`
- Source Line Ranges: `1-223`
- Chunk ID: `pg16_solution_0151_e533607500`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `9fc84563190b7a9c8a4393aa7e45164b7865f6b260eaf535e8dbe4b609d6b313`

## Retrieval Guidance

- Use When: Use after confirming index rebuild is required and a client utility is preferred.
- Retrieval Keywords: reindexdb, REINDEX wrapper, rebuild indexes, --concurrently, system catalogs
- Follow-up Guidance: Choose scope/concurrency, check locks, and verify index validity afterward.
- Classification Note: Client wrapper around REINDEX for rebuilding indexes across database/schema/table/index scopes.

## Official Source Content

reindexdb
1
Application

reindexdb
reindex a PostgreSQL database

`reindexdb`
`connection-option`
`option`

`-S`
`--schema`

`schema`

`-t`
`--table`

`table`

`-i`
`--index`

`index`

`dbname`

`reindexdb`
`connection-option`
`option`

`-a`
`--all`

`reindexdb`
`connection-option`
`option`

`-s`
`--system`

`dbname`

## Description

reindexdb is a utility for rebuilding indexes
in a PostgreSQL database.

reindexdb is a wrapper around the SQL
command [`REINDEX`](#sql-reindex).
There is no effective difference between reindexing databases via
this utility and via other methods for accessing the server.

## Options

reindexdb accepts the following command-line arguments:

**`-a`**
: Reindex all databases.

**`--concurrently`**
: Use the `CONCURRENTLY` option.  See
[sql-reindex](#sql-reindex), where all the caveats of this option
are explained in detail.

**`-d `dbname``**
: Specifies the name of the database to be reindexed,
when `-a`/`--all` is not used.
If this is not specified, the database name is read
from the environment variable `PGDATABASE`.  If
that is not set, the user name specified for the connection is
used.  The `dbname` can be a [connection string](#libpq-connstring).  If so,
connection string parameters will override any conflicting command
line options.

**`-e`**
: Echo the commands that reindexdb generates
and sends to the server.

**`-i `index``**
: Recreate `index` only.
Multiple indexes can be recreated by writing multiple
`-i` switches.

**`-j `njobs``**
: Execute the reindex commands in parallel by running
`njobs`
commands simultaneously.  This option may reduce the processing time
but it also increases the load on the database server.

reindexdb will open
`njobs` connections to the
database, so make sure your [guc-max-connections](#guc-max-connections)
setting is high enough to accommodate all connections.

Note that this option is incompatible with the `--index`
and `--system` options.

**`-q`**
: Do not display progress messages.

**`-s`**
: Reindex database's system catalogs only.

**`-S `schema``**
: Reindex `schema` only.
Multiple schemas can be reindexed by writing multiple
`-S` switches.

**`-t `table``**
: Reindex `table` only.
Multiple tables can be reindexed by writing multiple
`-t` switches.

**`--tablespace=`tablespace``**
: Specifies the tablespace where indexes are rebuilt. (This name is
processed as a double-quoted identifier.)

**`-v`**
: Print detailed information during processing.

**`-V`**
: Print the reindexdb version and exit.

**`-?`**
: Show help about reindexdb command line
arguments, and exit.

reindexdb also accepts
the following command-line arguments for connection parameters:

**`-h `host``**
: Specifies the host name of the machine on which the server is
running.  If the value begins with a slash, it is used as the
directory for the Unix domain socket.

**`-p `port``**
: Specifies the TCP port or local Unix domain socket file
extension on which the server
is listening for connections.

**`-U `username``**
: User name to connect as.

**`-w`**
: Never issue a password prompt.  If the server requires
password authentication and a password is not available by
other means such as a `.pgpass` file, the
connection attempt will fail.  This option can be useful in
batch jobs and scripts where no user is present to enter a
password.

**`-W`**
: Force reindexdb to prompt for a
password before connecting to a database.

This option is never essential, since
reindexdb will automatically prompt
for a password if the server demands password authentication.
However, reindexdb will waste a
connection attempt finding out that the server wants a password.
In some cases it is worth typing `-W` to avoid the extra
connection attempt.

**`--maintenance-db=`dbname``**
: When the `-a`/`--all` is used, connect
to this database to gather the list of databases to reindex.
If not specified, the `postgres` database will be used,
or if that does not exist, `template1` will be used.
This can be a [connection
string](#libpq-connstring).  If so, connection string parameters will override any
conflicting command line options.  Also, connection string parameters
other than the database name itself will be re-used when connecting
to other databases.

## Environment

**`PGDATABASE`**
: Default connection parameters

**`PG_COLOR`**
: Specifies whether to use color in diagnostic messages. Possible values
are `always`, `auto` and
`never`.

This utility, like most other PostgreSQL utilities,
also uses the environment variables supported by libpq
(see [libpq-envars](#libpq-envars)).

## Diagnostics

In case of difficulty, see [sql-reindex](#sql-reindex)
and [app-psql](#app-psql) for
discussions of potential problems and error messages.
The database server must be running at the
targeted host.  Also, any default connection settings and environment
variables used by the libpq front-end
library will apply.

## Notes

reindexdb might need to connect several
times to the PostgreSQL server, asking
for a password each time. It is convenient to have a
`~/.pgpass` file in such cases. See [libpq-pgpass](#libpq-pgpass) for more information.

## Examples

To reindex the database `test`:

```
$ reindexdb test
```

To reindex the table `foo` and the index
`bar` in a database named `abcd`:

```
$ reindexdb --table=foo --index=bar abcd
```

## See Also
