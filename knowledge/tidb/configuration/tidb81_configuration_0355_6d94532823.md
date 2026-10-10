# TiFlash Proxy learner configuration and topology label scheduling

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-configuration.md`
- Source Title: `Configure TiFlash`
- Source Heading Path: `Configure TiFlash > TiFlash configuration parameters > Configure the `tiflash.toml` file | Configure TiFlash > TiFlash configuration parameters > Configure the `tiflash-learner.toml` file | Configure TiFlash > TiFlash configuration parameters > Schedule replicas by topology labels`
- Source Line Ranges: `294-353`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tikv`, `pd`
- Topic Tags: `proxy-configuration`, `toml`, `raftstore`, `logging`, `encryption`, `topology-labels`, `replica-scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0355_6d94532823`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-configuration.md#configure-the-tiflash-toml-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43c62524a7341f7defdcf8d5ff6225df8e507857c55217bb3cd756754ecfc42e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflash-toml-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiFlash Proxy `tiflash-learner.toml` parameters, reserved labels, encryption settings, log settings, or the reference for scheduling replicas by topology labels.
- Retrieval Keywords: tiflash-learner.toml, TiFlash Proxy configuration, TiKV configuration, raftstore.snap-handle-pool-size, label key engine is reserved, log.level, log.file.max-backups, log.file.max-days, raftstore.apply-pool-size, raftstore.store-pool-size, security.redact-info-log, security.encryption.data-encryption-method, security.encryption.data-key-rotation-period, security.encryption.master-key, security.encryption.previous-master-key, Schedule replicas by topology labels, Set available zones
- Follow-up Guidance: For topology label replica scheduling, the source points to `Set available zones`.
- Classification Note: This is classified as configuration because the content lists TiFlash Proxy `tiflash-learner.toml` parameters and notes about topology-label-based replica scheduling.

## Official Source Content

### Configure the `tiflash-learner.toml` file

The parameters in `tiflash-learner.toml` are basically the same as those in TiKV. You can refer to [TiKV configuration](https://docs.pingcap.com/tidb/stable/tikv-configuration-file) for TiFlash Proxy configuration. The following are only commonly used parameters. Note that:

- Compared with TiKV, TiFlash Proxy has an extra `raftstore.snap-handle-pool-size` parameter.
- The `label` whose key is `engine` is reserved and cannot be configured manually.

```toml
[log]
    ## The log level of TiFlash Proxy (available options: "trace", "debug", "info", "warn", "error"). The default value is "info". Introduced in v5.4.0.
    level = "info"

[log.file]
    ## The maximum number of log files to save. Introduced in v5.4.0.
    ## If this parameter is not set or set to the default value `0`, TiFlash Proxy saves all log files.
    ## If this parameter is set to a non-zero value, TiFlash Proxy retains at most the number of old log files specified by `max-backups`. For example, if you set it to `7`, TiFlash Proxy retains at most 7 old log files.
    max-backups = 0
    ## The maximum number of days that the log files are retained. Introduced in v5.4.0.
    ## If this parameter is not set or set to the default value `0`, TiFlash Proxy retains all log files.
    ## If this parameter is set to a non-zero value, TiFlash Proxy cleans up outdated log files after the number of days specified by `max-days`.
    max-days = 0

[raftstore]
    ## The allowable number of threads in the pool that flushes Raft data to storage.
    apply-pool-size = 4

    ## The allowable number of threads that process Raft, which is the size of the Raftstore thread pool.
    store-pool-size = 4

    ## The number of threads that handle snapshots.
    ## The default value is 2. If you set it to 0, the multi-thread optimization is disabled.
    ## A specific parameter of TiFlash Proxy, introduced in v4.0.0.
    snap-handle-pool-size = 2

[security]
    ## New in v5.0. This configuration item enables or disables log redaction.
    ## If the configuration value is set to true,
    ## all user data in the log will be replaced by ?. The default value is false.
    redact-info-log = false

[security.encryption]
    ## The encryption method for data files.
    ## Value options: "aes128-ctr", "aes192-ctr", "aes256-ctr", "sm4-ctr" (supported since v6.4.0), and "plaintext".
    ## Default value: `"plaintext"`, which means encryption is disabled by default. A value other than "plaintext" means that encryption is enabled, in which case the master key must be specified.
    data-encryption-method = "aes128-ctr"
    ## Specifies how often the data encryption key is rotated. Default value: `7d`.
    data-key-rotation-period = "168h" # 7 days

[security.encryption.master-key]
    ## Specifies the master key if encryption is enabled. To learn how to configure a master key, see Configure encryption: https://docs.pingcap.com/tidb/dev/encryption-at-rest#configure-encryption .

[security.encryption.previous-master-key]
    ## Specifies the old master key when rotating the new master key. The configuration format is the same as that of `master-key`. To learn how to configure a master key, see  Configure encryption: https://docs.pingcap.com/tidb/dev/encryption-at-rest#configure-encryption .
```
### Schedule replicas by topology labels

See [Set available zones](https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas#set-available-zones).
