# TLS cipher suites, certificate reload, and monitoring

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/enable-tls-between-clients-and-servers.md`
- Source Title: `Enable TLS Between TiDB Clients and Servers`
- Source Heading Path: `Enable TLS between TiDB Clients and Servers > Supported TLS versions, key exchange protocols, and encryption algorithms > Supported key exchange protocols and encryption algorithms | Enable TLS between TiDB Clients and Servers > Reload certificate, key, and CA | Enable TLS between TiDB Clients and Servers > Monitoring | Enable TLS between TiDB Clients and Servers > See also`
- Source Line Ranges: `149-198`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `tls`, `cipher-suites`, `certificate-reload`, `ssl-ca`, `ssl-cert`, `ssl-key`, `monitoring`, `status-variables`, `encryption`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0104_93b8808a4d`
- Source ID: `tidb-docs-8.1:enable-tls-between-clients-and-servers.md#supported-key-exchange-protocols-and-encryption-algorithms`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dbd74bb70babf6f08bfbe7af37ae1a94aab9ffa6482b18f1f0cd57bde64ea8b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers#supported-key-exchange-protocols-and-encryption-algorithms
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/enable-tls-between-clients-and-servers.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB client-server TLS cipher suites, how to reload TLS files without restarting, or how to check certificate validity dates with status variables.
- Retrieval Keywords: TLS_RSA_WITH_AES_128_CBC_SHA, TLS_RSA_WITH_AES_256_CBC_SHA, TLS_RSA_WITH_AES_128_CBC_SHA256, TLS_RSA_WITH_AES_128_GCM_SHA256, TLS_RSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256, TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256, TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, TLS_AES_128_GCM_SHA256, TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256, ALTER INSTANCE RELOAD TLS, ssl-cert, ssl-key, ssl-ca, reload certificate key and CA, Ssl_server_not_after, Ssl_server_not_before, SHOW GLOBAL STATUS LIKE 'Ssl_server_not_%', certificate validity dates, Enable TLS Between TiDB Components
- Follow-up Guidance: The source also points to the related topic Enable TLS Between TiDB Components.
- Classification Note: This chunk is classified as configuration because it lists supported TLS cipher suites, names the ssl-cert, ssl-key, and ssl-ca configuration items, and includes the ALTER INSTANCE RELOAD TLS statement and monitoring status variables.

## Official Source Content

### Supported key exchange protocols and encryption algorithms

- TLS\_RSA\_WITH\_AES\_128\_CBC\_SHA
- TLS\_RSA\_WITH\_AES\_256\_CBC\_SHA
- TLS\_RSA\_WITH\_AES\_128\_CBC\_SHA256
- TLS\_RSA\_WITH\_AES\_128\_GCM\_SHA256
- TLS\_RSA\_WITH\_AES\_256\_GCM\_SHA384
- TLS\_ECDHE\_ECDSA\_WITH\_AES\_128\_CBC\_SHA
- TLS\_ECDHE\_ECDSA\_WITH\_AES\_256\_CBC\_SHA
- TLS\_ECDHE\_RSA\_WITH\_AES\_128\_CBC\_SHA
- TLS\_ECDHE\_RSA\_WITH\_AES\_256\_CBC\_SHA
- TLS\_ECDHE\_ECDSA\_WITH\_AES\_128\_CBC\_SHA256
- TLS\_ECDHE\_RSA\_WITH\_AES\_128\_CBC\_SHA256
- TLS\_ECDHE\_RSA\_WITH\_AES\_128\_GCM\_SHA256
- TLS\_ECDHE\_ECDSA\_WITH\_AES\_128\_GCM\_SHA256
- TLS\_ECDHE\_RSA\_WITH\_AES\_256\_GCM\_SHA384
- TLS\_ECDHE\_ECDSA\_WITH\_AES\_256\_GCM\_SHA384
- TLS\_ECDHE\_RSA\_WITH\_CHACHA20\_POLY1305\_SHA256
- TLS\_ECDHE\_ECDSA\_WITH\_CHACHA20\_POLY1305\_SHA256
- TLS\_AES\_128\_GCM\_SHA256
- TLS\_AES\_256\_GCM\_SHA384
- TLS\_CHACHA20\_POLY1305\_SHA256
## Reload certificate, key, and CA

To replace the certificate, the key or CA, first replace the corresponding files, then execute the [`ALTER INSTANCE RELOAD TLS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-instance) statement on the running TiDB instance to reload the certificate ([`ssl-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-cert)), the key ([`ssl-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-key)), and the CA ([`ssl-ca`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-ca)) from the original configuration path. In this way, you do not need to restart the TiDB instance.

The newly loaded certificate, key, and CA take effect on the connection that is established after the statement is successfully executed. The connection established before the statement execution is not affected.
## Monitoring

Since TiDB v5.2.0, you can use the `Ssl_server_not_after` and `Ssl_server_not_before` status variables to monitor the start and end dates of the validity of the certificate.

```sql
SHOW GLOBAL STATUS LIKE 'Ssl\_server\_not\_%';
```

```
+-----------------------+--------------------------+
| Variable_name         | Value                    |
+-----------------------+--------------------------+
| Ssl_server_not_after  | Nov 28 06:42:32 2021 UTC |
| Ssl_server_not_before | Aug 30 06:42:32 2021 UTC |
+-----------------------+--------------------------+
2 rows in set (0.0076 sec)
```
## See also

- [Enable TLS Between TiDB Components](https://docs.pingcap.com/tidb/stable/enable-tls-between-components).
