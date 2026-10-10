# Security, TLS, authentication, and session token settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > security | TiDB Configuration File > security > `enable-sem` | TiDB Configuration File > security > `ssl-ca` | TiDB Configuration File > security > `ssl-cert` | TiDB Configuration File > security > `ssl-key` | TiDB Configuration File > security > `cluster-ssl-ca` | TiDB Configuration File > security > `cluster-ssl-cert` | TiDB Configuration File > security > `cluster-ssl-key` | TiDB Configuration File > security > `cluster-verify-cn` | TiDB Configuration File > security > `spilled-file-encryption-method` | TiDB Configuration File > security > `auto-tls` | TiDB Configuration File > security > `tls-version` | TiDB Configuration File > security > `auth-token-jwks` <span class="version-mark">New in v6.4.0</span> | TiDB Configuration File > security > `auth-token-refresh-interval` <span class="version-mark">New in v6.4.0</span> | TiDB Configuration File > security > `disconnect-on-expired-password` <span class="version-mark">New in v6.5.0</span> | TiDB Configuration File > security > `session-token-signing-cert` <span class="version-mark">New in v6.4.0</span> | TiDB Configuration File > security > `session-token-signing-key` <span class="version-mark">New in v6.4.0</span>`
- Source Line Ranges: `388-487`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `tiproxy`
- Topic Tags: `security`, `tls`, `certificates`, `authentication`, `jwks`, `password-expiration`, `encryption`, `sem`, `session-migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0319_79ddbfa7c6`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#security`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e8c2ecaa9359156e9ae7d74fd4e49e3af46056e8bc6267cc5c8967d4dcf0aa58`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB security configuration related to SEM, TLS certificates, cluster TLS to TiKV or PD, certificate CN verification, spilled file encryption, TLS version, `tidb_auth_token` JWKS settings, expired password behavior, or TiProxy session migration token signing files.
- Retrieval Keywords: security, enable-sem, tidb_enable_enhanced_security, ssl-ca, ssl-cert, ssl-key, cluster-ssl-ca, cluster-ssl-cert, cluster-ssl-key, cluster-verify-cn, spilled-file-encryption-method, plaintext, aes128-ctr, auto-tls, tls-version, TLSv1.2, TLSv1.3, auth-token-jwks, auth-token-refresh-interval, tidb_auth_token, disconnect-on-expired-password, session-token-signing-cert, session-token-signing-key, TiProxy, session migration
- Follow-up Guidance: The content states that empty `session-token-signing-cert` or `session-token-signing-key` causes TiProxy session migration to fail, and that all TiDB nodes must use the same certificate and key to enable session migration.
- Classification Note: This is classified as TiDB configuration content because it documents security, authentication, encryption, and TLS-related configuration items in the TiDB configuration file.

## Official Source Content

## security

Configuration items related to security.
### `enable-sem`

- Enables the Security Enhanced Mode (SEM).
- Default value: `false`
- The status of SEM is available via the system variable [`tidb_enable_enhanced_security`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security).
### `ssl-ca`

- The file path of the trusted CA certificate in the PEM format.
- Default value: ""
- If you set this option and `--ssl-cert`, `--ssl-key` at the same time, TiDB authenticates the client certificate based on the list of trusted CAs specified by this option when the client presents the certificate. If the authentication fails, the connection is terminated.
- If you set this option but the client does not present the certificate, the secure connection continues without client certificate authentication.
### `ssl-cert`

- The file path of the SSL certificate in the PEM format.
- Default value: ""
- If you set this option and `--ssl-key` at the same time, TiDB allows (but not forces) the client to securely connect to TiDB using TLS.
- If the specified certificate or private key is invalid, TiDB starts as usual but cannot receive secure connection.
### `ssl-key`

- The file path of the SSL certificate key in the PEM format, that is, the private key of the certificate specified by `--ssl-cert`.
- Default value: ""
- Currently, TiDB does not support loading the private keys protected by passwords.
### `cluster-ssl-ca`

- The CA root certificate used to connect TiKV or PD with TLS.
- Default value: ""
### `cluster-ssl-cert`

- The path of the SSL certificate file used to connect TiKV or PD with TLS.
- Default value: ""
### `cluster-ssl-key`

- The path of the SSL private key file used to connect TiKV or PD with TLS.
- Default value: ""
### `cluster-verify-cn`

- A list of acceptable X.509 Common Names in certificates presented by clients. Requests are permitted only when the presented Common Name is an exact match with one of the entries in the list.
- Default value: [], which means that the client certificate CN check is disabled.
### `spilled-file-encryption-method`

+ Determines the encryption method used for saving the spilled files to disk.
+ Default value: `"plaintext"`, which disables encryption.
+ Optional values: `"plaintext"` and `"aes128-ctr"`
### `auto-tls`

- Determines whether to automatically generate the TLS certificates on startup.
- Default value: `false`
### `tls-version`

> **Warning:**
>
> `"TLSv1.0"` and `"TLSv1.1"` protocols are deprecated in TiDB v7.6.0, and will be removed in v8.0.0.

- Set the minimum TLS version for MySQL Protocol connections.
- Default value: "", which allows TLSv1.2 or later versions. Before TiDB v7.6.0, the default value allows TLSv1.1 or later versions.
- Optional values: `"TLSv1.2"` and `"TLSv1.3"`. Before TiDB v8.0.0, `"TLSv1.0"` and `"TLSv1.1"` are also allowed.
### `auth-token-jwks` New in v6.4.0

- Set the local file path of the JSON Web Key Sets (JWKS) for the [`tidb_auth_token`](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#tidb_auth_token) authentication method.
- Default value: `""`
### `auth-token-refresh-interval` New in v6.4.0

- Set the JWKS refresh interval for the [`tidb_auth_token`](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#tidb_auth_token) authentication method.
- Default value: `1h`
### `disconnect-on-expired-password` New in v6.5.0

- Determines whether TiDB disconnects the client connection when the password is expired.
- Default value: `true`
- Optional values: `true`, `false`
- If you set it to `true`, the client connection is disconnected when the password is expired. If you set it to `false`, the client connection is restricted to the "sandbox mode" and the user can only execute the password reset operation.
### `session-token-signing-cert` New in v6.4.0

+ The certificate file path, which is used by [TiProxy](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview) for session migration.
+ Default value: ""
+ Empty value will cause TiProxy session migration to fail. To enable session migration, all TiDB nodes must set this to the same certificate and key. This means that you should store the same certificate and key on every TiDB node.
### `session-token-signing-key` New in v6.4.0

+ The key file path used by [TiProxy](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview) for session migration.
+ Default value: ""
+ Refer to the descriptions of [`session-token-signing-cert`](#session-token-signing-cert-new-in-v640).
