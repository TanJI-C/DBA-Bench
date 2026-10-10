# DROP STATISTICS

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_statistics.md`
- Source Title: `drop statistics`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP STATISTICS`
- Source Line Ranges: `1-46`
- Chunk ID: `pg16_fact_0288_5ce8d99004`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `8566fbf31d3a9155fe097f9a17410e7b768ae0218b0e3cd95ccfe6940acb31e5`

## Retrieval Guidance

- Use When: Use for extended statistics drop syntax.
- Retrieval Keywords: DROP STATISTICS, extended statistics drop, planner statistics
- Follow-up Guidance: No section split needed.
- Classification Note: Extended statistics object removal syntax reference.

## Official Source Content

DROP STATISTICS
7
SQL - Language Statements

DROP STATISTICS
remove extended statistics

```
DROP STATISTICS [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP STATISTICS` removes statistics object(s) from the
database.  Only the statistics object's owner, the schema owner, or a
superuser can drop a statistics object.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the statistics object does not exist. A notice
is issued in this case.

**`name`**
: The name (optionally schema-qualified) of the statistics object to drop.

**`CASCADE`**
: These key words do not have any effect, since there are no dependencies
on statistics.

## Examples

To destroy two statistics objects in different schemas, without failing
if they don't exist:

```
DROP STATISTICS IF EXISTS
accounting.users_uid_creation,
public.grants_user_role;
```

## Compatibility

There is no `DROP STATISTICS` command in the SQL standard.

## See Also
