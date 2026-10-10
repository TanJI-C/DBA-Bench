# LISTEN

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/listen.md`
- Source Title: `listen`
- Source Heading Path: `Part VI Reference > SQL Commands > LISTEN`
- Source Line Ranges: `1-90`
- Chunk ID: `pg16_fact_0309_06503b12f2`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `bd98d3c5d439142d85108c3cce20a2c5b7c4d8f055efd09444f6d724f7dac3f4`

## Retrieval Guidance

- Use When: Use for notification listener syntax and behavior.
- Retrieval Keywords: LISTEN, NOTIFY, asynchronous notification, channel
- Follow-up Guidance: No section split needed.
- Classification Note: Asynchronous notification registration syntax reference.

## Official Source Content

LISTEN
7
SQL - Language Statements

LISTEN
listen for a notification

```
LISTEN `channel`
```

## Description

`LISTEN` registers the current session as a
listener on the notification channel named `channel`.
If the current session is already registered as a listener for
this notification channel, nothing is done.

Whenever the command `NOTIFY `channel`` is invoked, either
by this session or another one connected to the same database, all
the sessions currently listening on that notification channel are
notified, and each will in turn notify its connected client
application.

A session can be unregistered for a given notification channel with the
`UNLISTEN` command.  A session's listen
registrations are automatically cleared when the session ends.

The method a client application must use to detect notification events depends on
which PostgreSQL application programming interface it
uses.  With the libpq library, the application issues
`LISTEN` as an ordinary SQL command, and then must
periodically call the function `PQnotifies` to find out
whether any notification events have been received.  Other interfaces such as
libpgtcl provide higher-level methods for handling notify events; indeed,
with libpgtcl the application programmer should not even issue
`LISTEN` or `UNLISTEN` directly.  See the
documentation for the interface you are using for more details.

## Parameters

**`channel`**
: Name of a notification channel (any identifier).

## Notes

`LISTEN` takes effect at transaction commit.
If `LISTEN` or `UNLISTEN` is executed
within a transaction that later rolls back, the set of notification
channels being listened to is unchanged.

A transaction that has executed `LISTEN` cannot be
prepared for two-phase commit.

There is a race condition when first setting up a listening session:
if concurrently-committing transactions are sending notify events,
exactly which of those will the newly listening session receive?
The answer is that the session will receive all events committed after
an instant during the transaction's commit step.  But that is slightly
later than any database state that the transaction could have observed
in queries.  This leads to the following rule for
using `LISTEN`: first execute (and commit!) that
command, then in a new transaction inspect the database state as needed
by the application logic, then rely on notifications to find out about
subsequent changes to the database state.  The first few received
notifications might refer to updates already observed in the initial
database inspection, but this is usually harmless.

[sql-notify](#sql-notify)
contains a more extensive
discussion of the use of `LISTEN` and
`NOTIFY`.

## Examples

Configure and execute a listen/notify sequence from
psql:

```
LISTEN virtual;
NOTIFY virtual;
Asynchronous notification "virtual" received from server process with PID 8448.
```

## Compatibility

There is no `LISTEN` statement in the SQL
standard.

## See Also
