# ALTER TABLESPACE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_tablespace.md`
- Source Title: `alter tablespace`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER TABLESPACE`
- Source Line Ranges: `1-73`
- Chunk ID: `pg16_fact_0198_a65946e3b2`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ff634d0c9a90253c3bf036d5ffa9efa3adc337127d62ae905b66bb53fdb58bfd`

## Retrieval Guidance

- Use When: Use for tablespace metadata and option syntax.
- Retrieval Keywords: ALTER TABLESPACE, tablespace owner, tablespace options, tablespace rename
- Follow-up Guidance: No section split needed.
- Classification Note: Tablespace object DDL reference for rename, owner, and options.

## Official Source Content

ALTER TABLESPACE
7
SQL - Language Statements

ALTER TABLESPACE
change the definition of a tablespace

```
ALTER TABLESPACE `name` RENAME TO `new_name`
ALTER TABLESPACE `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER TABLESPACE `name` SET ( `tablespace_option` = `value` [, ... ] )
ALTER TABLESPACE `name` RESET ( `tablespace_option` [, ... ] )
```

## Description

`ALTER TABLESPACE` can be used to change the definition of
a tablespace.

You must own the tablespace to change the definition of a tablespace.
To alter the owner, you must also be able to `SET ROLE`
to the new owning role.
(Note that superusers have these privileges automatically.)

## Parameters

**`name`**
: The name of an existing tablespace.

**`new_name`**
: The new name of the tablespace.  The new name cannot
begin with `pg_`, as such names
are reserved for system tablespaces.

**`new_owner`**
: The new owner of the tablespace.

**`tablespace_option`**
: A tablespace parameter to be set or reset.  Currently, the only
available parameters are `seq_page_cost`,
`random_page_cost`, `effective_io_concurrency`
and `maintenance_io_concurrency`.
Setting these values for a particular tablespace will override the
planner's usual estimate of the cost of reading pages from tables in
that tablespace, and the executor's prefetching behavior, as established
by the configuration parameters of the
same name (see [guc-seq-page-cost](#guc-seq-page-cost),
[guc-random-page-cost](#guc-random-page-cost),
[guc-effective-io-concurrency](#guc-effective-io-concurrency),
[guc-maintenance-io-concurrency](#guc-maintenance-io-concurrency)).  This may be useful if
one tablespace is located on a disk which is faster or slower than the
remainder of the I/O subsystem.

## Examples

Rename tablespace `index_space` to `fast_raid`:

```
ALTER TABLESPACE index_space RENAME TO fast_raid;
```

Change the owner of tablespace `index_space`:

```
ALTER TABLESPACE index_space OWNER TO mary;
```

## Compatibility

There is no `ALTER TABLESPACE` statement in
the SQL standard.

## See Also
