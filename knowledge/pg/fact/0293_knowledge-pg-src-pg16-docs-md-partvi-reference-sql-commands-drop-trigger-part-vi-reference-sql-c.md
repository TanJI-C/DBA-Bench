# DROP TRIGGER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_trigger.md`
- Source Title: `drop trigger`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TRIGGER`
- Source Line Ranges: `1-57`
- Chunk ID: `pg16_fact_0293_60c8da691c`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `f541eca8bc03170b0777268f60d4994c68ac2bb017e82bd544c12b53cbf947cc`

## Retrieval Guidance

- Use When: Use for trigger drop syntax.
- Retrieval Keywords: DROP TRIGGER, trigger drop, ON table, CASCADE
- Follow-up Guidance: No section split needed.
- Classification Note: Trigger removal syntax reference.

## Official Source Content

DROP TRIGGER
7
SQL - Language Statements

DROP TRIGGER
remove a trigger

```
DROP TRIGGER [ IF EXISTS ] `name` ON `table_name` [ CASCADE | RESTRICT ]
```

## Description

`DROP TRIGGER` removes an existing
trigger definition. To execute this command, the current
user must be the owner of the table for which the trigger is defined.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the trigger does not exist. A notice is issued
in this case.

**`name`**
: The name of the trigger to remove.

**`table_name`**
: The name (optionally schema-qualified) of the table for which
the trigger is defined.

**`CASCADE`**
: Automatically drop objects that depend on the trigger,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the trigger if any objects depend on it.  This is
the default.

## Examples

Destroy the trigger `if_dist_exists` on the table
`films`:

```
DROP TRIGGER if_dist_exists ON films;
```

## Compatibility

The `DROP TRIGGER` statement in
PostgreSQL is incompatible with the SQL
standard.  In the SQL standard, trigger names are not local to
tables, so the command is simply `DROP TRIGGER
`name``.

## See Also
