# Performance improvements in transactions, cache, delete, and split strategy

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > Performance optimization > Async Commit | What's New in TiDB 5.0 > Performance optimization > Enable the Coprocessor cache feature by default | What's New in TiDB 5.0 > Performance optimization > Improve the execution performance of `delete from table where id <? Limit ?` statement | What's New in TiDB 5.0 > Performance optimization > Optimize load base split strategy to solve the performance problem that data cannot be split in some small table hotspot read scenarios`
- Source Line Ranges: `235-274`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `async-commit`, `1pc`, `causal-consistency`, `coprocessor-cache`, `latency`, `delete-performance`, `hotspot-read`, `load-based-split`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0150_6cc9bc31ab`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#async-commit`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc9d967e3ddfbc6375a353c274ecd1d349b3d7179c3d6d4a75a74270088f034b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#async-commit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this content when you need TiDB 5.0 release-note details on Async Commit, 1PC, causal consistency, Coprocessor cache defaults, delete performance, or load base split strategy improvements.
- Retrieval Keywords: Async Commit, tidb_enable_async_commit, tidb_enable_1pc, START TRANSACTION WITH CAUSAL CONSISTENCY, causal consistency, one-phase commit, 1PC, 2PC, set global tidb_enable_async_commit = ON;, set global tidb_enable_1pc = ON;, Coprocessor cache, tikv-client.copr-cache, capacity-mb, delete from table where id <? limit ?, load base split strategy, small table hotspot read
- Follow-up Guidance: The content notes that Async Commit is enabled by default for newly created v5.0 clusters, is disabled by default for clusters upgraded to v5.0, and has the limitation that direct downgrade is not supported.
- Classification Note: This is classified as performance content because it summarizes latency reductions for transaction commit and read caching, plus execution improvements for delete statements and hotspot read split behavior.

## Official Source Content

### Async Commit

[User document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_async_commit-new-in-v50), [#8316](https://github.com/tikv/tikv/issues/8316)

The client of the database will wait for the database system to complete the transaction commit in two phases (2PC) synchronously. The transaction returns the result to the client after the first phase commit is successful, and the system executes the second phase commit operation in the background asynchronously to reduce the transaction commit latency. If the transaction write involves only one Region, the second phase is omitted directly, and the transaction becomes a one-phase commit.

After the Async Commit feature is enabled, with the same hardware and configuration, when Sysbench is set to test the Update index with 64 threads, the average latency decreases by 41.7% from 12.04ms to 7.01ms.

When Async Commit feature is enabled, to reduce one network interaction latency and improve the performance of data writes, database application developers are recommended to consider reducing the consistency of transactions from linear consistency to [causal consistency](https://docs.pingcap.com/tidb/stable/transaction-overview#causal-consistency). The SQL statement to enable causal consistency is `START TRANSACTION WITH CAUSAL CONSISTENCY`.

After the causal consistency is enabled, with the same hardware and configuration, when Sysbench is set to test oltp_write_only with 64 threads, the average latency decreased by 5.6% from 11.86ms to 11.19ms.

After the consistency of transactions is reduced from the linear consistency to causal consistency, if there is no interdependence between multiple transactions in the application, the transactions do not have a globally consistent order.

**The Async Commit feature is enabled by default for newly created v5.0 clusters.**

This feature is disabled by default for clusters upgraded from earlier versions to v5.0. You can enable this feature by executing the `set global tidb_enable_async_commit = ON;` and `set global tidb_enable_1pc = ON;` statements.

The limitation for the Async Commit feature is as follows:

+ Direct downgrade is not supported.
### Enable the Coprocessor cache feature by default

[User document](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tikv-clientcopr-cache-new-in-v400), [#18028](https://github.com/pingcap/tidb/issues/18028)

In 5.0 GA, the Coprocessor cache feature is enabled by default. After this feature is enabled, to reduce the latency of reading data, TiDB caches the calculation results of the operators pushed down to tikv-server in tidb-server.

To disable the Coprocessor cache feature, you can modify the `capacity-mb` configuration item of `tikv-client.copr-cache` to `0.0`.
### Improve the execution performance of `delete from table where id <? Limit ?` statement

[#18028](https://github.com/pingcap/tidb/issues/18028)

The p99 performance of the `delete from table where id <? limit ?` statement is improved by 4 times.
### Optimize load base split strategy to solve the performance problem that data cannot be split in some small table hotspot read scenarios

[#18005](https://github.com/pingcap/tidb/issues/18005)
