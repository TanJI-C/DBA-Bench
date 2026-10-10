# Viewing Locks

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/13_monitoring_database_activity.md`
- Source Title: `Monitoring Database Activity`
- Source Heading Path: `Monitoring Database Activity > Viewing Locks`
- Source Line Ranges: `1269-1292`
- Chunk ID: `pg16_guide_0024_a5dff3f16f`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b8480b284c01acbb771e47a7ffd4664fa7b8b4a8b7675d91850903a6324f55db`

## Retrieval Guidance

- Use When: 诊断会话等待、锁竞争、阻塞链或某表未授予锁异常。
- Retrieval Keywords: Viewing Locks, pg_locks, ungranted locks, lock contention, blocking session, relation locks
- Follow-up Guidance: 联表 pg_stat_activity 确认 blocker、waiter 和当前 SQL。
- Classification Note: 说明 pg_locks 可确认锁、未授予锁和锁竞争影响。

## Official Source Content

## Viewing Locks

Another useful tool for monitoring database activity is the
`pg_locks` system table.  It allows the
database administrator to view information about the outstanding
locks in the lock manager. For example, this capability can be used
to:

- View all the locks currently outstanding, all the locks on
relations in a particular database, all the locks on a
particular relation, or all the locks held by a particular
PostgreSQL session.
- Determine the relation in the current database with the most
ungranted locks (which might be a source of contention among
database clients).
- Determine the effect of lock contention on overall database
performance, as well as the extent to which contention varies
with overall database traffic.

Details of the `pg_locks` view appear in
[view-pg-locks](#view-pg-locks).
For more information on locking and managing concurrency with
PostgreSQL, refer to [mvcc](#mvcc).
