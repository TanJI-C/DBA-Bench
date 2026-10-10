# LOAD

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/load.md`
- Source Title: `load`
- Source Heading Path: `Part VI Reference > SQL Commands > LOAD`
- Source Line Ranges: `1-43`
- Chunk ID: `pg16_fact_0310_d7167cd672`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `0c927bf08cf3da5cb7e1d02cc87905b46f209bc04b1b149cd59c304b546fcc3d`

## Retrieval Guidance

- Use When: Use for loading server-side shared libraries.
- Retrieval Keywords: LOAD, shared library, dynamic loading, module
- Follow-up Guidance: No section split needed.
- Classification Note: Shared library load syntax reference.

## Official Source Content

LOAD
7
SQL - Language Statements

LOAD
load a shared library file

```
LOAD '`filename`'
```

## Description

This command loads a shared library file into the PostgreSQL
server's address space.  If the file has been loaded already,
the command does nothing.  Shared library files that contain C functions
are automatically loaded whenever one of their functions is called.
Therefore, an explicit `LOAD` is usually only needed to
load a library that modifies the server's behavior through "hooks"
rather than providing a set of functions.

The library file name is typically given as just a bare file name,
which is sought in the server's library search path (set
by [guc-dynamic-library-path](#guc-dynamic-library-path)).  Alternatively it can be
given as a full path name.  In either case the platform's standard shared
library file name extension may be omitted.
See [xfunc-c-dynload](#xfunc-c-dynload) for more information on this topic.

Non-superusers can only apply `LOAD` to library files
located in `$libdir/plugins/` — the specified
`filename` must begin
with exactly that string.  (It is the database administrator's
responsibility to ensure that only "safe" libraries
are installed there.)

## Compatibility

`LOAD` is a PostgreSQL
extension.

## See Also

[sql-createfunction](#sql-createfunction)
