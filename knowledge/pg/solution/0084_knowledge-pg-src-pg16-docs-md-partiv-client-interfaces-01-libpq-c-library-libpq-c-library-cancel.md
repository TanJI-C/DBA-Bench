# Canceling Queries in Progress; PQgetCancel; PQcancel; PQcancelCreate; PQcancelBlocking; PQcancelStart; PQcancelPoll; PQcancelFinish

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/01_libpq_-_c_library.md`
- Source Title: `libpq — C Library`
- Source Heading Path: `libpq - C Library > Canceling Queries in Progress; PQgetCancel; PQcancel; PQcancelCreate; PQcancelBlocking; PQcancelStart; PQcancelPoll; PQcancelFinish`
- Source Line Ranges: `3862-3939`
- Chunk ID: `pg16_solution_0084_8b344e5078`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7582a6303fc27f54e0b0204a9ad86968a158f928b9cc74ad42f9832ce4b3ecbc`

## Retrieval Guidance

- Use When: Stop a confirmed long-running or unwanted query from a libpq client without closing unrelated client state.
- Retrieval Keywords: cancel query, PQcancel, PQgetCancel, PQcancelStart, PQcancelBlocking, cancel request, interrupt running query
- Follow-up Guidance: Verify the target backend and query first to avoid canceling the wrong operation.
- Classification Note: These sections document the client-side action for interrupting a running backend operation after the problematic query or session has been identified.

## Official Source Content

## Canceling Queries in Progress

A client application can request cancellation of a command that is
still being processed by the server, using the functions described in
this section.

**`PQgetCancel`**
: Creates a data structure containing the information needed to cancel
a command issued through a particular database connection.

```
PGcancel *PQgetCancel(PGconn *conn);
```

[libpq-PQgetCancel](#libpq-PQgetCancel) creates a
`PGcancel` object
given a `PGconn` connection object.  It will return
`NULL` if the given conn is `NULL` or an invalid
connection.  The `PGcancel` object is an opaque
structure that is not meant to be accessed directly by the
application; it can only be passed to [libpq-PQcancel](#libpq-PQcancel)
or [libpq-PQfreeCancel](#libpq-PQfreeCancel).

**`PQfreeCancel`**
: Frees a data structure created by [libpq-PQgetCancel](#libpq-PQgetCancel).

```
void PQfreeCancel(PGcancel *cancel);
```

[libpq-PQfreeCancel](#libpq-PQfreeCancel) frees a data object previously created
by [libpq-PQgetCancel](#libpq-PQgetCancel).

**`PQcancel`**
: Requests that the server abandon processing of the current command.

```
int PQcancel(PGcancel *cancel, char *errbuf, int errbufsize);
```

The return value is 1 if the cancel request was successfully
dispatched and 0 if not.  If not, errbuf is filled
with an explanatory error message.  errbuf
must be a char array of size errbufsize (the
recommended size is 256 bytes).

Successful dispatch is no guarantee that the request will have
any effect, however.  If the cancellation is effective, the current
command will terminate early and return an error result.  If the
cancellation fails (say, because the server was already done
processing the command), then there will be no visible result at
all.

[libpq-PQcancel](#libpq-PQcancel) can safely be invoked from a signal
handler, if the errbuf is a local variable in the
signal handler.  The `PGcancel` object is read-only
as far as [libpq-PQcancel](#libpq-PQcancel) is concerned, so it can
also be invoked from a thread that is separate from the one
manipulating the `PGconn` object.

**`PQrequestCancel`**
: [libpq-PQrequestCancel](#libpq-PQrequestCancel) is a deprecated variant of
[libpq-PQcancel](#libpq-PQcancel).

```
int PQrequestCancel(PGconn *conn);
```

Requests that the server abandon processing of the current
command.  It operates directly on the
`PGconn` object, and in case of failure stores the
error message in the `PGconn` object (whence it can
be retrieved by [libpq-PQerrorMessage](#libpq-PQerrorMessage)).  Although
the functionality is the same, this approach is not safe within
multiple-thread programs or signal handlers, since it is possible
that overwriting the `PGconn`'s error message will
mess up the operation currently in progress on the connection.
