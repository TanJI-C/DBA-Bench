# Creating a Schema; The Public Schema; Schemas and Privileges; The System Catalog Schema; Portability

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/02_data_definition.md`
- Source Title: `Data Definition`
- Source Heading Path: `Data Definition > Schemas > Creating a Schema; The Public Schema; Schemas and Privileges; The System Catalog Schema; Portability`
- Source Line Ranges: `1943-2014, 2015-2031, 2138-2164, 2165-2187, 2250-2273`
- Chunk ID: `pg16_fact_0144_b0f3b7128f`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `78a05c72cdcca9ad328cb18b235d2e5fb5669124cd24bfb26b5cfb3383783a9d`

## Retrieval Guidance

- Use When: Need facts about schema organization and name resolution context.
- Retrieval Keywords: schema, CREATE SCHEMA, public schema, pg_catalog, schema privileges
- Follow-up Guidance: Use the search_path configuration record for session path behavior.
- Classification Note: Reference material for schema objects, public schema behavior, schema privileges, pg_catalog visibility, and portability considerations.

## Official Source Content

### Creating a Schema

To create a schema, use the [sql-createschema](#sql-createschema)
command.  Give the schema a name
of your choice.  For example:

```
CREATE SCHEMA myschema;
```

To create or access objects in a schema, write a
*qualified name* consisting of the schema name and
table name separated by a dot:

```
`schema``.``table`
```

This works anywhere a table name is expected, including the table
modification commands and the data access commands discussed in
the following chapters.
(For brevity we will speak of tables only, but the same ideas apply
to other kinds of named objects, such as types and functions.)

Actually, the even more general syntax

```
`database``.``schema``.``table`
```

can be used too, but at present this is just for pro forma
compliance with the SQL standard.  If you write a database name,
it must be the same as the database you are connected to.

So to create a table in the new schema, use:

```
CREATE TABLE myschema.mytable (
...
);
```

To drop a schema if it's empty (all objects in it have been
dropped), use:

```
DROP SCHEMA myschema;
```

To drop a schema including all contained objects, use:

```
DROP SCHEMA myschema CASCADE;
```

See [ddl-depend](#ddl-depend) for a description of the general
mechanism behind this.

Often you will want to create a schema owned by someone else
(since this is one of the ways to restrict the activities of your
users to well-defined namespaces).  The syntax for that is:

```
CREATE SCHEMA `schema_name` AUTHORIZATION `user_name`;
```

You can even omit the schema name, in which case the schema name
will be the same as the user name.  See [ddl-schemas-patterns](#ddl-schemas-patterns) for how this can be useful.

Schema names beginning with `pg_` are reserved for
system purposes and cannot be created by users.

### The Public Schema

In the previous sections we created tables without specifying any
schema names.  By default such tables (and other objects) are
automatically put into a schema named "public".  Every new
database contains such a schema.  Thus, the following are equivalent:

```
CREATE TABLE products ( ... );
```

and:

```
CREATE TABLE public.products ( ... );
```

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

### The System Catalog Schema

In addition to `public` and user-created schemas, each
database contains a `pg_catalog` schema, which contains
the system tables and all the built-in data types, functions, and
operators.  `pg_catalog` is always effectively part of
the search path.  If it is not named explicitly in the path then
it is implicitly searched *before* searching the path's
schemas.  This ensures that built-in names will always be
findable.  However, you can explicitly place
`pg_catalog` at the end of your search path if you
prefer to have user-defined names override built-in names.

Since system table names begin with `pg_`, it is best to
avoid such names to ensure that you won't suffer a conflict if some
future version defines a system table named the same as your
table.  (With the default search path, an unqualified reference to
your table name would then be resolved as the system table instead.)
System tables will continue to follow the convention of having
names beginning with `pg_`, so that they will not
conflict with unqualified user-table names so long as users avoid
the `pg_` prefix.

### Portability

In the SQL standard, the notion of objects in the same schema
being owned by different users does not exist.  Moreover, some
implementations do not allow you to create schemas that have a
different name than their owner.  In fact, the concepts of schema
and user are nearly equivalent in a database system that
implements only the basic schema support specified in the
standard.  Therefore, many users consider qualified names to
really consist of
``user_name`.`table_name``.
This is how PostgreSQL will effectively
behave if you create a per-user schema for every user.

Also, there is no concept of a `public` schema in the
SQL standard.  For maximum conformance to the standard, you should
not use the `public` schema.

Of course, some SQL database systems might not implement schemas
at all, or provide namespace support by allowing (possibly
limited) cross-database access.  If you need to work with those
systems, then maximum portability would be achieved by not using
schemas at all.
