# EXECUTE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/execute.md`
- Source Title: `execute`
- Source Heading Path: `Part VI Reference > SQL Commands > EXECUTE`
- Source Line Ranges: `1-58`
- Chunk ID: `pg16_fact_0304_d9ad2e92dc`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `7982520ba5c8178f7a047a22862958226b1068c37c586aa4cdaf29591bea30b7`

## Retrieval Guidance

- Use When: Use for executing prepared statements.
- Retrieval Keywords: EXECUTE, prepared statement, PREPARE, parameter values
- Follow-up Guidance: No section split needed.
- Classification Note: Prepared statement execution syntax reference.

## Official Source Content

EXECUTE
7
SQL - Language Statements

EXECUTE
execute a prepared statement

```
EXECUTE `name` [ ( `parameter` [, ...] ) ]
```

## Description

`EXECUTE` is used to execute a previously prepared
statement. Since prepared statements only exist for the duration of a
session, the prepared statement must have been created by a
`PREPARE` statement executed earlier in the
current session.

If the `PREPARE` statement that created the statement
specified some parameters, a compatible set of parameters must be
passed to the `EXECUTE` statement, or else an
error is raised. Note that (unlike functions) prepared statements are
not overloaded based on the type or number of their parameters; the
name of a prepared statement must be unique within a database session.

For more information on the creation and usage of prepared statements,
see [sql-prepare](#sql-prepare).

## Parameters

**`name`**
: The name of the prepared statement to execute.

**`parameter`**
: The actual value of a parameter to the prepared statement.  This
must be an expression yielding a value that is compatible with
the data type of this parameter, as was determined when the
prepared statement was created.

## Outputs

The command tag returned by `EXECUTE`
is that of the prepared statement, and not `EXECUTE`.

## Examples

Examples are given in [sql-prepare-examples](#sql-prepare-examples)
in the [sql-prepare](#sql-prepare) documentation.

## Compatibility

The SQL standard includes an `EXECUTE` statement,
but it is only for use in embedded SQL.  This version of the
`EXECUTE` statement also uses a somewhat different
syntax.

## See Also
