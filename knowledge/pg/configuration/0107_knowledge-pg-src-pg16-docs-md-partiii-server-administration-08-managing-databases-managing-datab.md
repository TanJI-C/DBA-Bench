# Tablespaces

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/08_managing_databases.md`
- Source Title: `Managing Databases`
- Source Heading Path: `Managing Databases > Tablespaces`
- Source Line Ranges: `323-461`
- Chunk ID: `pg16_configuration_0107_6f36289398`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ae03eb55a7fa267c3b58cc07dd9fd291da1c6e38edf6d55305ea66d2f15af3c`

## Retrieval Guidance

- Use When: 需要将对象或临时文件放到特定文件系统以管理容量/性能。
- Retrieval Keywords: tablespace, CREATE TABLESPACE, LOCATION, default_tablespace, temp_tablespaces, pg_global, pg_default, disk layout
- Follow-up Guidance: tablespace 不能单独作为独立数据文件备份/迁移，丢失会影响整个 cluster。
- Classification Note: 定义 tablespace 文件系统位置、CREATE TABLESPACE、CREATE privilege、default_tablespace/temp_tablespaces 和可靠性约束。

## Official Source Content

## Tablespaces

Tablespaces in PostgreSQL allow database administrators to
define locations in the file system where the files representing
database objects can be stored. Once created, a tablespace can be referred
to by name when creating database objects.

By using tablespaces, an administrator can control the disk layout
of a PostgreSQL installation. This is useful in at
least two ways. First, if the partition or volume on which the
cluster was initialized runs out of space and cannot be extended,
a tablespace can be created on a different partition and used
until the system can be reconfigured.

Second, tablespaces allow an administrator to use knowledge of the
usage pattern of database objects to optimize performance. For
example, an index which is very heavily used can be placed on a
very fast, highly available disk, such as an expensive solid state
device. At the same time a table storing archived data which is
rarely used or not performance critical could be stored on a less
expensive, slower disk system.

> **Warning:**

> Even though located outside the main PostgreSQL data directory,
> tablespaces are an integral part of the database cluster and
> *cannot* be treated as an autonomous collection
> of data files. They are dependent on metadata contained in the main
> data directory, and therefore cannot be attached to a different
> database cluster or backed up individually.  Similarly, if you lose
> a tablespace (file deletion, disk failure, etc.), the database cluster
> might become unreadable or unable to start.  Placing a tablespace
> on a temporary file system like a RAM disk risks the reliability of
> the entire cluster.
>

To define a tablespace, use the [sql-createtablespace](#sql-createtablespace)
command, for example::

```
CREATE TABLESPACE fastspace LOCATION '/ssd1/postgresql/data';
```

The location must be an existing, empty directory that is owned by
the PostgreSQL operating system user.  All objects subsequently
created within the tablespace will be stored in files underneath this
directory.  The location must not be on removable or transient storage,
as the cluster might fail to function if the tablespace is missing
or lost.

> **Note:**

> There is usually not much point in making more than one
> tablespace per logical file system, since you cannot control the location
> of individual files within a logical file system.  However,
> PostgreSQL does not enforce any such limitation, and
> indeed it is not directly aware of the file system boundaries on your
> system.  It just stores files in the directories you tell it to use.
>

Creation of the tablespace itself must be done as a database superuser,
but after that you can allow ordinary database users to use it.
To do that, grant them the `CREATE` privilege on it.

Tables, indexes, and entire databases can be assigned to
particular tablespaces. To do so, a user with the `CREATE`
privilege on a given tablespace must pass the tablespace name as a
parameter to the relevant command. For example, the following creates
a table in the tablespace `space1`:

```
CREATE TABLE foo(i int) TABLESPACE space1;
```

Alternatively, use the [guc-default-tablespace](#guc-default-tablespace) parameter:

```
SET default_tablespace = space1;
CREATE TABLE foo(i int);
```

When `default_tablespace` is set to anything but an empty
string, it supplies an implicit `TABLESPACE` clause for
`CREATE TABLE` and `CREATE INDEX` commands that
do not have an explicit one.

There is also a [guc-temp-tablespaces](#guc-temp-tablespaces) parameter, which
determines the placement of temporary tables and indexes, as well as
temporary files that are used for purposes such as sorting large data
sets.  This can be a list of tablespace names, rather than only one,
so that the load associated with temporary objects can be spread over
multiple tablespaces.  A random member of the list is picked each time
a temporary object is to be created.

The tablespace associated with a database is used to store the system
catalogs of that database.  Furthermore, it is the default tablespace
used for tables, indexes, and temporary files created within the database,
if no `TABLESPACE` clause is given and no other selection is
specified by `default_tablespace` or
`temp_tablespaces` (as appropriate).
If a database is created without specifying a tablespace for it,
it uses the same tablespace as the template database it is copied from.

Two tablespaces are automatically created when the database cluster
is initialized.  The
`pg_global` tablespace is used for shared system catalogs. The
`pg_default` tablespace is the default tablespace of the
`template1` and `template0` databases (and, therefore,
will be the default tablespace for other databases as well, unless
overridden by a `TABLESPACE` clause in `CREATE
DATABASE`).

Once created, a tablespace can be used from any database, provided
the requesting user has sufficient privilege. This means that a tablespace
cannot be dropped until all objects in all databases using the tablespace
have been removed.

To remove an empty tablespace, use the [sql-droptablespace](#sql-droptablespace)
command.

To determine the set of existing tablespaces, examine the
[`pg_tablespace`
](#catalog-pg-tablespace) system catalog, for example

```
SELECT spcname FROM pg_tablespace;
```

The [app-psql](#app-psql) program's `\db` meta-command
is also useful for listing the existing tablespaces.

The directory `$PGDATA/pg_tblspc` contains symbolic links that
point to each of the non-built-in tablespaces defined in the cluster.
Although not recommended, it is possible to adjust the tablespace
layout by hand by redefining these links. Under no circumstances perform
this operation while the server is running. Note that in PostgreSQL 9.1
and earlier you will also need to update the `pg_tablespace`
catalog with the new locations. (If you do not, `pg_dump` will
continue to output the old tablespace locations.)
