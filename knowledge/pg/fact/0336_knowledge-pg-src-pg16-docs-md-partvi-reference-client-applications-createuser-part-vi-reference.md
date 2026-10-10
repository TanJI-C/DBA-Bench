# createuser

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/createuser.md`
- Source Title: `createuser`
- Source Heading Path: `Part VI Reference > Client Applications > createuser`
- Source Line Ranges: `1-260`
- Chunk ID: `pg16_fact_0336_eded528500`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `143f04c0d8f481491b784993052fef0cfe1bb9ecdd7f7c3bf408062741be1e00`

## Retrieval Guidance

- Use When: Use for createuser command-line syntax and role attribute options.
- Retrieval Keywords: createuser, CREATE ROLE wrapper, role attributes, CREATEROLE, LOGIN
- Follow-up Guidance: No section split needed.
- Classification Note: Client wrapper around CREATE ROLE; role/user creation reference.

## Official Source Content

createuser
1
Application

createuser
define a new PostgreSQL user account

`createuser`
`connection-option`
`option`
`username`

## Description

createuser creates a
new PostgreSQL user (or more precisely, a role).
Only superusers and users with `CREATEROLE` privilege can create
new users, so createuser must be
invoked by someone who can connect as a superuser or a user with
`CREATEROLE` privilege.

If you wish to create a role with the `SUPERUSER`,
`REPLICATION`, or `BYPASSRLS` privilege,
you must connect as a superuser, not merely with
`CREATEROLE` privilege.
Being a superuser implies the ability to bypass all access permission
checks within the database, so superuser access should not be granted
lightly. `CREATEROLE` also conveys
[very extensive privileges](#role-creation).

createuser is a wrapper around the
SQL command [`CREATE ROLE`](#sql-createrole).
There is no effective difference between creating users via
this utility and via other methods for accessing the server.

## Options

createuser accepts the following command-line arguments:

**`username`**
: Specifies the name of the PostgreSQL user
to be created.
This name must be different from all existing roles in this
PostgreSQL installation.

**`-a `role``**
: Specifies an existing role that will be automatically added as a member of the new
role with admin option, giving it the right to grant membership in the
new role to others.  Multiple existing roles can be specified by
writing multiple `-a` switches.

**`-c `number``**
: Set a maximum number of connections for the new user.
The default is to set no limit.

**`-d`**
: The new user will be allowed to create databases.

**`-D`**
: The new user will not be allowed to create databases.  This is the
default.

**`-e`**
: Echo the commands that createuser generates
and sends to the server.

**`-E`**
: This option is obsolete but still accepted for backward
compatibility.

**`-g `role``**
: Specifies the new role should be automatically added as a member
of the specified existing role. Multiple existing roles can be
specified by writing multiple `-g` switches.

**`-i`**
: The new role will automatically inherit privileges of roles
it is a member of.
This is the default.

**`-I`**
: The new role will not automatically inherit privileges of roles
it is a member of.

**`--interactive`**
: Prompt for the user name if none is specified on the command line, and
also prompt for whichever of the options
`-d`/`-D`,
`-r`/`-R`,
`-s`/`-S` is not specified on the command
line.  (This was the default behavior up to PostgreSQL 9.1.)

**`-l`**
: The new user will be allowed to log in (that is, the user name
can be used as the initial session user identifier).
This is the default.

**`-L`**
: The new user will not be allowed to log in.
(A role without login privilege is still useful as a means of
managing database permissions.)

**`-m `role``**
: Specifies an existing role that will be automatically
added as a member of the new role. Multiple existing roles can
be specified by writing multiple `-m` switches.

**`-P`**
: If given, createuser will issue a prompt for
the password of the new user. This is not necessary if you do not plan
on using password authentication.

**`-r`**
: The new user will be allowed to create, alter, drop, comment on,
change the security label for other roles; that is,
this user will have `CREATEROLE` privilege.
See [role-creation](#role-creation) for more details about what
capabilities are conferred by this privilege.

**`-R`**
: The new user will not be allowed to create new roles.  This is the
default.

**`-s`**
: The new user will be a superuser.

**`-S`**
: The new user will not be a superuser.  This is the default.

**`-v `timestamp``**
: Set a date and time after which the role's password is no longer valid.
The default is to set no password expiry date.

**`-V`**
: Print the createuser version and exit.

**`--bypassrls`**
: The new user will bypass every row-level security (RLS) policy.

**`--no-bypassrls`**
: The new user will not bypass row-level security (RLS) policies.  This is
the default.

**`--replication`**
: The new user will have the `REPLICATION` privilege,
which is described more fully in the documentation for [sql-createrole](#sql-createrole).

**`--no-replication`**
: The new user will not have the `REPLICATION`
privilege, which is described more fully in the documentation for [sql-createrole](#sql-createrole).  This is the default.

**`-?`**
: Show help about createuser command line
arguments, and exit.

createuser also accepts the following
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
: User name to connect as (not the user name to create).

**`-w`**
: Never issue a password prompt.  If the server requires
password authentication and a password is not available by
other means such as a `.pgpass` file, the
connection attempt will fail.  This option can be useful in
batch jobs and scripts where no user is present to enter a
password.

**`-W`**
: Force createuser to prompt for a
password (for connecting to the server, not for the
password of the new user).

This option is never essential, since
createuser will automatically prompt
for a password if the server demands password authentication.
However, createuser will waste a
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

In case of difficulty, see [sql-createrole](#sql-createrole)
and [app-psql](#app-psql) for
discussions of potential problems and error messages.
The database server must be running at the
targeted host.  Also, any default connection settings and environment
variables used by the libpq front-end
library will apply.

## Examples

To create a user `joe` on the default database
server:

```
$ createuser joe
```

To create a user `joe` on the default database
server with prompting for some additional attributes:

```
$ createuser --interactive joe
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) n
Shall the new role be allowed to create more new roles? (y/n) n
```

To create the same user `joe` using the
server on host `eden`, port 5000, with attributes explicitly specified,
taking a look at the underlying command:

```
$ createuser -h eden -p 5000 -S -D -R -e joe
CREATE ROLE joe NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;
```

To create the user `joe` as a superuser,
and assign a password immediately:

```
$ createuser -P -s -e joe
Enter password for new role: xyzzy
Enter it again: xyzzy
CREATE ROLE joe PASSWORD 'SCRAM-SHA-256$4096:44560wPMLfjqiAzyPDZ/eQ==$4CA054rZlSFEq8Z3FEhToBTa2X6KnWFxFkPwIbKoDe0=:L/nbSZRCjp6RhOhKK56GoR1zibCCSePKshCJ9lnl3yw=' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN NOREPLICATION NOBYPASSRLS;
```

In the above example, the new password isn't actually echoed when typed,
but we show what was typed for clarity.  As you see, the password is
encrypted before it is sent to the client.

## See Also
