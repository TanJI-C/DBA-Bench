# Additional Supplied Programs; Client Applications; Server Applications

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > Additional Supplied Programs; Client Applications; Server Applications`
- Source Line Ranges: `10763-10777, 10778-10796, 11150-11155`
- Chunk ID: `pg16_fact_0129_5ee4dea01f`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7696fbfa839e0eafc33aa73e84c3e2132e93228694687054fcd1a10e20b4d2fb`

## Retrieval Guidance

- Use When: Look up supplied program behavior and command options in the appendix.
- Retrieval Keywords: additional supplied programs, client applications, server applications, oid2name, vacuumlo
- Follow-up Guidance: Use tool-specific operational documentation when applying a program to production data.
- Classification Note: These sections list and describe supplied client/server programs, options, environment variables, notes, and examples as reference.

## Official Source Content

## Additional Supplied Programs

This appendix and the previous one contain information regarding the modules that
can be found in the `contrib` directory of the
PostgreSQL distribution.  See [contrib](#contrib) for
more information about the `contrib` section in general and
server extensions and plug-ins found in `contrib`
specifically.

This appendix covers utility programs found in `contrib`.
Once installed, either from source or a packaging system, they are found in
the `bin` directory of the
PostgreSQL installation and can be used like any
other program.

## Client Applications

This section covers PostgreSQL client
applications in `contrib`.  They can be run from anywhere,
independent of where the database server resides.  See
also [reference-client](#reference-client) for information about client
applications that are part of the core PostgreSQL
distribution.

oid2name
1
Application

oid2name
resolve OIDs and file nodes in a PostgreSQL data directory

`oid2name`
`option`

## Server Applications

Some applications run on the PostgreSQL server
itself.  Currently, no such applications are included in the
`contrib` directory.  See also [reference-server](#reference-server) for information about server applications that
are part of the core PostgreSQL distribution.
