# CALL

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/call.md`
- Source Title: `call`
- Source Heading Path: `Part VI Reference > SQL Commands > CALL`
- Source Line Ranges: `1-69`
- Chunk ID: `pg16_fact_0209_50aaffd34f`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `6c8b47e0e09201ed71ffa44e51a12c513da61bb12b4a79a468c52df44c1116fd`

## Retrieval Guidance

- Use When: Use for SQL procedure invocation syntax.
- Retrieval Keywords: CALL, procedure call, stored procedure, OUT parameter
- Follow-up Guidance: No section split needed.
- Classification Note: Procedure invocation syntax reference.

## Official Source Content

CALL
7
SQL - Language Statements

CALL
invoke a procedure

```
CALL `name` ( [ `argument` ] [, ...] )
```

## Description

`CALL` executes a procedure.

If the procedure has any output parameters, then a result row will be
returned, containing the values of those parameters.

## Parameters

**`name`**
: The name (optionally schema-qualified) of the procedure.

**`argument`**
: An argument expression for the procedure call.

Arguments can include parameter names, using the syntax
``name` => `value``.
This works the same as in ordinary function calls; see
[sql-syntax-calling-funcs](#sql-syntax-calling-funcs) for details.

Arguments must be supplied for all procedure parameters that lack
defaults, including `OUT` parameters.  However,
arguments matching `OUT` parameters are not evaluated,
so it's customary to just write `NULL` for them.
(Writing something else for an `OUT` parameter
might cause compatibility problems with
future PostgreSQL versions.)

## Notes

The user must have `EXECUTE` privilege on the procedure in
order to be allowed to invoke it.

To call a function (not a procedure), use `SELECT` instead.

If `CALL` is executed in a transaction block, then the
called procedure cannot execute transaction control statements.
Transaction control statements are only allowed if `CALL`
is executed in its own transaction.

PL/pgSQL handles output parameters
in `CALL` commands differently;
see [plpgsql-statements-calling-procedure](#plpgsql-statements-calling-procedure).

## Examples

```
CALL do_db_maintenance();
```

## Compatibility

`CALL` conforms to the SQL standard,
except for the handling of output parameters.  The standard
says that users should write variables to receive the values
of output parameters.

## See Also
