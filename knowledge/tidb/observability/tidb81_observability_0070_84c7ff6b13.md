# Conflict detection and latch wait monitoring in TiKV

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimistic-transaction.md`
- Source Title: `TiDB Optimistic Transaction Model`
- Source Heading Path: `TiDB Optimistic Transaction Model > Conflict detection`
- Source Line Ranges: `138-153`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `conflict-detection`, `prewrite-phase`, `latches`, `scheduler`, `metrics`, `write-conflicts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0070_84c7ff6b13`
- Source ID: `tidb-docs-8.1:optimistic-transaction.md#conflict-detection`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8bb79d4d9d5c865ef1669225bfe1b57afb4ac12fcc3a537be1f55aff95e04bf4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimistic-transaction#conflict-detection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how optimistic transaction conflict detection works in TiKV, the `scheduler-concurrency` setting, and how to interpret high `Scheduler latch wait duration` during write conflicts.
- Retrieval Keywords: Conflict detection, TiKV layer, prewrite phase, in-memory conflict detection, scheduler-concurrency, Scheduler latch wait duration, waiting latches in the scheduler, write conflicts, slow writes, stateless TiDB instances
- Follow-up Guidance: The source says that when `Scheduler latch wait duration` is high and there are no slow writes, it can be safely concluded that there are many write conflicts at this time.
- Classification Note: This is classified as observability because the content highlights monitoring `Scheduler latch wait duration` and using it to infer write conflict conditions in TiKV.

## Official Source Content

## Conflict detection

As a distributed database, TiDB performs in-memory conflict detection in the TiKV layer, mainly in the prewrite phase. TiDB instances are stateless and unaware of each other, which means they cannot know whether their writes result in conflicts across the cluster. Therefore, conflict detection is performed in the TiKV layer.

The configuration is as follows:

```toml
# Controls the number of slots. ("2048000" by default）
scheduler-concurrency = 2048000
```

In addition, TiKV supports monitoring the time spent on waiting latches in the scheduler.

![Scheduler latch wait duration](/media/optimistic-transaction-metric.png)

When `Scheduler latch wait duration` is high and there are no slow writes, it can be safely concluded that there are many write conflicts at this time.
