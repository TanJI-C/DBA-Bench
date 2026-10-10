# Installation; Architectural Fundamentals; Creating a Database; Accessing a Database

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partI_tutorial/01_getting_started.md`
- Source Title: `Getting Started`
- Source Heading Path: `Getting Started > Installation; Architectural Fundamentals; Creating a Database; Accessing a Database`
- Source Line Ranges: `3-40, 41-85, 86-216, 217-322`
- Chunk ID: `pg16_fact_0137_baac55edb0`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b637121ee8d88649090b6544c6bf34588c9a68d57ed3174c73ca1d7a1a7e72d`

## Retrieval Guidance

- Use When: Need basic facts about PostgreSQL setup, architecture, database creation, or connecting to a database.
- Retrieval Keywords: installation, client server, createdb, dropdb, psql, database connection
- Follow-up Guidance: For operational connection failures, use monitoring/logging and authentication documentation outside these tutorial sections.
- Classification Note: Introductory material about installing PostgreSQL, client/server architecture, creating a database, and connecting with psql; beginner error examples are tutorial context rather than fault-specific diagnosis.

## Official Source Content

## Installation

Before you can use PostgreSQL you need
to install it, of course.  It is possible that
PostgreSQL is already installed at your
site, either because it was included in your operating system
distribution or because the system administrator already installed
it.  If that is the case, you should obtain information from the
operating system documentation or your system administrator about
how to access PostgreSQL.

If you are not sure whether PostgreSQL
is already available or whether you can use it for your
experimentation then you can install it yourself.  Doing so is not
hard and it can be a good exercise.
PostgreSQL can be installed by any
unprivileged user; no superuser (root)
access is required.

