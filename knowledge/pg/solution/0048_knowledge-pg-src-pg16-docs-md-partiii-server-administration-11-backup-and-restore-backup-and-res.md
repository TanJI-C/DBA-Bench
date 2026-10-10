# Use `split`.

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/11_backup_and_restore.md`
- Source Title: `Backup and Restore`
- Source Heading Path: `Backup and Restore > SQL Dump > Handling Large Databases > Use `split`.`
- Source Line Ranges: `18-155, 177-202`
- Chunk ID: `pg16_solution_0048_7a40385210`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0226653e5c2cf7fc2f0f46b05d0d99df0c150d313c9081943bed20c10202990a`

## Retrieval Guidance

- Use When: 单个 dump 文件超过文件系统或传输限制。
- Retrieval Keywords: split pg_dump, 2G chunks, cat split files, filesystem file size limit
- Follow-up Guidance: 恢复前确认 split 文件顺序和完整性。
- Classification Note: 给出拆分大 dump 文件并合并恢复的操作。

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

## Use `split`.

The `split` command
allows you to split the output into smaller files that are
acceptable in size to the underlying file system. For example, to
make 2 gigabyte chunks:

```
pg_dump `dbname` | split -b 2G - `filename`
```

Reload with:

```
cat `filename`* | psql `dbname`
```

If using GNU split, it is possible to
use it and gzip together:

```
pg_dump `dbname` | split -b 2G --filter='gzip > $FILE.gz'
```

It can be restored using `zcat`.
