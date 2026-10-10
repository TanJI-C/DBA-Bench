# Database Configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/08_managing_databases.md`
- Source Title: `Managing Databases`
- Source Heading Path: `Managing Databases > Database Configuration`
- Source Line Ranges: `264-290`
- Chunk ID: `pg16_configuration_0106_986960d8c4`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `228f98c8db2f9e2cb9ef4bff952deeca832d21599f7a00855da22615d7db9a16`

## Retrieval Guidance

- Use When: 需要给某个数据库设置默认运行时参数。
- Retrieval Keywords: ALTER DATABASE SET, ALTER DATABASE RESET, database-specific default, geqo
- Follow-up Guidance: 新会话才生效，用户仍可在会话中覆盖可变参数。
- Classification Note: 说明 ALTER DATABASE SET/RESET 数据库级 GUC 默认值。

## Official Source Content

## Database Configuration

Recall from [runtime-config](#runtime-config) that the
PostgreSQL server provides a large number of
run-time configuration variables.  You can set database-specific
default values for many of these settings.

For example, if for some reason you want to disable the
GEQO optimizer for a given database, you'd
ordinarily have to either disable it for all databases or make sure
that every connecting client is careful to issue `SET geqo
TO off`.  To make this setting the default within a particular
database, you can execute the command:

```
ALTER DATABASE mydb SET geqo TO off;
```

This will save the setting (but not set it immediately).  In
subsequent connections to this database it will appear as though
`SET geqo TO off;` had been executed just before the
session started.
Note that users can still alter this setting during their sessions; it
will only be the default.  To undo any such setting, use
`ALTER DATABASE `dbname` RESET
`varname``.
