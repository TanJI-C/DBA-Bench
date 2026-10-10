# DM secret key customization, upgrade, and key rotation

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-customized-secret-key.md`
- Source Title: `Customize a Secret Key for DM Encryption and Decryption`
- Source Heading Path: `Customize a Secret Key for DM Encryption and Decryption | Customize a Secret Key for DM Encryption and Decryption > Usage | Customize a Secret Key for DM Encryption and Decryption > Upgrade from a version earlier than v8.0.0 | Customize a Secret Key for DM Encryption and Decryption > Update the secret key for encryption and decryption`
- Source Line Ranges: `5-36`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `encryption`, `secret-key`, `passwords`, `upgrade`, `rolling-upgrade`, `rolling-restart`, `configuration-file`, `command-line-flags`, `key-rotation`, `dmctl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0072_a3efcac25f`
- Source ID: `tidb-docs-8.1:dm/dm-customized-secret-key.md#customize-a-secret-key-for-dm-encryption-and-decryption`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e79211339f6960a1e11e09af2e3502b58fc9119d0cd48a8dd46a55d26150555f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-customized-secret-key#customize-a-secret-key-for-dm-encryption-and-decryption
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-customized-secret-key.md

## Retrieval Guidance

- Use When: Use this chunk when asking how DM customizes the encryption secret key, how `secret-key-path` is configured, what changes when upgrading from versions earlier than v8.0.0, or how to rotate the key for encrypted passwords.
- Retrieval Keywords: DM secret key customization, Customize a Secret Key for DM Encryption and Decryption, secret-key-path, DM-master configuration file, DM-master command-line flags, 64-character hexadecimal AES-256 secret key, fixed AES-256 secret key, v8.0.0, upgrade from a version earlier than v8.0.0, rolling upgrade, rolling restart of DM-master, tiup dmctl encrypt, encrypted passwords, data source configuration, migration task configuration
- Follow-up Guidance: The source states that all DM-master nodes must use the same secret key configuration, rolling upgrade DM-master before DM-worker when upgrading with encrypted passwords, and after key update perform a rolling restart of DM-master and use passwords encrypted with `tiup dmctl encrypt` (dmctl version >= v8.0.0) for new configuration files.
- Classification Note: This is classified as configuration for the self-managed DM component because the content centers on configuring `secret-key-path`, managing encrypted password handling, and operational steps for upgrade and key rotation in DM-master and DM-worker.

## Official Source Content

# Customize a Secret Key for DM Encryption and Decryption

Before v8.0.0, [DM](https://docs.pingcap.com/tidb/stable/dm/dm-overview) uses a [fixed AES-256 secret key](https://github.com/pingcap/tiflow/blob/1252979421fc83ffa2a1548d981e505f7fc0b909/dm/pkg/encrypt/encrypt.go#L27) to encrypt and decrypt passwords in the data source and migration task configurations. However, using a fixed secret key might pose security risks, especially in environments where security is crucial. To enhance security, starting from v8.0.0, DM removes the fixed secret key and enables you to customize a secret key.
## Usage

1. Create a custom key file, which must contain a 64-character hexadecimal AES-256 secret key. One way to generate this key is by calculating SHA256 checksum of random data, such as `head -n 256 /dev/urandom | sha256sum`.
2. In the DM-master [command-line flags](https://docs.pingcap.com/tidb/stable/dm/dm-command-line-flags) or [configuration file](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file), specify `secret-key-path` as the path of your custom key file.
## Upgrade from a version earlier than v8.0.0

Because DM no longer uses the fixed secret key starting from v8.0.0, pay attention to the following when upgrading DM from versions earlier than v8.0.0:

- If plaintext passwords are used in both [data source configurations](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file) and [migration task configurations](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full), no additional steps are required for the upgrade.
- If encrypted passwords are used in [data source configurations](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file) and [migration task configurations](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full) or if you want to use encrypted passwords in the future, you need to do the following:
    1. Add the `secret-key-path` parameter to the [DM-master configuration file](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file) and specify it as the path of your custom key file. The file must contain a 64-character hexadecimal AES-256 key. If the [fixed AES-256 secret key](https://github.com/pingcap/tiflow/blob/1252979421fc83ffa2a1548d981e505f7fc0b909/dm/pkg/encrypt/encrypt.go#L27) was used for encryption before upgrading, you can copy this secret key to your key file. Make sure all DM-master nodes use the same secret key configuration.
    2. Perform a rolling upgrade of DM-master first, followed by a rolling upgrade of DM-worker. For more information, see [Rolling upgrade](https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#rolling-upgrade).
## Update the secret key for encryption and decryption

To update the secret key used for encryption and decryption, take the following steps:

1. Update `secret-key-path` in the [DM-master configuration file](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file).

    > **Note:**
    >
    > - Make sure all DM-master nodes are updated to the same secret key configuration.
    > - During the secret key update, do not create new [data source configuration files](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file) or [migration task configuration files](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).

2. Perform a rolling restart of DM-master.
3. Use the passwords encrypted with `tiup dmctl encrypt` (dmctl version >= v8.0.0) when you create new [data source configuration files](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file) and [migration task configuration files](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).
