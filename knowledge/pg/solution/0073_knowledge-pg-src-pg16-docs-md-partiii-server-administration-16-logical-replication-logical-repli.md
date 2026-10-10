# Quick Setup

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Quick Setup`
- Source Line Ranges: `1541-1575`
- Chunk ID: `pg16_solution_0073_c38bf7a2da`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4eb75a81a8446e0752f71991e0294e6705ee29044b950ca6d59db823af3214ae`

## Retrieval Guidance

- Use When: 需要快速搭建基础逻辑复制链路。
- Retrieval Keywords: logical replication quick setup, wal_level logical, pg_hba repuser, CREATE PUBLICATION mypub, CREATE SUBSCRIPTION mysub
- Follow-up Guidance: 生产前补充权限最小化、slot/worker 容量和冲突监控。
- Classification Note: 给出 wal_level、pg_hba、CREATE PUBLICATION/SUBSCRIPTION 的最小可用搭建步骤。

## Official Source Content

## Quick Setup

First set the configuration options in `postgresql.conf`:

```
wal_level = logical
```

The other required settings have default values that are sufficient for a
basic setup.

`pg_hba.conf` needs to be adjusted to allow replication
(the values here depend on your actual network configuration and user you
want to use for connecting):

```
host     all     repuser     0.0.0.0/0     md5
```

Then on the publisher database:

```
CREATE PUBLICATION mypub FOR TABLE users, departments;
```

And on the subscriber database:

```
CREATE SUBSCRIPTION mysub CONNECTION 'dbname=foo host=bar user=repuser' PUBLICATION mypub;
```

The above will start the replication process, which synchronizes the
initial table contents of the tables `users` and
`departments` and then starts replicating
incremental changes to those tables.
