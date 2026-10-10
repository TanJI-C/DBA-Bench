# createdb

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/createdb.md`
- Source Title: `createdb`
- Source Heading Path: `Part VI Reference > Client Applications > createdb`
- Source Line Ranges: `1-200`
- Chunk ID: `pg16_fact_0335_9dff17d1bc`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `e0c0e6ce555484322090ebe592c31ac845f22a3c66a592ef44ddc805712c9dd8`

## Retrieval Guidance

- Use When: Use for createdb command-line syntax and option mapping to CREATE DATABASE.
- Retrieval Keywords: createdb, CREATE DATABASE wrapper, database encoding, locale, template
- Follow-up Guidance: Use initdb for cluster initialization defaults or ALTER DATABASE for runtime defaults.
- Classification Note: Client wrapper around CREATE DATABASE; reference for database creation options rather than diagnosis or remediation.

## Official Source Content

createdb
1
Application

createdb
create a new PostgreSQL database

`createdb`
`connection-option`
`option`
`dbname`
`description`

## Description

createdb creates a new PostgreSQL
database.

Normally, the database user who executes this command becomes the owner of
the new database.
However, a different owner can be specified via the `-O`
option, if the executing user has appropriate privileges.

createdb is a wrapper around the
SQL command [`CREATE DATABASE`](#sql-createdatabase).
There is no effective difference between creating databases via
this utility and via other methods for accessing the server.

## Options

createdb accepts the following command-line arguments:

**`dbname`**
: Specifies the name of the database to be created.  The name must be
unique among all PostgreSQL databases in this cluster.
The default is to create a database with the same name as the
current system user.

**`description`**
: Specifies a comment to be associated with the newly created
database.

**`-D `tablespace``**
: Specifies the default tablespace for the database. (This name
is processed as a double-quoted identifier.)

**`-e`**
: Echo the commands that createdb generates
and sends to the server.

**`-E `encoding``**
: Specifies the character encoding scheme to be used in this
database. The character sets supported by the
PostgreSQL server are described in
[multibyte-charset-supported](#multibyte-charset-supported).

**`-l `locale``**
: Specifies the locale to be used in this database.  This is equivalent
to specifying `--lc-collate`,
`--lc-ctype`, and `--icu-locale` to the
same value. Some locales are only valid for ICU and must be set with
`--icu-locale`.

**`--lc-collate=`locale``**
: Specifies the LC_COLLATE setting to be used in this database.

**`--lc-ctype=`locale``**
: Specifies the LC_CTYPE setting to be used in this database.

**`--icu-locale=`locale``**
: Specifies the ICU locale ID to be used in this database, if the
ICU locale provider is selected.

**`--icu-rules=`rules``**
: Specifies additional collation rules to customize the behavior of the
default collation of this database.  This is supported for ICU only.

**`--locale-provider={`libc`|`icu`}`**
: Specifies the locale provider for the database's default collation.

**`-O `owner``**
: Specifies the database user who will own the new database.
(This name is processed as a double-quoted identifier.)

**`-S `strategy``**
: Specifies the database creation strategy.  See
[create-database-strategy](#create-database-strategy) for more details.

**`-T `template``**
: Specifies the template database from which to build this
database.  (This name is processed as a double-quoted identifier.)

**`-V`**
: Print the createdb version and exit.

**`-?`**
: Show help about createdb command line
arguments, and exit.

The options `-D`, `-l`, `-E`,
`-O`, and
`-T` correspond to options of the underlying
SQL command [`CREATE DATABASE`](#sql-createdatabase); see there for more information
about them.

createdb also accepts the following
command-line arguments for connection parameters:

**`-h `host``**
: Specifies the host name of the machine on which the
server is running.  If the value begins with a slash, it is used
as the directory for the Unix domain socket.

**`-p `port``**
: Specifies the TCP port or the local Unix domain socket file
extension on which the server is listening for connections.

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
: Force createdb to prompt for a
password before connecting to a database.

This option is never essential, since
createdb will automatically prompt
for a password if the server demands password authentication.
However, createdb will waste a
connection attempt finding out that the server wants a password.
In some cases it is worth typing `-W` to avoid the extra
connection attempt.

**`--maintenance-db=`dbname``**
: Specifies the name of the database to connect to when creating the
new database. If not specified, the `postgres`
database will be used; if that does not exist (or if it is the name
of the new database being created), `template1` will
be used.
This can be a [connection
string](#libpq-connstring).  If so, connection string parameters will override any
conflicting command line options.

## Environment

**`PGDATABASE`**
: If set, the name of the database to create, unless overridden on
the command line.

**`PGHOST`**
: Default connection parameters.  `PGUSER` also
determines the name of the database to create, if it is not
specified on the command line or by `PGDATABASE`.

**`PG_COLOR`**
: Specifies whether to use color in diagnostic messages. Possible values
are `always`, `auto` and
`never`.

This utility, like most other PostgreSQL utilities,
also uses the environment variables supported by libpq
(see [libpq-envars](#libpq-envars)).

## Diagnostics

In case of difficulty, see [sql-createdatabase](#sql-createdatabase)
and [app-psql](#app-psql) for
discussions of potential problems and error messages.
The database server must be running at the
targeted host.  Also, any default connection settings and environment
variables used by the libpq front-end
library will apply.

## Examples

To create the database `demo` using the default
database server:

```
$ createdb demo
```

To create the database `demo` using the
server on host `eden`, port 5000, using the
`template0` template database,  here is the
command-line command and the underlying SQL command:

```
$ createdb -p 5000 -h eden -T template0 -e demo
CREATE DATABASE demo TEMPLATE template0;
```

## See Also
