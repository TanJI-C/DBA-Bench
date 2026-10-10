# TiProxy security and TLS configuration objects

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-configuration.md`
- Source Title: `TiProxy Configuration File`
- Source Heading Path: `TiProxy Configuration File > Configure the `tiproxy.toml` file > security | TiProxy Configuration File > Configure the `tiproxy.toml` file > security > `cluster-tls` | TiProxy Configuration File > Configure the `tiproxy.toml` file > security > `require-backend-tls` | TiProxy Configuration File > Configure the `tiproxy.toml` file > security > `sql-tls` | TiProxy Configuration File > Configure the `tiproxy.toml` file > security > `server-tls` | TiProxy Configuration File > Configure the `tiproxy.toml` file > security > `server-http-tls``
- Source Line Ranges: `149-207`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `pd`, `tidb`
- Topic Tags: `security`, `tls`, `certificates`, `ca-verification`, `client-tls`, `server-tls`, `backend-encryption`, `hot-reload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0392_14cce6b990`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-configuration.md#security`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1d26dee96a757d691c17cb6d6c8d5b873fdcfa14e96bd6b76fcd8bd6c8234085`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiProxy `[security]` TLS object definitions, shared TLS fields, or the meaning of `cluster-tls`, `sql-tls`, `server-tls`, `server-http-tls`, and `require-backend-tls`.
- Retrieval Keywords: [security], cluster-tls, require-backend-tls, sql-tls, server-tls, server-http-tls, TLS object fields, ca, cert, key, auto-certs, skip-ca, min-tls-version, rsa-key-size, autocert-expire-duration, client TLS object, server TLS object, Require TLS between TiProxy and TiDB servers, TiDB server does not support TLS
- Follow-up Guidance: The content states that all TLS options are hot-reloaded, and `require-backend-tls` applies only to new connections.
- Classification Note: This is configuration content because it specifies TiProxy security and TLS configuration objects, their fields, client-versus-server interpretation, and the backend TLS requirement behavior.

## Official Source Content

### security

There are four TLS objects in the `[security]` section with different names. They share the same configuration format and fields, but they are interpreted differently depending on their names.

```toml
[security]
    [sql-tls]
    skip-ca = true
    [server-tls]
    auto-certs = true
```

All TLS options are hot-reloaded.

TLS object fields:

+ `ca`: specifies the CA
+ `cert`: specifies the certificate
+ `key`: specifies the private key
+ `auto-certs`: mostly used for tests. It generates certificates if no certificate or key is specified.
+ `skip-ca`: skips verifying certificates using CA on client object or skips server-side verification on server object.
+ `min-tls-version`: sets the minimum TLS version. Possible values are `1.0`, `1.1`, `1.2`, and `1.3`. The default value is `1.2`, which allows v1.2 or higher TLS versions.
+ `rsa-key-size`: sets the RSA key size when `auto-certs` is enabled.
+ `autocert-expire-duration`: sets the default expiration duration for auto-generated certificates.

Objects are classified into client or server objects by their names.

For client TLS object:

- You must set either `ca` or `skip-ca` to skip verifying server certificates.
- Optionally, you can set `cert` or `key` to pass server-side client verification.
- Useless fields: auto-certs.

For server TLS object:

+ You can set either `cert` or `key` or `auto-certs` to support TLS connections. Otherwise, TiProxy doesn't support TLS connections.
+ Optionally, if `ca` is not empty, it enables server-side client verification. The client must provide their certificates. Alternatively, if both `skip-ca` is true and `ca` is not empty, the server will only verify client certificates if they provide one.
#### `cluster-tls`

A client TLS object. It is used to access TiDB or PD.
#### `require-backend-tls`

+ Default value: `false`
+ Support hot-reload: yes, but only for new connections
+ Require TLS between TiProxy and TiDB servers. If the TiDB server does not support TLS, clients will report an error when connecting to TiProxy.
#### `sql-tls`

A client TLS object. It is used to access TiDB SQL port (4000).
#### `server-tls`

A server TLS object. It is used to provide TLS on SQL port (6000).
#### `server-http-tls`

A server TLS object. It is used to provide TLS on HTTP status port (3080).
