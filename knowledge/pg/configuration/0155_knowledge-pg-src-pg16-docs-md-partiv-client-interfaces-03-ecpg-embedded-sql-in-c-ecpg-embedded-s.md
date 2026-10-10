# Connecting to the Database Server; Connection Options; Environment Variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/03_ecpg_-_embedded_sql_in_c.md`
- Source Title: `ECPG — Embedded SQL in C`
- Source Heading Path: `ECPG - Embedded SQL in C > Connecting to the Database Server; Connection Options; Environment Variables`
- Source Line Ranges: `73-169`
- Chunk ID: `pg16_configuration_0155_0ccf773cc1`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `39917fcc21b7c38b4d4464f0416d94ed946cac4576f5fc53a973c9fee10a0713`

## Retrieval Guidance

- Use When: Configure connection behavior for an embedded SQL C application.
- Retrieval Keywords: ECPG CONNECT, EXEC SQL CONNECT, connection name, CURRENT, ECPG environment variables, PGDATABASE, PGUSER
- Follow-up Guidance: Check libpq connection-parameter records because ECPG uses libpq underneath for many connection semantics.
- Classification Note: These sections define how ECPG programs specify target databases, users, passwords, connection names, and environment-provided connection defaults.

## Official Source Content

### Connecting to the Database Server

One connects to a database using the following statement:

```
EXEC SQL CONNECT TO `target` `AS `connection-name` USER `user-name`;
```

The `target` can be specified in the
following ways:

The connection target `DEFAULT` initiates a connection
to the default database under the default user name.  No separate
user name or connection name can be specified in that case.

If you specify the connection target directly (that is, not as a string
literal or variable reference), then the components of the target are
passed through normal SQL parsing; this means that, for example,
the `hostname` must look like one or more SQL
identifiers separated by dots, and those identifiers will be
case-folded unless double-quoted.  Values of
any `options` must be SQL identifiers,
integers, or variable references.  Of course, you can put nearly
anything into an SQL identifier by double-quoting it.
In practice, it is probably less error-prone to use a (single-quoted)
string literal or a variable reference than to write the connection
target directly.

There are also different ways to specify the user name:

As above, the parameters `username` and
`password` can be an SQL identifier, an
SQL string literal, or a reference to a character variable.

If the connection target includes any `options`,
those consist of
``keyword`=`value``
specifications separated by ampersands (`&`).
The allowed key words are the same ones recognized
by libpq (see
[libpq-paramkeywords](#libpq-paramkeywords)).  Spaces are ignored before
any `keyword` or `value`,
though not within or after one.  Note that there is no way to
write `&` within a `value`.

Notice that when specifying a socket connection
(with the `unix:` prefix), the host name must be
exactly `localhost`.  To select a non-default
socket directory, write the directory's pathname as the value of
a `host` option in
the `options` part of the target.

The `connection-name` is used to handle
multiple connections in one program.  It can be omitted if a
program uses only one connection.  The most recently opened
connection becomes the current connection, which is used by default
when an SQL statement is to be executed (see later in this
chapter).

Here are some examples of `CONNECT` statements:

```
EXEC SQL CONNECT TO mydb@sql.mydomain.com;

EXEC SQL CONNECT TO tcp:postgresql://sql.mydomain.com/mydb AS myconnection USER john;

EXEC SQL BEGIN DECLARE SECTION;
const char *target = "mydb@sql.mydomain.com";
const char *user = "john";
const char *passwd = "secret";
EXEC SQL END DECLARE SECTION;
...
EXEC SQL CONNECT TO :target USER :user USING :passwd;
/* or EXEC SQL CONNECT TO :target USER :user/:passwd; */
```

The last example makes use of the feature referred to above as
character variable references.  You will see in later sections how C
variables can be used in SQL statements when you prefix them with a
colon.

Be advised that the format of the connection target is not
specified in the SQL standard.  So if you want to develop portable
applications, you might want to use something based on the last
example above to encapsulate the connection target string
somewhere.

If untrusted users have access to a database that has not adopted a
[secure schema usage pattern](#ddl-schemas-patterns),
begin each session by removing publicly-writable schemas
from `search_path`.  For example,
add `options=-c search_path=`
to ``options``, or
issue `EXEC SQL SELECT pg_catalog.set_config('search_path', '',
false);` after connecting.  This consideration is not specific to
ECPG; it applies to every interface for executing arbitrary SQL commands.
