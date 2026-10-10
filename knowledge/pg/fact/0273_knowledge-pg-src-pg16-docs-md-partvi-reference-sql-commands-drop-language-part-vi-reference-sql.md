# DROP LANGUAGE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_language.md`
- Source Title: `drop language`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP LANGUAGE`
- Source Line Ranges: `1-59`
- Chunk ID: `pg16_fact_0273_1e8824583a`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `7c525314d6f7aa8a01bf85f3e3f1d14875a3e1a2b6af6f123e5969b9a70691fb`

## Retrieval Guidance

- Use When: Use for language drop syntax.
- Retrieval Keywords: DROP LANGUAGE, procedural language drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Procedural language object removal syntax reference.

## Official Source Content

DROP LANGUAGE
7
SQL - Language Statements

DROP LANGUAGE
remove a procedural language

```
DROP [ PROCEDURAL ] LANGUAGE [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP LANGUAGE` removes the definition of a
previously registered procedural language.  You must be a superuser
or the owner of the language to use `DROP LANGUAGE`.

> **Note:**

> As of PostgreSQL 9.1, most procedural
> languages have been made into "extensions", and should
> therefore be removed with [`DROP EXTENSION`](#sql-dropextension)
> not `DROP LANGUAGE`.
>

## Parameters

**`IF EXISTS`**
: Do not throw an error if the language does not exist. A notice is issued
in this case.

**`name`**
: The name of an existing procedural language.

**`CASCADE`**
: Automatically drop objects that depend on the language (such as
functions in the language),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the language if any objects depend on it.  This
is the default.

## Examples

This command removes the procedural language
`plsample`:

```
DROP LANGUAGE plsample;
```

## Compatibility

There is no `DROP LANGUAGE` statement in the SQL
standard.

## See Also
