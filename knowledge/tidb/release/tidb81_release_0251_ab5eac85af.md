# Bug fixes for TiCDC and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.4.md`
- Source Title: `TiDB 5.2.4 Release Notes`
- Source Heading Path: `TiDB 5.2.4 Release Notes > Bug fixes`
- Source Line Ranges: `168-202`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `lightning`, `pd`
- Topic Tags: `bug-fixes`, `replication`, `changefeed`, `sink`, `metrics`, `checkpoint`, `memory`, `panic`, `lightning-import`, `checksum`, `s3`, `gcs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0251_ab5eac85af`
- Source ID: `tidb-docs-8.1:releases/release-5.2.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cfce5918d072ce25725997314e31da7c6d8fd4560bcdf233ecd14906f243578d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.2.4 bug fixes in TiCDC or TiDB Lightning involving replication, changefeed, sink behavior, metrics, checkpoint lag, panic, memory, checksum, S3, or GCS issues.
- Retrieval Keywords: TiDB 5.2.4 Release Notes, Bug fixes, TiCDC, TiDB Lightning, default values cannot be replicated, sequence is incorrectly replicated, TiCDC node exits abnormally when a PD leader is killed, MySQL sink duplicated `replace` SQL statements, `batch-replace-enable`, panic and data inconsistency when outputting the default column value, `mq sink write row` does not have monitoring data, `min.insync.replicas`, `replication-factor`, potential data loss caused by inaccurate checkpoint, deadlock causes a replication task to get stuck, HTTP API panics when the required processor information does not exist, special comments in DDL statements cause the replication task to stop, `config.Metadata.Timeout`, `stopped` changefeeds resume automatically after a cluster upgrade, `enable-old-value`, Canal protocol, Avro sink does not support parsing JSON type columns, negative value error in the changefeed checkpoint lag, OOM issue in the container environment, memory leak after processing DDLs, querying status through open API may be blocked when the PD node is abnormal, incorrect metrics caused by owner changes, Unified Sorter workerpool, `cached region` monitoring metric is negative, wrong import result when TiDB Lightning does not have the privilege to access the `mysql.tidb` table, checksum error `GC life time is shorter than transaction duration`, TiDB Lightning may not delete the metadata schema, S3 storage path does not exist, iterating more than 1000 keys on GCS
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note because it lists official bug fixes in TiCDC and TiDB Lightning for TiDB 5.2.4.

## Official Source Content

- Fix the issue that default values cannot be replicated [#3793](https://github.com/pingcap/tiflow/issues/3793)
        - Fix a bug that sequence is incorrectly replicated in some cases [#4552](https://github.com/pingcap/tiflow/issues/4552)
        - Fix a bug that a TiCDC node exits abnormally when a PD leader is killed [#4248](https://github.com/pingcap/tiflow/issues/4248)
        - Fix a bug that MySQL sink generates duplicated `replace` SQL statements when `batch-replace-enable` is disabled [#4501](https://github.com/pingcap/tiflow/issues/4501)
        - Fix the issue of panic and data inconsistency that occurs when outputting the default column value [#3929](https://github.com/pingcap/tiflow/issues/3929)
        - Fix the issue that `mq sink write row` does not have monitoring data [#3431](https://github.com/pingcap/tiflow/issues/3431)
        - Fix the issue that replication cannot be performed when `min.insync.replicas` is smaller than `replication-factor` [#3994](https://github.com/pingcap/tiflow/issues/3994)
        - Fix the potential panic issue that occurs when a replication task is removed [#3128](https://github.com/pingcap/tiflow/issues/3128)
        - Fix the bug that HTTP API panics when the required processor information does not exist [#3840](https://github.com/pingcap/tiflow/issues/3840)
        - Fix the issue of potential data loss caused by inaccurate checkpoint [#3545](https://github.com/pingcap/tiflow/issues/3545)
        - Fix the potential issue that the deadlock causes a replication task to get stuck [#4055](https://github.com/pingcap/tiflow/issues/4055)
        - Fix the TiCDC panic issue that occurs when manually cleaning the task status in etcd [#2980](https://github.com/pingcap/tiflow/issues/2980)
        - Fix the issue that special comments in DDL statements cause the replication task to stop [#3755](https://github.com/pingcap/tiflow/issues/3755)
        - Fix the issue of replication stop caused by the incorrect configuration of `config.Metadata.Timeout` [#3352](https://github.com/pingcap/tiflow/issues/3352)
        - Fix the issue that the service cannot be started because of a timezone issue in the RHEL release [#3584](https://github.com/pingcap/tiflow/issues/3584)
        - Fix the issue that `stopped` changefeeds resume automatically after a cluster upgrade [#3473](https://github.com/pingcap/tiflow/issues/3473)
        - Fix the issue of overly frequent warnings caused by MySQL sink deadlock [#2706](https://github.com/pingcap/tiflow/issues/2706)
        - Fix the bug that the `enable-old-value` configuration item is not automatically set to `true` on the Canal protocol [#3676](https://github.com/pingcap/tiflow/issues/3676)
        - Fix the issue that Avro sink does not support parsing JSON type columns [#3624](https://github.com/pingcap/tiflow/issues/3624)
        - Fix the negative value error in the changefeed checkpoint lag [#3010](https://github.com/pingcap/tiflow/issues/3010)
        - Fix the OOM issue in the container environment [#1798](https://github.com/pingcap/tiflow/issues/1798)
        - Fix the memory leak issue after processing DDLs [#3174](https://github.com/pingcap/tiflow/issues/3174)
        - Fix the issue that changefeed gets stuck when tables are repeatedly scheduled in the same node [#4464](https://github.com/pingcap/tiflow/issues/4464)
        - Fix a bug that querying status through open API may be blocked when the PD node is abnormal [#4778](https://github.com/pingcap/tiflow/issues/4778)
        - Fix incorrect metrics caused by owner changes [#4774](https://github.com/pingcap/tiflow/issues/4774)
        - Fix a stability problem in workerpool used by Unified Sorter [#4447](https://github.com/pingcap/tiflow/issues/4447)
        - Fix the issue that the `cached region` monitoring metric is negative [#4300](https://github.com/pingcap/tiflow/issues/4300)

    + TiDB Lightning

        - Fix the issue of wrong import result that occurs when TiDB Lightning does not have the privilege to access the `mysql.tidb` table [#31088](https://github.com/pingcap/tidb/issues/31088)
        - Fix the checksum error "GC life time is shorter than transaction duration" [#32733](https://github.com/pingcap/tidb/issues/32733)
        - Fix a bug that TiDB Lightning may not delete the metadata schema when some import tasks do not contain source files [#28144](https://github.com/pingcap/tidb/issues/28144)
        - Fix the issue that TiDB Lightning does not report errors when the S3 storage path does not exist [#28031](https://github.com/pingcap/tidb/issues/28031) [#30709](https://github.com/pingcap/tidb/issues/30709)
        - Fix an error that occurs when iterating more than 1000 keys on GCS [#30377](https://github.com/pingcap/tidb/issues/30377)
