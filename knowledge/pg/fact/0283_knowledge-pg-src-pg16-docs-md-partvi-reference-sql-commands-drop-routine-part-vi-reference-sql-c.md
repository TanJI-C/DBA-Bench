# DROP ROUTINE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_routine.md`
- Source Title: `drop routine`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP ROUTINE`
- Source Line Ranges: `1-68`
- Chunk ID: `pg16_fact_0283_5e0b5f77f7`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `01074cdc3409fe77af1861c6cba6ba91dc7801b6b94b88fe3b7d7322f3e9c53b`

## Retrieval Guidance

- Use When: Use for generic routine drop syntax.
- Retrieval Keywords: DROP ROUTINE, function procedure drop, routine signature
- Follow-up Guidance: No section split needed.
- Classification Note: Generic routine removal syntax reference.

## Official Source Content

DROP ROUTINE
7
SQL - Language Statements

DROP ROUTINE
remove a routine

```
DROP ROUTINE [ IF EXISTS ] `name` [ ( [ [ `argmode` ] [ `argname` ] `argtype` [, ...] ] ) ] [, ...]
[ CASCADE | RESTRICT ]
```

## Description

`DROP ROUTINE` removes the definition of one or more
existing routines.  The term "routine" includes
aggregate functions, normal functions, and procedures.  See
under [sql-dropaggregate](#sql-dropaggregate), [sql-dropfunction](#sql-dropfunction),
and [sql-dropprocedure](#sql-dropprocedure) for the description of the
parameters, more examples, and further details.

## Notes

The lookup rules used by `DROP ROUTINE` are
fundamentally the same as for `DROP PROCEDURE`; in
particular, `DROP ROUTINE` shares that command's
behavior of considering an argument list that has
no `argmode` markers to be
possibly using the SQL standard's definition that `OUT`
arguments are included in the list.  (`DROP AGGREGATE`
and `DROP FUNCTION` do not do that.)

In some cases where the same name is shared by routines of different
kinds, it is possible for `DROP ROUTINE` to fail with
an ambiguity error when a more specific command (`DROP
FUNCTION`, etc.) would work.  Specifying the argument type
list more carefully will also resolve such problems.

These lookup rules are also used by other commands that
act on existing routines, such as `ALTER ROUTINE`
and `COMMENT ON ROUTINE`.

## Examples

To drop the routine `foo` for type
`integer`:

```
DROP ROUTINE foo(integer);
```

This command will work independent of whether `foo` is an
aggregate, function, or procedure.

## Compatibility

This command conforms to the SQL standard, with
these PostgreSQL extensions:

- The standard only allows one routine to be dropped per command.
- The `IF EXISTS` option is an extension.
- The ability to specify argument modes and names is an
extension, and the lookup rules differ when modes are given.
- User-definable aggregate functions are an extension.

## See Also

Note that there is no `CREATE ROUTINE` command.
