# DROP POLICY

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_policy.md`
- Source Title: `drop policy`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP POLICY`
- Source Line Ranges: `1-51`
- Chunk ID: `pg16_fact_0279_93dd5a52ef`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `f5fb2227c5504c4890874bfa98d46e8db082b587b4d741f47b63ffc19138bf29`

## Retrieval Guidance

- Use When: Use for policy drop syntax.
- Retrieval Keywords: DROP POLICY, RLS policy drop, row level security
- Follow-up Guidance: No section split needed.
- Classification Note: RLS policy removal syntax reference.

## Official Source Content

DROP POLICY
7
SQL - Language Statements

DROP POLICY
remove a row-level security policy from a table

```
DROP POLICY [ IF EXISTS ] `name` ON `table_name` [ CASCADE | RESTRICT ]
```

## Description

`DROP POLICY` removes the specified policy from the table.
Note that if the last policy is removed for a table and the table still has
row-level security enabled via `ALTER TABLE`, then the
default-deny policy will be used.  `ALTER TABLE ... DISABLE ROW
LEVEL SECURITY` can be used to disable row-level security for a
table, whether policies for the table exist or not.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the policy does not exist. A notice is issued
in this case.

**`name`**
: The name of the policy to drop.

**`table_name`**
: The name (optionally schema-qualified) of the table that
the policy is on.

**`CASCADE`**
: These key words do not have any effect, since there are no
dependencies on policies.

## Examples

To drop the policy called `p1` on the table named
`my_table`:

```
DROP POLICY p1 ON my_table;
```

## Compatibility

`DROP POLICY` is a PostgreSQL extension.

## See Also
