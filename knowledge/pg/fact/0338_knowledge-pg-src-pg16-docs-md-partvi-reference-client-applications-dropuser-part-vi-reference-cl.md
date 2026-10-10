# dropuser

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/dropuser.md`
- Source Title: `dropuser`
- Source Heading Path: `Part VI Reference > Client Applications > dropuser`
- Source Line Ranges: `1-137`
- Chunk ID: `pg16_fact_0338_74e6eb9d3c`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `27abd9ce19ac2bbbcc2086f78192387170093fe398383be17ca78f32f021054e`

## Retrieval Guidance

- Use When: Use for dropuser command-line syntax.
- Retrieval Keywords: dropuser, DROP ROLE wrapper, remove user, --if-exists
- Follow-up Guidance: Review REASSIGN OWNED/DROP OWNED before removing roles with objects.
- Classification Note: Client wrapper around DROP ROLE; role/user removal reference.

## Official Source Content

dropuser
1
Application

dropuser
remove a PostgreSQL user account

`dropuser`
`connection-option`
`option`
`username`

## Description

dropuser removes an existing
PostgreSQL user.
Superusers can use this command to remove any role; otherwise, only
non-superuser roles can be removed, and only by a user who possesses
the `CREATEROLE` privilege and has been granted
`ADMIN OPTION` on the target role.

dropuser is a wrapper around the
SQL command [`DROP ROLE`](#sql-droprole).
There is no effective difference between dropping users via
this utility and via other methods for accessing the server.

## Options

dropuser accepts the following command-line arguments:

**`username`**
: Specifies the name of the PostgreSQL user to be removed.
You will be prompted for a name if none is specified on the command
line and the `-i`/`--interactive` option
is used.

**`-e`**
: Echo the commands that dropuser generates
and sends to the server.

**`-i`**
: Prompt for confirmation before actually removing the user, and prompt
for the user name if none is specified on the command line.

**`-V`**
: Print the dropuser version and exit.

**`--if-exists`**
: Do not throw an error if the user does not exist. A notice is
issued in this case.

**`-?`**
: Show help about dropuser command line
arguments, and exit.

dropuser also accepts the following
command-line arguments for connection parameters:

**`-h `host``**
: Specifies the host name of the machine on which the
server
is running.  If the value begins with a slash, it is used
as the directory for the Unix domain socket.

**`-p `port``**
: Specifies the TCP port or local Unix domain socket file
extension on which the server
is listening for connections.

**`-U `username``**
: User name to connect as (not the user name to drop).

**`-w`**
: Never issue a password prompt.  If the server requires
password authentication and a password is not available by
other means such as a `.pgpass` file, the
connection attempt will fail.  This option can be useful in
batch jobs and scripts where no user is present to enter a
password.

**`-W`**
: Force dropuser to prompt for a
password before connecting to a database.

This option is never essential, since
dropuser will automatically prompt
for a password if the server demands password authentication.
However, dropuser will waste a
connection attempt finding out that the server wants a password.
In some cases it is worth typing `-W` to avoid the extra
connection attempt.

## Environment

**`PGHOST`**
: Default connection parameters

**`PG_COLOR`**
: Specifies whether to use color in diagnostic messages. Possible values
are `always`, `auto` and
`never`.

This utility, like most other PostgreSQL utilities,
also uses the environment variables supported by libpq
(see [libpq-envars](#libpq-envars)).

## Diagnostics

In case of difficulty, see [sql-droprole](#sql-droprole)
and [app-psql](#app-psql) for
discussions of potential problems and error messages.
The database server must be running at the
targeted host.  Also, any default connection settings and environment
variables used by the libpq front-end
library will apply.

## Examples

To remove user `joe` from the default database
server:

```
$ dropuser joe
```

To remove user `joe` using the server on host
`eden`, port 5000, with verification and a peek at the underlying
command:

```
$ dropuser -p 5000 -h eden -i -e joe
Role "joe" will be permanently removed.
Are you sure? (y/n) y
DROP ROLE joe;
```

## See Also
