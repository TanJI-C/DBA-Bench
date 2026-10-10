# ALTER STATISTICS

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_statistics.md`
- Source Title: `alter statistics`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER STATISTICS`
- Source Line Ranges: `1-63`
- Chunk ID: `pg16_fact_0195_d43a61a2c3`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `6c4e865e0d195f491a2e4757c426a0164feff2a3e3b757ffb7e98668d915df32`

## Retrieval Guidance

- Use When: Use for changing extended statistics object properties.
- Retrieval Keywords: ALTER STATISTICS, statistics target, extended statistics owner, statistics schema
- Follow-up Guidance: Pair with ANALYZE when changed statistics definitions need fresh data.
- Classification Note: Extended statistics object DDL reference for target, owner, schema, and rename; by itself it is object reference rather than collection/remediation.

## Official Source Content

ALTER STATISTICS
7
SQL - Language Statements

ALTER STATISTICS

change the definition of an extended statistics object

```
ALTER STATISTICS `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER STATISTICS `name` RENAME TO `new_name`
ALTER STATISTICS `name` SET SCHEMA `new_schema`
ALTER STATISTICS `name` SET STATISTICS `new_target`
```

## Description

`ALTER STATISTICS` changes the parameters of an existing
extended statistics object.  Any parameters not specifically set in the
`ALTER STATISTICS` command retain their prior settings.

You must own the statistics object to use `ALTER STATISTICS`.
To change a statistics object's schema, you must also
have `CREATE` privilege on the new schema.
To alter the owner, you must be able to `SET ROLE` to the
new owning role, and that role must have `CREATE`
privilege on the statistics object's schema.
(These restrictions enforce that altering
the owner doesn't do anything you couldn't do by dropping and recreating
the statistics object.  However, a superuser can alter ownership of any
statistics object anyway.)

## Parameters

**`name`**
: The name (optionally schema-qualified) of the statistics object to be
altered.

**`new_owner`**
: The user name of the new owner of the statistics object.

**`new_name`**
: The new name for the statistics object.

**`new_schema`**
: The new schema for the statistics object.

**`new_target`**
: The statistic-gathering target for this statistics object for subsequent
[`ANALYZE`](#sql-analyze) operations.
The target can be set in the range 0 to 10000; alternatively, set it
to -1 to revert to using the maximum of the statistics target of the
referenced columns, if set, or the system default statistics
target ([guc-default-statistics-target](#guc-default-statistics-target)).
For more information on the use of statistics by the
PostgreSQL query planner, refer to
[planner-stats](#planner-stats).

## Compatibility

There is no `ALTER STATISTICS` command in the SQL standard.

## See Also
