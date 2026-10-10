# Bug fixes across TiFlash, TiCDC, BR, Binlog, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.4.md`
- Source Title: `TiDB 5.1.4 Release Notes`
- Source Heading Path: `TiDB 5.1.4 Release Notes > Bug fixes`
- Source Line Ranges: `121-178`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `lightning`, `ticdc`, `tiflash`, `tidb`, `tikv`, `pd`
- Topic Tags: `bug-fixes`, `tiflash`, `ticdc`, `br`, `binlog`, `lightning`, `data-consistency`, `memory-leak`, `replication`, `restore`, `kafka`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0234_cb954a4160`
- Source ID: `tidb-docs-8.1:releases/release-5.1.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63a1c234239939f143ee3426d1b0af7b2de809e959ca704907988227cf1f8f78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.4.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 5.1.4 bug fixes related to TiFlash query behavior and crashes, TiCDC replication and Kafka issues, BR restore distribution, TiDB Binlog CSV import errors, or TiDB Lightning S3 path error reporting.
- Retrieval Keywords: TiDB 5.1.4 Release Notes bug fixes, str_to_date() leading zeros microseconds, unix_timestamp earlier than 1970-01-01 00:00:01 UTC, TiFlash memory limit enabled crash, EstablishMPPConnection error after restart, where <string> clause return wrong results, substringUTF8 3rd arguments of function must be constants, Unexpected type of column: Nullable(Nothing), CastStringAsDecimal inconsistent, castStringAsReal inconsistent, widening the primary key column when the primary key is handle, Can't compare DECIMAL overflow, TiCDC duplicated replace SQL batch-replace-enable disabled, cached region monitoring metric is negative, min.insync.replicas smaller than replication-factor, special comments in DDL statements cause the replication task to stop, stopped changefeeds resume automatically after a cluster upgrade, enable-old-value automatically set to true on the Canal protocol, changefeed checkpoint lag negative value, ErrGCTTLExceeded fail fast enough, Kafka max-message-bytes 10M, BR Regions unevenly distributed after restore, TiDB Binlog importing CSV InvalidRange strict-format true 256MB, TiDB Lightning S3 storage path does not exist does not report errors
- Follow-up Guidance: The source further lists specific fixed symptoms including TiCDC panic, deadlock, checkpoint, OOM, memory leak, default value replication, Avro JSON parsing, Kafka write error pauses, and TiFlash MPP stop panic issues.
- Classification Note: This is a release-notes bug-fix summary covering multiple shared components, with concrete issue descriptions and identifiers from TiFlash, TiCDC, BR, TiDB Binlog, and TiDB Lightning.

## Official Source Content

- Fix the issue that the `str_to_date()` function incorrectly handles leading zeros when parsing microseconds
    - Fix the TiFlash crash problem when the memory limit is enabled
    - Fix the issue that when an input time is earlier than 1970-01-01 00:00:01 UTC, the behavior of `unix_timestamp` is inconsistent with that of TiDB or MySQL
    - Fix the potential data inconsistency caused by widening the primary key column when the primary key is handle
    - Fix the overflow bug and the issue of reporting `Can't compare` error when comparing data in the `DECIMAL` data type
    - Fix the unexpected error of `3rd arguments of function substringUTF8 must be constants.`
    - Fix the issue that TiFlash fails to start on platforms without the `nsl` library
    - Fix the overflow bug when casting data to the `DECIMAL` data type
    - Fix the issue that the `castStringAsReal` behavior is inconsistent in TiFlash and in TiDB/TiKV
    - Fix the issue that TiFlash might return the `EstablishMPPConnection` error after it is restarted
    - Fix the issue that obsolete data cannot be reclaimed after setting the number of TiFlash replicas to 0
    - Fix the issue that the `CastStringAsDecimal` behavior is inconsistent in TiFlash and in TiDB/TiKV
    - Fix the issue that queries with the `where <string>` clause return wrong results
    - Fix the issue that TiFlash might panic when an MPP query is stopped
    - Fix the unexpected error of `Unexpected type of column: Nullable(Nothing)`

