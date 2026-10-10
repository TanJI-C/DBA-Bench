# Bug fixes for TiFlash and data movement tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.1.md`
- Source Title: `TiDB 8.1.1 Release Notes`
- Source Heading Path: `TiDB 8.1.1 Release Notes > Bug fixes`
- Source Line Ranges: `162-210`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `pd`, `br`, `tidb`, `tikv`, `ticdc`, `dm`, `lightning`, `dumpling`
- Topic Tags: `bug-fixes`, `tiflash`, `network-partition`, `timeouts`, `crash`, `tls`, `ddl`, `fastscan`, `backup`, `restore`, `incremental-backup`, `log-backup`, `advancer-owner`, `changefeed`, `kafka`, `data-consistency`, `migration`, `replication`, `schema-tracker`, `export`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0605_4742a4eb3c`
- Source ID: `tidb-docs-8.1:releases/release-8.1.1.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `87d690040ca0304be9de7efe2a1bc1170df3b4d1e61efcf7adc5cf6ebe1c15c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 8.1.1 bug fixes for TiFlash or data movement tools involving read timeouts, crashes, TLS startup failures, backup and restore errors, TiCDC changefeed issues, DM replication problems, Dumpling export errors, or TiDB Binlog DDL-related errors.
- Retrieval Keywords: TiDB 8.1.1 bug fixes, TiFlash network partition read request timeout, TiFlash SUBSTRING_INDEX() crash, FastScan duplicate rows after BR or TiDB Lightning import, TiFlash panic after database deleted shortly after creation, SSL certificate configuration empty string incorrectly enables TLS, disaggregated storage and compute null values after adding non-null columns, RENAME TABLE ... TO ... partitioned table empty partitions across databases, query timeout on partitioned tables with empty partitions, late materialization column type mismatch, virtual generated columns incorrect results after late materialization, BR checkpoint backup Region leaders seeking interruptions, incremental backups scanning DDL jobs inefficiency, BR nested retries restore process error identification, transactional KV cluster empty EndKey restore failure, log backup paused after advancer owner migration, ADD INDEX incremental restore backfilling, MODIFY COLUMN incremental restore backfilling, PD connection failure log backup advancer owner panic, TiCDC Region changes downstream panic, TiCDC clustered index primary keys new collation disabled, checksum set to 0 after splitting UPDATE events, Changefeed repeatedly restarting data inconsistency multi-node UPDATE, Processor module stuck when downstream Kafka is inaccessible, DM SET statements MariaDB panic, go-mysql connection blocking, max-index-length data replication interrupted, schema tracker LIST partition tables DM errors, TiDB Lightning WARN log keyspace name, Dumpling exporting tables and views at the same time, TiDB Binlog data and columnID count not match, ADD COLUMN binlog enabled
- Follow-up Guidance: 
- Classification Note: The official content is a TiDB 8.1.1 release-notes bug-fix summary covering TiFlash and multiple tools including BR, TiCDC, DM, TiDB Lightning, Dumpling, and TiDB Binlog.

## Official Source Content

- Fix the issue that a network partition (network disconnection) between TiFlash and any PD might cause read request timeout errors [#9243](https://github.com/pingcap/tiflash/issues/9243) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that the `SUBSTRING_INDEX()` function might cause TiFlash to crash in some corner cases [#9116](https://github.com/pingcap/tiflash/issues/9116) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that a large number of duplicate rows might be read in FastScan mode after importing data via BR or TiDB Lightning [#9118](https://github.com/pingcap/tiflash/issues/9118) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that TiFlash might panic when a database is deleted shortly after creation [#9266](https://github.com/pingcap/tiflash/issues/9266) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that setting the SSL certificate configuration to an empty string in TiFlash incorrectly enables TLS and causes TiFlash to fail to start [#9235](https://github.com/pingcap/tiflash/issues/9235) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that in the disaggregated storage and compute architecture, null values might be incorrectly returned in queries after adding non-null columns in DDL operations [#9084](https://github.com/pingcap/tiflash/issues/9084) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that TiFlash might panic after executing `RENAME TABLE ... TO ...` on a partitioned table with empty partitions across databases [#9132](https://github.com/pingcap/tiflash/issues/9132) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue of query timeout when executing queries on partitioned tables that contain empty partitions [#9024](https://github.com/pingcap/tiflash/issues/9024) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that some queries might report a column type mismatch error after late materialization is enabled [#9175](https://github.com/pingcap/tiflash/issues/9175) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that queries with virtual generated columns might return incorrect results after late materialization is enabled [#9188](https://github.com/pingcap/tiflash/issues/9188) @[JinheLin](https://github.com/JinheLin)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the backup performance during checkpoint backups is affected due to interruptions in seeking Region leaders [#17168](https://github.com/tikv/tikv/issues/17168) @[Leavrth](https://github.com/Leavrth)
        - Fix the inefficiency issue in scanning DDL jobs during incremental backups [#54139](https://github.com/pingcap/tidb/issues/54139) @[3pointer](https://github.com/3pointer)
        - Fix the issue that BR fails to correctly identify errors due to multiple nested retries during the restore process [#54053](https://github.com/pingcap/tidb/issues/54053) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that BR fails to restore a transactional KV cluster due to an empty `EndKey` [#52574](https://github.com/pingcap/tidb/issues/52574) @[3pointer](https://github.com/3pointer)
        - Fix the issue that log backup might be paused after the advancer owner migration [#53561](https://github.com/pingcap/tidb/issues/53561) @[RidRisR](https://github.com/RidRisR)
        - Fix the issue that DDLs requiring backfilling, such as `ADD INDEX` and `MODIFY COLUMN`, might not be correctly recovered during incremental restore [#54426](https://github.com/pingcap/tidb/issues/54426) @[3pointer](https://github.com/3pointer)
        - Fix the issue that a PD connection failure could cause the TiDB instance where the log backup advancer owner is located to panic [#52597](https://github.com/pingcap/tidb/issues/52597) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Fix the issue that Region changes cause downstream panic [#17233](https://github.com/tikv/tikv/issues/17233) @[hicqu](https://github.com/hicqu)
        - Fix the issue that TiCDC fails to decode primary keys in clustered index tables correctly when the new collation is disabled in the upstream [#11371](https://github.com/pingcap/tiflow/issues/11371) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue that the checksum is not correctly set to `0` after splitting `UPDATE` events [#11402](https://github.com/pingcap/tiflow/issues/11402) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that data inconsistency might occur when restarting Changefeed repeatedly when performing a large number of `UPDATE` operations in a multi-node environment [#11219](https://github.com/pingcap/tiflow/issues/11219) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue that the Processor module might get stuck when the downstream Kafka is inaccessible [#11340](https://github.com/pingcap/tiflow/issues/11340) @[asddongmen](https://github.com/asddongmen)

    + TiDB Data Migration (DM)

        - Fix the issue that `SET` statements cause DM to panic during the migration of MariaDB data [#10206](https://github.com/pingcap/tiflow/issues/10206) @[dveeden](https://github.com/dveeden)
        - Fix the connection blocking issue by upgrading `go-mysql` [#11041](https://github.com/pingcap/tiflow/issues/11041) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that data replication is interrupted when the index length exceeds the default value of `max-index-length` [#11459](https://github.com/pingcap/tiflow/issues/11459) @[michaelmdeng](https://github.com/michaelmdeng)
        - Fix the issue that schema tracker incorrectly handles LIST partition tables, causing DM errors [#11408](https://github.com/pingcap/tiflow/issues/11408) @[lance6716](https://github.com/lance6716)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning outputs a confusing `WARN` log when it fails to obtain the keyspace name [#54232](https://github.com/pingcap/tidb/issues/54232) @[kennytm](https://github.com/kennytm)

    + Dumpling

        - Fix the issue that Dumpling reports an error when exporting tables and views at the same time [#53682](https://github.com/pingcap/tidb/issues/53682) @[tangenta](https://github.com/tangenta)

    + TiDB Binlog

        - Fix the issue that deleting rows during the execution of `ADD COLUMN` might report an error `data and columnID count not match` when TiDB Binlog is enabled [#53133](https://github.com/pingcap/tidb/issues/53133) @[tangenta](https://github.com/tangenta)
