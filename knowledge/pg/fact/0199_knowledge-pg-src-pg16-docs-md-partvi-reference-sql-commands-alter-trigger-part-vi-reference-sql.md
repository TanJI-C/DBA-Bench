# ALTER TRIGGER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_trigger.md`
- Source Title: `alter trigger`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER TRIGGER`
- Source Line Ranges: `1-75`
- Chunk ID: `pg16_fact_0199_516a2d015d`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `8f9c697c060f40721de0b627f38d26d7ad264a6d04c534ed6cdc98a63be2f818`

## Retrieval Guidance

- Use When: Use for trigger metadata syntax.
- Retrieval Keywords: ALTER TRIGGER, trigger rename, trigger dependency
- Follow-up Guidance: No section split needed.
- Classification Note: Trigger object DDL reference for rename and dependency changes.

## Official Source Content

ALTER TRIGGER
7
SQL - Language Statements

ALTER TRIGGER
change the definition of a trigger

```
ALTER TRIGGER `name` ON `table_name` RENAME TO `new_name`
ALTER TRIGGER `name` ON `table_name` [ NO ] DEPENDS ON EXTENSION `extension_name`
```

## Description

`ALTER TRIGGER` changes properties of an existing
trigger.

The `RENAME` clause changes the name of
the given trigger without otherwise changing the trigger
definition.
If the table that the trigger is on is a partitioned table,
then corresponding clone triggers in the partitions are
renamed too.

The `DEPENDS ON EXTENSION` clause marks
the trigger as dependent on an extension, such that if the extension is
dropped, the trigger will automatically be dropped as well.

You must own the table on which the trigger acts to be allowed to change its properties.

## Parameters

**`name`**
: The name of an existing trigger to alter.

**`table_name`**
: The name of the table on which this trigger acts.

**`new_name`**
: The new name for the trigger.

**`extension_name`**
: The name of the extension that the trigger is to depend on (or no longer
dependent on, if `NO` is specified).  A trigger
that's marked as dependent on an extension is automatically dropped when
the extension is dropped.

## Notes

The ability to temporarily enable or disable a trigger is provided by
[`ALTER TABLE`](#sql-altertable), not by
`ALTER TRIGGER`, because `ALTER TRIGGER` has no
convenient way to express the option of enabling or disabling all of
a table's triggers at once.

## Examples

To rename an existing trigger:

```
ALTER TRIGGER emp_stamp ON emp RENAME TO emp_track_chgs;
```

To mark a trigger as being dependent on an extension:

```
ALTER TRIGGER emp_stamp ON emp DEPENDS ON EXTENSION emplib;
```

## Compatibility

`ALTER TRIGGER` is a PostgreSQL
extension of the SQL standard.

## See Also
