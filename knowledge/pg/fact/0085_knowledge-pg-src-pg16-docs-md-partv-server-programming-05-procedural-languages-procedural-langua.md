# Installing Procedural Languages; PL handler concepts; trusted and untrusted languages

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/05_procedural_languages.md`
- Source Title: `Procedural Languages`
- Source Heading Path: `Procedural Languages > Installing Procedural Languages; PL handler concepts; trusted and untrusted languages`
- Source Line Ranges: `30-47`
- Chunk ID: `pg16_fact_0085_a410cda35f`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d293b55d14f68af1a703b62b624df833e3c9d8ac7bba78d8b175b98c7ce84042`

## Retrieval Guidance

- Use When: Understand PostgreSQL procedural-language concepts and installation model.
- Retrieval Keywords: procedural languages, CREATE LANGUAGE, trusted language, untrusted language, language handler
- Follow-up Guidance: Use language-specific records for PL/pgSQL, PL/Tcl, PL/Perl, or PL/Python behavior.
- Classification Note: The chapter provides conceptual and installation reference for procedural-language support rather than live diagnostic or repair instructions.

## Official Source Content

## Installing Procedural Languages

A procedural language must be "installed" into each
database where it is to be used.  But procedural languages installed in
the database `template1` are automatically available in all
subsequently created databases, since their entries in
`template1` will be copied by `CREATE DATABASE`.
So the database administrator can
decide which languages are available in which databases and can make
some languages available by default if desired.

For the languages supplied with the standard distribution, it is
only necessary to execute `CREATE EXTENSION`
`language_name` to install the language into the
current database.
The manual procedure described below is only recommended for
installing languages that have not been packaged as extensions.
