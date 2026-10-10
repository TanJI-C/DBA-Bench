# Encryption at rest support across TiDB components

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/encryption-at-rest.md`
- Source Title: `Encryption at Rest`
- Source Heading Path: `Encryption at Rest | Encryption at Rest > Encryption support in different TiDB components | Encryption at Rest > Encryption support in different TiDB components > TiKV | Encryption at Rest > Encryption support in different TiDB components > TiFlash | Encryption at Rest > Encryption support in different TiDB components > PD | Encryption at Rest > Encryption support in different TiDB components > Backups with BR | Encryption at Rest > Encryption support in different TiDB components > Logging`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `tiflash`, `pd`, `br`, `tidb`
- Topic Tags: `encryption-at-rest`, `component-support`, `master-key`, `kms`, `tls`, `core-dumps`, `path-configuration`, `sm4`, `performance`, `logging`, `log-redaction`, `backup-encryption`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0035_1501d6ecd5`
- Source ID: `tidb-docs-8.1:encryption-at-rest.md#encryption-at-rest`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a30549d25cf55dc63071ecef9a57b2f1304de6371f9f26fc77d2829772b8557`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/encryption-at-rest#encryption-at-rest
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/encryption-at-rest.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which TiDB components support encryption at rest and the related limits, monitoring, logging, backup, path, TLS, KMS, and SM4 details across TiKV, TiFlash, PD, and BR.
- Retrieval Keywords: Encryption at Rest, Encryption support in different TiDB components, TiKV supports encryption at rest, TiFlash supports encryption at rest, PD experimental feature, Backups with BR, S3 server-side encryption, Logging, master key, KMS, TLS, core dumps, storage.data-dir, raftstore.raftdb-path, rocksdb.wal-dir, raftdb.wal-dir, SM4, TiFlash-Proxy-Details, Encryption panel, log redaction
- Follow-up Guidance: For TiKV, the source states that once encryption is turned on, data file path configurations such as `storage.data-dir`, `raftstore.raftdb-path`, `rocksdb.wal-dir`, and `raftdb.wal-dir` should not be changed.
- Classification Note: This is classified as architecture because the content compares encryption-at-rest support and behavior across multiple TiDB components and related subsystems.

## Official Source Content

# Encryption at Rest

> **Note:**
>
> If your cluster is deployed on AWS and uses the EBS storage, it is recommended to use the EBS encryption. See [AWS documentation - EBS Encryption](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html). You are using the non-EBS storage on AWS such as the local NVMe storage, it is recommended to use encryption at rest introduced in this document.

Encryption at rest means that data is encrypted when it is stored. For databases, this feature is also referred to as TDE (transparent data encryption). This is opposed to encryption in flight (TLS) or encryption in use (rarely used). Different things could be doing encryption at rest (such as SSD drive, file system, and cloud vendor), but by having TiKV do the encryption before storage this helps ensure that attackers must authenticate with the database to gain access to data. For example, when an attacker gains access to the physical machine, data cannot be accessed by copying files on disk.
## Encryption support in different TiDB components

In a TiDB cluster, different components use different encryption methods. This section introduces the encryption supports in different TiDB components such as TiKV, TiFlash, PD, and Backup & Restore (BR).

When a TiDB cluster is deployed, the majority of user data is stored on TiKV and TiFlash nodes. Some metadata is stored on PD nodes (for example, secondary index keys used as TiKV Region boundaries). To get the full benefits of encryption at rest, you need to enable encryption for all components. Backups, log files, and data transmitted over the network should also be considered when you implement encryption.
### TiKV

TiKV supports encryption at rest. This feature allows TiKV to transparently encrypt data files using [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) or [SM4](https://en.wikipedia.org/wiki/SM4_(cipher)) in [CTR](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation) mode. To enable encryption at rest, an encryption key must be provided by the user and this key is called master key. TiKV automatically rotates data keys that it used to encrypt actual data files. Manually rotating the master key can be done occasionally. Note that encryption at rest only encrypts data at rest (namely, on disk) and not while data is transferred over network. It is advised to use TLS together with encryption at rest.

You can use Key Management Service (KMS) for both cloud and self-hosted deployments or supply the plaintext master key in a file.

TiKV currently does not exclude encryption keys and user data from core dumps. It is advised to disable core dumps for the TiKV process when using encryption at rest. This is not currently handled by TiKV itself.

TiKV tracks encrypted data files using the absolute path of the files. As a result, once encryption is turned on for a TiKV node, the user should not change data file paths configuration such as `storage.data-dir`, `raftstore.raftdb-path`, `rocksdb.wal-dir` and `raftdb.wal-dir`.

SM4 encryption is only supported in v6.3.0 and later versions of TiKV. TiKV versions earlier than v6.3.0 only support AES encryption. SM4 encryption affects performance. In the worst-case scenario, it might cause a ​50% to 80% throughput degradation. However, a sufficiently large [`storage.block-cache`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#storageblock-cache) can significantly mitigate this impact, reducing the throughput degradation to around 10%.
### TiFlash

TiFlash supports encryption at rest. Data keys are generated by TiFlash. All files (including data files, schema files, and temporary files) written into TiFlash (including TiFlash Proxy) are encrypted using the current data key. The encryption algorithms, the encryption configuration (in the [`tiflash-learner.toml` file](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) supported by TiFlash), and the meanings of monitoring metrics are consistent with those of TiKV.

If you have deployed TiFlash with Grafana, you can check the **TiFlash-Proxy-Details** -> **Encryption** panel.

SM4 encryption is only supported in v6.4.0 and later versions of TiFlash. TiFlash versions earlier than v6.4.0 only support AES encryption.
### PD

Encryption-at-rest for PD is an experimental feature, which is configured in the same way as in TiKV.
### Backups with BR

BR supports S3 server-side encryption (SSE) when backing up data to S3. A customer-owned AWS KMS key can also be used together with S3 server-side encryption. See [BR S3 server-side encryption](https://docs.pingcap.com/tidb/stable/encryption-at-rest#br-s3-server-side-encryption) for details.
### Logging

TiKV, TiDB, and PD info logs might contain user data for debugging purposes. The info log and this data in it are not encrypted. It is recommended to enable [log redaction](https://docs.pingcap.com/tidb/stable/log-redaction).
