# Upgrade paths, warnings, and upgrade caveats

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-tidb-using-tiup.md`
- Source Title: `Upgrade TiDB Using TiUP`
- Source Heading Path: `Upgrade TiDB Using TiUP | Upgrade TiDB Using TiUP > Upgrade caveat`
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tiflash`, `ticdc`, `pd`, `tikv`, `shared`
- Topic Tags: `upgrade`, `compatibility`, `warnings`, `ddl`, `timeouts`, `offline-upgrade`, `online-upgrade`, `version-paths`, `rollback-limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0530_6327c06c32`
- Source ID: `tidb-docs-8.1:upgrade-tidb-using-tiup.md#upgrade-tidb-using-tiup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e9ed4c83b4a55fc2f212cad8eda94104c0994d67721fd8383e3f806839dace3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#upgrade-tidb-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when checking supported TiDB upgrade paths to 8.1 and reviewing upgrade warnings, DDL restrictions, startup timeout caveats, offline versus online upgrade limits, and rollback limitations for TiUP-managed self-managed clusters.
- Retrieval Keywords: Upgrade TiDB Using TiUP, Upgrade caveat, Upgrade from TiDB 4.0 versions to TiDB 8.1, Upgrade from TiDB 5.0-5.4 versions to TiDB 8.1, Upgrade from TiDB 6.0-6.6 to TiDB 8.1, Upgrade from TiDB 7.0-7.6 to TiDB 8.1, Upgrade from TiDB 8.0 to TiDB 8.1, TiFlash online upgrade earlier than 5.3 to 5.3 or later, DO NOT run DDL statements during the upgrade process, ADMIN SHOW DDL, ADMIN CANCEL DDL, server-version, performance.force-init-stats, SHOW CONFIG WHERE type = 'tidb' AND name = 'performance.force-init-stats';, --wait-timeout, init stats info time, performance.lite-init-stats, TiDB currently does not support version downgrade, Prometheus v2.27.1 time format change
- Follow-up Guidance: The content points to release notes for compatibility changes and to the section about fixing upgrades that get stuck when upgrading to v6.2.0 or later versions.
- Classification Note: This is classified as an operation chunk because it describes upgrade procedures, caveats, version-path constraints, and operational checks and command examples for TiUP-managed upgrades.

## Official Source Content

# Upgrade TiDB Using TiUP

This document is targeted for the following upgrade paths:

- Upgrade from TiDB 4.0 versions to TiDB 8.1.
- Upgrade from TiDB 5.0-5.4 versions to TiDB 8.1.
- Upgrade from TiDB 6.0-6.6 to TiDB 8.1.
- Upgrade from TiDB 7.0-7.6 to TiDB 8.1.
- Upgrade from TiDB 8.0 to TiDB 8.1.

> **Warning:**
>
> 1. You cannot upgrade TiFlash online from versions earlier than 5.3 to 5.3 or later. Instead, you must first stop all the TiFlash instances of the early version, and then upgrade the cluster offline. If other components (such as TiDB and TiKV) do not support an online upgrade, follow the instructions in warnings in [Online upgrade](#online-upgrade).
> 2. **DO NOT** run DDL statements during the upgrade process. Otherwise, the issue of undefined behavior might occur.
> 3. **DO NOT** upgrade a TiDB cluster when a DDL statement is being executed in the cluster (usually for the time-consuming DDL statements such as `ADD INDEX` and the column type changes). Before the upgrade, it is recommended to use the [`ADMIN SHOW DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) command to check whether the TiDB cluster has an ongoing DDL job. If the cluster has a DDL job, to upgrade the cluster, wait until the DDL execution is finished or use the [`ADMIN CANCEL DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) command to cancel the DDL job before you upgrade the cluster.
> 4. If the TiDB version before upgrade is 7.1.0 or later, you can ignore the preceding warnings 2 and 3. For more information, see [limitations on using TiDB smooth upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb#limitations).
> 5. Be sure to read [limitations on user operations](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb#limitations-on-user-operations) before upgrading your TiDB cluster using TiUP.

> **Note:**
>
> - If your cluster to be upgraded is v3.1 or an earlier version (v3.0 or v2.1), the direct upgrade to v8.1.0 or a later v8.1.x version is not supported. You need to upgrade your cluster first to v4.0 and then to the target TiDB version.
> - If your cluster to be upgraded is earlier than v6.2, the upgrade might get stuck when you upgrade the cluster to v6.2 or later versions in some scenarios. You can refer to [How to fix the issue](#how-to-fix-the-issue-that-the-upgrade-gets-stuck-when-upgrading-to-v620-or-later-versions).
> - TiDB nodes use the value of the [`server-version`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#server-version) configuration item to verify the current TiDB version. Therefore, to avoid unexpected behaviors, before upgrading the TiDB cluster, you need to set the value of `server-version` to empty or the real version of the current TiDB cluster.
> - Setting the [`performance.force-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#force-init-stats-new-in-v657-and-v710) configuration item to `ON` prolongs the TiDB startup time, which might cause startup timeouts and upgrade failures. To avoid this issue, it is recommended to set a longer waiting timeout for TiUP.
>     - Scenarios that might be affected:
>         - The original cluster version is earlier than v6.5.7 and v7.1.0 (which does not support `performance.force-init-stats` yet), and the target version is v7.2.0 or later.
>         - The original cluster version is equal to or later than v6.5.7 and v7.1.0, and the `performance.force-init-stats` configuration item is set to `ON`.
>
>     - Check the value of the `performance.force-init-stats` configuration item:
>
>         ```
>         SHOW CONFIG WHERE type = 'tidb' AND name = 'performance.force-init-stats';
>         ```
>
>     - You can increase the TiUP waiting timeout by adding the command-line option [`--wait-timeout`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#--wait-timeout). For example, execute the following command to set the waiting timeout to 1200 seconds (20 minutes).
>
>         ```shell
>         tiup update cluster --wait-timeout 1200 [other options]
>         ```
>
>         Generally, a 20-minute waiting timeout is sufficient for most scenarios. For a more precise estimate, search for `init stats info time` in the TiDB log to get the statistics loading time during the previous startup as a reference. For example:
>
>         ```
>         [domain.go:2271] ["init stats info time"] [lite=true] ["take time"=2.151333ms]
>         ```
>
>          If the original cluster is v7.1.0 or earlier, when upgrading to v7.2.0 or later, because of the introduction of [`performance.lite-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#lite-init-stats-new-in-v710), the statistics loading time is greatly reduced. In this case, the `init stats info time` before the upgrade is longer than the loading time after the upgrade.
>     - If you want to shorten the rolling upgrade duration of TiDB and the potential performance impact of missing initial statistical information during the upgrade is acceptable for your cluster, you can set `performance.force-init-stats` to `OFF` before the upgrade by [modifying the configuration of the target instance with TiUP](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration). After the upgrade is completed, you can reassess and revert this setting if necessary.
## Upgrade caveat

- TiDB currently does not support version downgrade or rolling back to an earlier version after the upgrade.
- For the v4.0 cluster managed using TiDB Ansible, you need to import the cluster to TiUP (`tiup cluster`) for new management according to [Upgrade TiDB Using TiUP (v4.0)](https://docs.pingcap.com/tidb/v4.0/upgrade-tidb-using-tiup#import-tidb-ansible-and-the-inventoryini-configuration-to-tiup). Then you can upgrade the cluster to v8.1.2 according to this document.
- To update versions earlier than v3.0 to v8.1.2:
    1. Update this version to 3.0 using [TiDB Ansible](https://docs.pingcap.com/tidb/v3.0/upgrade-tidb-using-ansible).
    2. Use TiUP (`tiup cluster`) to import the TiDB Ansible configuration.
    3. Update the 3.0 version to 4.0 according to [Upgrade TiDB Using TiUP (v4.0)](https://docs.pingcap.com/tidb/v4.0/upgrade-tidb-using-tiup#import-tidb-ansible-and-the-inventoryini-configuration-to-tiup).
    4. Upgrade the cluster to v8.1.2 according to this document.
- Support upgrading the versions of TiDB Binlog, TiCDC, TiFlash, and other components.
- When upgrading TiFlash from versions earlier than v6.3.0 to v6.3.0 and later versions, note that the CPU must support the AVX2 instruction set under the Linux AMD64 architecture and the ARMv8 instruction set architecture under the Linux ARM64 architecture. For details, see the description in [v6.3.0 Release Notes](https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#others).
- For detailed compatibility changes of different versions, see the [Release Notes](https://docs.pingcap.com/releases/tidb-self-managed/) of each version. Modify your cluster configuration according to the "Compatibility Changes" section of the corresponding release notes.
- When updating clusters from versions earlier than v5.3 to v5.3 or later versions, note that there is a time format change in the alerts generated by the default deployed Prometheus. This format change is introduced starting from Prometheus v2.27.1. For more information, see [Prometheus commit](https://github.com/prometheus/prometheus/commit/7646cbca328278585be15fa615e22f2a50b47d06).
