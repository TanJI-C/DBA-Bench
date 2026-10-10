# pg_test_fsync

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/pgtestfsync.md`
- Source Title: `pgtestfsync`
- Source Heading Path: `Part VI Reference > Applications > pg_test_fsync`
- Source Line Ranges: `1-58`
- Chunk ID: `pg16_guide_0090_7a03d92d0a`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `1dd032b282c057548b8e79806be8062c22f3e4dd5dfd53857d6135d8ff45c95f`

## Retrieval Guidance

- Use When: Use when investigating WAL sync latency, storage behavior, or configuration choices for sync method.
- Retrieval Keywords: pg_test_fsync, wal_sync_method, fsync performance, I/O diagnostic, commit_delay
- Follow-up Guidance: Use measured results to inform wal_sync_method and storage tuning decisions.
- Classification Note: Measures filesystem sync behavior and helps diagnose I/O/fsync performance or choose wal_sync_method; it produces evidence rather than directly remediating.

## Official Source Content

pg_test_fsync
1
Application

pg_test_fsync
determine fastest `wal_sync_method` for PostgreSQL

`pg_test_fsync`
`option`

## Description

pg_test_fsync is intended to give you a reasonable
idea of what the fastest [guc-wal-sync-method](#guc-wal-sync-method) is on your
specific system,
as well as supplying diagnostic information in the event of an identified I/O
problem.  However, differences shown by
pg_test_fsync might not make any significant
difference in real database throughput, especially since many database servers
are not speed-limited by their write-ahead logs.
pg_test_fsync reports average file sync operation
time in microseconds for each `wal_sync_method`, which can also be used to
inform efforts to optimize the value of [guc-commit-delay](#guc-commit-delay).

## Options

pg_test_fsync accepts the following
command-line options:

**`-f`**
: Specifies the file name to write test data in.
This file should be in the same file system that the
`pg_wal` directory is or will be placed in.
(`pg_wal` contains the WAL files.)
The default is `pg_test_fsync.out` in the current
directory.

**`-s`**
: Specifies the number of seconds for each test.  The more time
per test, the greater the test's accuracy, but the longer it takes
to run.  The default is 5 seconds, which allows the program to
complete in under 2 minutes.

**`-V`**
: Print the pg_test_fsync version and exit.

**`-?`**
: Show help about pg_test_fsync command line
arguments, and exit.

## Environment

The environment variable `PG_COLOR` specifies whether to use
color in diagnostic messages. Possible values are
`always`, `auto` and
`never`.

## See Also
