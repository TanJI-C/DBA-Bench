# TiDB 5.0.6 release date, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.6.md`
- Source Title: `TiDB 5.0.6 Release Notes`
- Source Heading Path: `TiDB 5.0.6 Release Notes | TiDB 5.0.6 Release Notes > Compatibility changes | TiDB 5.0.6 Release Notes > Improvements`
- Source Line Ranges: `6-59`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `ticdc`, `br`, `lightning`
- Topic Tags: `release-notes`, `compatibility`, `improvements`, `kafka`, `monitoring`, `scheduler`, `restore`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0217_e8642c6a34`
- Source ID: `tidb-docs-8.1:releases/release-5.0.6.md#tidb-5-0-6-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1ee8f4a49c922ee9132ef2968c50135cbd219ead640b7eb94f2218ab51f81505`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.6#tidb-5-0-6-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.0.6 release-note details about compatibility changes and improvements across TiCDC, TiDB, TiKV, PD, BR, and TiDB Lightning.
- Retrieval Keywords: TiDB 5.0.6 Release Notes, Release date December 31, 2021, Compatibility changes, Improvements, cdc server command error stdout stderr, Kafka sink max-message-bytes 10M, Kafka Sink partition-num 3, affected SQL statements debug log coprocessor lock, Import thread pool Apply thread pool SST files, Raft logs garbage collection metrics, Grafana dashboard uncommon storage-related metrics, scatter-range-scheduler, evict leader scheduler unhealthy peers, TiCDC gRPC congestion during changefeed initialization, EtcdWorker frequent etcd writes affecting PD services, config.Metadata.Timeout, Prometheus and Grafana monitoring metrics and alerts, no owner alert, mounter row, table sink total row, buffer sink total row, BR PD request error TiKV I/O timeout error, Improve the robustness of restoring, expression index, virtual generated columns
- Follow-up Guidance: The chunk also provides specific default-value changes for TiCDC Kafka sink settings and named monitoring metrics and alerts added in this release.
- Classification Note: This is a release-notes chunk because the official content lists TiDB 5.0.6 compatibility changes and improvements by component.

## Official Source Content

# TiDB 5.0.6 Release Notes

Release date: December 31, 2021

TiDB version: 5.0.6
## Compatibility changes

+ Tools

    + TiCDC

        - Change the output of the `cdc server` command error from stdout to stderr [#3133](https://github.com/pingcap/tiflow/issues/3133)
        - Set the default value of Kafka sink `max-message-bytes` to `10M` [#3081](https://github.com/pingcap/tiflow/issues/3081)
        - Change the default value of Kafka Sink `partition-num` to 3 so that TiCDC distributes messages across Kafka partitions more evenly [#3337](https://github.com/pingcap/ticdc/issues/3337)
## Improvements

+ TiDB

    - Show the affected SQL statements in the debug log when the coprocessor encounters a lock, which is helpful in diagnosing problems [#27718](https://github.com/pingcap/tidb/issues/27718)

+ TiKV

    - Increase the speed of inserting SST files by moving the verification process to the `Import` thread pool from the `Apply` thread pool [#11239](https://github.com/tikv/tikv/issues/11239)
    - Add more metrics for the garbage collection module of Raft logs to locate performance problems in the module [#11374](https://github.com/tikv/tikv/issues/11374)
    - Collapse some uncommon storage-related metrics in Grafana dashboard [#11681](https://github.com/tikv/tikv/issues/11681)

+ PD

    - Speed up the exit process of schedulers [#4146](https://github.com/tikv/pd/issues/4146)
    - Make the scheduling results of the `scatter-range-scheduler` scheduler more even by allowing the scheduler to schedule empty Regions and fix the configurations of the scheduler [#4497](https://github.com/tikv/pd/issues/4497)
    - Support that the evict leader scheduler can schedule Regions with unhealthy peers [#4093](https://github.com/tikv/pd/issues/4093)

+ Tools

    + TiCDC

        - Optimize rate limiting control on TiKV reloads to reduce gPRC congestion during changefeed initialization [#3110](https://github.com/pingcap/ticdc/issues/3110)
        - Add a tick frequency limit to EtcdWorker to prevent frequent etcd writes from affecting PD services [#3112](https://github.com/pingcap/ticdc/issues/3112)
        - Add the default configuration for `config.Metadata.Timeout` in Kafka sink [#3352](https://github.com/pingcap/tiflow/issues/3352)
        - Set the default value of `max-message-bytes` to `10M`, to reduce the probability that Kafka messages cannot be sent [#3081](https://github.com/pingcap/tiflow/issues/3081)
        - Add more Prometheus and Grafana monitoring metrics and alerts, including `no owner alert`, `mounter row`, `table sink total row`, and `buffer sink total row` [#4054](https://github.com/pingcap/tiflow/issues/4054) [#1606](https://github.com/pingcap/tiflow/issues/1606) 

    + Backup & Restore (BR)

        - Retry BR tasks when encountering the PD request error or the TiKV I/O timeout error [#27787](https://github.com/pingcap/tidb/issues/27787)
        - Improve the robustness of restoring [#27421](https://github.com/pingcap/tidb/issues/27421)

    + TiDB Lightning

        - Support importing data into tables that have expression index or the index that depends on virtual generated columns [#1404](https://github.com/pingcap/br/issues/1404)
