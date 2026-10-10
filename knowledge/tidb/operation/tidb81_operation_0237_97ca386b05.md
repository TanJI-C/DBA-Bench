# Disable Titan and migrate data back to RocksDB

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/storage-engine/titan-configuration.md`
- Source Title: `Titan Configuration`
- Source Heading Path: `Titan Configuration > Disable Titan`
- Source Line Ranges: `133-173`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `tiup`
- Topic Tags: `titan`, `disable`, `blob-run-mode`, `fallback`, `compaction`, `disk-space`, `performance-impact`, `tikv-ctl`, `metrics`, `version-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0237_97ca386b05`
- Source ID: `tidb-docs-8.1:storage-engine/titan-configuration.md#disable-titan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4bab5740e00bd4bac5a01bdac9137dd736d4177f3f99de5a2ab1785c227262e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/storage-engine/titan-configuration#disable-titan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/storage-engine/titan-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to disable Titan, move data back to RocksDB, or interpret blob-run-mode values and related compaction effects in TiKV.
- Retrieval Keywords: Disable Titan, rocksdb.defaultcf.titan.blob-run-mode, blob-run-mode, normal, read-only, fallback, rocksdb.titan.enabled, discardable-ratio, tikv-ctl --pd <PD_ADDR> compact-cluster --bottommost force, Blob file count, TiKV-Details, Titan - kv, tiup cluster edit-config, tiup cluster reload -R tikv
- Follow-up Guidance: After compaction is finished, wait for the Blob file count metric under TiKV-Details/Titan - kv to decrease to 0.
- Classification Note: This is classified as an operation because the content describes the procedure, warnings, optional full compaction, and metrics involved in disabling Titan and migrating data back to RocksDB.

## Official Source Content

## Disable Titan

To disable Titan, you can configure the `rocksdb.defaultcf.titan.blob-run-mode` option. The optional values for `blob-run-mode` are as follows:

- When the option is set to `normal`, Titan performs read and write operations normally.
- When the option is set to `read-only`, all newly written values are written into RocksDB, regardless of the value size.
- When the option is set to `fallback`, all newly written values are written into RocksDB, regardless of the value size. Also, all compacted values stored in the Titan blob file are automatically moved back to RocksDB.

To disable Titan for all existing and future data, you can take the following steps. Note that you can skip Step 2 because it greatly affects online traffic performance. In fact even without Step 2, the data compaction consumes extra I/O and CPU resources when it moves data from Titan to RocksDB, and performance will degrade (sometimes as much as 50%) when TiKV I/O or CPU resources are limited.

> **Warning:**
>
> When disabling Titan for TiDB versions earlier than v8.5.0, it is not recommended to modify the TiKV configuration item [`rocksdb.titan.enabled`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enabled) to `false`, as this might cause TiKV to crash. Following Step 1 is sufficient to disable Titan.

1. Update the configuration of the TiKV nodes you wish to disable Titan for. You can update configuration in two methods:

    + Execute `tiup cluster edit-config`, edit the configuration file, and execute `tiup cluster reload -R tikv`.
    + Manually update the configuration file and restart TiKV.

        ```toml
        [rocksdb.defaultcf.titan]
        blob-run-mode = "fallback"
        discardable-ratio = 1.0
        ```

    > **Note:**
    >
    > When there is insufficient disk space to accommodate both Titan and RocksDB data, it is recommended to use the default value of `0.5` for [`discardable-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#discardable-ratio). In general, the default value is recommended when available disk space is less than 50%. This is because when `discardable-ratio = 1.0`, the RocksDB data continues to increase. At the same time, the recycling of existing blob files in Titan requires all the data in that file to be converted to RocksDB, which is a slow process. However, if the disk size is large enough, setting `discardable-ratio = 1.0` can reduce the GC of the blob file itself during compaction, which saves bandwidth.

2. (Optional) Perform a full compaction using tikv-ctl. This process will consume a large amount of I/O and CPU resources.

    > **Warning:**
    >
    > When disk space is insufficient, executing the following command might result in the entire cluster running out of available space and thus unable to write data.

    ```bash
    tikv-ctl --pd <PD_ADDR> compact-cluster --bottommost force
    ```

3. After the compaction is finished, wait for the **Blob file count** metrics under **TiKV-Details**/**Titan - kv** to decrease to `0`.
