# GC process and implementation details

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/garbage-collection-overview.md`
- Source Title: `GC Overview`
- Source Heading Path: `GC Overview | GC Overview > GC process | GC Overview > Implementation details | GC Overview > Implementation details > Resolve Locks | GC Overview > Implementation details > Delete Ranges | GC Overview > Implementation details > Do GC`
- Source Line Ranges: `5-51`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `garbage-collection`, `mvcc`, `safe-point`, `gc-leader`, `resolve-locks`, `delete-ranges`, `distributed-gc`, `transactions`, `drop-table`, `drop-index`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0040_61aeb36794`
- Source ID: `tidb-docs-8.1:garbage-collection-overview.md#gc-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8ccccac7d9899d9d69b1280217a6d109ec2f5ae9077c49c822109b4803ebf2f4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/garbage-collection-overview#gc-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/garbage-collection-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about how TiDB garbage collection works, including safe point calculation, the GC leader, and the Resolve Locks, Delete Ranges, and Do GC steps.
- Retrieval Keywords: GC Overview, garbage collection, MVCC, safe point, GC leader, Resolve Locks, Delete Ranges, Do GC, tidb_gc_scan_lock_mode, LEGACY, PHYSICAL, Green GC, DROP TABLE, DROP INDEX, DISTRIBUTED gc mode, CENTRAL gc mode, PD, TiKV, two-phase commit, primary lock, secondary locks
- Follow-up Guidance: This content also states the default GC interval and GC life time are 10 minutes and notes that the Do GC step always uses the `DISTRIBUTED` gc mode starting with TiDB 5.0.
- Classification Note: This is classified as architecture because the content describes the cluster-wide GC workflow, component roles across TiDB, TiKV, and PD, and the implementation details of distributed MVCC garbage collection.

## Official Source Content

# GC Overview

TiDB uses MVCC to control transaction concurrency. When you update the data, the original data is not deleted immediately but is kept together with the new data, with a timestamp to distinguish the version. The goal of Garbage Collection (GC) is to clear the obsolete data.
## GC process

Each TiDB cluster contains a TiDB instance that is selected as the GC leader, which controls the GC process.

GC runs periodically on TiDB. For each GC, TiDB firstly calculates a timestamp called "safe point". Then, TiDB clears the obsolete data under the premise that all the snapshots after the safe point retain the integrity of the data. Specifically, there are three steps involved in each GC process:

1. Resolve Locks. During this step, TiDB scans locks before the safe point on all Regions and clears these locks.
2. Delete Ranges. During this step, the obsolete data of the entire range generated from the `DROP TABLE`/`DROP INDEX` operation is quickly cleared.
3. Do GC. During this step, each TiKV node scans data on it and deletes unneeded old versions of each key.

In the default configuration, GC is triggered every 10 minutes. Each GC retains data of the recent 10 minutes, which means that the GC life time is 10 minutes by default (safe point = the current time - GC life time). If one round of GC has been running for too long, before this round of GC is completed, the next round of GC will not start even if it is time to trigger the next GC. In addition, for long-duration transactions to run properly after exceeding the GC life time, the safe point does not exceed the start time (start_ts) of the ongoing transactions.
## Implementation details
### Resolve Locks

The TiDB transaction model is implemented based on [Google's Percolator](https://ai.google/research/pubs/pub36726). It's mainly a two-phase commit protocol with some practical optimizations. When the first phase is finished, all the related keys are locked. Among these locks, one is the primary lock and the others are secondary locks which contain a pointer to the primary lock; in the second phase, the key with the primary lock gets a write record and its lock is removed. The write record indicates the write or delete operation in the history or the transactional rollback record of this key. The type of write record that replaces the primary lock indicates whether the corresponding transaction is committed successfully. Then all the secondary locks are replaced successively. If, for some reason such as failure, these secondary locks are retained and not replaced, you can still find the primary key based on the information in the secondary locks and determines whether the entire transaction is committed based on whether the primary key is committed. However, if the primary key information is cleared by GC and this transaction has uncommitted secondary locks, you will never learn whether these locks can be committed. As a result, data integrity cannot be guaranteed.

The Resolve Locks step clears the locks before the safe point. This means that if the primary key of a lock is committed, this lock needs to be committed; otherwise, it needs to be rolled back. If the primary key is still locked (not committed or rolled back), this transaction is seen as timing out and rolled back.

The Resolve Locks step is implemented in either of the following two ways, which can be configured using the system variable [`tidb_gc_scan_lock_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_scan_lock_mode-new-in-v50):

> **Warning:**
>
> Currently, `PHYSICAL` (Green GC) is an experimental feature. It is not recommended that you use it in the production environment.

- `LEGACY` (default): The GC leader sends requests to all Regions to scan obsolete locks, checks the primary key statuses of scanned locks, and sends requests to commit or roll back the corresponding transaction.
- `PHYSICAL`: TiDB bypasses the Raft layer and directly scans data on each TiKV node.
### Delete Ranges

A great amount of data with consecutive keys is removed during operations such as `DROP TABLE/INDEX`. Removing each key and performing GC later for them can result in low execution efficiency on storage reclaiming. In such scenarios, TiDB actually does not delete each key. Instead, it only records the range to be removed and the timestamp of the deletion. Then the Delete Ranges step performs a fast physical deletion on the ranges whose timestamp is before the safe point.
### Do GC

The Do GC step clears the outdated versions for all keys. To guarantee that all timestamps after the safe point have consistent snapshots, this step deletes the data committed before the safe point, but retains the last write for each key before the safe point as long as it is not a deletion.

In this step, TiDB only needs to send the safe point to PD, and then the whole round of GC is completed. TiKV automatically detects the change of safe point and performs GC for all Region leaders on the current node. At the same time, the GC leader can continue to trigger the next round of GC.

> **Note:**
>
> Starting with TiDB 5.0, the Do GC step will always use the `DISTRIBUTED` gc mode. This replaces the earlier `CENTRAL` gc mode, which was implemented by TiDB servers sending GC requests to each Region.
