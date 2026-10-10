# Security TLS and encryption at rest settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > security | TiKV Configuration File > security > `ca-path` | TiKV Configuration File > security > `cert-path` | TiKV Configuration File > security > `key-path` | TiKV Configuration File > security > `cert-allowed-cn` | TiKV Configuration File > security > `redact-info-log` <span class="version-mark">New in v4.0.8</span> | TiKV Configuration File > security.encryption | TiKV Configuration File > security.encryption > `data-encryption-method` | TiKV Configuration File > security.encryption > `data-key-rotation-period` | TiKV Configuration File > security.encryption > `enable-file-dictionary-log` | TiKV Configuration File > security.encryption > `master-key` | TiKV Configuration File > security.encryption > `previous-master-key``
- Source Line Ranges: `2127-2185`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `security`, `tls`, `certificates`, `x509`, `log-redaction`, `encryption-at-rest`, `tde`, `key-rotation`, `master-key`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0381_e161e43346`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#security`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ed3fa62031e9a30f96efb906ddfd7668ef9e80c7304f12974780c080a091f8a0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV security configuration for TLS certificate paths, allowed certificate Common Names, log redaction, or encryption at rest and master key settings.
- Retrieval Keywords: security, ca-path, cert-path, key-path, cert-allowed-cn, redact-info-log, security.encryption, data-encryption-method, data-key-rotation-period, enable-file-dictionary-log, master-key, previous-master-key, X.509, PEM, Common Names, log redaction, encryption at rest, TDE, plaintext, aes128-ctr, aes192-ctr, aes256-ctr, sm4-ctr
- Follow-up Guidance: The content also notes that when `data-encryption-method` is not `plaintext`, the master key must be specified, and it links to encryption-at-rest documentation for configuring `master-key` and `previous-master-key`.
- Classification Note: This is classified as configuration for the TiKV component because the content lists TiKV security and security.encryption configuration items, defaults, value options, and behavior.

## Official Source Content

## security

Configuration items related to security.
### `ca-path`

+ The path of the CA file
+ Default value: `""`
### `cert-path`

+ The path of the Privacy Enhanced Mail (PEM) file that contains the X.509 certificate
+ Default value: `""`
### `key-path`

+ The path of the PEM file that contains the X.509 key
+ Default value: `""`
### `cert-allowed-cn`

+ A list of acceptable X.509 Common Names in certificates presented by clients. Requests are permitted only when the presented Common Name is an exact match with one of the entries in the list.
+ Default value: `[]`. This means that the client certificate CN check is disabled by default.
### `redact-info-log` New in v4.0.8

+ This configuration item enables or disables log redaction. If the configuration value is set to `true`, all user data in the log will be replaced by `?`.
+ Default value: `false`
## security.encryption

Configuration items related to [encryption at rest](https://docs.pingcap.com/tidb/stable/encryption-at-rest) (TDE).
### `data-encryption-method`

+ The encryption method for data files
+ Value options: "plaintext", "aes128-ctr", "aes192-ctr", "aes256-ctr", and "sm4-ctr" (supported since v6.3.0)
+ A value other than "plaintext" means that encryption is enabled, in which case the master key must be specified.
+ Default value: `"plaintext"`
### `data-key-rotation-period`

+ Specifies how often TiKV rotates the data encryption key.
+ Default value: `7d`
### `enable-file-dictionary-log`

+ Enables the optimization to reduce I/O and mutex contention when TiKV manages the encryption metadata.
+ To avoid possible compatibility issues when this configuration parameter is enabled (by default), see [Encryption at Rest - Compatibility between TiKV versions](https://docs.pingcap.com/tidb/stable/encryption-at-rest#compatibility-between-tikv-versions) for details.
+ Default value: `true`
### `master-key`

+ Specifies the master key if encryption is enabled. To learn how to configure a master key, see [Encryption at Rest - Configure encryption](https://docs.pingcap.com/tidb/stable/encryption-at-rest#configure-encryption).
### `previous-master-key`

+ Specifies the old master key when rotating the new master key. The configuration format is the same as that of `master-key`. To learn how to configure a master key, see [Encryption at Rest - Configure encryption](https://docs.pingcap.com/tidb/stable/encryption-at-rest#configure-encryption).
