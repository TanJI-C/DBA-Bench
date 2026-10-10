# Upgrade FAQ for resuming and stuck upgrades

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-tidb-using-tiup.md`
- Source Title: `Upgrade TiDB Using TiUP`
- Source Heading Path: `Upgrade TiDB Using TiUP > FAQ | Upgrade TiDB Using TiUP > FAQ > If an error occurs and the upgrade is interrupted, how to resume the upgrade after fixing this error? | Upgrade TiDB Using TiUP > FAQ > How to fix the issue that the upgrade gets stuck when upgrading to v6.2.0 or later versions?`
- Source Line Ranges: `305-354`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`
- Topic Tags: `faq`, `upgrade`, `resume`, `replay`, `audit`, `stuck-upgrade`, `ddl`, `plugin`, `restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0534_96c6c56330`
- Source ID: `tidb-docs-8.1:upgrade-tidb-using-tiup.md#faq`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6937c6d0ba420ee20bff173d7e6a2660dfdd68e35598433f002e936c0f456f8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when an upgrade was interrupted or got stuck and you need the documented TiUP retry commands or the listed stuck-upgrade scenarios for v6.2.0 or later.
- Retrieval Keywords: tiup cluster upgrade, tiup cluster audit, tiup cluster replay <audit-id>, resume the upgrade, failed upgrade operation record, upgrade gets stuck, v6.2.0 or later, concurrent DDL framework, plugin loading, kill -9, offline upgrade, DDL Owner change, restart the affected TiDB node
- Follow-up Guidance: It also explains that re-executing `tiup cluster upgrade` resumes the upgrade but restarts nodes that were previously upgraded, while `tiup cluster replay <audit-id>` retries the recorded failed operation.
- Classification Note: This is classified as an operation chunk because the FAQ provides concrete recovery and retry procedures for interrupted or stuck TiUP upgrade operations.

## Official Source Content

## FAQ

This section describes common problems encountered when updating the TiDB cluster using TiUP.
### If an error occurs and the upgrade is interrupted, how to resume the upgrade after fixing this error?

Re-execute the `tiup cluster upgrade` command to resume the upgrade. The upgrade operation restarts the nodes that have been previously upgraded. If you do not want the upgraded nodes to be restarted, use the `replay` sub-command to retry the operation:

1. Execute `tiup cluster audit` to see the operation records:

    ```shell
    tiup cluster audit
    ```

    Find the failed upgrade operation record and keep the ID of this operation record. The ID is the `<audit-id>` value in the next step.

2. Execute `tiup cluster replay <audit-id>` to retry the corresponding operation:

    ```shell
    tiup cluster replay <audit-id>
    ```
### How to fix the issue that the upgrade gets stuck when upgrading to v6.2.0 or later versions?

Starting from v6.2.0, TiDB enables the [concurrent DDL framework](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction#how-the-online-ddl-asynchronous-change-works-in-tidb) by default to execute concurrent DDLs. This framework changes the DDL job storage from a KV queue to a table queue. This change might cause the upgrade to get stuck in some scenarios. The following are some scenarios that might trigger this issue and the corresponding solutions:

- Upgrade gets stuck due to plugin loading

    During the upgrade, loading certain plugins that require executing DDL statements might cause the upgrade to get stuck.

    **Solution**: avoid loading plugins during the upgrade. Instead, load plugins only after the upgrade is completed.

- Upgrade gets stuck due to using the `kill -9` command for offline upgrade

    - Precautions: avoid using the `kill -9` command to perform the offline upgrade. If it is necessary, restart the new version TiDB node after 2 minutes.
    - If the upgrade is already stuck, restart the affected TiDB node. If the issue has just occurred, it is recommended to restart the node after 2 minutes.

- Upgrade gets stuck due to DDL Owner change

    In multi-instance scenarios, network or hardware failures might cause DDL Owner change. If there are unfinished DDL statements in the upgrade phase, the upgrade might get stuck.

    **Solution**:

    1. Terminate the stuck TiDB node (avoid using `kill -9`).
    2. Restart the new version TiDB node.
