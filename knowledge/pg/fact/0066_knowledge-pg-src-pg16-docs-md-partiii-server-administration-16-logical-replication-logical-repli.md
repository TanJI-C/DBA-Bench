# Restrictions

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Restrictions`
- Source Line Ranges: `562-574, 1279-1332`
- Chunk ID: `pg16_fact_0066_e342b95f6a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3d0b6ab0d2933deb7ad837b750bc160e22a50d74d47e20af1b93939ec69c71a6`

## Retrieval Guidance

- Use When: 解释逻辑复制为什么未同步 schema、sequence 或特定对象类型。
- Retrieval Keywords: logical replication restrictions, DDL not replicated, sequence not replicated, large objects not replicated, TRUNCATE foreign keys, partitioned tables
- Follow-up Guidance: schema 用 pg_dump --schema-only 或手动同步；failover 前更新 sequence。
- Classification Note: 列出 DDL、sequence、large object、非表关系和 partition 复制限制。

## Official Source Content

### Expression Restrictions

The `WHERE` clause allows only simple expressions. It
cannot contain user-defined functions, operators, types, and collations,
system column references or non-immutable built-in functions.

If a publication publishes `UPDATE` or
`DELETE` operations, the row filter `WHERE`
clause must contain only columns that are covered by the replica identity
(see [sql-altertable-replica-identity](#sql-altertable-replica-identity)). If a publication
publishes only `INSERT` operations, the row filter
`WHERE` clause can use any column.

## Restrictions

Logical replication currently has the following restrictions or missing
functionality.  These might be addressed in future releases.

- The database schema and DDL commands are not replicated.  The initial
schema can be copied by hand using `pg_dump
--schema-only`.  Subsequent schema changes would need to be kept
in sync manually.  (Note, however, that there is no need for the schemas
to be absolutely the same on both sides.)  Logical replication is robust
when schema definitions change in a live database: When the schema is
changed on the publisher and replicated data starts arriving at the
subscriber but does not fit into the table schema, replication will error
until the schema is updated.  In many cases, intermittent errors can be
avoided by applying additive schema changes to the subscriber first.
- Sequence data is not replicated.  The data in serial or identity columns
backed by sequences will of course be replicated as part of the table,
but the sequence itself would still show the start value on the
subscriber.  If the subscriber is used as a read-only database, then this
should typically not be a problem.  If, however, some kind of switchover
or failover to the subscriber database is intended, then the sequences
would need to be updated to the latest values, either by copying the
current data from the publisher (perhaps
using `pg_dump`) or by determining a sufficiently high
value from the tables themselves.
- Replication of `TRUNCATE` commands is supported, but
some care must be taken when truncating groups of tables connected by
foreign keys.  When replicating a truncate action, the subscriber will
truncate the same group of tables that was truncated on the publisher,
either explicitly specified or implicitly collected via
`CASCADE`, minus tables that are not part of the
subscription.  This will work correctly if all affected tables are part
of the same subscription.  But if some tables to be truncated on the
subscriber have foreign-key links to tables that are not part of the same
(or any) subscription, then the application of the truncate action on the
subscriber will fail.
- Large objects (see [largeobjects](#largeobjects)) are not replicated.
There is no workaround for that, other than storing data in normal
tables.
- Replication is only supported by tables, including partitioned tables.
Attempts to replicate other types of relations, such as views, materialized
views, or foreign tables, will result in an error.
- When replicating between partitioned tables, the actual replication
originates, by default, from the leaf partitions on the publisher, so
partitions on the publisher must also exist on the subscriber as valid
target tables. (They could either be leaf partitions themselves, or they
could be further subpartitioned, or they could even be independent
tables.)  Publications can also specify that changes are to be replicated
using the identity and schema of the partitioned root table instead of
that of the individual leaf partitions in which the changes actually
originate (see
[`publish_via_partition_root`](#sql-createpublication-with-publish-via-partition-root)
parameter of `CREATE PUBLICATION`).