If you are installing PostgreSQL
yourself, then refer to [installation](#installation)
for instructions on installation, and return to
this guide when the installation is complete.  Be sure to follow
closely the section about setting up the appropriate environment
variables.

If your site administrator has not set things up in the default
way, you might have some more work to do.  For example, if the
database server machine is a remote machine, you will need to set
the `PGHOST` environment variable to the name of the
database server machine.  The environment variable
`PGPORT` might also have to be set.  The bottom line is
this: if you try to start an application program and it complains
that it cannot connect to the database, you should consult your
site administrator or, if that is you, the documentation to make
sure that your environment is properly set up.  If you did not
understand the preceding paragraph then read the next section.

## Architectural Fundamentals

Before we proceed, you should understand the basic
PostgreSQL system architecture.
Understanding how the parts of
PostgreSQL interact will make this
chapter somewhat clearer.

In database jargon, PostgreSQL uses a
client/server model.  A PostgreSQL
session consists of the following cooperating processes
(programs):

- A server process, which manages the database files, accepts
connections to the database from client applications, and
performs database actions on behalf of the clients.  The
database server program is called
`postgres`.
- The user's client (frontend) application that wants to perform
database operations.  Client applications can be very diverse
in nature:  a client could be a text-oriented tool, a graphical
application, a web server that accesses the database to
display web pages, or a specialized database maintenance tool.
Some client applications are supplied with the
PostgreSQL distribution; most are
developed by users.

As is typical of client/server applications, the client and the
server can be on different hosts.  In that case they communicate
over a TCP/IP network connection.  You should keep this in mind,
because the files that can be accessed on a client machine might
not be accessible (or might only be accessible using a different
file name) on the database server machine.

The PostgreSQL server can handle
multiple concurrent connections from clients.  To achieve this it
starts ("forks") a new process for each connection.
From that point on, the client and the new server process
communicate without intervention by the original
`postgres` process.  Thus, the
supervisor server process is always running, waiting for
client connections, whereas client and associated server processes
come and go.  (All of this is of course invisible to the user.  We
only mention it here for completeness.)

## Creating a Database

The first test to see whether you can access the database server
is to try to create a database.  A running
PostgreSQL server can manage many
databases.  Typically, a separate database is used for each
project or for each user.

Possibly, your site administrator has already created a database
for your use.  In that case you can omit this step and skip ahead
to the next section.

To create a new database, in this example named
`mydb`, you use the following command:

```
$ createdb mydb
```

If this produces no response then this step was successful and you can skip over the
remainder of this section.

If you see a message similar to:

```
createdb: command not found
```

then PostgreSQL was not installed properly.  Either it was not
installed at all or your shell's search path was not set to include it.
Try calling the command with an absolute path instead:

```
$ /usr/local/pgsql/bin/createdb mydb
```

The path at your site might be different.  Contact your site
administrator or check the installation instructions to
correct the situation.

Another response could be this:

```
createdb: error: connection to server on socket "/tmp/.s.PGSQL.5432" failed: No such file or directory
Is the server running locally and accepting connections on that socket?
```

This means that the server was not started, or it is not listening
where `createdb` expects to contact it.  Again, check the
installation instructions or consult the administrator.

Another response could be this:

```
createdb: error: connection to server on socket "/tmp/.s.PGSQL.5432" failed: FATAL:  role "joe" does not exist
```

where your own login name is mentioned.  This will happen if the
administrator has not created a PostgreSQL user account
for you.  (PostgreSQL user accounts are distinct from
operating system user accounts.)  If you are the administrator, see
[user-manag](#user-manag) for help creating accounts.  You will need to
become the operating system user under which PostgreSQL
was installed (usually `postgres`) to create the first user
account.  It could also be that you were assigned a
PostgreSQL user name that is different from your
operating system user name; in that case you need to use the `-U`
switch or set the `PGUSER` environment variable to specify your
PostgreSQL user name.

If you have a user account but it does not have the privileges required to
create a database, you will see the following:

```
createdb: error: database creation failed: ERROR:  permission denied to create database
```

Not every user has authorization to create new databases.  If
PostgreSQL refuses to create databases
for you then the site administrator needs to grant you permission
to create databases.  Consult your site administrator if this
occurs.  If you installed PostgreSQL
yourself then you should log in for the purposes of this tutorial
under the user account that you started the server as.

(Note: As an explanation for why this works:
PostgreSQL user names are separate
from operating system user accounts.  When you connect to a
database, you can choose what
PostgreSQL user name to connect as;
if you don't, it will default to the same name as your current
operating system account.  As it happens, there will always be a
PostgreSQL user account that has the
same name as the operating system user that started the server,
and it also happens that that user always has permission to
create databases.  Instead of logging in as that user you can
also specify the `-U` option everywhere to select
a PostgreSQL user name to connect as.)

You can also create databases with other names.
PostgreSQL allows you to create any
number of databases at a given site.  Database names must have an
alphabetic first character and are limited to 63 bytes in
length.  A convenient choice is to create a database with the same
name as your current user name.  Many tools assume that database
name as the default, so it can save you some typing.  To create
that database, simply type:

```
$ createdb
```

If you do not want to use your database anymore you can remove it.
For example, if you are the owner (creator) of the database
`mydb`, you can destroy it using the following
command:

```
$ dropdb mydb
```

(For this command, the database name does not default to the user
account name.  You always need to specify it.)  This action
physically removes all files associated with the database and
cannot be undone, so this should only be done with a great deal of
forethought.

More about `createdb` and `dropdb` can
be found in [app-createdb](#app-createdb) and [app-dropdb](#app-dropdb)
respectively.

## Accessing a Database

Once you have created a database, you can access it by:

- Running the PostgreSQL interactive
terminal program, called *psql*, which allows you
to interactively enter, edit, and execute
SQL commands.
- Using an existing graphical frontend tool like
pgAdmin or an office suite with
ODBC or JDBC support to create and manipulate a
database.  These possibilities are not covered in this
tutorial.
- Writing a custom application, using one of the several
available language bindings.  These possibilities are discussed
further in [client-interfaces](#client-interfaces).

You probably want to start up `psql` to try
the examples in this tutorial.  It can be activated for the
`mydb` database by typing the command:

```
$ psql mydb
```

If you do not supply the database name then it will default to your
user account name.  You already discovered this scheme in the
previous section using `createdb`.

In `psql`, you will be greeted with the following
message:

```
psql ()
Type "help" for help.

mydb=>
```

The last line could also be:

```
mydb=#
```

That would mean you are a database superuser, which is most likely
the case if you installed the PostgreSQL instance
yourself.  Being a superuser means that you are not subject to
access controls.  For the purposes of this tutorial that is not
important.

If you encounter problems starting `psql`
then go back to the previous section.  The diagnostics of
`createdb` and `psql` are
similar, and if the former worked the latter should work as well.

The last line printed out by `psql` is the
prompt, and it indicates that `psql` is listening
to you and that you can type SQL queries into a
work space maintained by `psql`.  Try out these
commands:

```
mydb=> SELECT version();
version
------------------------------------------------------------------------------------------
PostgreSQL  on x86_64-pc-linux-gnu, compiled by gcc (Debian 4.9.2-10) 4.9.2, 64-bit
(1 row)

mydb=> SELECT current_date;
date
------------
2016-01-07
(1 row)

mydb=> SELECT 2 + 2;
?column?
----------
4
(1 row)
```

The `psql` program has a number of internal
commands that are not SQL commands.  They begin with the backslash
character, "`\`".
For example,
you can get help on the syntax of various
PostgreSQL SQL
commands by typing:

```
mydb=> \h
```

To get out of `psql`, type:

```
mydb=> \q
```

and `psql` will quit and return you to your
command shell. (For more internal commands, type
`\?` at the `psql` prompt.)  The
full capabilities of `psql` are documented in
[app-psql](#app-psql).  In this tutorial we will not use these
features explicitly, but you can use them yourself when it is helpful.
