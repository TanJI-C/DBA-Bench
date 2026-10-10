# DROP TABLESPACE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_tablespace.md`
- Source Title: `drop tablespace`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TABLESPACE`
- Source Line Ranges: `1-50`
- Chunk ID: `pg16_fact_0291_4ae221bb7c`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `f05c0881bce29578e45d9ac781922961b0b6434fe124a810b82a9cbc5d4310fd`

## Retrieval Guidance

- Use When: Use for tablespace drop syntax and restrictions.
- Retrieval Keywords: DROP TABLESPACE, tablespace drop, empty tablespace
- Follow-up Guidance: No section split needed.
- Classification Note: Tablespace removal syntax reference.

## Official Source Content

DROP TABLESPACE
7
SQL - Language Statements

DROP TABLESPACE
remove a tablespace

```
DROP TABLESPACE [ IF EXISTS ] `name`
```

## Description

`DROP TABLESPACE` removes a tablespace from the system.

A tablespace can only be dropped by its owner or a superuser.
The tablespace must be empty of all database objects before it can be
dropped. It is possible that objects in other databases might still reside
in the tablespace even if no objects in the current database are using
the tablespace.  Also, if the tablespace is listed in the [guc-temp-tablespaces](#guc-temp-tablespaces) setting of any active session, the
`DROP` might fail due to temporary files residing in the
tablespace.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the tablespace does not exist. A notice is issued
in this case.

**`name`**
: The name of a tablespace.

## Notes

`DROP TABLESPACE` cannot be executed inside a transaction block.

## Examples

To remove tablespace `mystuff` from the system:

```
DROP TABLESPACE mystuff;
```

## Compatibility

`DROP TABLESPACE` is a PostgreSQL
extension.

## See Also
