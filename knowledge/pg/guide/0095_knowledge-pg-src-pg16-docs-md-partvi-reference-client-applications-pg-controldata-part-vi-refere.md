# pg_controldata

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/pg_controldata.md`
- Source Title: `pg controldata`
- Source Heading Path: `Part VI Reference > Client Applications > pg_controldata`
- Source Line Ranges: `1-41`
- Chunk ID: `pg16_guide_0095_d4957253b8`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `33ed32008493cba21f39f39a0c8384330505d5274a78aece3a3cb09f4aced2af`

## Retrieval Guidance

- Use When: Use when diagnosing cluster control-file state, checkpoint/WAL metadata, or version/initialization facts offline.
- Retrieval Keywords: pg_controldata, pg_control, checkpoint, WAL information, catalog version, cluster state
- Follow-up Guidance: Correlate with logs, pg_resetwal dry run, or recovery tooling before making changes.
- Classification Note: Displays cluster control information, WAL/checkpoint state, catalog version, and pg_control facts used for diagnosis.

## Official Source Content

pg_controldata
1
Application

pg_controldata
display control information of a PostgreSQL database cluster

`pg_controldata`
`option`

`-D`
`--pgdata`

`datadir`

## Description

`pg_controldata` prints information initialized during
`initdb`, such as the catalog version.
It also shows information about write-ahead logging and checkpoint
processing.  This information is cluster-wide, and not specific to any one
database.

This utility can only be run by the user who initialized the cluster because
it requires read access to the data directory.
You can specify the data directory on the command line, or use
the environment variable `PGDATA`.  This utility supports the options
`-V` and `--version`, which print the
pg_controldata version and exit.  It also
supports options `-?` and `--help`, which output the
supported arguments.

## Environment

**`PGDATA`**
: Default data directory location

**`PG_COLOR`**
: Specifies whether to use color in diagnostic messages. Possible values
are `always`, `auto` and
`never`.
