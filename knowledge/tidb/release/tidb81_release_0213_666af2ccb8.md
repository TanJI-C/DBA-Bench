# TiDB 5.0.4 feature enhancements and improvements across components

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.4.md`
- Source Title: `TiDB 5.0.4 Release Notes`
- Source Heading Path: `TiDB 5.0.4 Release Notes > Feature enhancements | TiDB 5.0.4 Release Notes > Improvements`
- Source Line Ranges: `38-106`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `dumpling`, `ticdc`
- Topic Tags: `release-notes`, `features`, `improvements`, `mpp`, `autoanalyze`, `dashboard-sso`, `grafana`, `backup`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0213_666af2ccb8`
- Source ID: `tidb-docs-8.1:releases/release-5.0.4.md#feature-enhancements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c3d6b1cb177ab603cddf28b94478495b33598006eb79dcda96208aa154b0f85d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.4#feature-enhancements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.0.4 feature enhancements and improvements across TiDB, TiKV, PD, TiFlash, Dumpling, and TiCDC.
- Retrieval Keywords: TiDB 5.0.4 feature enhancements, tidb_enforce_mpp=1, forcibly use the MPP mode, TiCDC configurations dynamically, OIDC-based SSO support for TiDB Dashboard, TiFlash HAVING() function in DAG requests, TiFlash DATE() function, Grafana panels for write throughput per instance, auto-analyze based on the histogram row count, stable result mode, init_connect system variable, COUNT(DISTINCT) pushed down in the MPP mode, aggregation function cannot be pushed down in EXPLAIN statements, TiFlashQueryTotalCounter error labels, MVCC data of a clustered index table through a secondary index by HTTP API, prepared statement memory allocation in parser, read ready and write ready separately, Resolved TS messages reduce network bandwidth, false "GC can not work" alert, restored always match the original cluster size during backup, Dumpling START TRANSACTION ... WITH CONSISTENT SNAPSHOT, SHOW CREATE TABLE syntax, TiCDC Unified Sorter memory management, Prohibit operating TiCDC clusters across major or minor versions, Remove file sorter, enable-old-value, PD endpoint misses the certificate, global gRPC connection pool
- Follow-up Guidance: The source groups the items into feature enhancements and improvements by component, including TiDB, TiKV, PD, TiFlash, Dumpling, and TiCDC.
- Classification Note: This is classified as a shared release note because it summarizes new capabilities and improvements spanning multiple TiDB ecosystem components rather than a single component only.

## Official Source Content

## Feature enhancements

+ TiDB

    - Support setting `tidb_enforce_mpp=1` to ignore the optimizer estimation and forcibly use the MPP mode [#26382](https://github.com/pingcap/tidb/pull/26382)

+ TiKV

    - Support changing TiCDC configurations dynamically [#10645](https://github.com/tikv/tikv/issues/10645)

+ PD

    - Add OIDC-based SSO support for TiDB Dashboard [#3884](https://github.com/tikv/pd/pull/3884)

+ TiFlash

    - Support the `HAVING()` function in DAG requests
    - Support the `DATE()` function
    - Add Grafana panels for write throughput per instance
## Improvements

+ TiDB

    - Trigger auto-analyze based on the histogram row count [#24237](https://github.com/pingcap/tidb/issues/24237)
    - Stop sending requests to a TiFlash node for a period if the node has failed and restarted before [#26757](https://github.com/pingcap/tidb/pull/26757)
    - Increase the `split region` upper limit to make `split table` and `presplit` more stable [#26657](https://github.com/pingcap/tidb/pull/26657)
    - Support retry for MPP queries [#26483](https://github.com/pingcap/tidb/pull/26483)
    - Check the availability of TiFlash before launching MPP queries [#1807](https://github.com/pingcap/tics/issues/1807)
    - Support the stable result mode to make the query result more stable [#26084](https://github.com/pingcap/tidb/pull/26084)
    - Support the MySQL system variable `init_connect` and its associated features [#18894](https://github.com/pingcap/tidb/issues/18894)
    - Thoroughly push down the `COUNT(DISTINCT)` aggregation function in the MPP mode [#25861](https://github.com/pingcap/tidb/pull/25861)
    - Print log warnings when the aggregation function cannot be pushed down in `EXPLAIN` statements [#25736](https://github.com/pingcap/tidb/pull/25736)
    - Add error labels for `TiFlashQueryTotalCounter` in Grafana dashboard [#25327](https://github.com/pingcap/tidb/pull/25327)
    - Support getting the MVCC data of a clustered index table through a secondary index by HTTP API [#24209](https://github.com/pingcap/tidb/issues/24209)
    - Optimize the memory allocation of `prepared` statement in parser [#24371](https://github.com/pingcap/tidb/pull/24371)

+ TiKV

    - Handle read ready and write ready separately to reduce read latency [#10475](https://github.com/tikv/tikv/issues/10475)
    - Reduce the size of Resolved TS messages to save network bandwidth [#2448](https://github.com/pingcap/tiflow/issues/2448)
    - Drop log instead of blocking threads when the slogger thread is overloaded and the queue is filled up [#10841](https://github.com/tikv/tikv/issues/10841)
    - Make the slow log of TiKV coprocessor only consider the time spent on processing requests [#10841](https://github.com/tikv/tikv/issues/10841)
    - Make prewrite as idempotent as possible to reduce the chance of undetermined errors [#10587](https://github.com/tikv/tikv/pull/10587)
    - Avoid the false "GC can not work" alert under low write flow [#10662](https://github.com/tikv/tikv/pull/10662)
    - Make the database to be restored always match the original cluster size during backup. [#10643](https://github.com/tikv/tikv/pull/10643)
    - Ensure that the panic output is flushed to the log [#9955](https://github.com/tikv/tikv/pull/9955)

+ PD

    - Improve the performance of synchronizing Region information between PDs [#3993](https://github.com/tikv/pd/pull/3993)

+ Tools

    + Dumpling

        - Support backing up MySQL-compatible databases that do not support the `START TRANSACTION ... WITH CONSISTENT SNAPSHOT` or the `SHOW CREATE TABLE` syntax [#309](https://github.com/pingcap/dumpling/issues/309)

    + TiCDC

        - Optimize memory management when Unified Sorter is using memory to sort [#2553](https://github.com/pingcap/tiflow/issues/2553)
        - Prohibit operating TiCDC clusters across major or minor versions [#2598](https://github.com/pingcap/tiflow/pull/2598)
        - Reduce the goroutine usage when a table's Regions are all transferred away from a TiKV node [#2284](https://github.com/pingcap/tiflow/issues/2284)
        - Remove `file sorter` [#2326](https://github.com/pingcap/tiflow/pull/2326)
        - Always pull the old values from TiKV and the output is adjusted according to `enable-old-value` [#2301](https://github.com/pingcap/tiflow/issues/2301)
        - Improve the error message returned when a PD endpoint misses the certificate [#1973](https://github.com/pingcap/tiflow/issues/1973)
        - Optimize workerpool for fewer goroutines when concurrency is high [#2211](https://github.com/pingcap/tiflow/issues/2211)
        - Add a global gRPC connection pool and share gRPC connections among KV clients [#2533](https://github.com/pingcap/tiflow/pull/2533)
