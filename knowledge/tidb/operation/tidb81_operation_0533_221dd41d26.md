# Upgrade cluster online or offline and verify version

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-tidb-using-tiup.md`
- Source Title: `Upgrade TiDB Using TiUP`
- Source Heading Path: `Upgrade TiDB Using TiUP > Upgrade the TiDB cluster | Upgrade TiDB Using TiUP > Upgrade the TiDB cluster > Upgrade the TiDB cluster to a specified version | Upgrade TiDB Using TiUP > Upgrade the TiDB cluster > Upgrade the TiDB cluster to a specified version > Online upgrade | Upgrade TiDB Using TiUP > Upgrade the TiDB cluster > Upgrade the TiDB cluster to a specified version > Specify the component version during upgrade | Upgrade TiDB Using TiUP > Upgrade the TiDB cluster > Upgrade the TiDB cluster to a specified version > Offline upgrade | Upgrade TiDB Using TiUP > Upgrade the TiDB cluster > Verify the cluster version`
- Source Line Ranges: `200-304`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`, `dashboard`, `tiproxy`, `shared`
- Topic Tags: `upgrade`, `online-upgrade`, `offline-upgrade`, `version-pinning`, `leader-eviction`, `restart`, `verification`, `mixed-version`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0533_221dd41d26`
- Source ID: `tidb-docs-8.1:upgrade-tidb-using-tiup.md#upgrade-the-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `275e65f82de0cd0c6b34dc17460e7f74c0387bff5dc14b70acc278eae846e522`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#upgrade-the-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP commands and notes for online or offline cluster upgrade, component version pinning during upgrade, and post-upgrade version verification.
- Retrieval Keywords: tiup cluster upgrade <cluster-name> <version>, tiup cluster upgrade <cluster-name> v8.1.2, online upgrade, offline upgrade, --offline, tiup cluster stop <cluster-name>, tiup cluster start <cluster-name>, tiup cluster display <cluster-name>, Cluster version: v8.1.2, --force, --transfer-timeout, Specify the component version during upgrade, tiup cluster upgrade -h | grep "version", --pd-version, --tidb-dashboard-version, --tiflash-version, --tikv-version, --tiproxy-version, mixed-version deployment scenario
- Follow-up Guidance: It also includes the `display` command output example used to verify the resulting `Cluster version` after the upgrade.
- Classification Note: This is classified as an operation chunk because the content defines the upgrade procedures, command options, and verification steps for upgrading a TiDB cluster with TiUP.

## Official Source Content

## Upgrade the TiDB cluster

This section describes how to upgrade the TiDB cluster and verify the version after the upgrade.
### Upgrade the TiDB cluster to a specified version

You can upgrade your cluster in one of the two ways: online upgrade and offline upgrade.

By default, TiUP Cluster upgrades the TiDB cluster using the online method, which means that the TiDB cluster can still provide services during the upgrade process. With the online method, the leaders are migrated one by one on each node before the upgrade and restart. Therefore, for a large-scale cluster, it takes a long time to complete the entire upgrade operation.

If your application has a maintenance window for the database to be stopped for maintenance, you can use the offline upgrade method to quickly perform the upgrade operation.
#### Online upgrade

```shell
tiup cluster upgrade <cluster-name> <version>
```

For example, if you want to upgrade the cluster to v8.1.2:

```shell
tiup cluster upgrade <cluster-name> v8.1.2
```

> **Note:**
>
> + An online upgrade upgrades all components one by one. During the upgrade of TiKV, all leaders in a TiKV instance are evicted before stopping the instance. The default timeout time is 5 minutes (300 seconds). The instance is directly stopped after this timeout time.
>
> + You can use the `--force` parameter to upgrade the cluster immediately without evicting the leader. However, the errors that occur during the upgrade will be ignored, which means that you are not notified of any upgrade failure. Therefore, use the `--force` parameter with caution.
>
> + To keep a stable performance, make sure that all leaders in a TiKV instance are evicted before stopping the instance. You can set `--transfer-timeout` to a larger value, for example, `--transfer-timeout 3600` (unit: second).
>
> + To upgrade TiFlash from versions earlier than v5.3.0 to v5.3.0 or later, you must stop TiFlash and then upgrade it, and the TiUP version must be earlier than v1.12.0. For more information, see [Upgrade TiFlash using TiUP](https://docs.pingcap.com/tidb/stable/tiflash-upgrade-guide#upgrade-tiflash-using-tiup).
>
> + Try to avoid creating a new clustered index table when you apply rolling updates to the clusters using TiDB Binlog.
#### Specify the component version during upgrade

Starting from tiup-cluster v1.14.0, you can specify certain components to a specific version during cluster upgrade. These components will remain at their fixed version in the subsequent upgrade unless you specify a different version.

> **Note:**
>
> For components that share a version number, such as TiDB, TiKV, PD, and TiCDC, there are no complete tests to ensure that they work properly in a mixed-version deployment scenario. Ensure that you use this section only in test environments, or with the help of [technical support](https://docs.pingcap.com/tidb/stable/support).

```shell
tiup cluster upgrade -h | grep "version"
      --alertmanager-version string        Fix the version of alertmanager and no longer follows the cluster version.
      --blackbox-exporter-version string   Fix the version of blackbox-exporter and no longer follows the cluster version.
      --cdc-version string                 Fix the version of cdc and no longer follows the cluster version.
      --ignore-version-check               Ignore checking if target version is bigger than current version.
      --node-exporter-version string       Fix the version of node-exporter and no longer follows the cluster version.
      --pd-version string                  Fix the version of pd and no longer follows the cluster version.
      --tidb-dashboard-version string      Fix the version of tidb-dashboard and no longer follows the cluster version.
      --tiflash-version string             Fix the version of tiflash and no longer follows the cluster version.
      --tikv-cdc-version string            Fix the version of tikv-cdc and no longer follows the cluster version.
      --tikv-version string                Fix the version of tikv and no longer follows the cluster version.
      --tiproxy-version string             Fix the version of tiproxy and no longer follows the cluster version.
```
#### Offline upgrade

1. Before the offline upgrade, you first need to stop the entire cluster.

    ```shell
    tiup cluster stop <cluster-name>
    ```

2. Use the `upgrade` command with the `--offline` option to perform the offline upgrade. Fill in the name of your cluster for `<cluster-name>` and the version to upgrade to for `<version>`, such as `v8.1.2`.

    ```shell
    tiup cluster upgrade <cluster-name> <version> --offline
    ```

3. After the upgrade, the cluster will not be automatically restarted. You need to use the `start` command to restart it.

    ```shell
    tiup cluster start <cluster-name>
    ```
### Verify the cluster version

Execute the `display` command to view the latest cluster version `TiDB Version`:

```shell
tiup cluster display <cluster-name>
```

```
Cluster type:       tidb
Cluster name:       <cluster-name>
Cluster version:    v8.1.2
```
