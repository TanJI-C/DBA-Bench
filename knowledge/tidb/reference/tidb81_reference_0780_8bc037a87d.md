# TiDB Binlog notes and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-overview.md`
- Source Title: `TiDB Binlog Overview`
- Source Heading Path: `TiDB Binlog Cluster Overview > Notes`
- Source Line Ranges: `56-78`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `sql`, `shared`
- Topic Tags: `compatibility`, `clustered index`, `async commit`, `1pc`, `data recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0780_8bc037a87d`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-overview.md#notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `79243424d3efce957c4e49a9718f7f87bc5bf4e69aa0189dd1fbd374dcd1c5ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview#notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB Binlog compatibility notes, clustered index limitations, `tidb_enable_async_commit`, `tidb_enable_1pc`, supported Drainer destinations, or incremental recovery with `db-type` and Reparo.
- Retrieval Keywords: Notes, TiDB Binlog incompatibility, clustered index, TiDB Clustered Index, tidb_enable_clustered_index, tidb_enable_async_commit, tidb_enable_1pc, v5.1, Drainer supports replicating binlogs to MySQL, TiDB, Kafka or local files, db-type, db-type="file", db-type="pb", proto buffer format, Reparo, sync-diff-inspector, Binlog Consumer Client User Guide
- Follow-up Guidance: The source also states version-specific `db-type` values for incremental recovery and mentions using sync-diff-inspector to verify replicated data for MySQL, MariaDB, or another TiDB cluster downstream.
- Classification Note: This is classified as reference because the content is a notes section listing compatibility constraints, version-specific behavior, supported destinations, and related recovery and verification references.

## Official Source Content

## Notes

* In v5.1, the incompatibility between the clustered index feature introduced in v5.0 and TiDB Binlog has been resolved. After you upgrade TiDB Binlog and TiDB Server to v5.1 and enable TiDB Binlog, TiDB will support creating tables with clustered indexes; data insertion, deletion, and update on the created tables with clustered indexes will be replicated to the downstream via TiDB Binlog. When you use TiDB Binlog to replicate the tables with clustered indexes, pay attention to the following:

    - If you have upgraded the cluster to v5.1 from v5.0 by manually controlling the upgrade sequence, make sure that TiDB binlog is upgraded to v5.1 before upgrading the TiDB server to v5.1.
    - It is recommended to configure the system variable [`tidb_enable_clustered_index`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_clustered_index-new-in-v50) to a same value to ensure that the structure of TiDB clustered index tables between the upstream and downstream is consistent.

* TiDB Binlog is incompatible with the following features introduced in TiDB v5.0 and they cannot be used together.

    - [TiDB Clustered Index](https://docs.pingcap.com/tidb/stable/clustered-indexes#limitations): After TiDB Binlog is enabled, TiDB does not allow creating clustered indexes with non-single integer columns as primary keys; data insertion, deletion, and update of the created clustered index tables will not be replicated downstream via TiDB Binlog. If you need to replicate tables with clustered indexes, upgrade your cluster to v5.1 or use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) instead.
    - TiDB system variable [tidb_enable_async_commit](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_async_commit-new-in-v50): After TiDB Binlog is enabled, performance cannot be improved by enabling this option. It is recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) instead of TiDB Binlog.
    - TiDB system variable [tidb_enable_1pc](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_1pc-new-in-v50): After TiDB Binlog is enabled, performance cannot be improved by enabling this option. It is recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) instead of TiDB Binlog.

* Drainer supports replicating binlogs to MySQL, TiDB, Kafka or local files. If you need to replicate binlogs to other Drainer unsuppored destinations, you can set Drainer to replicate the binlog to Kafka and read the data in Kafka for customized processing according to binlog consumer protocol. See [Binlog Consumer Client User Guide](https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-consumer-client).

* To use TiDB Binlog for recovering incremental data, set the config `db-type` to `file` (local files in the proto buffer format). Drainer converts the binlog to data in the specified [proto buffer format](https://github.com/pingcap/tidb-binlog/blob/release-8.1/proto/pb_binlog.proto) and writes the data to local files. In this way, you can use [Reparo](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-reparo) to recover data incrementally.

    Pay attention to the value of `db-type`:

    - If your TiDB version is earlier than 2.1.9, set `db-type="pb"`.
    - If your TiDB version is 2.1.9 or later, set `db-type="file"` or `db-type="pb"`.

* If the downstream is MySQL, MariaDB, or another TiDB cluster, you can use [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) to verify the data after data replication.
