# Preparation steps and TiUP upgrade methods

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-tidb-using-tiup.md`
- Source Title: `Upgrade TiDB Using TiUP`
- Source Heading Path: `Upgrade TiDB Using TiUP > Preparations | Upgrade TiDB Using TiUP > Preparations > Step 1: Review compatibility changes | Upgrade TiDB Using TiUP > Preparations > Step 2: Upgrade TiUP or TiUP offline mirror | Upgrade TiDB Using TiUP > Preparations > Step 2: Upgrade TiUP or TiUP offline mirror > Upgrade TiUP and TiUP Cluster | Upgrade TiDB Using TiUP > Preparations > Step 2: Upgrade TiUP or TiUP offline mirror > Upgrade TiUP offline mirror`
- Source Line Ranges: `69-148`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `preparation`, `release-notes`, `compatibility`, `tiup-upgrade`, `offline-mirror`, `control-machine`, `commands`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0531_84adcf33e6`
- Source ID: `tidb-docs-8.1:upgrade-tidb-using-tiup.md#preparations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e17144eb759902038ed55282b9526fdc147ca1756e02d47dbcfe83caabc84550`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#preparations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when preparing for a TiDB upgrade with TiUP, including reviewing release-note compatibility changes and upgrading TiUP, the TiUP Cluster component, or an offline mirror on the control machine.
- Retrieval Keywords: Preparations, Step 1: Review compatibility changes, Step 2: Upgrade TiUP or TiUP offline mirror, Upgrade TiUP and TiUP Cluster, Upgrade TiUP offline mirror, tiup update --self, tiup --version, tiup update cluster, tiup cluster --version, 1.11.3 or later, https://tiup-mirrors.pingcap.com, local_install.sh, source /home/tidb/.bash_profile, tiup mirror merge, rm -rf ~/.tiup/manifests/*, TiDB v8.1.0 compatibility changes, TiDB v8.1.1 compatibility changes, TiDB v8.1.2 release notes
- Follow-up Guidance: If the control machine cannot access https://tiup-mirrors.pingcap.com, the content directs readers to the offline mirror upgrade steps instead.
- Classification Note: This is classified as an operation chunk because it covers pre-upgrade preparation tasks and command-based upgrade methods for TiUP and offline mirrors.

## Official Source Content

## Preparations

This section introduces the preparation works needed before upgrading your TiDB cluster, including upgrading TiUP and the TiUP Cluster component.
### Step 1: Review compatibility changes

Review compatibility changes in TiDB release notes. If any changes affect your upgrade, take actions accordingly.

The following provides compatibility changes you need to know when you upgrade from v8.0.0 to the current version (v8.1.2). If you are upgrading from v7.6.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions in the corresponding [release notes](https://docs.pingcap.com/releases/tidb-self-managed/).

- TiDB v8.1.0 [compatibility changes](https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#compatibility-changes)
- TiDB v8.1.1 [compatibility changes](https://docs.pingcap.com/tidb/stable/releases/release-8.1.1#compatibility-changes)
- TiDB v8.1.2 [release notes](https://docs.pingcap.com/tidb/stable/releases/release-8.1.2)
### Step 2: Upgrade TiUP or TiUP offline mirror

Before upgrading your TiDB cluster, you first need to upgrade TiUP or TiUP mirror.
#### Upgrade TiUP and TiUP Cluster

> **Note:**
>
> If the control machine of the cluster to upgrade cannot access `https://tiup-mirrors.pingcap.com`, skip this section and see [Upgrade TiUP offline mirror](#upgrade-tiup-offline-mirror).

1. Upgrade the TiUP version. It is recommended that the TiUP version is `1.11.3` or later.

    ```shell
    tiup update --self
    tiup --version
    ```

2. Upgrade the TiUP Cluster version. It is recommended that the TiUP Cluster version is `1.11.3` or later.

    ```shell
    tiup update cluster
    tiup cluster --version
    ```
#### Upgrade TiUP offline mirror

> **Note:**
>
> If the cluster to upgrade was deployed not using the offline method, skip this step.

Refer to [Deploy a TiDB Cluster Using TiUP - Deploy TiUP offline](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#deploy-tiup-offline) to download the TiUP mirror of the new version and upload it to the control machine. After executing `local_install.sh`, TiUP will complete the overwrite upgrade.

```shell
tar xzvf tidb-community-server-${version}-linux-amd64.tar.gz
sh tidb-community-server-${version}-linux-amd64/local_install.sh
source /home/tidb/.bash_profile
```

After the overwrite upgrade, run the following command to merge the server and toolkit offline mirrors to the server directory:

```bash
tar xf tidb-community-toolkit-${version}-linux-amd64.tar.gz
ls -ld tidb-community-server-${version}-linux-amd64 tidb-community-toolkit-${version}-linux-amd64
cd tidb-community-server-${version}-linux-amd64/
cp -rp keys ~/.tiup/
tiup mirror merge ../tidb-community-toolkit-${version}-linux-amd64
```

After merging the mirrors, run the following command to upgrade the TiUP Cluster component:

```shell
tiup update cluster
```

Now, the offline mirror has been upgraded successfully. If an error occurs during TiUP operation after the overwriting, it might be that the `manifest` is not updated. You can try `rm -rf ~/.tiup/manifests/*` before running TiUP again.
