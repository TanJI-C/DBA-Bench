# TiFlash multi-disk deployment by TiDB version

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-configuration.md`
- Source Title: `Configure TiFlash`
- Source Heading Path: `Configure TiFlash > TiFlash configuration parameters > Multi-disk deployment | Configure TiFlash > TiFlash configuration parameters > Multi-disk deployment > Multi-disk deployment with TiDB version earlier than v4.0.9 | Configure TiFlash > TiFlash configuration parameters > Multi-disk deployment > Multi-disk deployment with TiDB v4.0.9 or later`
- Source Line Ranges: `354-378`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tiup`
- Topic Tags: `multi-disk`, `storage-directories`, `path`, `path-realtime-mode`, `storage-main-dir`, `storage-latest-dir`, `version-specific`, `tiup-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0356_0d936c8fa2`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-configuration.md#multi-disk-deployment`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6480fa2d43b448881252b7e9c0ff29a96f5b754949cfca9b3811c43904fb5b78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#multi-disk-deployment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiFlash multi-disk deployment settings and how the configuration differs between versions earlier than v4.0.9 and v4.0.9 or later.
- Retrieval Keywords: Multi-disk deployment, path, data_dir in TiUP, path_realtime_mode, storage.main.dir, storage.latest.dir, TiDB version earlier than v4.0.9, TiDB v4.0.9 or later, TiUP v1.2.5, [storage] configuration, The complex template for the TiFlash topology
- Follow-up Guidance: The source also points to `The complex template for the TiFlash topology` for the TiFlash configuration template used for TiUP.
- Classification Note: This is classified as configuration because the content describes TiFlash multi-disk storage directory parameters and version-specific configuration formats, including `path`, `path_realtime_mode`, and `[storage]`.

## Official Source Content

### Multi-disk deployment

TiFlash supports multi-disk deployment. If there are multiple disks in your TiFlash node, you can make full use of those disks by configuring the parameters described in the following sections. For TiFlash's configuration template to be used for TiUP, see [The complex template for the TiFlash topology](https://github.com/pingcap/docs/blob/master/config-templates/complex-tiflash.yaml).
#### Multi-disk deployment with TiDB version earlier than v4.0.9

For TiDB clusters earlier than v4.0.9, TiFlash only supports storing the main data of the storage engine on multiple disks. You can set up a TiFlash node on multiple disks by specifying the `path` (`data_dir` in TiUP) and `path_realtime_mode` configuration.

If there are multiple data storage directories in `path`, separate each with a comma. For example, `/nvme_ssd_a/data/tiflash,/sata_ssd_b/data/tiflash,/sata_ssd_c/data/tiflash`. If there are multiple disks in your environment, it is recommended that each directory corresponds to one disk and you put disks with the best performance at the front to maximize the performance of all disks.

If there are multiple disks with similar I/O metrics on your TiFlash node, you can leave the `path_realtime_mode` parameter to the default value (or you can explicitly set it to `false`). It means that data will be evenly distributed among all storage directories. However, the latest data is written only to the first directory, so the corresponding disk is busier than other disks.

If there are multiple disks with different I/O metrics on your TiFlash node, it is recommended to set `path_realtime_mode` to `true` and put disks with the best I/O metrics at the front of `path`. It means that the first directory only stores the latest data, and the older data are evenly distributed among the other directories. Note that in this case, the capacity of the first directory should be planned as 10% of the total capacity of all directories.
#### Multi-disk deployment with TiDB v4.0.9 or later

For TiDB clusters with v4.0.9 or later versions, TiFlash supports storing the main data and the latest data of the storage engine on multiple disks. If you want to deploy a TiFlash node on multiple disks, it is recommended to specify your storage directories in the `[storage]` section to make full use of your node. Note that the configurations earlier than v4.0.9 (`path` and `path_realtime_mode`) are still supported.

If there are multiple disks with similar I/O metrics on your TiFlash node, it is recommended to specify corresponding directories in the `storage.main.dir` list and leave `storage.latest.dir` empty. TiFlash will distribute I/O pressure and data among all directories.

If there are multiple disks with different I/O metrics on your TiFlash node, it is recommended to specify directories with higher metrics in the `storage.latest.dir` list, and specify directories with lower metrics in the `storage.main.dir` list. For example, for one NVMe-SSD and two SATA-SSDs, you can set `storage.latest.dir` to `["/nvme_ssd_a/data/tiflash"]` and `storage.main.dir` to `["/sata_ssd_b/data/tiflash", "/sata_ssd_c/data/tiflash"]`. TiFlash will distribute I/O pressure and data among these two directories list respectively. Note that in this case, the capacity of `storage.latest.dir` should be planned as 10% of the total planned capacity.

> **Warning:**
>
> The `[storage]` configuration is supported in TiUP since v1.2.5. If your TiDB cluster version is v4.0.9 or later, make sure that your TiUP version is v1.2.5 or later. Otherwise, the data directories defined in `[storage]` will not be managed by TiUP.
