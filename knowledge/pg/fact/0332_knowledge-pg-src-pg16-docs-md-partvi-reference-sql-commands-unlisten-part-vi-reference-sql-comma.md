# UNLISTEN

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/unlisten.md`
- Source Title: `unlisten`
- Source Heading Path: `Part VI Reference > SQL Commands > UNLISTEN`
- Source Line Ranges: `1-69`
- Chunk ID: `pg16_fact_0332_79c217c560`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `725156bf7eb755a605c3de94810aa54e7084b98a8dd66d50184f3ab82985ebc1`

## Retrieval Guidance

- Use When: Use for removing notification registrations.
- Retrieval Keywords: UNLISTEN, LISTEN, NOTIFY, notification channel
- Follow-up Guidance: No section split needed.
- Classification Note: Asynchronous notification deregistration syntax reference.

## Official Source Content

UNLISTEN
7
SQL - Language Statements

UNLISTEN
stop listening for a notification

```
UNLISTEN { `channel` | * }
```

## Description

`UNLISTEN` is used to remove an existing
registration for `NOTIFY` events.
`UNLISTEN` cancels any existing registration of
the current PostgreSQL session as a
listener on the notification channel named `channel`.  The special wildcard
`*` cancels all listener registrations for the
current session.

[sql-notify](#sql-notify)
contains a more extensive
discussion of the use of `LISTEN` and
`NOTIFY`.

## Parameters

**`channel`**
: Name of a notification channel (any identifier).

**`*`**
: All current listen registrations for this session are cleared.

## Notes

You can unlisten something you were not listening for; no warning or error
will appear.

At the end of each session, `UNLISTEN *` is
automatically executed.

A transaction that has executed `UNLISTEN` cannot be
prepared for two-phase commit.

## Examples

To make a registration:

```
LISTEN virtual;
NOTIFY virtual;
Asynchronous notification "virtual" received from server process with PID 8448.
```

Once `UNLISTEN` has been executed, further `NOTIFY`
messages will be ignored:

```
UNLISTEN virtual;
NOTIFY virtual;
-- no NOTIFY event is received
```

## Compatibility

There is no `UNLISTEN` command in the SQL standard.

## See Also
