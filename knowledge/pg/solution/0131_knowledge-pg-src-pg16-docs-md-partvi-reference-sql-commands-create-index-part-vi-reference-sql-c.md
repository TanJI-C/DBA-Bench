# index creation / concurrent build / examples

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_index.md`
- Source Title: `create index`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE INDEX > index creation / concurrent build / examples`
- Source Line Ranges: `548-629`
- Chunk ID: `pg16_solution_0131_da5565e53b`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6f09fb7d90e060b43dbad48e0f845072a97a708b0fcc84652b316c9bd9af496`

## Retrieval Guidance

- Use When: Use after EXPLAIN/workload evidence confirms an index is the appropriate remediation.
- Retrieval Keywords: CREATE INDEX, missing index, CONCURRENTLY, partial index, expression index, covering index
- Follow-up Guidance: Choose concurrent/non-concurrent build based on lock tolerance; run ANALYZE and verify plan changes.
- Classification Note: Index creation is a corrective/tuning action after confirming missing index, access path, uniqueness, or partial-index need.

## Official Source Content

## Examples

To create a unique B-tree index on the column `title` in
the table `films`:

```
CREATE UNIQUE INDEX title_idx ON films (title);
```

To create a unique B-tree index on the column `title`
with included columns `director`
and `rating` in the table `films`:

```
CREATE UNIQUE INDEX title_idx ON films (title) INCLUDE (director, rating);
```

To create a B-Tree index with deduplication disabled:

```
CREATE INDEX title_idx ON films (title) WITH (deduplicate_items = off);
```

To create an index on the expression `lower(title)`,
allowing efficient case-insensitive searches:

```
CREATE INDEX ON films ((lower(title)));
```

(In this example we have chosen to omit the index name, so the system
will choose a name, typically `films_lower_idx`.)

To create an index with non-default collation:

```
CREATE INDEX title_idx_german ON films (title COLLATE "de_DE");
```

To create an index with non-default sort ordering of nulls:

```
CREATE INDEX title_idx_nulls_low ON films (title NULLS FIRST);
```

To create an index with non-default fill factor:

```
CREATE UNIQUE INDEX title_idx ON films (title) WITH (fillfactor = 70);
```

To create a GIN index with fast updates disabled:

```
CREATE INDEX gin_idx ON documents_table USING GIN (locations) WITH (fastupdate = off);
```

To create an index on the column `code` in the table
`films` and have the index reside in the tablespace
`indexspace`:

```
CREATE INDEX code_idx ON films (code) TABLESPACE indexspace;
```

To create a GiST index on a point attribute so that we
can efficiently use box operators on the result of the
conversion function:

```
CREATE INDEX pointloc
ON points USING gist (box(location,location));
SELECT * FROM points
WHERE box(location,location) && '(0,0),(1,1)'::box;
```

To create an index without locking out writes to the table:

```
CREATE INDEX CONCURRENTLY sales_quantity_index ON sales_table (quantity);
```
