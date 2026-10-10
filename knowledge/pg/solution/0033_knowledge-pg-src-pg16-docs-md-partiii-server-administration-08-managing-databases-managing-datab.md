# Creating a Database

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/08_managing_databases.md`
- Source Title: `Managing Databases`
- Source Heading Path: `Managing Databases > Creating a Database`
- Source Line Ranges: `74-161`
- Chunk ID: `pg16_solution_0033_4262ec8cda`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6225bbbb0f02e7409f77fba55e35163cc92815b67153989749c93c91a2417403`

## Retrieval Guidance

- Use When: 需要创建新数据库或为指定 role 创建数据库。
- Retrieval Keywords: CREATE DATABASE, createdb, OWNER, postgres database, template1, template0, CREATEDB
- Follow-up Guidance: 非 superuser 为他人创建数据库受角色成员关系/权限限制。
- Classification Note: 给出 CREATE DATABASE、createdb、OWNER、template/postgres 初始数据库等创建动作。

## Official Source Content

## Creating a Database

In order to create a database, the PostgreSQL
server must be up and running (see [server-start](#server-start)).

Databases are created with the SQL command
[sql-createdatabase](#sql-createdatabase):

```
CREATE DATABASE `name`;
```

where `name` follows the usual rules for
SQL identifiers.  The current role automatically
becomes the owner of the new database. It is the privilege of the
owner of a database to remove it later (which also removes all
the objects in it, even if they have a different owner).

The creation of databases is a restricted operation. See [role-attributes](#role-attributes) for how to grant permission.

Since you need to be connected to the database server in order to
execute the `CREATE DATABASE` command, the
question remains how the *first* database at any given
site can be created. The first database is always created by the
`initdb` command when the data storage area is
initialized. (See [creating-cluster](#creating-cluster).)  This
database is called
`postgres`. So to
create the first "ordinary" database you can connect to
`postgres`.

Two additional databases,
`template1`
and
`template0`,
are also created during database cluster initialization.  Whenever a
new database is created within the
cluster, `template1` is essentially cloned.
This means that any changes you make in `template1` are
propagated to all subsequently created databases. Because of this,
avoid creating objects in `template1` unless you want them
propagated to every newly created database.
`template0` is meant as a pristine copy of the original
contents of `template1`.  It can be cloned instead
of `template1` when it is important to make a database
without any such site-local additions.  More details
appear in [manage-ag-templatedbs](#manage-ag-templatedbs).

As a convenience, there is a program you can
execute from the shell to create new databases,
`createdb`.

```
createdb `dbname`
```

`createdb` does no magic. It connects to the `postgres`
database and issues the `CREATE DATABASE` command,
exactly as described above.
The [app-createdb](#app-createdb) reference page contains the invocation
details. Note that `createdb` without any arguments will create
a database with the current user name.

> **Note:**

> [client-authentication](#client-authentication) contains information about
> how to restrict who can connect to a given database.
>

Sometimes you want to create a database for someone else, and have them
become the owner of the new database, so they can
configure and manage it themselves.  To achieve that, use one of the
following commands:

```
CREATE DATABASE `dbname` OWNER `rolename`;
```

from the SQL environment, or:

```
createdb -O `rolename` `dbname`
```

from the shell.
Only the superuser is allowed to create a database for
someone else (that is, for a role you are not a member of).
