# ALTER LANGUAGE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_language.md`
- Source Title: `alter language`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER LANGUAGE`
- Source Line Ranges: `1-36`
- Chunk ID: `pg16_fact_0180_c1f8fe825f`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `4b407d7d145d793b9c375eb32bad47777c6a976292a25739c92efaa1c8751022`

## Retrieval Guidance

- Use When: Use for procedural language metadata syntax.
- Retrieval Keywords: ALTER LANGUAGE, procedural language, language owner, language rename
- Follow-up Guidance: No section split needed.
- Classification Note: Procedural language object DDL reference for rename and owner changes.

## Official Source Content

ALTER LANGUAGE
7
SQL - Language Statements

ALTER LANGUAGE
change the definition of a procedural language

```
ALTER [ PROCEDURAL ] LANGUAGE `name` RENAME TO `new_name`
ALTER [ PROCEDURAL ] LANGUAGE `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
```

## Description

`ALTER LANGUAGE` changes the definition of a
procedural language.  The only functionality is to rename the language or
assign a new owner.  You must be superuser or owner of the language to
use `ALTER LANGUAGE`.

## Parameters

**`name`**
: Name of a language

**`new_name`**
: The new name of the language

**`new_owner`**
: The new owner of the language

## Compatibility

There is no `ALTER LANGUAGE` statement in the SQL
standard.

## See Also
