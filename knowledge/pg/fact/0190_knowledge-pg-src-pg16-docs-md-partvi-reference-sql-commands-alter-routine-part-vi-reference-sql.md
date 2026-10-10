# non-configuration properties

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_routine.md`
- Source Title: `alter routine`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER ROUTINE > non-configuration properties`
- Source Line Ranges: `1-65`
- Chunk ID: `pg16_fact_0190_1eff3174b5`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `900d2d3cfcd904b7630eb0593446232068458846cf58bcd3c98bfd64dd401087`

## Retrieval Guidance

- Use When: Use for generic routine DDL syntax.
- Retrieval Keywords: ALTER ROUTINE, routine owner, routine schema, routine volatility
- Follow-up Guidance: Split SET/RESET configuration_parameter separately.
- Classification Note: Routine metadata reference covering aggregate/function/procedure rename, owner, schema, dependency, and planner/security properties.

## Official Source Content

ALTER ROUTINE
7
SQL - Language Statements

ALTER ROUTINE
change the definition of a routine

```
ALTER ROUTINE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
`action` [ ... ] [ RESTRICT ]
ALTER ROUTINE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
RENAME TO `new_name`
ALTER ROUTINE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER ROUTINE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
SET SCHEMA `new_schema`
ALTER ROUTINE `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ]
[ NO ] DEPENDS ON EXTENSION `extension_name`

where `action` is one of:

IMMUTABLE | STABLE | VOLATILE
[ NOT ] LEAKPROOF
[ EXTERNAL ] SECURITY INVOKER | [ EXTERNAL ] SECURITY DEFINER
PARALLEL { UNSAFE | RESTRICTED | SAFE }
COST `execution_cost`
ROWS `result_rows`
SET `configuration_parameter` { TO | = } { `value` | DEFAULT }
SET `configuration_parameter` FROM CURRENT
RESET `configuration_parameter`
RESET ALL
```

## Description

`ALTER ROUTINE` changes the definition of a routine, which
can be an aggregate function, a normal function, or a procedure.  See
under [sql-alteraggregate](#sql-alteraggregate), [sql-alterfunction](#sql-alterfunction),
and [sql-alterprocedure](#sql-alterprocedure) for the description of the
parameters, more examples, and further details.

## Examples

To rename the routine `foo` for type
`integer` to `foobar`:

```
ALTER ROUTINE foo(integer) RENAME TO foobar;
```

This command will work independent of whether `foo` is an
aggregate, function, or procedure.

## Compatibility

This statement is partially compatible with the `ALTER
ROUTINE` statement in the SQL standard.  See
under [sql-alterfunction](#sql-alterfunction)
and [sql-alterprocedure](#sql-alterprocedure) for more details.  Allowing
routine names to refer to aggregate functions is
a PostgreSQL extension.

## See Also

Note that there is no `CREATE ROUTINE` command.
