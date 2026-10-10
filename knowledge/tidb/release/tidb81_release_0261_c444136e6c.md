# TiDB 5.3.1 release overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.1.md`
- Source Title: `TiDB 5.3.1 Release Notes`
- Source Heading Path: `TiDB 5.3.1 Release Notes | TiDB 5.3.1 Release Notes > Compatibility changes | TiDB 5.3.1 Release Notes > Improvements`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `lightning`, `tidb`, `tikv`, `pd`, `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `improvements`, `login`, `gc`, `kafka`, `s3`, `monitoring`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0261_c444136e6c`
- Source ID: `tidb-docs-8.1:releases/release-5.3.1.md#tidb-5-3-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e88bd91efe41dde8e35524653655038650283bb6aa86d0e5e09ba294203757be`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.1#tidb-5-3-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.3.1 compatibility changes or improvement notes across TiDB, TiKV, PD, TiCDC, and TiDB Lightning.
- Retrieval Keywords: TiDB 5.3.1 Release Notes, Compatibility changes, Improvements, regionMaxKeyCount, TiDB Lightning, user login mode, MySQL-compatible logging, Garbage Collection GC, Raft logs, DR_STATE, TiCDC Kafka producer configurable, S3 backend storage pre-cleanup, Kafka Sink partition-num, max-message-bytes, Prometheus and Grafana monitoring metrics, no owner alert, mounter row, table sink total row, buffer sink total row
- Follow-up Guidance: The chunk also points to TiDB 5.3.1 bug fixes in the same release notes.
- Classification Note: This is a release-notes chunk summarizing compatibility changes and improvements introduced in TiDB 5.3.1 for multiple components.

## Official Source Content

# TiDB 5.3.1 Release Notes

Release Date: March 3, 2022

TiDB version: 5.3.1
## Compatibility changes

- Tools

    + TiDB Lightning

        - Change the default value of `regionMaxKeyCount` from 1_440_000 to 1_280_000, to avoid too many empty Regions after data import [#30018](https://github.com/pingcap/tidb/issues/30018)
## Improvements

- TiDB

    - Optimize the mapping logic of user login mode to make the logging more MySQL-compatible [#32648](https://github.com/pingcap/tidb/issues/32648)

- TiKV

    - Reduce the TiCDC recovery time by reducing the number of the Regions that require the Resolve Locks step [#11993](https://github.com/tikv/tikv/issues/11993)
    - Speed up the Garbage Collection (GC) process by increasing the write batch size when performing GC to Raft logs [#11404](https://github.com/tikv/tikv/issues/11404)
    - Update the proc filesystem (procfs) to v0.12.0 [#11702](https://github.com/tikv/tikv/issues/11702)

- PD

    - Optimize the content format of the `DR_STATE` file [#4341](https://github.com/tikv/pd/issues/4341)

- Tools

    - TiCDC

        - Expose configuration parameters of the Kafka producer to make them configurable in TiCDC [#4385](https://github.com/pingcap/tiflow/issues/4385)
        - Add a pre-cleanup process upon TiCDC startup if S3 is used as backend storage [#3878](https://github.com/pingcap/tiflow/issues/3878)
        - The TiCDC client works when no certificate name is specified [#3627](https://github.com/pingcap/tiflow/issues/3627)
        - Manage sink checkpoints per table to avoid unexpected advance of checkpoint timestamps [#3545](https://github.com/pingcap/tiflow/issues/3545)
        - Add the exponential backoff mechanism for restarting a changefeed. [#3329](https://github.com/pingcap/tiflow/issues/3329)
        - Change the default value of Kafka Sink `partition-num` to 3 so that TiCDC distributes messages across Kafka partitions more evenly [#3337](https://github.com/pingcap/tiflow/issues/3337)
        - Reduce the count of "EventFeed retry rate limited" logs [#4006](https://github.com/pingcap/tiflow/issues/4006)
        - Set the default value of `max-message-bytes` to 10M [#4041](https://github.com/pingcap/tiflow/issues/4041)
        - Add more Prometheus and Grafana monitoring metrics and alerts, including `no owner alert`, `mounter row`, `table sink total row`, and `buffer sink total row` [#4054](https://github.com/pingcap/tiflow/issues/4054) [#1606](https://github.com/pingcap/tiflow/issues/1606)
        - Reduce the time for the KV client to recover when a TiKV store is down [#3191](https://github.com/pingcap/tiflow/issues/3191)

    - TiDB Lightning

        - Refine the output message of the precheck to make it more user-friendly when the local disk space check fails [#30395](https://github.com/pingcap/tidb/issues/30395)
