# New performance features across TiKV, TiDB, and TiFlash

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes > New Features > Performance`
- Source Line Ranges: `60-103`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `tidb`, `tiflash`
- Topic Tags: `release-notes`, `new-features`, `performance`, `region-size`, `buckets`, `raft-engine`, `join-hints`, `dynamic-pruning`, `partitioned-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0296_3fe6f2c509`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c545dc0aa59d7c4a45ddc00c987c9e856d5dca945cfc0143b58729852c07fb3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.1.0 release-note details about performance features involving Region sizing, buckets, Raft Engine, join order hints, TiFlash functions, or dynamic pruning for partitioned tables.
- Retrieval Keywords: TiDB 6.1.0 Release Notes, Performance, coprocessor.region-split-size, Region size, bucket, use bucket to increase concurrency, Raft Engine, default log storage engine, LEADING hint, STRAIGHT_JOIN, join order hint syntax, FROM_DAYS, TO_DAYS, TO_SECONDS, WEEKOFYEAR, TiFlash partitioned tables, dynamic pruning mode, MPP mode
- Follow-up Guidance: The content references user documents for region split size tuning, bucket concurrency, raft-engine configuration, optimizer hints, TiFlash supported pushdown calculations, access partitioned tables in the MPP mode, and dynamic pruning mode.
- Classification Note: This is classified as a release chunk because it lists TiDB 6.1.0 performance-related new features and improvements across TiKV, TiDB, and TiFlash.

## Official Source Content

### Performance

* Support customized Region size

    Starting from v6.1.0, you can configure [`coprocessor.region-split-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-split-size) to set Regions to a larger size. This can effectively reduce the number of Regions, make Regions easier to manage, and improve the cluster performance and stability.

    [User document](https://docs.pingcap.com/tidb/stable/tune-region-performance#use-region-split-size-to-adjust-region-size), [#11515](https://github.com/tikv/tikv/issues/11515)

* Support using buckets to increase concurrency (experimental)

    To help you further improve the query concurrency after setting Regions to a larger size, TiDB introduces the concept of bucket, which is a smaller range within a Region. Using buckets as the query unit can optimize concurrent query performance when Regions are set to a larger size. Using buckets as the query unit can also dynamically adjust the sizes of hotspot Regions to ensure the scheduling efficiency and load balance. This feature is currently experimental. It is not recommended to use it in production environments.

    [User document](https://docs.pingcap.com/tidb/stable/tune-region-performance#use-bucket-to-increase-concurrency), [#11515](https://github.com/tikv/tikv/issues/11515)

* Use Raft Engine as the default log storage engine

    Since v6.1.0, TiDB uses Raft Engine as the default storage engine for logs. Compared with RocksDB, Raft Engine can reduce TiKV I/O write traffic by up to 40% and CPU usage by 10%, while improving foreground throughput by about 5% and reducing tail latency by 20% under certain loads.

    [User document](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-engine), [#95](https://github.com/tikv/raft-engine/issues/95)

* Support the join order hint syntax

    * The `LEADING` hint reminds the optimizer to use the specified order as the prefix of join operations. A good prefix of join can quickly reduce the amount of data at the early phase of join and improve the query performance.
    * The `STRAIGHT_JOIN` hint reminds the optimizer to join tables in an order that is consistent with the order of tables in the `FROM` clause.

    This provides a method for you to fix the order of table joins. A proper use of the hints can effectively enhance the SQL performance and cluster stability.

    User document: [`LEADING`](https://docs.pingcap.com/tidb/stable/optimizer-hints#leadingt1_name--tl_name-), [`STRAIGHT_JOIN`](https://docs.pingcap.com/tidb/stable/optimizer-hints#straight_join), [#29932](https://github.com/pingcap/tidb/issues/29932)

* TiFlash supports four more functions:

    * `FROM_DAYS`
    * `TO_DAYS`
    * `TO_SECONDS`
    * `WEEKOFYEAR`

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations), [#4679](https://github.com/pingcap/tiflash/issues/4679), [#4678](https://github.com/pingcap/tiflash/issues/4678), [#4677](https://github.com/pingcap/tiflash/issues/4677)

* TiFlash supports partitioned tables in dynamic pruning mode.

    To enhance performance in OLAP scenarios, dynamic pruning mode is supported for partitioned tables. If your TiDB is upgraded from versions earlier than v6.0.0, it is recommended that you manually update statistics of existing partitioned tables, so as to maximize the performance (not required for new installations or new partitions created after upgrade to v6.1.0).

    User documents: [Access partitioned tables in the MPP mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#access-partitioned-tables-in-the-mpp-mode), [Dynamic pruning mode](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode), [#3873](https://github.com/pingcap/tiflash/issues/3873)
