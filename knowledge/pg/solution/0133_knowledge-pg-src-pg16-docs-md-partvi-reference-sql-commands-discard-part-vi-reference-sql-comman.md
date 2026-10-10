# DISCARD

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/discard.md`
- Source Title: `discard`
- Source Heading Path: `Part VI Reference > SQL Commands > DISCARD`
- Source Line Ranges: `1-61`
- Chunk ID: `pg16_solution_0133_5b0c39bf95`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `27618df3e02210f70677aec6aa317d1328f0fd3f7f4bd9ad8a4b987246a48935`

## Retrieval Guidance

- Use When: Use after confirming a contaminated/reused session or stale session-local state needs to be cleared.
- Retrieval Keywords: DISCARD ALL, DISCARD PLANS, DISCARD TEMP, session state, reset session
- Follow-up Guidance: Check transaction-block restriction and connection-pool reset behavior.
- Classification Note: Releases or resets session-local resources such as cached plans, temp objects, sequence state, listeners, and GUCs; useful as a confirmed session-state cleanup action.

## Official Source Content

DISCARD
7
SQL - Language Statements

DISCARD
discard session state

```
DISCARD { ALL | PLANS | SEQUENCES | TEMPORARY | TEMP }
```

## Description

`DISCARD` releases internal resources associated with a
database session.  This command is useful for partially or fully
resetting the session's state.  There are several subcommands to
release different types of resources; the `DISCARD ALL`
variant subsumes all the others, and also resets additional state.

## Parameters

**`PLANS`**
: Releases all cached query plans, forcing re-planning to occur
the next time the associated prepared statement is used.

**`SEQUENCES`**
: Discards all cached sequence-related state,
including `currval()`/`lastval()`
information and any preallocated sequence values that have not
yet been returned by `nextval()`.
(See [sql-createsequence](#sql-createsequence) for a description of
preallocated sequence values.)

**`TEMPORARY` or `TEMP`**
: Drops all temporary tables created in the current session.

**`ALL`**
: Releases all temporary resources associated with the current
session and resets the session to its initial state.
Currently, this has the same effect as executing the following sequence
of statements:

```
CLOSE ALL;
SET SESSION AUTHORIZATION DEFAULT;
RESET ALL;
DEALLOCATE ALL;
UNLISTEN *;
SELECT pg_advisory_unlock_all();
DISCARD PLANS;
DISCARD TEMP;
DISCARD SEQUENCES;
```

## Notes

`DISCARD ALL` cannot be executed inside a transaction block.

## Compatibility

`DISCARD` is a PostgreSQL extension.
