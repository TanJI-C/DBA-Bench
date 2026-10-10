# TiFlash upgrade overview and TiUP procedure

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash-upgrade-guide.md`
- Source Title: `TiFlash Upgrade Guide`
- Source Heading Path: `TiFlash Upgrade Guide | TiFlash Upgrade Guide > Upgrade TiFlash using TiUP`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tiup`, `tidb`
- Topic Tags: `upgrade`, `tiup`, `prerequisites`, `offline-upgrade`, `version-compatibility`, `major-version`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0470_28f6cb4af4`
- Source ID: `tidb-docs-8.1:tiflash-upgrade-guide.md#tiflash-upgrade-guide`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fde3ca2a19b7a5e314905bf42014feaab160cc4fa99a776a612bb512f8470730`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash-upgrade-guide#tiflash-upgrade-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash-upgrade-guide.md

## Retrieval Guidance

- Use When: Use this chunk when asking about the TiFlash upgrade overview, major-version upgrade cautions, FastScan note, or the TiUP procedure for upgrading TiFlash from earlier than v5.3.0 to v5.3.0 or later.
- Retrieval Keywords: TiFlash Upgrade Guide, Upgrade TiFlash using TiUP, FastScan, major versions, v4.x to v5.x to v6.x, TiUP cluster version v1.12.0, tiup cluster:v1.11.3, tiup cluster stop <cluster-name> -R tiflash, tiup cluster upgrade <cluster-name> <version> --offline, tiup cluster reload <cluster-name>, offline upgrade
- Follow-up Guidance: The chunk points to the standard upgrade process documents: Upgrade TiDB Using TiUP and Upgrade TiDB on Kubernetes.
- Classification Note: This is classified as an operation chunk because the content describes upgrade prerequisites, version-specific cautions, and exact TiUP commands for stopping, upgrading, and reloading TiFlash.

## Official Source Content

# TiFlash Upgrade Guide

This document describes the function changes and recommended actions that you need to learn when you upgrade TiFlash.

To learn the standard upgrade process, see the following documents:

- [Upgrade TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup)
- [Upgrade TiDB on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/upgrade-a-tidb-cluster)

> **Note:**
>
> - [FastScan](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan) is introduced in v6.2.0 as an experimental feature and becomes generally available (GA) in v7.0.0. It provides more efficient query performance at the cost of strong data consistency.
>
> - It is not recommended that you upgrade TiDB that includes TiFlash across major versions, for example, from v4.x to v6.x. Instead, you need to upgrade from v4.x to v5.x first, and then to v6.x.
>
> - v4.x is near the end of its life cycle. It is recommended that you upgrade to v5.x or later as soon as possible. For more information, see [TiDB Release Support Policy](https://www.pingcap.com/tidb-release-support-policy/).
>
> - PingCAP does not provide bug fixes for non-LTS versions, such as v6.0. It is recommended that you upgrade to v6.1 and later LTS versions whenever possible.
>
## Upgrade TiFlash using TiUP

To upgrade TiFlash from versions earlier than v5.3.0 to v5.3.0 or later, you must stop TiFlash and then upgrade it. When you upgrade TiFlash using TiUP, note the following:

- If the TiUP cluster version is v1.12.0 or later, you cannot stop TiFlash and then upgrade it. If the target version requires a TiUP cluster version of v1.12.0 or later, it is recommended that you first use `tiup cluster:v1.11.3 <subcommand>` to upgrade TiFlash to an intermediate version, perform an online upgrade of the TiDB cluster, upgrade the TiUP version, and then upgrade the TiDB cluster to the target version directly without stopping it.
- If the TiUP cluster version is earlier than v1.12.0, perform the following steps to upgrade TiFlash.

The following steps help you use TiUP to upgrade TiFlash without interrupting other components:

1. Stop the TiFlash instance:

    ```shell
    tiup cluster stop <cluster-name> -R tiflash
    ```

2. Upgrade the TiDB cluster without restarting it (only updating the files):

    ```shell
    tiup cluster upgrade <cluster-name> <version> --offline 
    ```

    For example:

    ```shell
    tiup cluster upgrade <cluster-name> v5.3.0 --offline
    ```

3. Reload the TiDB cluster. After the reload, the TiFlash instance is started and you do not need to manually start it.

    ```shell
    tiup cluster reload <cluster-name>
    ```
