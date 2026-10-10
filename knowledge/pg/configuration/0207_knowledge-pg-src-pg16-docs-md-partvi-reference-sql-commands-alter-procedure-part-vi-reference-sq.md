# SET/RESET configuration_parameter

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_procedure.md`
- Source Title: `alter procedure`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER PROCEDURE > SET/RESET configuration_parameter`
- Source Line Ranges: `1-168`
- Chunk ID: `pg16_configuration_0207_a5fdf0c8fe`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `5ea27f90067f2e6997d52ea3d9464c83d96cabd62da2a44d7e8762fbca796e41`

## Retrieval Guidance

- Use When: Use when changing runtime parameter context for a stored procedure.
- Retrieval Keywords: ALTER PROCEDURE SET, procedure-local setting, configuration_parameter, search_path procedure
- Follow-up Guidance: Verify behavior on procedure entry and reset semantics.
- Classification Note: This subsection attaches or removes procedure-local runtime configuration values applied when the procedure is called.

## Official Source Content

ALTER PROCEDURE
7
SQL - Language Statements

ALTER PROCEDURE
change the definition of a procedure

```
ALTER PROCEDURE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
`action` [ ... ] [ RESTRICT ]
ALTER PROCEDURE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
RENAME TO `new_name`
ALTER PROCEDURE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER PROCEDURE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
SET SCHEMA `new_schema`
ALTER PROCEDURE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
[ NO ] DEPENDS ON EXTENSION `extension_name`

where `action` is one of:

[ EXTERNAL ] SECURITY INVOKER | [ EXTERNAL ] SECURITY DEFINER
SET `configuration_parameter` { TO | = } { `value` | DEFAULT }
SET `configuration_parameter` FROM CURRENT
RESET `configuration_parameter`
RESET ALL
```

## Description

`ALTER PROCEDURE` changes the definition of a
procedure.

You must own the procedure to use `ALTER PROCEDURE`.
To change a procedure's schema, you must also have `CREATE`
privilege on the new schema.
To alter the owner, you must be able to `SET ROLE` to the
new owning role, and that role must have `CREATE`
privilege on the procedure's schema.
(These restrictions enforce that altering the owner
doesn't do anything you couldn't do by dropping and recreating the procedure.
However, a superuser can alter ownership of any procedure anyway.)

## Parameters

**`name`**
: The name (optionally schema-qualified) of an existing procedure.  If no
argument list is specified, the name must be unique in its schema.

**`argmode`**
: The mode of an argument: `IN`, `OUT`,
`INOUT`, or `VARIADIC`.  If omitted,
the default is `IN`.

**`argname`**
: The name of an argument.
Note that `ALTER PROCEDURE` does not actually pay
any attention to argument names, since only the argument data
types are used to determine the procedure's identity.

**`argtype`**
: The data type(s) of the procedure's arguments (optionally
schema-qualified), if any.
See [sql-dropprocedure](#sql-dropprocedure) for the details of how
the procedure is looked up using the argument data type(s).

**`new_name`**
: The new name of the procedure.

**`new_owner`**
: The new owner of the procedure.  Note that if the procedure is
marked `SECURITY DEFINER`, it will subsequently
execute as the new owner.

**`new_schema`**
: The new schema for the procedure.

**`extension_name`**
: This form marks the procedure as dependent on the extension, or no longer
dependent on the extension if `NO` is specified.
A procedure that's marked as dependent on an extension is dropped when the
extension is dropped, even if cascade is not specified.
A procedure can depend upon multiple extensions, and will be dropped when
any one of those extensions is dropped.

**` EXTERNAL  SECURITY INVOKER`**
: Change whether the procedure is a security definer or not. The
key word `EXTERNAL` is ignored for SQL
conformance. See [sql-createprocedure](#sql-createprocedure) for more information about
this capability.

**`configuration_parameter`**
: Add or change the assignment to be made to a configuration parameter
when the procedure is called.  If
`value` is `DEFAULT`
or, equivalently, `RESET` is used, the procedure-local
setting is removed, so that the procedure executes with the value
present in its environment.  Use `RESET
ALL` to clear all procedure-local settings.
`SET FROM CURRENT` saves the value of the parameter that
is current when `ALTER PROCEDURE` is executed as the value
to be applied when the procedure is entered.

See [sql-set](#sql-set) and
[runtime-config](#runtime-config)
for more information about allowed parameter names and values.

**`RESTRICT`**
: Ignored for conformance with the SQL standard.

## Examples

To rename the procedure `insert_data` with two arguments
of type `integer` to `insert_record`:

```
ALTER PROCEDURE insert_data(integer, integer) RENAME TO insert_record;
```

To change the owner of the procedure `insert_data` with
two arguments of type `integer` to `joe`:

```
ALTER PROCEDURE insert_data(integer, integer) OWNER TO joe;
```

To change the schema of the procedure `insert_data` with
two arguments of type `integer`
to `accounting`:

```
ALTER PROCEDURE insert_data(integer, integer) SET SCHEMA accounting;
```

To mark the procedure `insert_data(integer, integer)` as
being dependent on the extension `myext`:

```
ALTER PROCEDURE insert_data(integer, integer) DEPENDS ON EXTENSION myext;
```

To adjust the search path that is automatically set for a procedure:

```
ALTER PROCEDURE check_password(text) SET search_path = admin, pg_temp;
```

To disable automatic setting of `search_path` for a procedure:

```
ALTER PROCEDURE check_password(text) RESET search_path;
```

The procedure will now execute with whatever search path is used by its
caller.

## Compatibility

This statement is partially compatible with the `ALTER
PROCEDURE` statement in the SQL standard. The standard allows more
properties of a procedure to be modified, but does not provide the
ability to rename a procedure, make a procedure a security definer,
attach configuration parameter values to a procedure,
or change the owner, schema, or volatility of a procedure. The standard also
requires the `RESTRICT` key word, which is optional in
PostgreSQL.

## See Also
