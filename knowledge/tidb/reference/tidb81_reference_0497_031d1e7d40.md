# Authentication plugin support and tidb_auth_token

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/security-compatibility-with-mysql.md`
- Source Title: `Security Compatibility with MySQL`
- Source Heading Path: `Security Compatibility with MySQL > Authentication plugin status | Security Compatibility with MySQL > Authentication plugin status > `tidb_auth_token``
- Source Line Ranges: `108-146`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `cloud`, `sql`
- Topic Tags: `authentication`, `auth-plugin`, `jwt`, `tidb-auth-token`, `tls`, `ldap`, `passwordless-authentication`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0497_031d1e7d40`
- Source ID: `tidb-docs-8.1:security-compatibility-with-mysql.md#authentication-plugin-status`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40dc1b5714994b0e3140b04122257fa15a86466244cd1c71e3058ee4f3e435ce`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#authentication-plugin-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/security-compatibility-with-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which authentication plugins TiDB supports, how to set the default advertised authentication method, or what `tidb_auth_token` means.
- Retrieval Keywords: Authentication plugin status, CREATE USER, ALTER USER, default_authentication_plugin, mysql_native_password, sha256_password, caching_sha2_password, auth_socket, tidb_sm3_password, tidb_auth_token, authentication_ldap_sasl, authentication_ldap_simple, TLS Certificates, LDAP, PAM, ed25519, GSSAPI, FIDO, JSON Web Token, JWT, TiDB-JDBC, Enable TLS between TiDB Clients and Servers
- Follow-up Guidance: For related details, the content references `CREATE USER`, `ALTER USER`, `default_authentication_plugin`, TiDB-JDBC for `tidb_sm3_password`, and the TLS document "Enable TLS between TiDB Clients and Servers."
- Classification Note: This is a reference chunk because it lists supported and unsupported authentication methods and defines `tidb_auth_token` using exact plugin names and related identifiers from the official content.

## Official Source Content

## Authentication plugin status

TiDB supports multiple authentication methods. These methods can be specified on a per user basis using [`CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user) and [`ALTER USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user). These methods are compatible with the authentication methods of MySQL with the same names.

You can use one of the following supported authentication methods in the table. To specify a default method that the server advertises when the client-server connection is being established, set the [`default_authentication_plugin`](https://docs.pingcap.com/tidb/stable/system-variables#default_authentication_plugin) variable. `tidb_sm3_password` is the SM3 authentication method only supported in TiDB. Therefore, to authenticate using this method, you must connect to TiDB using [TiDB-JDBC](https://github.com/pingcap/mysql-connector-j/tree/release/8.0-sm3). `tidb_auth_token` is a JSON Web Token (JWT)-based authentication method used in TiDB Cloud, and you can also configure it for use in TiDB Self-Managed.

The support for TLS authentication is configured differently. For detailed information, see [Enable TLS between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers).

The support for TLS authentication is configured differently. For detailed information, see [Enable TLS between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers).

| Authentication Method        | Supported        |
| :----------------------------| :--------------- |
| `mysql_native_password`      | Yes              |
| `sha256_password`            | No               |
| `caching_sha2_password`      | Yes, since 5.2.0 |
| `auth_socket`                | Yes, since 5.3.0 |
| `tidb_sm3_password`          | Yes, since 6.3.0 |
| `tidb_auth_token`            | Yes, since 6.4.0 |
| `authentication_ldap_sasl`   | Yes, since 7.1.0 |
| `authentication_ldap_simple` | Yes, since 7.1.0 |
| TLS Certificates             | Yes              |
| LDAP                         | Yes, since 7.1.0 |
| PAM                          | No               |
| ed25519 (MariaDB)            | No               |
| GSSAPI (MariaDB)             | No               |
| FIDO                         | No               |
### `tidb_auth_token`

`tidb_auth_token` is a passwordless authentication method based on [JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519). In v6.4.0, `tidb_auth_token` is only used for user authentication in TiDB Cloud. Starting from v6.5.0, you can also configure `tidb_auth_token` as a user authentication method for TiDB Self-Managed. Different from password-based authentication methods such as `mysql_native_password` and `caching_sha2_password`, when you create users using `tidb_auth_token`, there is no need to set or store custom passwords. To log into TiDB, users only need to use a signed token instead of a password, which simplifies the authentication process and improves security.