+ Tools

    + TiCDC

        - Fix a bug that MySQL sink generates duplicated `replace` SQL statements if `batch-replace-enable` is disabled [#4501](https://github.com/pingcap/tiflow/issues/4501)
        - Fix the issue that the `cached region` monitoring metric is negative [#4300](https://github.com/pingcap/tiflow/issues/4300)
        - Fix the issue that replication cannot be performed when `min.insync.replicas` is smaller than `replication-factor` [#3994](https://github.com/pingcap/tiflow/issues/3994)
        - Fix the potential panic issue that occurs when a replication task is removed [#3128](https://github.com/pingcap/tiflow/issues/3128)
        - Fix the issue of potential data loss caused by inaccurate checkpoint [#3545](https://github.com/pingcap/tiflow/issues/3545)
        - Fix the potential issue that the deadlock causes a replication task to get stuck [#4055](https://github.com/pingcap/tiflow/issues/4055)
        - Fix the issue that special comments in DDL statements cause the replication task to stop [#3755](https://github.com/pingcap/tiflow/issues/3755)
        - Fix a bug that EtcdWorker might hang the owner and processor [#3750](https://github.com/pingcap/tiflow/issues/3750)
        - Fix the issue that `stopped` changefeeds resume automatically after a cluster upgrade [#3473](https://github.com/pingcap/tiflow/issues/3473)
        - Fix the issue that default values cannot be replicated [#3793](https://github.com/pingcap/tiflow/issues/3793)
        - Fix data inconsistency caused by TiCDC default value padding exceptions [#3918](https://github.com/pingcap/tiflow/issues/3918) [#3929](https://github.com/pingcap/tiflow/issues/3929)
        - Fix a bug that an owner gets stuck when a PD leader shuts down and transfers to a new node [#3615](https://github.com/pingcap/tiflow/issues/3615)
        - Fix the TiCDC panic issue that occurs when manually cleaning the task status in etcd [#2980](https://github.com/pingcap/tiflow/issues/2980)
        - Fix the issue that the service cannot be started because of a timezone issue in the RHEL release [#3584](https://github.com/pingcap/tiflow/issues/3584)
        - Fix the issue of overly frequent warnings caused by MySQL sink deadlock [#2706](https://github.com/pingcap/tiflow/issues/2706)
        - Fix the bug that the `enable-old-value` configuration item is not automatically set to `true` on the Canal protocol [#3676](https://github.com/pingcap/tiflow/issues/3676)
        - Fix the issue that Avro sink does not support parsing JSON type columns [#3624](https://github.com/pingcap/tiflow/issues/3624)
        - Fix the negative value error in the changefeed checkpoint lag [#3010](https://github.com/pingcap/ticdc/issues/3010)
        - Fix the OOM issue in the container environment [#1798](https://github.com/pingcap/tiflow/issues/1798)
        - Fix the TiCDC replication interruption issue when multiple TiKVs crash or during a forced restart [#3288](https://github.com/pingcap/ticdc/issues/3288)
        - Fix the memory leak issue after processing DDLs [#3174](https://github.com/pingcap/ticdc/issues/3174)
        - Fix the issue that changefeed does not fail fast enough when the ErrGCTTLExceeded error occurs [#3111](https://github.com/pingcap/ticdc/issues/3111)
        - Fix the issue that TiCDC replication task might terminate when the upstream TiDB instance unexpectedly exits [#3061](https://github.com/pingcap/tiflow/issues/3061)
        - Fix the issue that TiCDC process might panic when TiKV sends duplicate requests to the same Region [#2386](https://github.com/pingcap/tiflow/issues/2386)
        - Fix the issue that Kafka may send excessively large messages by setting the default value of `max-message-bytes` to `10M` [#3081](https://github.com/pingcap/tiflow/issues/3081)
        - Fix the issue that TiCDC sync task might pause when an error occurs during writing a Kafka message [#2978](https://github.com/pingcap/tiflow/issues/2978)

    + Backup & Restore (BR)

        - Fix the potential issue that Regions might be unevenly distributed after a restore operation is finished [#30425](https://github.com/pingcap/tidb/issues/30425) [#31034](https://github.com/pingcap/tidb/issues/31034)

    + TiDB Binlog

        - Fix the issue that DBaaS importing CSV fails with InvalidRange if CSV file size is about 256MB and `strict-format` is `true` [#27763](https://github.com/pingcap/tidb/issues/27763)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning does not report errors when the S3 storage path does not exist [#28031](https://github.com/pingcap/tidb/issues/28031) [#30709](https://github.com/pingcap/tidb/issues/30709)
