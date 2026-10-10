# Enablement and restrictions for Partitioned Raft KV

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-raft-kv.md`
- Source Title: `Partitioned Raft KV`
- Source Heading Path: `Partitioned Raft KV > Usage | Partitioned Raft KV > Restrictions`
- Source Line Ranges: `30-47`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tiflash`
- Topic Tags: `enablement`, `configuration`, `storage.engine`, `rocksdb`, `limitations`, `backup`, `unsafe-recovery`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0121_f3fa074811`
- Source ID: `tidb-docs-8.1:partitioned-raft-kv.md#usage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1aa6652671842e1a720679375193ba888b808b1f297ce8177075a20ffa33dca7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-raft-kv#usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-raft-kv.md

## Retrieval Guidance

- Use When: Use this chunk when answering how to enable Partitioned Raft KV at cluster creation time or what configuration limits, compatibility limits, and unsupported tools or features apply.
- Retrieval Keywords: storage.engine, partitioned-raft-kv, rocksdb.write-buffer-flush-oldest-first, rocksdb.write-buffer-limit, enable Partitioned Raft KV, when creating a cluster, Restrictions, EBS volume snapshot backup, online unsafe recovery, Titan, tikv-ctl, unsafe-recover, raw-scan, remove-fail-stores, recreate-region, reset-to-version, not compatible with TiFlash, cannot enable or disable this feature after the cluster is initialized
- Follow-up Guidance: The source also notes that the RocksDB memory usage can be controlled with rocksdb.write-buffer-flush-oldest-first and rocksdb.write-buffer-limit when using Raft KV.
- Classification Note: This is classified as configuration because the content centers on the storage.engine setting and related configuration items, followed by explicit feature restrictions and incompatibilities from the official documentation.

## Official Source Content

## Usage

To enable Partitioned Raft KV, set the configuration item [`storage.engine`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#engine-new-in-v660) to `"partitioned-raft-kv"` when creating a cluster. At the same time, you can use the configuration items [`rocksdb.write-buffer-flush-oldest-first`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#write-buffer-flush-oldest-first-new-in-v660) and [`rocksdb.write-buffer-limit`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#write-buffer-limit-new-in-v660) to control the memory usage of RocksDB when using Raft KV.
## Restrictions

Partitioned Raft KV has the following restrictions:

* It does not support EBS volume snapshot backup yet.
* It does not support online unsafe recovery or Titan yet.
* It does not support the following subcommands of the tikv-ctl command-line tool:
    * `unsafe-recover`
    * `raw-scan`
    * `remove-fail-stores`
    * `recreate-region`
    * `reset-to-version`
* It is not compatible with TiFlash yet.
* You cannot enable or disable this feature after the cluster is initialized.
