# Upgrade from 5.x or 6.0 to 6.1 considerations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash-upgrade-guide.md`
- Source Title: `TiFlash Upgrade Guide`
- Source Heading Path: `TiFlash Upgrade Guide > From 5.x or v6.0 to v6.1 | TiFlash Upgrade Guide > From 5.x or v6.0 to v6.1 > TiFlash Proxy | TiFlash Upgrade Guide > From 5.x or v6.0 to v6.1 > Dynamic pruning`
- Source Line Ranges: `59-82`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tikv`, `tidb`
- Topic Tags: `upgrade`, `downgrade`, `proxy`, `rocksdb`, `dynamic-pruning`, `partitioned-tables`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0471_d31ac79d5c`
- Source ID: `tidb-docs-8.1:tiflash-upgrade-guide.md#from-5-x-or-v6-0-to-v6-1`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `52cdddb8813fbf94cf824b2a009f53131a42a4ba520d60e2e841184e3ab46f79`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash-upgrade-guide#from-5-x-or-v6-0-to-v6-1
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash-upgrade-guide.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiFlash-specific considerations when upgrading from v5.x or v6.0 to v6.1, especially TiFlash Proxy downgrade risks or dynamic pruning behavior after upgrade.
- Retrieval Keywords: From 5.x or v6.0 to v6.1, TiFlash Proxy, RocksDB version, data format is converted automatically, downgrade TiFlash from v6.1, fail to parse the new RocksDB configuration, TiFlash will fail to restart, dynamic pruning, tidb_partition_prune_mode, GlobalStats, partitioned tables
- Follow-up Guidance: For downgrade in testing or other special scenarios, the chunk says you can forcibly scale in the target TiFlash node and then replicate data from TiKV again, and for dynamic pruning details it refers to Dynamic pruning mode.
- Classification Note: This is classified as an operation chunk because it covers upgrade compatibility effects, downgrade implications, and post-upgrade behavior for TiFlash Proxy and dynamic pruning.

## Official Source Content

## From 5.x or v6.0 to v6.1

When you upgrade TiFlash from v5.x or v6.0 to v6.1, pay attention to the functional changes in TiFlash Proxy and dynamic pruning.
### TiFlash Proxy

TiFlash Proxy is upgraded in v6.1.0 (aligned with TiKV v6.0.0). The new version has upgraded the RocksDB version. After you upgrade TiFlash to v6.1, the data format is converted to the new version automatically.

In regular upgrades, the data conversion does not involve any risks. However, if you need to downgrade TiFlash from v6.1 to any earlier version in special scenarios (for example, testing or verification scenarios), the earlier version might fail to parse the new RocksDB configuration. As result, TiFlash will fail to restart. It is recommended that you fully test and verify the upgrade process and prepare an emergency plan.

**Workaround for downgrading TiFlash in testing or other special scenarios**

You can forcibly scale in the target TiFlash node and then replicate data from TiKV again. For detailed steps, see [Scale in a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-tiflash-cluster).
### Dynamic pruning

If you do not enable [dynamic pruning mode](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode) and will not use it in the future, you can skip this section.

- Newly installed TiDB v6.1.0: Dynamic pruning is enabled by default.

- TiDB v6.0 and earlier: Dynamic pruning is disabled by default. The setting of dynamic pruning after an upgrade inherits that of the previous version. That is, dynamic pruning will not be enabled (or disabled) automatically after an upgrade.

    After an upgrade, to enable dynamic pruning, set `tidb_partition_prune_mode` to `dynamic` and manually update GlobalStats of partitioned tables. For details, see [Dynamic pruning mode](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode).
