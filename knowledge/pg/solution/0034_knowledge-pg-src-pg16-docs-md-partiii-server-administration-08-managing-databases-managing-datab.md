# Destroying a Database

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/08_managing_databases.md`
- Source Title: `Managing Databases`
- Source Heading Path: `Managing Databases > Destroying a Database`
- Source Line Ranges: `291-322`
- Chunk ID: `pg16_solution_0034_c533daae7a`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `185b892ad459b9a5c836b4587d69c6ebee38b5dc8e69ecdcf8eeec1fe8f3e280`

## Retrieval Guidance

- Use When: 需要删除数据库。
- Retrieval Keywords: DROP DATABASE, dropdb, database owner, cannot be connected, template1
- Follow-up Guidance: 删除不可撤销，执行前确认备份和连接终止。
- Classification Note: 说明 DROP DATABASE/dropdb、权限要求、不可连接到目标库执行和不可恢复性。

## Official Source Content

## Destroying a Database

Databases are destroyed with the command
[sql-dropdatabase](#sql-dropdatabase):

```
DROP DATABASE `name`;
```

Only the owner of the database, or
a superuser, can drop a database. Dropping a database removes all objects
that were
contained within the database. The destruction of a database cannot
be undone.

You cannot execute the `DROP DATABASE` command
while connected to the victim database. You can, however, be
connected to any other database, including the `template1`
database.
`template1` would be the only option for dropping the last user database of a
given cluster.

For convenience, there is also a shell program to drop
databases, [app-dropdb](#app-dropdb):

```
dropdb `dbname`
```

(Unlike `createdb`, it is not the default action to drop
the database with the current user name.)
