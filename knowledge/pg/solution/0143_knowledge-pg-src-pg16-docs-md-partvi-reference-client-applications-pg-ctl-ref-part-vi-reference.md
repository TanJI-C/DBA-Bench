# stop/restart/promote/logrotate/kill

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/pg_ctl-ref.md`
- Source Title: `pg ctl-ref`
- Source Heading Path: `Part VI Reference > Client Applications > pg_ctl > stop/restart/promote/logrotate/kill`
- Source Line Ranges: `385-399, 400-418`
- Chunk ID: `pg16_solution_0143_8ef2004b10`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aa5548268e3277ee224c327e71d6fac56b442dd109cbe5458e0b1b020a679766`

## Retrieval Guidance

- Use When: Use after confirming an instance lifecycle action is required.
- Retrieval Keywords: pg_ctl stop, pg_ctl restart, pg_ctl promote, pg_ctl logrotate, pg_ctl kill, shutdown mode
- Follow-up Guidance: Choose smart/fast/immediate shutdown carefully and verify completion with status/logs/pg_isready.
- Classification Note: These modes perform lifecycle/remediation actions such as controlled shutdown, restart for non-reloadable settings, standby promotion, log rotation, or signaling processes.

## Official Source Content

### Stopping the Server

To stop the server, use:

```
$ pg_ctl stop
```

The `-m` option allows control over
*how* the server shuts down:

```
$ pg_ctl stop -m smart
```

### Restarting the Server

Restarting the server is almost equivalent to stopping the
server and starting it again, except that by default,
`pg_ctl` saves and reuses the command line options that
were passed to the previously-running instance.  To restart
the server using the same options as before, use:

```
$ pg_ctl restart
```

But if `-o` is specified, that replaces any previous options.
To restart using port 5433, disabling `fsync` upon restart:

```
$ pg_ctl -o "-F -p 5433" restart
```
