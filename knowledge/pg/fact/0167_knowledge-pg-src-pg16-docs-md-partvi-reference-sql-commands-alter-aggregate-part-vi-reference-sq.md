# ALTER AGGREGATE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_aggregate.md`
- Source Title: `alter aggregate`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER AGGREGATE`
- Source Line Ranges: `1-115`
- Chunk ID: `pg16_fact_0167_2611a51e84`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `c2a71e0bfdce048e30cf0451cd59e582445b24b5383165398bb2d3a148eb12d9`

## Retrieval Guidance

- Use When: Use for aggregate DDL syntax and ownership/schema changes.
- Retrieval Keywords: ALTER AGGREGATE, aggregate owner, aggregate schema, aggregate rename
- Follow-up Guidance: No section split needed.
- Classification Note: Object-definition reference for changing aggregate metadata such as name, owner, schema, or extension dependency.

## Official Source Content

ALTER AGGREGATE
7
SQL - Language Statements

ALTER AGGREGATE
change the definition of an aggregate function

```
ALTER AGGREGATE `name` ( `aggregate_signature` ) RENAME TO `new_name`
ALTER AGGREGATE `name` ( `aggregate_signature` )
OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER AGGREGATE `name` ( `aggregate_signature` ) SET SCHEMA `new_schema`

where `aggregate_signature` is:

* |
[ `argmode` ] [ `argname` ] `argtype` [ , ... ] |
[ [ `argmode` ] [ `argname` ] `argtype` [ , ... ] ] ORDER BY [ `argmode` ] [ `argname` ] `argtype` [ , ... ]
```

## Description

`ALTER AGGREGATE` changes the definition of an
aggregate function.

You must own the aggregate function to use `ALTER AGGREGATE`.
To change the schema of an aggregate function, you must also have
`CREATE` privilege on the new schema.
To alter the owner, you must be able to `SET ROLE` to the
new owning role, and that role must have `CREATE`
privilege on the aggregate function's schema.
(These restrictions enforce that altering
the owner doesn't do anything you couldn't do by dropping and recreating
the aggregate function.  However, a superuser can alter ownership of any
aggregate function anyway.)

## Parameters

**`name`**
: The name (optionally schema-qualified) of an existing aggregate function.

**`argmode`**
: The mode of an argument: `IN` or `VARIADIC`.
If omitted, the default is `IN`.

**`argname`**
: The name of an argument.
Note that `ALTER AGGREGATE` does not actually pay
any attention to argument names, since only the argument data
types are needed to determine the aggregate function's identity.

**`argtype`**
: An input data type on which the aggregate function operates.
To reference a zero-argument aggregate function, write `*`
in place of the list of argument specifications.
To reference an ordered-set aggregate function, write
`ORDER BY` between the direct and aggregated argument
specifications.

**`new_name`**
: The new name of the aggregate function.

**`new_owner`**
: The new owner of the aggregate function.

**`new_schema`**
: The new schema for the aggregate function.

## Notes

The recommended syntax for referencing an ordered-set aggregate
is to write `ORDER BY` between the direct and aggregated
argument specifications, in the same style as in
[`CREATE AGGREGATE`](#sql-createaggregate).  However, it will also work to
omit `ORDER BY` and just run the direct and aggregated
argument specifications into a single list.  In this abbreviated form,
if `VARIADIC "any"` was used in both the direct and
aggregated argument lists, write `VARIADIC "any"` only once.

## Examples

To rename the aggregate function `myavg` for type
`integer` to `my_average`:

```
ALTER AGGREGATE myavg(integer) RENAME TO my_average;
```

To change the owner of the aggregate function `myavg` for type
`integer` to `joe`:

```
ALTER AGGREGATE myavg(integer) OWNER TO joe;
```

To move the ordered-set aggregate `mypercentile` with
direct argument of type `float8` and aggregated argument
of type `integer` into schema `myschema`:

```
ALTER AGGREGATE mypercentile(float8 ORDER BY integer) SET SCHEMA myschema;
```

This will work too:

```
ALTER AGGREGATE mypercentile(float8, integer) SET SCHEMA myschema;
```

## Compatibility

There is no `ALTER AGGREGATE` statement in the SQL
standard.

## See Also
