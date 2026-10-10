# SQL Dump

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/11_backup_and_restore.md`
- Source Title: `Backup and Restore`
- Source Heading Path: `Backup and Restore > SQL Dump`
- Source Line Ranges: `18-155`
- Chunk ID: `pg16_solution_0043_1627612a1a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c78bef73d60a6453516f6aad10375e23ad11dc3134e8b3a5fb84ecd50ccf4637`

## Retrieval Guidance

- Use When: 需要对单库做可跨版本/跨架构恢复的逻辑备份。
- Retrieval Keywords: pg_dump, SQL dump, logical backup, snapshot consistency, database backup
- Follow-up Guidance: 确认备份用户读权限、认证方式和目标版本兼容性。
- Classification Note: 提供 pg_dump 逻辑备份的基本命令、权限和适用边界。

## Official Source Content

## SQL Dump

The idea behind this dump method is to generate a file with SQL
commands that, when fed back to the server, will recreate the
database in the same state as it was at the time of the dump.
PostgreSQL provides the utility program
[app-pgdump](#app-pgdump) for this purpose. The basic usage of this
command is:

```
pg_dump `dbname` > `dumpfile`
```

As you see, pg_dump writes its result to the
standard output. We will see below how this can be useful.
While the above command creates a text file, pg_dump
can create files in other formats that allow for parallelism and more
fine-grained control of object restoration.

pg_dump is a regular PostgreSQL
client application (albeit a particularly clever one). This means
that you can perform this backup procedure from any remote host that has
access to the database. But remember that pg_dump
does not operate with special permissions. In particular, it must
have read access to all tables that you want to back up, so in order
to back up the entire database you almost always have to run it as a
database superuser.  (If you do not have sufficient privileges to back up
the entire database, you can still back up portions of the database to which
you do have access using options such as
`-n `schema``
or `-t `table``.)

To specify which database server pg_dump should
contact, use the command line options `-h
`host`` and `-p `port``. The
default host is the local host or whatever your
`PGHOST` environment variable specifies. Similarly,
the default port is indicated by the `PGPORT`
environment variable or, failing that, by the compiled-in default.
(Conveniently, the server will normally have the same compiled-in
default.)

Like any other PostgreSQL client application,
pg_dump will by default connect with the database
user name that is equal to the current operating system user name. To override
this, either specify the `-U` option or set the
environment variable `PGUSER`. Remember that
pg_dump connections are subject to the normal
client authentication mechanisms (which are described in [client-authentication](#client-authentication)).

An important advantage of pg_dump over the other backup
methods described later is that pg_dump's output can
generally be re-loaded into newer versions of PostgreSQL,
whereas file-level backups and continuous archiving are both extremely
server-version-specific.  pg_dump is also the only method
that will work when transferring a database to a different machine
architecture, such as going from a 32-bit to a 64-bit server.

Dumps created by pg_dump are internally consistent,
meaning, the dump represents a snapshot of the database at the time
pg_dump began running. pg_dump does not
block other operations on the database while it is working.
(Exceptions are those operations that need to operate with an
exclusive lock, such as most forms of `ALTER TABLE`.)

### Restoring the Dump

Text files created by pg_dump are intended to
be read by the psql program using its default
settings. The general command form to restore a text dump is

```
psql -X `dbname`  **Important:**

> The dumps produced by pg_dump are relative to
> `template0`. This means that any languages, procedures,
> etc. added via `template1` will also be dumped by
> pg_dump. As a result, when restoring, if you are
> using a customized `template1`, you must create the
> empty database from `template0`, as in the example
> above.
>

After restoring a backup, it is wise to run [`ANALYZE`](#sql-analyze) on each
database so the query optimizer has useful statistics;
see [vacuum-for-statistics](#vacuum-for-statistics)
and [autovacuum](#autovacuum) for more information.
For more advice on how to load large amounts of data
into PostgreSQL efficiently, refer to [populate](#populate).

### Using pg_dumpall

pg_dump dumps only a single database at a time,
and it does not dump information about roles or tablespaces
(because those are cluster-wide rather than per-database).
To support convenient dumping of the entire contents of a database
cluster, the [app-pg-dumpall](#app-pg-dumpall) program is provided.
pg_dumpall backs up each database in a given
cluster, and also preserves cluster-wide data such as role and
tablespace definitions. The basic usage of this command is:

```
pg_dumpall > `dumpfile`
```

The resulting dump can be restored with psql:

```
psql -X -f `dumpfile` postgres
```

(Actually, you can specify any existing database name to start from,
but if you are loading into an empty cluster then `postgres`
should usually be used.)  It is always necessary to have
database superuser access when restoring a pg_dumpall
dump, as that is required to restore the role and tablespace information.
If you use tablespaces, make sure that the tablespace paths in the
dump are appropriate for the new installation.

pg_dumpall works by emitting commands to re-create
roles, tablespaces, and empty databases, then invoking
pg_dump for each database.  This means that while
each database will be internally consistent, the snapshots of
different databases are not synchronized.

Cluster-wide data can be dumped alone using the
pg_dumpall `--globals-only` option.
This is necessary to fully backup the cluster if running the
pg_dump command on individual databases.

### Handling Large Databases

Some operating systems have maximum file size limits that cause
problems when creating large pg_dump output files.
Fortunately, pg_dump can write to the standard
output, so you can use standard Unix tools to work around this
potential problem.  There are several possible methods:
