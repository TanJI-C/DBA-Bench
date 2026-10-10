# Slow space reclamation after deleting data

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/sql-faq.md`
- Source Title: `SQL FAQs`
- Source Heading Path: `SQL FAQs > What should I do if it is slow to reclaim storage space after deleting data?`
- Source Line Ranges: `191-194`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `mvcc`, `garbage-collection`, `space-reclamation`, `delete`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0152_6d1a85da0b`
- Source ID: `tidb-docs-8.1:faq/sql-faq.md#what-should-i-do-if-it-is-slow-to-reclaim-storage-space-after-deleting-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `62a16b2b96d284743cd0632442c2141bf55562b3080a8051e5c723f3908108f9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/sql-faq#what-should-i-do-if-it-is-slow-to-reclaim-storage-space-after-deleting-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/sql-faq.md

## Retrieval Guidance

- Use When: Use this chunk when explaining why deleting data does not immediately reclaim storage space in TiDB and how MVCC and garbage collection timing affect space reclamation.
- Retrieval Keywords: MVCC, garbage collection, space reclamation after deleting data, deleting data does not immediately reclaim space, tidb_gc_life_time, old data retained along with the new data, timestamps identify the data version
- Follow-up Guidance: The source points to the `tidb_gc_life_time` system variable, whose default is `10m0s`, as the configurable garbage collection delay.
- Classification Note: This is classified as operation content because it describes runtime storage reclamation behavior and the relevant system variable for garbage collection timing.

## Official Source Content

## What should I do if it is slow to reclaim storage space after deleting data?

Because TiDB uses multi-version concurrency control (MVCC), when the old data is overwritten with new data, the old data is not replaced but retained along with the new data. Timestamps are used to identify the data version. Deleting data does not immediately reclaim space. Garbage collection is delayed so that concurrent transactions are able to see earlier versions of rows. This can be configured via the [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) (default: `10m0s`) system variable.
