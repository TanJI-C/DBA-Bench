# Drainer, binlogctl, and main features

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-overview.md`
- Source Title: `TiDB Binlog Overview`
- Source Heading Path: `TiDB Binlog Cluster Overview > TiDB Binlog architecture > Drainer | TiDB Binlog Cluster Overview > TiDB Binlog architecture > `binlogctl` guide | TiDB Binlog Cluster Overview > Main features`
- Source Line Ranges: `35-55`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `sql`, `shared`
- Topic Tags: `drainer`, `binlogctl`, `replication`, `relay log`, `operations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0279_de8aae4c4e`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-overview.md#drainer`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d07a26d86098257a61bf9b3a8f06dd50515ec9c21c0c8806814a8da84e933ed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview#drainer
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about Drainer behavior, `binlogctl` capabilities, relay log support, or the main operational flow of TiDB Binlog components.
- Retrieval Keywords: Drainer, binlogctl, operations tool for TiDB Binlog, Obtaining the current `tso` of TiDB cluster, Checking the Pump/Drainer state, Modifying the Pump/Drainer state, Pausing or closing Pump/Drainer, relay log, Drainer ensures that the downstream clusters are in a consistent state, converts the binlog to SQL, replicates the data to a specific downstream platform, TiDB uses the built-in Pump Client
- Follow-up Guidance: The same source explains that multiple Pumps can scale out horizontally and that Drainer reads, merges, sorts, and sends binlogs downstream.
- Classification Note: This is classified as operation because the content focuses on Drainer processing, `binlogctl` operational functions, and runtime behavior such as state checks and relay log handling.

## Official Source Content

### Drainer

[Drainer](https://github.com/pingcap/tidb-binlog/tree/release-8.1/drainer) collects and merges binlogs from each Pump, converts the binlog to SQL or data of a specific format, and replicates the data to a specific downstream platform.
### `binlogctl` guide

[`binlogctl`](https://github.com/pingcap/tidb-binlog/tree/release-8.1/binlogctl) is an operations tool for TiDB Binlog with the following features:

* Obtaining the current `tso` of TiDB cluster
* Checking the Pump/Drainer state
* Modifying the Pump/Drainer state
* Pausing or closing Pump/Drainer
## Main features

* Multiple Pumps form a cluster which can scale out horizontally
* TiDB uses the built-in Pump Client to send the binlog to each Pump
* Pump stores binlogs and sends the binlogs to Drainer in order
* Drainer reads binlogs of each Pump, merges and sorts the binlogs, and sends the binlogs downstream
* Drainer supports [relay log](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-relay-log). By the relay log, Drainer ensures that the downstream clusters are in a consistent state.
