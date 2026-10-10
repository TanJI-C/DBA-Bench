# Upgrade to 7.3 or later storage format and downgrade limits

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash-upgrade-guide.md`
- Source Title: `TiFlash Upgrade Guide`
- Source Heading Path: `TiFlash Upgrade Guide > From v6.x or v7.x to v7.3 with `storage.format_version = 5` configured | TiFlash Upgrade Guide > From v6.x or v7.x to v7.4 or a later version`
- Source Line Ranges: `116-128`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `shared`
- Topic Tags: `upgrade`, `storage-format`, `dtfile`, `experimental`, `configuration`, `compaction`, `downgrade`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0473_a34e5a3571`
- Source ID: `tidb-docs-8.1:tiflash-upgrade-guide.md#from-v6-x-or-v7-x-to-v7-3-with-storage-format-version-5-configured`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `35aff41b57236408ae6920ec74a9b3bbca85967bb1e39ad2eacef7aa464ab883`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash-upgrade-guide#from-v6-x-or-v7-x-to-v7-3-with-storage-format-version-5-configured
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash-upgrade-guide.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiFlash storage format changes in v7.3 or later, including DTFile V3, storage.format_version = 5, DTTool migration, or in-place downgrade limits after upgrading to v7.4 or later.
- Retrieval Keywords: From v6.x or v7.x to v7.3 with storage.format_version = 5 configured, From v6.x or v7.x to v7.4 or a later version, DTFile V3, experimental, DTFile V2, storage.format_version = 5, data compaction, DTTool offline, rewrite V3 DTFiles back to V2 DTFiles, DTTool Migration Tool, in-place downgrading is not supported, PageStorage V3
- Follow-up Guidance: The chunk says that after upgrading to v7.4 or a later version, in-place downgrading to the original version is not supported, and for testing or other special scenarios it provides the scale-in and replicate-from-TiKV workaround.
- Classification Note: This is classified as an operation chunk because it focuses on upgrade-time storage-format behavior, configuration-driven format selection, migration tooling, and downgrade compatibility constraints.

## Official Source Content

## From v6.x or v7.x to v7.3 with `storage.format_version = 5` configured

Starting from v7.3, TiFlash introduces a new DTFile version: DTFile V3 (experimental). This new DTFile version can merge multiple small files into a single larger file to reduce the total number of files. In v7.3, the default DTFile version is still V2. To use V3, you can set the [TiFlash configuration parameter](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration) `storage.format_version = 5`. After the setting, TiFlash can still read V2 DTFiles and will gradually rewrite existing V2 DTFiles to V3 DTFiles during subsequent data compaction.

After upgrading TiFlash to v7.3 and configuring TiFlash to use V3 DTFiles, if you need to revert TiFlash to an earlier version, you can use the DTTool offline to rewrite V3 DTFiles back to V2 DTFiles. For more information, see [DTTool Migration Tool](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-command-line-flags#dttool-migrate).
## From v6.x or v7.x to v7.4 or a later version

Starting from v7.4, to reduce the read and write amplification generated during data compaction, TiFlash optimizes the data compaction logic of PageStorage V3, which leads to changes to some of the underlying storage file names. Therefore, after the upgrade to v7.4 or a later version, in-place downgrading to the original version is not supported.

**Workaround for downgrading TiFlash in testing or other special scenarios**

To downgrade TiFlash in testing or other special scenarios, you can forcibly scale in the target TiFlash node and then replicate data from TiKV again. For detailed steps, see [Scale in a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-tiflash-cluster).
