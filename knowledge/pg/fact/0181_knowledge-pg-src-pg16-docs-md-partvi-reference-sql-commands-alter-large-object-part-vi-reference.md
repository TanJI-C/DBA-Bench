# ALTER LARGE OBJECT

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_large_object.md`
- Source Title: `alter large object`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER LARGE OBJECT`
- Source Line Ranges: `1-37`
- Chunk ID: `pg16_fact_0181_94be115789`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `3dcda0a2616d2b9115da54c6dde68090c04e4501270a5b56f31e25d5b7f37a76`

## Retrieval Guidance

- Use When: Use for large object ownership syntax.
- Retrieval Keywords: ALTER LARGE OBJECT, large object owner, LOID
- Follow-up Guidance: No section split needed.
- Classification Note: Large object metadata DDL reference for owner changes.

## Official Source Content

ALTER LARGE OBJECT
7
SQL - Language Statements

ALTER LARGE OBJECT
change the definition of a large object

```
ALTER LARGE OBJECT `large_object_oid` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
```

## Description

`ALTER LARGE OBJECT` changes the definition of a
large object.

You must own the large object to use `ALTER LARGE OBJECT`.
To alter the owner, you must also be able to `SET ROLE` to
the new owning role.
(However, a superuser can alter any large object anyway.)
Currently, the only functionality is to assign a new owner, so both
restrictions always apply.

## Parameters

**`large_object_oid`**
: OID of the large object to be altered

**`new_owner`**
: The new owner of the large object

## Compatibility

There is no `ALTER LARGE OBJECT` statement in the SQL
standard.

## See Also
