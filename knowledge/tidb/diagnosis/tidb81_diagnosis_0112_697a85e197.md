# TiDB Binlog troubleshooting map

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map > 6. Ecosystem tools | TiDB Troubleshooting Map > 6. Ecosystem tools > 6.1 TiDB Binlog`
- Source Line Ranges: `398-469`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `binlog`, `pump`, `drainer`, `kafka`, `replication`, `downstream`, `upstream`, `ddl`, `dml`, `checkpoint`, `disk-space`, `panic`, `timezone`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0112_697a85e197`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#6-ecosystem-tools`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8204efc992719d7fd3ffd41de6ded9175e015b054676c5a2969cbf2345573dba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#6-ecosystem-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiDB Binlog Pump or Drainer symptoms such as no downstream writes, Kafka errors, upstream-downstream inconsistency, slow replication, disk-space errors, hung checkpoints, or component panics.
- Retrieval Keywords: TiDB Binlog, Pump/Drainer Status, Update Time, Binlog is not enabled, [binlog], sarama, EOF, [syncer.to] kafka-version, Message was too large, message.max.bytes, replica.fetch.max.bytes, fetch.message.max.bytes, inconsistent data in upstream and downstream, http://127.0.0.1:10080/info/all, ignore binlog, /etc/localtime, TZ environment variable, set @@global.explicit_defaults_for_timestamp=on;, slow replication, frequent DDL operations, no primary key and no unique index, no space left on device, fail to notify all living drainer, binlogctl, gen update sqls failed: table xxx: row data is corruption [], checkpoint is not updated, Drainer replication is hung
- Follow-up Guidance: The content includes concrete follow-up identifiers such as the status interface `http://127.0.0.1:10080/info/all`, the SQL statement `set @@global.explicit_defaults_for_timestamp=on;`, the Kafka size settings, and the `binlogctl` tool name.
- Classification Note: This is classified as diagnosis because the content is a troubleshooting map of TiDB Binlog failure symptoms, specific error strings, status indicators, and related configuration or state checks.

## Official Source Content

## 6. Ecosystem tools
### 6.1 TiDB Binlog

- 6.1.1 TiDB Binlog is a tool that collects changes from TiDB and provides backup and replication to downstream TiDB or MySQL platforms. For details, see [TiDB Binlog on GitHub](https://github.com/pingcap/tidb-binlog).

- 6.1.2 The `Update Time` in Pump/Drainer Status is updated normally, and no anomaly shows in the log, but no data is written to the downstream.

    - Binlog is not enabled in the TiDB configuration. Modify the `[binlog]` configuration in TiDB.

- 6.1.3 `sarama` in Drainer reports the `EOF` error.

    - The Kafka client version in Drainer is inconsistent with the version of Kafka. You need to modify the `[syncer.to] kafka-version` configuration.

- 6.1.4 Drainer fails to write to Kafka and panics, and Kafka reports the `Message was too large` error.

    - The binlog data is too large, so the single message written to Kafka is too large. You need to modify the following configuration of Kafka:

        ```properties
        message.max.bytes=1073741824
        replica.fetch.max.bytes=1073741824
        fetch.message.max.bytes=1073741824
        ```

        For details, see [case-789](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case789.md) in Chinese.

- 6.1.5 Inconsistent data in upstream and downstream

    - Some TiDB nodes do not enable binlog. For v3.0.6 or later versions, you can check the binlog status of all the nodes by accessing the <http://127.0.0.1:10080/info/all> interface. For versions earlier than v3.0.6, you can check the binlog status by viewing the configuration file.

    - Some TiDB nodes go into the `ignore binlog` status. For v3.0.6 or later versions, you can check the binlog status of all the nodes by accessing the <http://127.0.0.1:10080/info/all> interface. For versions earlier than v3.0.6, check the TiDB log to see whether it contains the `ignore binlog` keyword.

    - The value of the timestamp column is inconsistent in upstream and downstream.

        - This is caused by different time zones. You need to ensure that Drainer is in the same time zone as the upstream and downstream databases. Drainer obtains its time zone from `/etc/localtime` and does not support the `TZ` environment variable. See [case-826](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case826.md) in Chinese.

        - In TiDB, the default value of timestamp is `null`, but the same default value in MySQL 5.7 (not including MySQL 8) is the current time. Therefore, when the timestamp in upstream TiDB is `null` and the downstream is MySQL 5.7, the data in the timestamp column is inconsistent. You need to run `set @@global.explicit_defaults_for_timestamp=on;` in the upstream before enabling binlog.

    - For other situations, [report a bug](https://github.com/pingcap/tidb-binlog/issues/new?labels=bug&template=bug-report.md).

- 6.1.6 Slow replication

    - The downstream is TiDB/MySQL, and the upstream performs frequent DDL operations. See [case-1023](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case1023.md) in Chinese.

    - The downstream is TiDB/MySQL, and the table to be replicated has no primary key and no unique index, which causes reduced performance in binlog. It is recommended to add the primary key or unique index.

    - If the downstream outputs to files, check whether the output disk or network disk is slow.

    - For other situations, [report a bug](https://github.com/pingcap/tidb-binlog/issues/new?labels=bug&template=bug-report.md).

- 6.1.7 Pump cannot write binlog and reports the `no space left on device` error.

    - The local disk space is insufficient for Pump to write binlog data normally. You need to clean up the disk space and then restart Pump.

- 6.1.8 Pump reports the `fail to notify all living drainer` error when it is started.

    - Cause: When Pump is started, it notifies all Drainer nodes that are in the `online` state. If it fails to notify Drainer, this error log is printed.

    - Solution: Use the binlogctl tool to check whether each Drainer node is normal or not. This is to ensure that all Drainer nodes in the `online` state are working normally. If the state of a Drainer node is not consistent with its actual working status, use the binlogctl tool to change its state and then restart Pump. See the case [fail-to-notify-all-living-drainer](https://docs.pingcap.com/tidb/stable/tidb-binlog/handle-tidb-binlog-errors#fail-to-notify-all-living-drainer-is-returned-when-pump-is-started).

- 6.1.9 Drainer reports the `gen update sqls failed: table xxx: row data is corruption []` error.

    - Trigger: The upstream performs DML operations on this table while performing `DROP COLUMN` DDL. This issue has been fixed in v3.0.6. See [case-820](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case820.md) in Chinese.

- 6.1.10 Drainer replication is hung. The process remains active but the checkpoint is not updated.

    - This issues has been fixed in v3.0.4. See [case-741](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case741.md) in Chinese.

- 6.1.11 Any component panics.

    - [Report a bug](https://github.com/pingcap/tidb-binlog/issues/new?labels=bug&template=bug-report.md).
