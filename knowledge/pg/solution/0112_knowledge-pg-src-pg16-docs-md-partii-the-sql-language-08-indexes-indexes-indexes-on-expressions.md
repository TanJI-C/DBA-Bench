# Indexes on Expressions

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/08_indexes.md`
- Source Title: `Indexes`
- Source Heading Path: `Indexes > Indexes on Expressions`
- Source Line Ranges: `528-582`
- Chunk ID: `pg16_solution_0112_ba2c6c9d84`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `34f38677bfc4d446a04da49e1d4b43068809cf36cbecef7d40458500d83f86fb`

## Retrieval Guidance

- Use When: Root cause is a slow predicate on an expression that cannot use a plain column index.
- Retrieval Keywords: expression index, functional index, lower, computed expression, case-insensitive search
- Follow-up Guidance: Ensure the query expression matches the index expression and verify with EXPLAIN.
- Classification Note: Shows expression indexes for queries such as lower(column) lookups or computed expressions, including the maintenance tradeoff.

## Official Source Content

## Indexes on Expressions

An index column need not be just a column of the underlying table,
but can be a function or scalar expression computed from one or
more columns of the table.  This feature is useful to obtain fast
access to tables based on the results of computations.

For example, a common way to do case-insensitive comparisons is to
use the `lower` function:

```
SELECT * FROM test1 WHERE lower(col1) = 'value';
```

This query can use an index if one has been
defined on the result of the `lower(col1)`
function:

```
CREATE INDEX test1_lower_col1_idx ON test1 (lower(col1));
```

If we were to declare this index `UNIQUE`, it would prevent
creation of rows whose `col1` values differ only in case,
as well as rows whose `col1` values are actually identical.
Thus, indexes on expressions can be used to enforce constraints that
are not definable as simple unique constraints.

As another example, if one often does queries like:

```
SELECT * FROM people WHERE (first_name || ' ' || last_name) = 'John Smith';
```

then it might be worth creating an index like this:

```
CREATE INDEX people_names ON people ((first_name || ' ' || last_name));
```

The syntax of the `CREATE INDEX` command normally requires
writing parentheses around index expressions, as shown in the second
example.  The parentheses can be omitted when the expression is just
a function call, as in the first example.

Index expressions are relatively expensive to maintain, because the
derived expression(s) must be computed for each row insertion
and [non-HOT update.](#storage-hot)  However, the index expressions are
*not* recomputed during an indexed search, since they are
already stored in the index.  In both examples above, the system
sees the query as just `WHERE indexedcolumn = 'constant'`
and so the speed of the search is equivalent to any other simple index
query.  Thus, indexes on expressions are useful when retrieval speed
is more important than insertion and update speed.
