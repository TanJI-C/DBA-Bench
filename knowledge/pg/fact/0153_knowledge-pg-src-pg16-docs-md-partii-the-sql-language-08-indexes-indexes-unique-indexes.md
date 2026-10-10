# Unique Indexes

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/08_indexes.md`
- Source Title: `Indexes`
- Source Heading Path: `Indexes > Unique Indexes`
- Source Line Ranges: `497-527`
- Chunk ID: `pg16_fact_0153_2011991588`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `082f219f765d0be6b469d50a7b5b7ba241f84de356ac9665e957619274dc8bba`

## Retrieval Guidance

- Use When: Need facts about uniqueness semantics and how PostgreSQL enforces them.
- Retrieval Keywords: unique index, unique constraint, NULLS DISTINCT, NULLS NOT DISTINCT, primary key
- Follow-up Guidance: Use ALTER TABLE constraint syntax for schema-level uniqueness declarations where appropriate.
- Classification Note: Explains uniqueness enforcement, NULL behavior, and relationship to unique constraints as schema semantics.

## Official Source Content

## Unique Indexes

Indexes can also be used to enforce uniqueness of a column's value,
or the uniqueness of the combined values of more than one column.

```
CREATE UNIQUE INDEX `name` ON `table` (`column` , ...)  NULLS  NOT  DISTINCT ;
```

Currently, only B-tree indexes can be declared unique.

When an index is declared unique, multiple table rows with equal
indexed values are not allowed.  By default, null values in a unique column
are not considered equal, allowing multiple nulls in the column.  The
`NULLS NOT DISTINCT` option modifies this and causes the
index to treat nulls as equal.  A multicolumn unique index will only reject
cases where all indexed columns are equal in multiple rows.

PostgreSQL automatically creates a unique
index when a unique constraint or primary key is defined for a table.
The index covers the columns that make up the primary key or unique
constraint (a multicolumn index, if appropriate), and is the mechanism
that enforces the constraint.

> **Note:**

> There's no need to manually
> create indexes on unique columns; doing so would just duplicate
> the automatically-created index.
>
