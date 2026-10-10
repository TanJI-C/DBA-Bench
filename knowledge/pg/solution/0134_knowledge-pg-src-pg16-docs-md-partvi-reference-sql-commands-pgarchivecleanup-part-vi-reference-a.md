# standalone cleanup/options

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/pgarchivecleanup.md`
- Source Title: `pgarchivecleanup`
- Source Heading Path: `Part VI Reference > Applications > pg_archivecleanup > standalone cleanup/options`
- Source Line Ranges: `64-88`
- Chunk ID: `pg16_solution_0134_6d49642d31`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `87aec70d1364f92eb20a6d9d57d246bc05be75fb26c95875807ca4c3d3db006f`

## Retrieval Guidance

- Use When: Use after confirming which WAL segments are no longer needed for recovery.
- Retrieval Keywords: pg_archivecleanup, WAL archive cleanup, oldestkeptwalfile, dry run, remove WAL
- Follow-up Guidance: Run dry run first and verify retention requirements for backups/standbys.
- Classification Note: Standalone mode deletes obsolete WAL archive files after identifying the oldest WAL that must be kept.

## Official Source Content

## Options

pg_archivecleanup accepts the following command-line arguments:

**`-d`**
: Print lots of debug logging output on `stderr`.

**`-n`**
: Print the names of the files that would have been removed on `stdout` (performs a dry run).

**`-V`**
: Print the pg_archivecleanup version and exit.

**`-x` `extension`**
: Provide an extension
that will be stripped from all file names before deciding if they
should be deleted.  This is typically useful for cleaning up archives
that have been compressed during storage, and therefore have had an
extension added by the compression program.  For example: `-x
.gz`.

**`-?`**
: Show help about pg_archivecleanup command line
arguments, and exit.
