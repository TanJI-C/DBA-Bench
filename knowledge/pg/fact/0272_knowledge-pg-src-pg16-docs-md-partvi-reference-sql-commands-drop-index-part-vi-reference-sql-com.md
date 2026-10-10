# DROP INDEX

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_index.md`
- Source Title: `drop index`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP INDEX`
- Source Line Ranges: `1-72`
- Chunk ID: `pg16_fact_0272_01b87a8d64`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `0d3d8200c9f921e4feb6c2d7b9090f681c661fa271aa75f7f481c11069a7b3fa`

## Retrieval Guidance

- Use When: Use for index drop syntax and concurrency restrictions.
- Retrieval Keywords: DROP INDEX, DROP INDEX CONCURRENTLY, index removal, CASCADE, RESTRICT
- Follow-up Guidance: Confirm usage and dependencies before treating as remediation.
- Classification Note: Index removal syntax reference; removal can be operational but the page is general DDL reference.

## Official Source Content

DROP INDEX
7
SQL - Language Statements

DROP INDEX
remove an index

```
DROP INDEX [ CONCURRENTLY ] [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP INDEX` drops an existing index from the database
system. To execute this command you must be the owner of
the index.

## Parameters

**`CONCURRENTLY`**
: Drop the index without locking out concurrent selects, inserts, updates,
and deletes on the index's table.  A normal `DROP INDEX`
acquires an `ACCESS EXCLUSIVE` lock on the table,
blocking other accesses until the index drop can be completed.  With
this option, the command instead waits until conflicting transactions
have completed.

There are several caveats to be aware of when using this option.
Only one index name can be specified, and the `CASCADE` option
is not supported.  (Thus, an index that supports a `UNIQUE` or
`PRIMARY KEY` constraint cannot be dropped this way.)
Also, regular `DROP INDEX` commands can be
performed within a transaction block, but
`DROP INDEX CONCURRENTLY` cannot.
Lastly, indexes on partitioned tables cannot be dropped using this
option.

For temporary tables, `DROP INDEX` is always
non-concurrent, as no other session can access them, and
non-concurrent index drop is cheaper.

**`IF EXISTS`**
: Do not throw an error if the index does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of an index to remove.

**`CASCADE`**
: Automatically drop objects that depend on the index,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the index if any objects depend on it.  This is
the default.

## Examples

This command will remove the index `title_idx`:

```
DROP INDEX title_idx;
```

## Compatibility

`DROP INDEX` is a
PostgreSQL language extension.  There
are no provisions for indexes in the SQL standard.

## See Also
