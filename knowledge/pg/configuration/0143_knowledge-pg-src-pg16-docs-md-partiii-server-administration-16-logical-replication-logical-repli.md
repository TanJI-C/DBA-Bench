# Configuration Settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Configuration Settings`
- Source Line Ranges: `1486-1540`
- Chunk ID: `pg16_configuration_0143_5f4f3e1027`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `09ff8e4d500cdc524888dd2509a1fb0ae1b5e06226eb67cd82d0b995b5b6c86e`

## Retrieval Guidance

- Use When: 需要确认逻辑复制所需 postgresql.conf 参数。
- Retrieval Keywords: logical replication configuration settings, max_replication_slots, publisher settings, subscriber settings, logical workers
- Follow-up Guidance: 按 publisher/subscriber 分别核对参数含义和 worker/slot 余量。
- Classification Note: 概述逻辑复制发布端/订阅端所需参数，尤其 max_replication_slots 双侧语义。

## Official Source Content

## Configuration Settings

Logical replication requires several configuration options to be set. Most
options are relevant only on one side of the replication. However,
`max_replication_slots` is used on both the publisher and
the subscriber, but it has a different meaning for each.

### Publishers

[`wal_level`](#guc-wal-level) must be
set to `logical`.

[`max_replication_slots`](#guc-max-replication-slots)
must be set to at least the number of subscriptions expected to connect,
plus some reserve for table synchronization.

[`max_wal_senders`](#guc-max-wal-senders)
should be set to at least the same as
`max_replication_slots`, plus the number of physical
replicas that are connected at the same time.

Logical replication walsender is also affected by
[`wal_sender_timeout`](#guc-wal-sender-timeout).

### Subscribers

[`max_replication_slots`](#guc-max-replication-slots-subscriber)
must be set to at least the number of subscriptions that will be added to
the subscriber, plus some reserve for table synchronization.

[`max_logical_replication_workers`](#guc-max-logical-replication-workers)
must be set to at least the number of subscriptions (for leader apply
workers), plus some reserve for the table synchronization workers and
parallel apply workers.

[`max_worker_processes`](#guc-max-worker-processes)
may need to be adjusted to accommodate for replication workers, at least
([`max_logical_replication_workers`](#guc-max-logical-replication-workers)
+ `1`). Note, some extensions and parallel queries also
take worker slots from `max_worker_processes`.

[`max_sync_workers_per_subscription`](#guc-max-sync-workers-per-subscription)
controls the amount of parallelism of the initial data copy during the
subscription initialization or when new tables are added.

[`max_parallel_apply_workers_per_subscription`](#guc-max-parallel-apply-workers-per-subscription)
controls the amount of parallelism for streaming of in-progress
transactions with subscription parameter
`streaming = parallel`.

Logical replication workers are also affected by
[`wal_receiver_timeout`](#guc-wal-receiver-timeout),
[`wal_receiver_status_interval`](#guc-wal-receiver-status-interval) and
[`wal_retrieve_retry_interval`](#guc-wal-retrieve-retry-interval).
