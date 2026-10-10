# Diagnostics

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/postgres-ref.md`
- Source Title: `postgres-ref`
- Source Heading Path: `Part VI Reference > Applications > postgres > Diagnostics`
- Source Line Ranges: `315-354`
- Chunk ID: `pg16_guide_0093_de1d16d760`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4679791299a88748923276c4aa6d358ba16976115978ed8f0bf5ab2d0a3e80cd`

## Retrieval Guidance

- Use When: Use when diagnosing postgres startup failure messages.
- Retrieval Keywords: postgres diagnostics, semget, shmget, port already in use, lock file, server already running
- Follow-up Guidance: Confirm with OS process/socket checks before deleting lock files or changing kernel/server settings.
- Classification Note: Diagnostics section maps startup failure messages to likely causes such as shared memory/semaphore limits, existing server, or port binding conflicts.

## Official Source Content

## Diagnostics

A failure message mentioning `semget` or
`shmget` probably indicates you need to configure your
kernel to provide adequate shared memory and semaphores.  For more
discussion see [kernel-resources](#kernel-resources).  You might be able
to postpone reconfiguring your kernel by decreasing [guc-shared-buffers](#guc-shared-buffers) to reduce the shared memory
consumption of PostgreSQL, and/or by reducing
[guc-max-connections](#guc-max-connections) to reduce the semaphore
consumption.

A failure message suggesting that another server is already running
should be checked carefully, for example by using the command

```
$ ps ax | grep postgres
```

or

```
$ ps -ef | grep postgres
```

depending on your system.  If you are certain that no conflicting
server is running, you can remove the lock file mentioned in the
message and try again.

A failure message indicating inability to bind to a port might
indicate that that port is already in use by some
non-PostgreSQL process.  You might also
get this error if you terminate `postgres`
and immediately restart it using the same port; in this case, you
must simply wait a few seconds until the operating system closes
the port before trying again.  Finally, you might get this error if
you specify a port number that your operating system considers to
be reserved.  For example, many versions of Unix consider port
numbers under 1024 to be "trusted" and only permit
the Unix superuser to access them.
