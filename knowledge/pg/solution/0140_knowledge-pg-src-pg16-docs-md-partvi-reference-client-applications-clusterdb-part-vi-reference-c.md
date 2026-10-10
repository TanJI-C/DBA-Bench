# clusterdb

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/clusterdb.md`
- Source Title: `clusterdb`
- Source Heading Path: `Part VI Reference > Client Applications > clusterdb`
- Source Line Ranges: `1-163`
- Chunk ID: `pg16_solution_0140_e58006c408`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `484e5e5bf2fa565177a251cc241a0802d345adea2d4ec95c6e331029c503a162`

## Retrieval Guidance

- Use When: Use after deciding to recluster tables or all previously clustered tables from a client utility.
- Retrieval Keywords: clusterdb, CLUSTER wrapper, recluster database, physical table order
- Follow-up Guidance: Consider locks, disk space, and ANALYZE after clustering.
- Classification Note: Wrapper around CLUSTER for reclustering tables/databases; maintenance/tuning action after confirming clustering benefit.

## Official Source Content

clusterdb
1
Application

clusterdb
cluster a PostgreSQL database

`clusterdb`
`connection-option`
`--verbose``-v`

`--table`
`-t`

`table`

`dbname`

`clusterdb`
`connection-option`
`--verbose``-v`
`--all``-a`

## Description

clusterdb is a utility for reclustering tables
in a PostgreSQL database.  It finds tables
that have previously been clustered, and clusters them again on the same
index that was last used.  Tables that have never been clustered are not
affected.

clusterdb is a wrapper around the SQL
command [sql-cluster](#sql-cluster).
There is no effective difference between clustering databases via
this utility and via other methods for accessing the server.

## Options

clusterdb accepts the following command-line arguments:

**`-a`**
: Cluster all databases.

**`-d `dbname``**
: Specifies the name of the database to be clustered,
when `-a`/`--all` is not used.
If this is not specified, the database name is read
from the environment variable `PGDATABASE`.  If
that is not set, the user name specified for the connection is
used.  The `dbname` can be a [connection string](#libpq-connstring).  If so,
connection string parameters will override any conflicting command
line options.

**`-e`**
: Echo the commands that clusterdb generates
and sends to the server.

**`-q`**
: Do not display progress messages.

**`-t `table``**
: Cluster `table` only.
Multiple tables can be clustered by writing multiple
`-t` switches.

**`-v`**
: Print detailed information during processing.

**`-V`**
: Print the clusterdb version and exit.

**`-?`**
: Show help about clusterdb command line
arguments, and exit.

clusterdb also accepts
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
: Force clusterdb to prompt for a
password before connecting to a database.

This option is never essential, since
clusterdb will automatically prompt
for a password if the server demands password authentication.
However, clusterdb will waste a
connection attempt finding out that the server wants a password.
In some cases it is worth typing `-W` to avoid the extra
connection attempt.

**`--maintenance-db=`dbname``**
: When the `-a`/`--all` is used, connect
to this database to gather the list of databases to cluster.
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

In case of difficulty, see [sql-cluster](#sql-cluster)
and [app-psql](#app-psql) for
discussions of potential problems and error messages.
The database server must be running at the
targeted host.  Also, any default connection settings and environment
variables used by the libpq front-end
library will apply.

## Examples

To cluster the database `test`:

```
$ clusterdb test
```

To cluster a single table
`foo` in a database named
`xyzzy`:

```
$ clusterdb --table=foo xyzzy
```

## See Also
