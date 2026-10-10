# Compatibility and behavior changes in v8.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Compatibility changes | TiDB 8.0.0 Release Notes > Compatibility changes > Behavior changes | TiDB 8.0.0 Release Notes > Compatibility changes > MySQL compatibility`
- Source Line Ranges: `288-307`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `pd`, `sql`, `tidb`, `tiup`
- Topic Tags: `upgrade`, `compatibility-changes`, `behavior-changes`, `mysql-compatibility`, `prometheus`, `grafana`, `security-enhanced-mode`, `secret-key`, `ddl`, `indexing`, `partitioning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0580_af5d5a5dd1`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2954ee952ea498cfdde6108b84be56ffb184f1b23ae517d95b37799feb3da20e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 8.0.0 compatibility changes and behavior changes that affect upgrades from v7.6.0, TiUP defaults, DM secret key handling, SEM, DDL indexing, and MySQL compatibility.
- Retrieval Keywords: TiDB 8.0.0 Compatibility changes, upgrade from v7.6.0 to v8.0.0, TiUP Prometheus 2.49.1, TiUP Grafana 7.5.17, remove witness-related schedulers, Behavior changes, require_secure_transport, Security Enhanced Mode, SEM, DM removes the fixed secret key, Customize a Secret Key for DM Encryption and Decryption, data source configurations, migration task configurations, tidb_ddl_enable_fast_reorg, ADD INDEX, CREATE INDEX, tidb_ddl_reorg_worker_cnt, default value is 4, KEY partition type, empty list of partition fields, MySQL compatibility
- Follow-up Guidance: If encrypted passwords are used in DM data source configurations or migration task configurations before upgrade, the source says to refer to the upgrade steps in Customize a Secret Key for DM Encryption and Decryption for additional operations.
- Classification Note: This is a compatibility-change release section covering upgrade-impacting defaults, behavior changes, and MySQL compatibility in self-managed TiDB 8.0.0.

## Official Source Content

## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v7.6.0 to the current version (v8.0.0). If you are upgrading from v7.5.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.

- Upgrade the default Prometheus version deployed by TiUP from 2.27.1 to 2.49.1.
- Upgrade the default Grafana version deployed by TiUP from 7.5.11 to 7.5.17.
- Remove witness-related schedulers that are not GA but are enabled by default [#7765](https://github.com/tikv/pd/pull/7765) @[rleungx](https://github.com/rleungx)
### Behavior changes

* Prohibit setting [`require_secure_transport`](https://docs.pingcap.com/tidb/stable/system-variables#require_secure_transport-new-in-v610) to `ON` in Security Enhanced Mode (SEM) to prevent potential connectivity issues for users. [#47665](https://github.com/pingcap/tidb/issues/47665) @[tiancaiamao](https://github.com/tiancaiamao)
* DM removes the fixed secret key for encryption and decryption and enables you to customize a secret key for encryption and decryption. If encrypted passwords are used in [data source configurations](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file) and [migration task configurations](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) before the upgrade, you need to refer to the upgrade steps in [Customize a Secret Key for DM Encryption and Decryption](https://docs.pingcap.com/tidb/stable/dm/dm-customized-secret-key) for additional operations. [#9492](https://github.com/pingcap/tiflow/issues/9492) @[D3Hunter](https://github.com/D3Hunter)
* Before v8.0.0, after enabling the acceleration of `ADD INDEX` and `CREATE INDEX` (`tidb_ddl_enable_fast_reorg = ON`), the encoded index key ingests data to TiKV with a fixed concurrency of `16`, which cannot be dynamically adjusted according to the downstream TiKV capacity. Starting from v8.0.0, you can adjust the concurrency using the [`tidb_ddl_reorg_worker_cnt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_worker_cnt) system variable. The default value is `4`. Compared with the previous default value of `16`, the new default value reduces performance when ingesting indexed key-value pairs. You can adjust this system variable based on the workload of your cluster.
### MySQL compatibility

* The `KEY` partition type supports statements with an empty list of partition fields, which is consistent with the behavior of MySQL.
