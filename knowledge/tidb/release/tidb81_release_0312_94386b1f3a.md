# TiDB 6.1.3 release overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.3.md`
- Source Title: `TiDB 6.1.3 Release Notes`
- Source Heading Path: `TiDB 6.1.3 Release Notes | TiDB 6.1.3 Release Notes > Compatibility changes | TiDB 6.1.3 Release Notes > Improvements`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `ticdc`, `tidb`
- Topic Tags: `release-notes`, `compatibility-changes`, `improvements`, `transaction-atomicity`, `changefeed`, `replication-latency`, `oom`, `lock-contention`, `heartbeat`, `kafka`, `go-compiler`, `gomemlimit`, `memory-usage`, `stability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0312_94386b1f3a`
- Source ID: `tidb-docs-8.1:releases/release-6.1.3.md#tidb-6-1-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d1b363137547cd7c4bc916e60202d3d097302ca38ac54690ac5f89f1c68df3b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.3#tidb-6-1-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving what changed in TiDB 6.1.3 around compatibility changes and performance or stability improvements for TiCDC, PD, and TiDB memory usage.
- Retrieval Keywords: TiDB 6.1.3 Release Notes, 6.1.3 compatibility changes, transaction-atomicity, default value from table to none, reduce replication latency, reduce OOM risks, single transaction exceeds 1024 rows, PD lock contention, processing heartbeat in high concurrency, TiCDC enable transaction split by default, disable the safe mode of a changefeed in TiCDC by default, Kafka protocol encoder, go1.19, GOMEMLIMIT, mitigate OOM issues, configure-memory-usage
- Follow-up Guidance: The content also points to the memory usage documentation for mitigating OOM issues by configuring `GOMEMLIMIT`.
- Classification Note: This is a release-notes overview chunk because it lists TiDB 6.1.3 compatibility changes and improvements across shared components rather than a single feature workflow.

## Official Source Content

# TiDB 6.1.3 Release Notes

Release date: December 5, 2022

TiDB version: 6.1.3

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.1/production-deployment-using-tiup)
## Compatibility changes

- Tools

    - TiCDC

        - Change the default value of [`transaction-atomicity`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#configure-sink-uri-for-mysql-or-tidb) from `table` to `none`, which helps reduce replication latency and reduce OOM risks, and ensures that only a few transactions (the size of a single transaction exceeds 1024 rows) are split, instead of all transactions [#7505](https://github.com/pingcap/tiflow/issues/7505) [#5231](https://github.com/pingcap/tiflow/issues/5231) @[asddongmen](https://github.com/asddongmen)
## Improvements

- PD

    - Optimize the granularity of locks to reduce lock contention and improve the capability of processing heartbeat in high concurrency [#5586](https://github.com/tikv/pd/issues/5586) @[rleungx](https://github.com/rleungx)

- Tools

    - TiCDC

        - Enable transaction split and disable the safe mode of a changefeed in TiCDC by default to improve performance [#7505](https://github.com/pingcap/tiflow/issues/7505) @[asddongmen](https://github.com/asddongmen)
        - Improve the performance of Kafka protocol encoder [#7540](https://github.com/pingcap/tiflow/issues/7540), [#7532](https://github.com/pingcap/tiflow/issues/7532), [#7543](https://github.com/pingcap/tiflow/issues/7543) @[sdojjy](https://github.com/sdojjy) @[3AceShowHand](https://github.com/3AceShowHand)

- Others

    - Upgrade the Go compiler version of TiDB from go1.18 to [go1.19](https://go.dev/doc/go1.19), which improves the TiDB stability. Specifically, a Go environment variable [`GOMEMLIMIT`](https://pkg.go.dev/runtime@go1.19#hdr-Environment_Variables) is introduced to keep the memory usage of TiDB below a certain threshold. This helps mitigate most OOM issues. For more information, see [Mitigate OOM issues by configuring the `GOMEMLIMIT`](https://docs.pingcap.com/tidb/stable/configure-memory-usage#mitigate-oom-issues-by-configuring-gomemlimit).
