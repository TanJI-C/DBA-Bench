# The Schema Search Path; Usage Patterns

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/02_data_definition.md`
- Source Title: `Data Definition`
- Source Heading Path: `Data Definition > Schemas > The Schema Search Path; Usage Patterns`
- Source Line Ranges: `2032-2137, 2138-2164, 2188-2249`
- Chunk ID: `pg16_configuration_0181_a5761d9a83`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4fc647c9b85ac567344930df37c046e781238f067e9391b01e97a89268252d9`

## Retrieval Guidance

- Use When: Need to explain object lookup, unsafe schema search paths, or how to view/change schema resolution.
- Retrieval Keywords: search_path, SHOW search_path, SET search_path, ALTER ROLE SET, schema resolution, secure schema
- Follow-up Guidance: Check effective current_schemas and role/database-level settings before changing defaults.
- Classification Note: Explains SHOW search_path, SET search_path, secure search path patterns, and ALTER ROLE ALL SET search_path usage.

## Official Source Content

### The Schema Search Path

Qualified names are tedious to write, and it's often best not to
wire a particular schema name into applications anyway.  Therefore
tables are often referred to by *unqualified names*,
which consist of just the table name.  The system determines which table
is meant by following a *search path*, which is a list
of schemas to look in.  The first matching table in the search path
is taken to be the one wanted.  If there is no match in the search
path, an error is reported, even if matching table names exist
in other schemas in the database.

The ability to create like-named objects in different schemas complicates
writing a query that references precisely the same objects every time.  It
also opens up the potential for users to change the behavior of other
users' queries, maliciously or accidentally.  Due to the prevalence of
unqualified names in queries and their use
in PostgreSQL internals, adding a schema
to `search_path` effectively trusts all users having
`CREATE` privilege on that schema.  When you run an
ordinary query, a malicious user able to create objects in a schema of
your search path can take control and execute arbitrary SQL functions as
though you executed them.

The first schema named in the search path is called the current schema.
Aside from being the first schema searched, it is also the schema in
which new tables will be created if the `CREATE TABLE`
command does not specify a schema name.

To show the current search path, use the following command:

```
SHOW search_path;
```

In the default setup this returns:

```
search_path
--------------
"$user", public
```

The first element specifies that a schema with the same name as
the current user is to be searched.  If no such schema exists,
the entry is ignored.  The second element refers to the
public schema that we have seen already.

The first schema in the search path that exists is the default
location for creating new objects.  That is the reason that by
default objects are created in the public schema.  When objects
are referenced in any other context without schema qualification
(table modification, data modification, or query commands) the
search path is traversed until a matching object is found.
Therefore, in the default configuration, any unqualified access
again can only refer to the public schema.

To put our new schema in the path, we use:

```
SET search_path TO myschema,public;
```

(We omit the `$user` here because we have no
immediate need for it.)  And then we can access the table without
schema qualification:

```
DROP TABLE mytable;
```

Also, since `myschema` is the first element in
the path, new objects would by default be created in it.

We could also have written:

```
SET search_path TO myschema;
```

Then we no longer have access to the public schema without
explicit qualification.  There is nothing special about the public
schema except that it exists by default.  It can be dropped, too.

See also [functions-info](#functions-info) for other ways to manipulate
the schema search path.

The search path works in the same way for data type names, function names,
and operator names as it does for table names.  Data type and function
names can be qualified in exactly the same way as table names.  If you
need to write a qualified operator name in an expression, there is a
special provision: you must write

```
`OPERATOR(``schema``.``operator``)`
```

This is needed to avoid syntactic ambiguity.  An example is:

```
SELECT 3 OPERATOR(pg_catalog.+) 4;
```

In practice one usually relies on the search path for operators,
so as not to have to write anything so ugly as that.

### Schemas and Privileges

By default, users cannot access any objects in schemas they do not
own.  To allow that, the owner of the schema must grant the
`USAGE` privilege on the schema.  By default, everyone
has that privilege on the schema `public`.  To allow
users to make use of the objects in a schema, additional privileges might
need to be granted, as appropriate for the object.

A user can also be allowed to create objects in someone else's schema.  To
allow that, the `CREATE` privilege on the schema needs to
be granted.  In databases upgraded from
PostgreSQL 14 or earlier, everyone has that
privilege on the schema `public`.
Some [usage patterns](#ddl-schemas-patterns) call for
revoking that privilege:

```
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

(The first "public" is the schema, the second
"public" means "every user".  In the
first sense it is an identifier, in the second sense it is a
key word, hence the different capitalization; recall the
guidelines from [sql-syntax-identifiers](#sql-syntax-identifiers).)

### Usage Patterns

Schemas can be used to organize your data in many ways.
A *secure schema usage pattern* prevents untrusted
users from changing the behavior of other users' queries.  When a database
does not use a secure schema usage pattern, users wishing to securely
query that database would take protective action at the beginning of each
session.  Specifically, they would begin each session by
setting `search_path` to the empty string or otherwise
removing schemas that are writable by non-superusers
from `search_path`.  There are a few usage patterns
easily supported by the default configuration:

- Constrain ordinary users to user-private schemas.
To implement this pattern, first ensure that no schemas have
public `CREATE` privileges.  Then, for every user
needing to create non-temporary objects, create a schema with the
same name as that user, for example
`CREATE SCHEMA alice AUTHORIZATION alice`.
(Recall that the default search path starts
with `$user`, which resolves to the user
name. Therefore, if each user has a separate schema, they access
their own schemas by default.)  This pattern is a secure schema
usage pattern unless an untrusted user is the database owner or
has been granted `ADMIN OPTION` on a relevant role,
in which case no secure schema usage pattern exists.

In PostgreSQL 15 and later, the default
configuration supports this usage pattern.  In prior versions, or
when using a database that has been upgraded from a prior version,
you will need to remove the public `CREATE`
privilege from the `public` schema (issue
`REVOKE CREATE ON SCHEMA public FROM PUBLIC`).
Then consider auditing the `public` schema for
objects named like objects in schema `pg_catalog`.
- Remove the public schema from the default search path, by modifying
[`postgresql.conf`](#config-setting-configuration-file)
or by issuing `ALTER ROLE ALL SET search_path =
"$user"`.  Then, grant privileges to create in the public
schema.  Only qualified names will choose public schema objects.  While
qualified table references are fine, calls to functions in the public
schema [will be unsafe or
unreliable](#typeconv-func).  If you create functions or extensions in the public
schema, use the first pattern instead.  Otherwise, like the first
pattern, this is secure unless an untrusted user is the database owner
or has been granted `ADMIN OPTION` on a relevant role.
- Keep the default search path, and grant privileges to create in the
public schema.  All users access the public schema implicitly.  This
simulates the situation where schemas are not available at all, giving
a smooth transition from the non-schema-aware world.  However, this is
never a secure pattern.  It is acceptable only when the database has a
single user or a few mutually-trusting users.  In databases upgraded
from PostgreSQL 14 or earlier, this is the
default.

For any pattern, to install shared applications (tables to be used by
everyone, additional functions provided by third parties, etc.), put them
into separate schemas.  Remember to grant appropriate privileges to allow
the other users to access them.  Users can then refer to these additional
objects by qualifying the names with a schema name, or they can put the
additional schemas into their search path, as they choose.
