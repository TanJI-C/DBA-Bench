# Single-User Mode / signal actions

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/postgres-ref.md`
- Source Title: `postgres-ref`
- Source Heading Path: `Part VI Reference > Applications > postgres > Single-User Mode / signal actions`
- Source Line Ranges: `273-297, 405-447`
- Chunk ID: `pg16_solution_0136_a822e109e5`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `269bdc6dc26bcb9674b4f59a271a4e5aed1a28f640b07e99cba54b5caf8acc8e`

## Retrieval Guidance

- Use When: Use after confirming need for single-user recovery, safe shutdown/reload, or backend cancellation/termination behavior.
- Retrieval Keywords: postgres single-user mode, -P, system catalog recovery, SIGTERM, SIGHUP, pg_terminate_backend
- Follow-up Guidance: Prefer pg_ctl for normal lifecycle operations and avoid SIGKILL/SIGQUIT except documented emergency cases.
- Classification Note: Single-user mode and signal actions are operational recovery/control mechanisms, including catalog-damage recovery and query/backend termination.

## Official Source Content

### Options for Single-User Mode

The following options only apply to the single-user mode
(see [app-postgres-single-user](#app-postgres-single-user) below).

**`--single`**
: Selects the single-user mode.  This must be the first argument
on the command line.

**`database`**
: Specifies the name of the database to be accessed.  This must be
the last argument on the command line.  If it is
omitted it defaults to the user name.

**`-E`**
: Echo all commands to standard output before executing them.

**`-j`**
: Use semicolon followed by two newlines, rather than just newline,
as the command entry terminator.

**`-r` `filename`**
: Send all server log output to `filename`.  This option is only
honored when supplied as a command-line option.

## Single-User Mode

To start a single-user mode server, use a command like

```
postgres --single -D /usr/local/pgsql/data `other-options` my_database
```

Provide the correct path to the database directory with `-D`, or
make sure that the environment variable `PGDATA` is set.
Also specify the name of the particular database you want to work in.

Normally, the single-user mode server treats newline as the command
entry terminator; there is no intelligence about semicolons,
as there is in psql.  To continue a command
across multiple lines, you must type backslash just before each
newline except the last one.  The backslash and adjacent newline are
both dropped from the input command.  Note that this will happen even
when within a string literal or comment.

But if you use the `-j` command line switch, a single newline
does not terminate command entry; instead, the sequence
semicolon-newline-newline does.  That is, type a semicolon immediately
followed by a completely empty line.  Backslash-newline is not
treated specially in this mode.  Again, there is no intelligence about
such a sequence appearing within a string literal or comment.

In either input mode, if you type a semicolon that is not just before or
part of a command entry terminator, it is considered a command separator.
When you do type a command entry terminator, the multiple statements
you've entered will be executed as a single transaction.

To quit the session, type EOF
(ControlD, usually).
If you've entered any text since the last command entry terminator,
then EOF will be taken as a command entry terminator,
and another EOF will be needed to exit.

Note that the single-user mode server does not provide sophisticated
line-editing features (no command history, for example).
Single-user mode also does not do any background processing, such as
automatic checkpoints or replication.
