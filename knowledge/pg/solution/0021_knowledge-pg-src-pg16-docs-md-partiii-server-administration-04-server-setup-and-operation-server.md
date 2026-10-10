# Shutting Down the Server

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > Shutting Down the Server`
- Source Line Ranges: `1123-1193`
- Chunk ID: `pg16_solution_0021_2312191e3d`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d733e92b49dcce2e9a689d23e2aeec3c402ef835ae779e86de91a208e1d7f1b9`

## Retrieval Guidance

- Use When: 需要安全停止服务器或终止单个会话。
- Retrieval Keywords: pg_ctl stop, SIGTERM, SIGINT, SIGQUIT, smart shutdown, fast shutdown, immediate shutdown, pg_terminate_backend, postmaster.pid
- Follow-up Guidance: 避免 SIGKILL；紧急 immediate shutdown 后预期下次启动 WAL recovery。
- Classification Note: 说明 smart/fast/immediate shutdown 信号、pg_ctl stop、kill 和 pg_terminate_backend 的处置动作。

## Official Source Content

## Shutting Down the Server

There are several ways to shut down the database server.
Under the hood, they all reduce to sending a signal to the supervisor
`postgres` process.

If you are using a pre-packaged version
of PostgreSQL, and you used its provisions
for starting the server, then you should also use its provisions for
stopping the server.  Consult the package-level documentation for
details.

When managing the server directly, you can control the type of shutdown
by sending different signals to the `postgres`
process:

**SIGTERM**
: This is the *Smart Shutdown* mode.
After receiving SIGTERM, the server
disallows new connections, but lets existing sessions end their
work normally. It shuts down only after all of the sessions terminate.
If the server is in recovery when a smart
shutdown is requested, recovery and streaming replication will be
stopped only after all regular sessions have terminated.

**SIGINT**
: This is the *Fast Shutdown* mode.
The server disallows new connections and sends all existing
server processes SIGTERM, which will cause them
to abort their current transactions and exit promptly. It then
waits for all server processes to exit and finally shuts down.

**SIGQUIT**
: This is the *Immediate Shutdown* mode.
The server will send SIGQUIT to all child
processes and wait for them to terminate.  If any do not terminate
within 5 seconds, they will be sent SIGKILL.
The supervisor server process exits as soon as all child processes have
exited, without doing normal database shutdown processing.
This will lead to recovery (by
replaying the WAL log) upon next start-up. This is recommended
only in emergencies.

The [app-pg-ctl](#app-pg-ctl) program provides a convenient
interface for sending these signals to shut down the server.
Alternatively, you can send the signal directly using `kill`
on non-Windows systems.
The PID of the `postgres` process can be
found using the `ps` program, or from the file
`postmaster.pid` in the data directory. For
example, to do a fast shutdown:

```
$ kill -INT `head -1 /usr/local/pgsql/data/postmaster.pid`
```

> **Important:**

> It is best not to use SIGKILL to shut down the
> server.  Doing so will prevent the server from releasing shared memory and
> semaphores.  Furthermore, SIGKILL kills
> the `postgres` process without letting it relay the
> signal to its subprocesses, so it might be necessary to kill the
> individual subprocesses by hand as well.
>

To terminate an individual session while allowing other sessions to
continue, use `pg_terminate_backend()` (see [functions-admin-signal-table](#functions-admin-signal-table)) or send a
SIGTERM signal to the child process associated with
the session.
