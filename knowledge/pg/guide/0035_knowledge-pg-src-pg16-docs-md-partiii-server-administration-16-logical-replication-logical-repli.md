# Monitoring

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Monitoring`
- Source Line Ranges: `1395-1417`
- Chunk ID: `pg16_guide_0035_7c203cb4d0`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01b6a0a129d2b2c60ba1b79c861e5c05ff9b94b9814a043f5c6dd8f880d48272`

## Retrieval Guidance

- Use When: 诊断 logical replication 是否运行、是否在初始同步或 worker 崩溃。
- Retrieval Keywords: logical replication monitoring, pg_stat_subscription, subscription workers, apply process, table synchronization, parallel apply workers
- Follow-up Guidance: 无 worker 行时检查 subscription disabled/crashed 和 subscriber log。
- Classification Note: 指出 publication 端类似物理复制，subscription 端用 pg_stat_subscription 诊断。

## Official Source Content

## Monitoring

Because logical replication is based on a similar architecture as
[physical streaming replication](#streaming-replication),
the monitoring on a publication node is similar to monitoring of a
physical replication primary
(see [streaming-replication-monitoring](#streaming-replication-monitoring)).

The monitoring information about subscription is visible in
[
`pg_stat_subscription`](#monitoring-pg-stat-subscription).
This view contains one row for every subscription worker.  A subscription
can have zero or more active subscription workers depending on its state.

Normally, there is a single apply process running for an enabled
subscription.  A disabled subscription or a crashed subscription will have
zero rows in this view.  If the initial data synchronization of any
table is in progress, there will be additional workers for the tables
being synchronized. Moreover, if the
[`streaming`](#sql-createsubscription-with-streaming)
transaction is applied in parallel, there may be additional parallel apply
workers.
