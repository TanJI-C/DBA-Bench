# SELECT

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/select.md`
- Source Title: `select`
- Source Heading Path: `Part VI Reference > SQL Commands > SELECT`
- Source Line Ranges: `827-892, 1601-1609, 1627-1632`
- Chunk ID: `pg16_fact_0325_27329bf66b`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1bd17432207cb4efa38a71fdabaa683726ddeabd2a8605305b08d88f3d66f6ed`

## Retrieval Guidance

- Use When: Use for SELECT syntax and clause semantics.
- Retrieval Keywords: SELECT, WITH, FROM, WHERE, GROUP BY, ORDER BY, LIMIT, FOR UPDATE
- Follow-up Guidance: Use EXPLAIN for diagnostic confirmation of SELECT performance behavior.
- Classification Note: Large query syntax reference for clauses, locking clause, set operations, and compatibility; it is foundational SQL reference rather than a diagnostic guide.

## Official Source Content

### `SELECT` List

The `SELECT` list (between the key words
`SELECT` and `FROM`) specifies expressions
that form the output rows of the `SELECT`
statement.  The expressions can (and usually do) refer to columns
computed in the `FROM` clause.

Just as in a table, every output column of a `SELECT`
has a name.  In a simple `SELECT` this name is just
used to label the column for display, but when the `SELECT`
is a sub-query of a larger query, the name is seen by the larger query
as the column name of the virtual table produced by the sub-query.
To specify the name to use for an output column, write
`AS` `output_name`
after the column's expression.  (You can omit `AS`,
but only if the desired output name does not match any
PostgreSQL keyword (see [sql-keywords-appendix](#sql-keywords-appendix)).  For protection against possible
future keyword additions, it is recommended that you always either
write `AS` or double-quote the output name.)
If you do not specify a column name, a name is chosen automatically
by PostgreSQL.  If the column's expression
is a simple column reference then the chosen name is the same as that
column's name.  In more complex cases a function or type name may be
used, or the system may fall back on a generated name such as
`?column?`.

An output column's name can be used to refer to the column's value in
`ORDER BY` and `GROUP BY` clauses, but not in the
`WHERE` or `HAVING` clauses; there you must write
out the expression instead.

Instead of an expression, `*` can be written in
the output list as a shorthand for all the columns of the selected
rows.  Also, you can write ``table_name`.*` as a
shorthand for the columns coming from just that table.  In these
cases it is not possible to specify new names with `AS`;
the output column names will be the same as the table columns' names.

According to the SQL standard, the expressions in the output list should
be computed before applying `DISTINCT`, `ORDER
BY`, or `LIMIT`.  This is obviously necessary
when using `DISTINCT`, since otherwise it's not clear
what values are being made distinct.  However, in many cases it is
convenient if output expressions are computed after `ORDER
BY` and `LIMIT`; particularly if the output list
contains any volatile or expensive functions.  With that behavior, the
order of function evaluations is more intuitive and there will not be
evaluations corresponding to rows that never appear in the output.
PostgreSQL will effectively evaluate output expressions
after sorting and limiting, so long as those expressions are not
referenced in `DISTINCT`, `ORDER BY`
or `GROUP BY`.  (As a counterexample, `SELECT
f(x) FROM tab ORDER BY 1` clearly must evaluate `f(x)`
before sorting.)  Output expressions that contain set-returning functions
are effectively evaluated after sorting and before limiting, so
that `LIMIT` will act to cut off the output from a
set-returning function.

> **Note:**

> PostgreSQL versions before 9.6 did not provide any
> guarantees about the timing of evaluation of output expressions versus
> sorting and limiting; it depended on the form of the chosen query plan.
>

### Empty `SELECT` Lists

The list of output expressions after `SELECT` can be
empty, producing a zero-column result table.
This is not valid syntax according to the SQL standard.
PostgreSQL allows it to be consistent with
allowing zero-column tables.
However, an empty list is not allowed when `DISTINCT` is used.

### Omitting Sub-`SELECT` Aliases in `FROM`

According to the SQL standard, a sub-`SELECT` in the
`FROM` list must have an alias.  In
PostgreSQL, this alias may be omitted.
