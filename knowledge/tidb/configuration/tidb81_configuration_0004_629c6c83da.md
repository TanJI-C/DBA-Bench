# Disable local latches for write-conflict-free batch tasks

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/high-concurrency-best-practices.md`
- Source Title: `Highly Concurrent Write Best Practices`
- Source Heading Path: `Highly Concurrent Write Best Practices > Parameter configuration`
- Source Line Ranges: `243-250`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `latch`, `txn-local-latches`, `write-conflict`, `batch-tasks`, `memory-allocation`, `transaction-retry`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0004_629c6c83da`
- Source ID: `tidb-docs-8.1:best-practices/high-concurrency-best-practices.md#parameter-configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `21ab272ac4e01e657328a60aebefd04b17310023da1c1343a323849e9f964e68`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices#parameter-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/high-concurrency-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when asking about disabling TiDB local latches for batch tasks that do not have transaction write conflicts to reduce memory allocation.
- Retrieval Keywords: txn-local-latches, latch mechanism, enabled = false, write conflicts, batch tasks, transaction retry, memory allocation for small objects, TiDB configuration file
- Follow-up Guidance: The source says the latch mechanism is used to identify transaction conflicts in advance and reduce retries of transaction commits in TiDB and TiKV caused by write conflicts.
- Classification Note: This is classified as configuration content because it provides the `txn-local-latches` setting and the condition under which disabling it is described in the official content.

## Official Source Content

## Parameter configuration

In v2.1, the [latch mechanism](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-local-latches) is introduced in TiDB to identify transaction conflicts in advance in scenarios where write conflicts frequently appear. The aim is to reduce the retry of transaction commits in TiDB and TiKV caused by write conflicts. Generally, batch tasks use the data already stored in TiDB, so the write conflicts of transaction do not exist. In this situation, you can disable the latch in TiDB to reduce memory allocation for small objects:

```
[txn-local-latches]
enabled = false
```
