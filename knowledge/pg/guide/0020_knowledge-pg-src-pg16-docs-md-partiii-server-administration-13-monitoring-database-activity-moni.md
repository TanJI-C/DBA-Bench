# Standard Unix Tools

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/13_monitoring_database_activity.md`
- Source Title: `Monitoring Database Activity`
- Source Heading Path: `Monitoring Database Activity > Standard Unix Tools`
- Source Line Ranges: `19-99`
- Chunk ID: `pg16_guide_0020_421b2803bc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `79ec8a7bdc6cf61e5bd0c8c340a26de56803251f74d6cbf28431a0c1281d38a5`

## Retrieval Guidance

- Use When: 需要快速从操作系统层面确认 PostgreSQL 进程活动和阻塞线索。
- Retrieval Keywords: ps aux postgres, process title, idle in transaction, waiting, cluster_name, update_process_title
- Follow-up Guidance: 复杂阻塞继续查询 pg_locks 和 pg_stat_activity。
- Classification Note: 说明用 ps/top/iostat/vmstat 识别进程状态和锁等待信号。

## Official Source Content

## Standard Unix Tools

On most Unix platforms, PostgreSQL modifies its
command title as reported by `ps`, so that individual server
processes can readily be identified.  A sample display is

```
$ ps auxww | grep ^postgres
postgres  15551  0.0  0.1  57536  7132 pts/0    S    18:02   0:00 postgres -i
postgres  15554  0.0  0.0  57536  1184 ?        Ss   18:02   0:00 postgres: background writer
postgres  15555  0.0  0.0  57536   916 ?        Ss   18:02   0:00 postgres: checkpointer
postgres  15556  0.0  0.0  57536   916 ?        Ss   18:02   0:00 postgres: walwriter
postgres  15557  0.0  0.0  58504  2244 ?        Ss   18:02   0:00 postgres: autovacuum launcher
postgres  15582  0.0  0.0  58772  3080 ?        Ss   18:04   0:00 postgres: joe runbug 127.0.0.1 idle
postgres  15606  0.0  0.0  58772  3052 ?        Ss   18:07   0:00 postgres: tgl regression [local] SELECT waiting
postgres  15610  0.0  0.0  58772  3056 ?        Ss   18:07   0:00 postgres: tgl regression [local] idle in transaction
```

(The appropriate invocation of `ps` varies across different
platforms, as do the details of what is shown.  This example is from a
recent Linux system.)  The first process listed here is the
primary server process.  The command arguments
shown for it are the same ones used when it was launched.  The next four
processes are background worker processes automatically launched by the
primary process.  (The "autovacuum launcher" process will not
be present if you have set the system not to run autovacuum.)
Each of the remaining
processes is a server process handling one client connection.  Each such
process sets its command line display in the form

```
postgres: `user` `database` `host` `activity`
```

The user, database, and (client) host items remain the same for
the life of the client connection, but the activity indicator changes.
The activity can be `idle` (i.e., waiting for a client command),
`idle in transaction` (waiting for client inside a `BEGIN` block),
or a command type name such as `SELECT`.  Also,
`waiting` is appended if the server process is presently waiting
on a lock held by another session.  In the above example we can infer
that process 15606 is waiting for process 15610 to complete its transaction
and thereby release some lock.  (Process 15610 must be the blocker, because
there is no other active session.  In more complicated cases it would be
necessary to look into the
[`pg_locks`](#view-pg-locks)
system view to determine who is blocking whom.)

If [guc-cluster-name](#guc-cluster-name) has been configured the
cluster name will also be shown in `ps` output:

```
$ psql -c 'SHOW cluster_name'
cluster_name
--------------
server1
(1 row)

$ ps aux|grep server1
postgres   27093  0.0  0.0  30096  2752 ?        Ss   11:34   0:00 postgres: server1: background writer
...
```

If you have turned off [guc-update-process-title](#guc-update-process-title) then the
activity indicator is not updated; the process title is set only once
when a new process is launched.  On some platforms this saves a measurable
amount of per-command overhead;  on others it's insignificant.

> **Tip:**

> Solaris requires special handling. You must
> use `/usr/ucb/ps`, rather than
> `/bin/ps`. You also must use two `w`
> flags, not just one. In addition, your original invocation of the
> `postgres` command must have a shorter
> `ps` status display than that provided by each
> server process.  If you fail to do all three things, the `ps`
> output for each server process will be the original `postgres`
> command line.
>
