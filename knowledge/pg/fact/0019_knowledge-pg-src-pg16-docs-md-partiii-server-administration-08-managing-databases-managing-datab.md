# Template Databases

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/08_managing_databases.md`
- Source Title: `Managing Databases`
- Source Heading Path: `Managing Databases > Template Databases`
- Source Line Ranges: `162-263`
- Chunk ID: `pg16_fact_0019_4f4c063124`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5d41744b99fe179e8ddf2060980f26841aef5c49651aff8f817290585afea92`

## Retrieval Guidance

- Use When: 需要理解新数据库从哪个模板复制，以及如何使用 template0。
- Retrieval Keywords: template1, template0, TEMPLATE template0, datistemplate, datallowconn, pristine database, CREATE DATABASE copy
- Follow-up Guidance: 复制模板数据库时源数据库不能有其他连接。
- Classification Note: 解释 template1/template0、pristine database、datistemplate/datallowconn 和复制模板限制。

## Official Source Content

## Template Databases

`CREATE DATABASE` actually works by copying an existing
database.  By default, it copies the standard system database named
`template1`. Thus that
database is the "template" from which new databases are
made.  If you add objects to `template1`, these objects
will be copied into subsequently created user databases.  This
behavior allows site-local modifications to the standard set of
objects in databases.  For example, if you install the procedural
language PL/Perl in `template1`, it will
automatically be available in user databases without any extra
action being taken when those databases are created.

However, `CREATE DATABASE` does not copy database-level
`GRANT` permissions attached to the source database.
The new database has default database-level permissions.

There is a second standard system database named
`template0`. This
database contains the same data as the initial contents of
`template1`, that is, only the standard objects
predefined by your version of
PostgreSQL.  `template0`
should never be changed after the database cluster has been
initialized.  By instructing
`CREATE DATABASE` to copy `template0` instead
of `template1`, you can create a "pristine" user
database (one where no user-defined objects exist and where the system
objects have not been altered) that contains none of the site-local additions in
`template1`.  This is particularly handy when restoring a
`pg_dump` dump: the dump script should be restored in a
pristine database to ensure that one recreates the correct contents
of the dumped database, without conflicting with objects that
might have been added to `template1` later on.

Another common reason for copying `template0` instead
of `template1` is that new encoding and locale settings
can be specified when copying `template0`, whereas a copy
of `template1` must use the same settings it does.
This is because `template1` might contain encoding-specific
or locale-specific data, while `template0` is known not to.

To create a database by copying `template0`, use:

```
CREATE DATABASE `dbname` TEMPLATE template0;
```

from the SQL environment, or:

```
createdb -T template0 `dbname`
```

from the shell.

It is possible to create additional template databases, and indeed
one can copy any database in a cluster by specifying its name
as the template for `CREATE DATABASE`.  It is important to
understand, however, that this is not (yet) intended as
a general-purpose "`COPY DATABASE`" facility.
The principal limitation is that no other sessions can be connected to
the source database while it is being copied.  `CREATE
DATABASE` will fail if any other connection exists when it starts;
during the copy operation, new connections to the source database
are prevented.

Two useful flags exist in `pg_database` for each
database: the columns `datistemplate` and
`datallowconn`.  `datistemplate`
can be set to indicate that a database is intended as a template for
`CREATE DATABASE`.  If this flag is set, the database can be
cloned by any user with `CREATEDB` privileges; if it is not set,
only superusers and the owner of the database can clone it.
If `datallowconn` is false, then no new connections
to that database will be allowed (but existing sessions are not terminated
simply by setting the flag false).  The `template0`
database is normally marked `datallowconn = false` to prevent its modification.
Both `template0` and `template1`
should always be marked with `datistemplate = true`.

> **Note:**

> `template1` and `template0` do not have any special
> status beyond the fact that the name `template1` is the default
> source database name for `CREATE DATABASE`.
> For example, one could drop `template1` and recreate it from
> `template0` without any ill effects.  This course of action
> might be advisable if one has carelessly added a bunch of junk in
> `template1`. (To delete `template1`,
> it must have `pg_database.datistemplate = false`.)
>

>

> The `postgres` database is also created when a database
> cluster is initialized.  This database is meant as a default database for
> users and applications to connect to. It is simply a copy of
> `template1` and can be dropped and recreated if necessary.
>
