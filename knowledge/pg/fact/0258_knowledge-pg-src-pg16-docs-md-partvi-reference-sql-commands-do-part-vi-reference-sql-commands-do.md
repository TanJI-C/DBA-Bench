# DO

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/do.md`
- Source Title: `do`
- Source Heading Path: `Part VI Reference > SQL Commands > DO`
- Source Line Ranges: `1-71`
- Chunk ID: `pg16_fact_0258_d1b45e26c3`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `653cdac71bf5c902ce1dc83e43d9bae6c4b4b66363e9cf6f32c4afe401116a43`

## Retrieval Guidance

- Use When: Use for one-off procedural code block syntax.
- Retrieval Keywords: DO, anonymous code block, PL/pgSQL, LANGUAGE
- Follow-up Guidance: No section split needed.
- Classification Note: Anonymous code block execution syntax reference.

## Official Source Content

DO
7
SQL - Language Statements

DO
execute an anonymous code block

```
DO [ LANGUAGE `lang_name` ] `code`
```

## Description

`DO` executes an anonymous code block, or in other
words a transient anonymous function in a procedural language.

The code block is treated as though it were the body of a function
with no parameters, returning `void`.  It is parsed and
executed a single time.

The optional `LANGUAGE` clause can be written either
before or after the code block.

## Parameters

**`code`**
: The procedural language code to be executed.  This must be specified
as a string literal, just as in `CREATE FUNCTION`.
Use of a dollar-quoted literal is recommended.

**`lang_name`**
: The name of the procedural language the code is written in.
If omitted, the default is `plpgsql`.

## Notes

The procedural language to be used must already have been installed
into the current database by means of `CREATE EXTENSION`.
`plpgsql` is installed by default, but other languages are not.

The user must have `USAGE` privilege for the procedural
language, or must be a superuser if the language is untrusted.
This is the same privilege requirement as for creating a function
in the language.

If `DO` is executed in a transaction block, then the
procedure code cannot execute transaction control statements.  Transaction
control statements are only allowed if `DO` is executed in
its own transaction.

## Examples

Grant all privileges on all views in schema `public` to
role `webuser`:

```
DO $$DECLARE r record;
BEGIN
FOR r IN SELECT table_schema, table_name FROM information_schema.tables
WHERE table_type = 'VIEW' AND table_schema = 'public'
LOOP
EXECUTE 'GRANT ALL ON ' || quote_ident(r.table_schema) || '.' || quote_ident(r.table_name) || ' TO webuser';
END LOOP;
END$$;
```

## Compatibility

There is no `DO` statement in the SQL standard.

## See Also
