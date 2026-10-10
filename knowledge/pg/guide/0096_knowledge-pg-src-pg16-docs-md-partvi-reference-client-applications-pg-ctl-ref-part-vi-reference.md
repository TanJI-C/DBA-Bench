# status / Files

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/pg_ctl-ref.md`
- Source Title: `pg ctl-ref`
- Source Heading Path: `Part VI Reference > Client Applications > pg_ctl > status / Files`
- Source Line Ranges: `353-366, 419-433`
- Chunk ID: `pg16_guide_0096_7e3ebf14df`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dd7c5b7546ac1142c5f6b810feadee9a8fa9018e80f3a298aee23b709e1fc402`

## Retrieval Guidance

- Use When: Use to confirm whether a server is running and which options were used.
- Retrieval Keywords: pg_ctl status, postmaster.pid, postmaster.opts, server PID, exit status
- Follow-up Guidance: Correlate with process list, logs, pg_isready, and service manager state.
- Classification Note: status mode and postmaster.pid/postmaster.opts handling provide instance-running evidence and startup command-line visibility.

## Official Source Content

## Files

**`postmaster.pid`**
: pg_ctl examines this file in the data
directory to determine whether the server is currently running.

**`postmaster.opts`**
: If this file exists in the data directory,
pg_ctl (in `restart` mode)
will pass the contents of the file as options to
postgres, unless overridden
by the `-o` option. The contents of this file
are also displayed in `status` mode.

### Showing the Server Status

Here is sample status output from
pg_ctl:

```
$ pg_ctl status

pg_ctl: server is running (PID: 13718)
/usr/local/pgsql/bin/postgres "-D" "/usr/local/pgsql/data" "-p" "5433" "-B" "128"

```

The second line is the command that would be invoked in restart mode.
