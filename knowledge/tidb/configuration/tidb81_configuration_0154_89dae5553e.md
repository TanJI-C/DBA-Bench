# Enable Titan and convert existing data

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/storage-engine/titan-configuration.md`
- Source Title: `Titan Configuration`
- Source Heading Path: `Titan Configuration | Titan Configuration > Enable Titan | Titan Configuration > Data conversion`
- Source Line Ranges: `5-77`
- Source Scope: `all`
- Primary Component: `tikv`
- Related Components: `operator`, `tiup`, `br`, `lightning`
- Topic Tags: `titan`, `enablement`, `upgrade-behavior`, `data-conversion`, `compaction`, `rolling-restart`, `kubernetes`, `tiup`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0154_89dae5553e`
- Source ID: `tidb-docs-8.1:storage-engine/titan-configuration.md#titan-configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a33eaa5c87696d137d5b7de095602ef842f90845c79c1a7f3bcc7f8a3cf39920`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/storage-engine/titan-configuration#titan-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/storage-engine/titan-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about enabling Titan on TiKV, understanding upgrade-time default behavior, converting existing RocksDB data into Titan, or recognizing the startup error caused by disabling Titan after data has been moved.
- Retrieval Keywords: Titan Configuration, Enable Titan, Data conversion, rocksdb.titan.enabled, min-blob-size, tiup cluster edit-config ${cluster-name}, tiup cluster reload ${cluster-name} -R tikv, [rocksdb.titan] enabled = true, ${cluster_name}/tidb-cluster.yaml, kubectl apply -f ${cluster_name} -n ${namespace}, You have disabled titan when its data directory is not empty, TiKV Details > Titan kv > blob file size, tikv-ctl, manual compaction, BR snapshot/log, TiDB Lightning Physical Import Mode
- Follow-up Guidance: The chunk also points to Disable Titan for correct disablement and to manual compaction with tikv-ctl for speeding up RocksDB-to-Titan conversion.
- Classification Note: This is classified as configuration because the content explains how to enable Titan through TiUP, direct TiKV configuration, or TiDB Operator, and describes related conversion behavior and warnings.

## Official Source Content

# Titan Configuration

This document introduces how to enable and disable [Titan](https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview) using the corresponding configuration items, data conversion mechanism, the relevant parameters, and the Level Merge feature.
## Enable Titan

> **Note:**
>
> - Starting from TiDB v7.6.0, Titan is enabled by default for new clusters to enhance the performance of writing wide tables and JSON data. The default value of the [`min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size) threshold is changed from `1KB` to `32KB`.
> - Existing clusters upgraded to v7.6.0 or later versions retain the original configuration, which means that if Titan is not explicitly enabled, it still uses RocksDB.
> - If you have enabled Titan before upgrading a cluster to TiDB v7.6.0 or later versions, Titan will be enabled after the upgrade, and the configuration of [`min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size) before the upgrade will also be retained. If you do not explicitly configure the value before the upgrade, the default value of the old version `1KB` will be retained to ensure the stability of the cluster configuration after the upgrade.

Titan is compatible with RocksDB, so you can directly enable Titan on the existing TiKV instances that use RocksDB. You can use one of the following methods to enable Titan:

+ Method 1: If you have deployed the cluster using TiUP, you can execute the `tiup cluster edit-config ${cluster-name}` command and edit the TiKV configuration file as the following example shows:

    ```shell
    tikv:
      rocksdb.titan.enabled: true
    ```

    Reload the configuration and TiKV will be rolling restarted dynamically:

    ```shell
    tiup cluster reload ${cluster-name} -R tikv
    ```

    For the detailed command, see [Modify the configuration using TiUP](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration).

+ Method 2: Directly edit the TiKV configuration file to enable Titan (**NOT** recommended for the production environment).

    ```toml
    [rocksdb.titan]
    enabled = true
    ```

+ Method 3: Edit the `${cluster_name}/tidb-cluster.yaml` configuration file for TiDB Operator:

    ```yaml
    spec:
      tikv:
        ## Base image of the component
        baseImage: pingcap/tikv
        ## tikv-server configuration
        ## Ref: https://docs.pingcap.com/tidb/stable/tikv-configuration-file
        config: |
          log-level = "info"
          [rocksdb]
            [rocksdb.titan]
              enabled = true
    ```

    Apply the configuration to trigger an online rolling restart of the TiDB cluster for the changes to take effect:

    ```shell
    kubectl apply -f ${cluster_name} -n ${namespace}
    ```

    For more information, refer to [Configuring a TiDB Cluster in Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/configure-a-tidb-cluster).
## Data conversion

> **Warning:**
>
> When Titan is disabled, RocksDB cannot read data that has been moved to Titan. If Titan is incorrectly disabled on a TiKV instance with Titan already enabled (mistakenly set `rocksdb.titan.enabled` to `false`), TiKV will fail to start, and the `You have disabled titan when its data directory is not empty` error appears in the TiKV log. To correctly disabled Titan, see [Disable Titan](#disable-titan).

After Titan is enabled, the existing data stored in RocksDB is not immediately moved to the Titan engine. As new data is written to the TiKV and RocksDB performs compaction, **the values are progressively separated from keys and written to Titan**. Similarly, the data restored through BR snapshot/log, the data converted during scaling, or the data imported by TiDB Lightning Physical Import Mode, is not written directly into Titan. As compaction proceeds, the large values exceeding the default value (`32KB`) of [`min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size) in the processed SST files are separated into Titan. You can monitor the size of files stored in Titan by observing the **TiKV Details > Titan kv > blob file size** panel to estimate the data size.

If you want to speed up the writing process, you can use tikv-ctl to compact data of the whole TiKV cluster manually. For details, see [manual compaction](https://docs.pingcap.com/tidb/stable/tikv-control#compact-data-of-the-whole-tikv-cluster-manually). The data access is continuous during the conversion from RocksDB to Titan, therefore the block cache of RocksDB significantly accelerates the data conversion process. In the test, by using tikv-ctl, a volume of 670 GiB TiKV data can be converted to Titan in one hour.

Note that the values in Titan Blob files are not continuous, and Titan's cache is at the value level, so the Blob Cache does not help during compaction. The conversion speed from Titan to RocksDB is an order of magnitude slower than that from RocksDB to Titan. In the test, it takes 12 hours to convert a volume of 800 GiB Titan data on a TiKV node to RocksDB by tikv-ctl in a full compaction.
