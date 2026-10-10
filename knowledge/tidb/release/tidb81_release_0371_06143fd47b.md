# 6.5.0 bug fixes across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.0.md`
- Source Title: `TiDB 6.5.0 Release Notes`
- Source Heading Path: `TiDB 6.5.0 Release Notes > Bug fixes`
- Source Line Ranges: `437-498`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`
- Topic Tags: `bug-fixes`, `upgrade`, `ddl`, `logging`, `execution-plan`, `collation`, `raft`, `log-backup`, `tls`, `s3-compatibility`, `changefeed`, `data-loss`, `replication`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0371_06143fd47b`
- Source ID: `tidb-docs-8.1:releases/release-6.5.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8635769c6558279efcc16eba19454aaf83f839700aaef4a21e8ab8c134127329`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching the TiDB 6.5.0 release notes for bug fixes across TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, or TiDB Lightning and for exact issue statements or identifiers.
- Retrieval Keywords: TiDB 6.5.0 Bug fixes, #38917 memory chunk misuse chunk reuse feature, #38766 tidb_constraint_check_in_place_pessimistic internal sessions global setting, #38894 AUTO_INCREMENT CHECK constraint, #38483 INSERT IGNORE INTO STRING auto-increment SMALLINT, #38932 renaming the partition column null pointer error, #38530 modifying the partition column DDL hang, #38980 ADMIN SHOW JOB panics after upgrading from v4.0.16 to v6.4.0, #39304 tidb_decode_key partitioned tables encoding, #38941 gRPC error logs log rotation, #39344 BEGIN SELECT FOR UPDATE point query TiKV read engine, #39266 StreamAgg TiFlash wrong results, #11119 Raft Engine ctl, #13515 Get raft db is not allowed compact raft tikv-ctl, #13867 log backup TLS enabled, #13651 Geometry field type, #13769 LIKE _ non-ASCII characters new collation, #13829 reset-to-version tikv-ctl terminated unexpectedly, #5701 balance-hot-region-scheduler configuration not persisted, #5698 rank-formula-version pre-upgrade configuration, #6159 delta layer compacted after restarting TiFlash, #6345 TiFlash File Open OPS too high, #38939 BR deletes log backup data mistakenly deletes data, #39150 restore tasks fail old framework for collations, #39545 Alibaba Cloud Huawei Cloud Amazon S3 storage compatibility, #7470 TiCDC stuck when PD leader crashes, #7682 DDL first then pausing and resuming the changefeed data loss, #7744 TiCDC mistakenly reports an error later version of TiFlash, #7706 sink component gets stuck downstream network unavailable, #7657 quickly deletes a replication task same task name data lost, #7037 task-mode:all GTID mode does not have any data, #7658 replicated for multiple times new DM worker scheduled, #7645 DM precheck regular expressions grant privileges, #39331 TiDB Lightning memory leakage huge source data file, #39476 TiDB Lightning cannot detect conflicts correctly importing data in parallel
- Follow-up Guidance: The chunk enumerates bug fixes by component and includes exact issue numbers and phrases for each fix in TiDB 6.5.0.
- Classification Note: This is classified as a release chunk because it is the Bug fixes section of the TiDB 6.5.0 release notes covering multiple components and tools.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue of memory chunk misuse for the chunk reuse feature that occurs in some cases [#38917](https://github.com/pingcap/tidb/issues/38917) @[keeplearning20221](https://github.com/keeplearning20221)
    - Fix the issue that the internal sessions of `tidb_constraint_check_in_place_pessimistic` might be affected by the global setting [#38766](https://github.com/pingcap/tidb/issues/38766) @[ekexium](https://github.com/ekexium)
    - Fix the issue that the `AUTO_INCREMENT` column cannot work with the `CHECK` constraint [#38894](https://github.com/pingcap/tidb/issues/38894) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that using `INSERT IGNORE INTO` to insert data of the `STRING` type into an auto-increment column of the `SMALLINT` type will cause an error [#38483](https://github.com/pingcap/tidb/issues/38483) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the null pointer error occurs in the operation of renaming the partition column of a partitioned table [#38932](https://github.com/pingcap/tidb/issues/38932) @[mjonss](https://github.com/mjonss)
    - Fix the issue that modifying the partition column of a partitioned table causes DDL to hang [#38530](https://github.com/pingcap/tidb/issues/38530) @[mjonss](https://github.com/mjonss)
    - Fix the issue that the `ADMIN SHOW JOB` operation panics after upgrading from v4.0.16 to v6.4.0 [#38980](https://github.com/pingcap/tidb/issues/38980) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the `tidb_decode_key` function fails to correctly parse the encoding of partitioned tables [#39304](https://github.com/pingcap/tidb/issues/39304) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that gRPC error logs are not redirected to the correct log file during log rotation [#38941](https://github.com/pingcap/tidb/issues/38941) @[xhebox](https://github.com/xhebox)
    - Fix the issue that TiDB generates an unexpected execution plan for the `BEGIN; SELECT... FOR UPDATE;` point query when TiKV is not configured as a read engine [#39344](https://github.com/pingcap/tidb/issues/39344) @[Yisaer](https://github.com/Yisaer)
    - Fix the issue that mistakenly pushing down `StreamAgg` to TiFlash causes wrong results [#39266](https://github.com/pingcap/tidb/issues/39266) @[fixdb](https://github.com/fixdb)

+ TiKV

    - Fix an error in Raft Engine ctl [#11119](https://github.com/tikv/tikv/issues/11119) @[tabokie](https://github.com/tabokie)
    - Fix the `Get raft db is not allowed` error when executing the `compact raft` command in tikv-ctl [#13515](https://github.com/tikv/tikv/issues/13515) @[guoxiangCN](https://github.com/guoxiangCN)
    - Fix the issue that log backup does not work when TLS is enabled [#13867](https://github.com/tikv/tikv/issues/13867) @[YuJuncen](https://github.com/YuJuncen)
    - Fix the support issue of the Geometry field type [#13651](https://github.com/tikv/tikv/issues/13651) @[dveeden](https://github.com/dveeden)
    - Fix the issue that `_` in the `LIKE` operator cannot match non-ASCII characters when new collation is not enabled [#13769](https://github.com/tikv/tikv/issues/13769) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that tikv-ctl is terminated unexpectedly when executing the `reset-to-version` command [#13829](https://github.com/tikv/tikv/issues/13829) @[tabokie](https://github.com/tabokie)

+ PD

    - Fix the issue that the `balance-hot-region-scheduler` configuration is not persisted if not modified [#5701](https://github.com/tikv/pd/issues/5701) @[HunDunDM](https://github.com/HunDunDM)
    - Fix the issue that `rank-formula-version` does not retain the pre-upgrade configuration during the upgrade process [#5698](https://github.com/tikv/pd/issues/5698) @[HunDunDM](https://github.com/HunDunDM)

+ TiFlash

    - Fix the issue that column files in the delta layer cannot be compacted after restarting TiFlash [#6159](https://github.com/pingcap/tiflash/issues/6159) @[lidezhu](https://github.com/lidezhu)
    - Fix the issue that TiFlash File Open OPS is too high [#6345](https://github.com/pingcap/tiflash/issues/6345) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that when BR deletes log backup data, it mistakenly deletes data that should not be deleted [#38939](https://github.com/pingcap/tidb/issues/38939) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that restore tasks fail when using old framework for collations in databases or tables [#39150](https://github.com/pingcap/tidb/issues/39150) @[MoCuishle28](https://github.com/MoCuishle28)
        - Fix the issue that backup fails because Alibaba Cloud and Huawei Cloud are not fully compatible with Amazon S3 storage [#39545](https://github.com/pingcap/tidb/issues/39545) @[3pointer](https://github.com/3pointer)

    + TiCDC

        - Fix the issue that TiCDC gets stuck when the PD leader crashes [#7470](https://github.com/pingcap/tiflow/issues/7470) @[zeminzhou](https://github.com/zeminzhou)
        - Fix data loss occurred in the scenario of executing DDL statements first and then pausing and resuming the changefeed [#7682](https://github.com/pingcap/tiflow/issues/7682) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that TiCDC mistakenly reports an error when there is a later version of TiFlash [#7744](https://github.com/pingcap/tiflow/issues/7744) @[overvenus](https://github.com/overvenus)
        - Fix the issue that the sink component gets stuck if the downstream network is unavailable [#7706](https://github.com/pingcap/tiflow/issues/7706) @[hicqu](https://github.com/hicqu)
        - Fix the issue that data is lost when a user quickly deletes a replication task and then creates another one with the same task name [#7657](https://github.com/pingcap/tiflow/issues/7657) @[overvenus](https://github.com/overvenus)

    + TiDB Data Migration (DM)

        - Fix the issue that a `task-mode:all` task cannot be started when the upstream database enables the GTID mode but does not have any data [#7037](https://github.com/pingcap/tiflow/issues/7037) @[liumengya94](https://github.com/liumengya94)
        - Fix the issue that data is replicated for multiple times when a new DM worker is scheduled before the existing worker exits [#7658](https://github.com/pingcap/tiflow/issues/7658) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that DM precheck is not passed when the upstream database uses regular expressions to grant privileges [#7645](https://github.com/pingcap/tiflow/issues/7645) @[lance6716](https://github.com/lance6716)

    + TiDB Lightning

        - Fix the memory leakage issue when TiDB Lightning imports a huge source data file [#39331](https://github.com/pingcap/tidb/issues/39331) @[dsdashun](https://github.com/dsdashun)
        - Fix the issue that TiDB Lightning cannot detect conflicts correctly when importing data in parallel [#39476](https://github.com/pingcap/tidb/issues/39476) @[dsdashun](https://github.com/dsdashun)
