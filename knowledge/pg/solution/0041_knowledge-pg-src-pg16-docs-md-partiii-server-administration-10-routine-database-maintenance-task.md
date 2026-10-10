# Routine Reindexing

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/10_routine_database_maintenance_tasks.md`
- Source Title: `Routine Database Maintenance Tasks`
- Source Heading Path: `Routine Database Maintenance Tasks > Routine Reindexing`
- Source Line Ranges: `753-782`
- Chunk ID: `pg16_solution_0041_dca59fded9`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4c74606e75f8d2c36c735b523aa01bbb86f361e51a398b1a46dabc5b5cd91b00`

## Retrieval Guidance

- Use When: 确认索引膨胀、索引空间利用差或重建索引提升访问速度。
- Retrieval Keywords: REINDEX, REINDEX CONCURRENTLY, index bloat, B-tree, ACCESS EXCLUSIVE, SHARE UPDATE EXCLUSIVE
- Follow-up Guidance: 评估锁级别和维护窗口，优先考虑 CONCURRENTLY。
- Classification Note: 说明何时重建索引以及 REINDEX CONCURRENTLY 的低阻塞处置方式。

## Official Source Content

## Routine Reindexing

In some situations it is worthwhile to rebuild indexes periodically
with the [sql-reindex](#sql-reindex) command or a series of individual
rebuilding steps.

B-tree index pages that have become completely empty are reclaimed for
re-use.  However, there is still a possibility
of inefficient use of space: if all but a few index keys on a page have
been deleted, the page remains allocated.  Therefore, a usage
pattern in which most, but not all, keys in each range are eventually
deleted will see poor use of space.  For such usage patterns,
periodic reindexing is recommended.

The potential for bloat in non-B-tree indexes has not been well
researched.  It is a good idea to periodically monitor the index's physical
size when using any non-B-tree index type.

Also, for B-tree indexes, a freshly-constructed index is slightly faster to
access than one that has been updated many times because logically
adjacent pages are usually also physically adjacent in a newly built index.
(This consideration does not apply to non-B-tree indexes.)  It
might be worthwhile to reindex periodically just to improve access speed.

[sql-reindex](#sql-reindex) can be used safely and easily in all cases.
This command requires an `ACCESS EXCLUSIVE` lock by
default, hence it is often preferable to execute it with its
`CONCURRENTLY` option, which requires only a
`SHARE UPDATE EXCLUSIVE` lock.
