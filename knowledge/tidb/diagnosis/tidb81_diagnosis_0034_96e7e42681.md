# TiKV encryption monitoring, debugging, and version compatibility

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/encryption-at-rest.md`
- Source Title: `Encryption at Rest`
- Source Heading Path: `Encryption at Rest > TiKV encryption at rest > Monitoring and debugging | Encryption at Rest > TiKV encryption at rest > Compatibility between TiKV versions | Encryption at Rest > TiFlash encryption at rest`
- Source Line Ranges: `253-279`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `shared`, `tiflash`
- Topic Tags: `encryption-at-rest`, `monitoring`, `debugging`, `grafana`, `metrics`, `tikv-ctl`, `compatibility`, `downgrade`, `startup-failure`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0034_96e7e42681`
- Source ID: `tidb-docs-8.1:encryption-at-rest.md#monitoring-and-debugging`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d62595a45827fad72b781aec0f0c16b0403cecd8323a3dbe66d2d02205231485`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/encryption-at-rest#monitoring-and-debugging
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/encryption-at-rest.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiKV encryption-at-rest monitoring metrics, `tikv-ctl` debugging context, or the documented compatibility issue involving `security.encryption.enable-file-dictionary-log` and downgrades.
- Retrieval Keywords: TiKV-Details, Encryption panel, Encryption initialized, Encryption data keys, Encrypted files, Encryption meta file size, Read/Write encryption meta duration, tikv-ctl, dump encryption metadata, security.encryption.enable-file-dictionary-log, TiKV v4.0.9, TiKV v4.0.8, failed to load file dictionary, unknown version 2, Compatibility between TiKV versions, TiFlash encryption at rest
- Follow-up Guidance: The source includes a startup failure example during downgrade and notes that `tikv-ctl` dumping encryption metadata can expose sensitive data and is not recommended to use in production.
- Classification Note: This is classified as diagnosis because the content focuses on observing encryption state through Grafana metrics, debugging with `tikv-ctl`, and recognizing a version-compatibility startup failure related to encryption metadata.

## Official Source Content

### Monitoring and debugging

To monitor encryption at rest, if you deploy TiKV with Grafana, you can look at the **Encryption** panel in the **TiKV-Details** dashboard. There are a few metrics to look for:

* Encryption initialized: 1 if encryption is initialized during TiKV startup, 0 otherwise. In case of master key rotation, after encryption is initialized, TiKV do not need access to the previous master key.
* Encryption data keys: number of existing data keys. The number is bumped by 1 after each time data key rotation happened. Use this metrics to monitor if data key rotation works as expected.
* Encrypted files: number of encrypted data files currently exists. Compare this number to existing data files in the data directory to estimate portion of data being encrypted, when turning on encryption for a previously unencrypted cluster.
* Encryption meta file size: size of the encryption meta data files.
* Read/Write encryption meta duration: the extra overhead to operate on metadata for encryption.

For debugging, the `tikv-ctl` command can be used to dump encryption metadata such as encryption method and data key id used to encryption the file, as well as list of data keys. Since the operation can expose sensitive data, it is not recommended to use in production. Please refer to [TiKV Control](https://docs.pingcap.com/tidb/stable/tikv-control#dump-encryption-metadata) document.
### Compatibility between TiKV versions

To reduce the overhead caused by I/O and mutex contention when TiKV manages the encryption metadata, an optimization is introduced in TiKV v4.0.9 and controlled by `security.encryption.enable-file-dictionary-log` in the TiKV configuration file. This configuration parameter takes effect only on TiKV v4.0.9 or later versions.

When it is enabled (by default), the data format of encryption metadata is unrecognizable by TiKV v4.0.8 or earlier versions. For example, assume that you use TiKV v4.0.9 or later with encryption at rest and the default `enable-file-dictionary-log` configuration. If you downgrade your cluster to TiKV v4.0.8 or earlier, TiKV will fail to start, with an error in the info log similar to the following one:

```
[2020/12/07 07:26:31.106 +08:00] [ERROR] [mod.rs:110] ["encryption: failed to load file dictionary."]
[2020/12/07 07:26:33.598 +08:00] [FATAL] [lib.rs:483] ["called `Result::unwrap()` on an `Err` value: Other(\"[components/encryption/src/encrypted_file/header.rs:18]: unknown version 2\")"]
```

To avoid the error above, you can first set `security.encryption.enable-file-dictionary-log` to `false` and start TiKV with v4.0.9 or later. Once TiKV starts successfully, the data format of encryption metadata is downgraded to the version recognizable to earlier TiKV versions. At this point, you can then downgrade your TiKV cluster to an earlier version.
## TiFlash encryption at rest
