# Configure and verify TLS between TiDB clients and server

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/enable-tls-between-clients-and-servers.md`
- Source Title: `Enable TLS Between TiDB Clients and Servers`
- Source Heading Path: `Enable TLS between TiDB Clients and Servers | Enable TLS between TiDB Clients and Servers > Configure TiDB server to use secure connections | Enable TLS between TiDB Clients and Servers > Configure the MySQL client to use TLS connections | Enable TLS between TiDB Clients and Servers > Enable authentication | Enable TLS between TiDB Clients and Servers > Check whether the current connection uses encryption | Enable TLS between TiDB Clients and Servers > Supported TLS versions, key exchange protocols, and encryption algorithms | Enable TLS between TiDB Clients and Servers > Supported TLS versions, key exchange protocols, and encryption algorithms > Supported TLS versions`
- Source Line Ranges: `5-148`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `tls`, `ssl-mode`, `certificate`, `ca`, `x509`, `secure-connections`, `client-authentication`, `server-authentication`, `connection-verification`, `tls-version`, `cipher-suite`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0103_e7b7cc2227`
- Source ID: `tidb-docs-8.1:enable-tls-between-clients-and-servers.md#enable-tls-between-tidb-clients-and-servers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d97b8a9673b8412e8cfb80b530c6cc12b3204dae1e43e7c570ca7f94e8784e68`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers#enable-tls-between-tidb-clients-and-servers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/enable-tls-between-clients-and-servers.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB client-server TLS configuration details, client ssl-mode behavior, certificate-based authentication requirements, or how to verify that a current connection is encrypted.
- Retrieval Keywords: require_secure_transport, CREATE USER 'u1'@'%' IDENTIFIED BY 'my_random_password' REQUIRE SSL, CREATE USER 'u1'@'%' REQUIRE X509, auto-tls, ssl-cert, ssl-key, ssl-ca, tls-version, mysql protocol server secure connection is enabled, --ssl-mode=REQUIRED, --ssl-mode=VERIFY_CA, --ssl-mode=VERIFY_IDENTITY, --ssl-verify-server-cert, SHOW STATUS LIKE "Ssl%", Ssl_cipher, Ssl_version, STATUS, \s, TLSv1.2, TLSv1.3, Enable TLS between TiDB Clients and Servers
- Follow-up Guidance: The content also gives the exact conditions for server authentication, client authentication, mutual authentication, and the SQL or status commands used to confirm TLS encryption.
- Classification Note: This is classified as configuration for TiDB because the official content explains server TLS parameters, MySQL client TLS options, user REQUIRE SSL or REQUIRE X509 settings, and connection verification behavior.

## Official Source Content

# Enable TLS between TiDB Clients and Servers

By default, TiDB allows insecure connections between the server and clients. This enables third parties that monitor channel traffic to know and possibly modify the data sent and received between the server and the client, including query content and query results. If a channel is untrustworthy (such as if the client is connected to the TiDB server via a public network), an insecure connection is prone to information leakage. In this case, for security reasons, it is recommended to require a connection that is secured with TLS.

The TiDB server supports secure connections based on the TLS (Transport Layer Security) protocol. The protocol is consistent with MySQL secure connections and is directly supported by existing MySQL clients such as MySQL Client, MySQL Shell and MySQL drivers. TLS is sometimes referred to as SSL (Secure Sockets Layer). Because the SSL protocol has [known security vulnerabilities](https://en.wikipedia.org/wiki/Transport_Layer_Security), TiDB does not support SSL. TiDB supports the following protocols: TLSv1.2 and TLSv1.3.

When a TLS secured connection is used, the connection has the following security properties:

- Confidentiality: the traffic plaintext is encrypted to avoid eavesdropping
- Integrity: the traffic plaintext cannot be tampered
- Authentication: (optional) the client can verify the identity of the server and the server can verify the identity of the client to avoid man-in-the-middle attacks

To use connections secured with TLS, you first need to configure the TiDB server to enable TLS. Then you need to configure the client application to use TLS. Most client libraries enable TLS automatically when the server has TLS support configured correctly.

Similar to MySQL, TiDB allows TLS and non-TLS connections on the same TCP port. For a TiDB server with TLS enabled, you can choose to securely connect to the TiDB server through an encrypted connection, or to use an unencrypted connection. You can use the following ways to require the use of secure connections:

+ Configure the system variable [`require_secure_transport`](https://docs.pingcap.com/tidb/stable/system-variables#require_secure_transport-new-in-v610) to require secure connections to the TiDB server for all users.
+ Specify `REQUIRE SSL` when you create a user (`create user`), or modify an existing user (`alter user`), which is to specify that specified users must use TLS connections to access TiDB. The following is an example of creating a user:

    ```sql
    CREATE USER 'u1'@'%' IDENTIFIED BY 'my_random_password' REQUIRE SSL;
    ```

> **Note:**
>
> If the login user has configured using the [TiDB Certificate-Based Authentication for Login](https://docs.pingcap.com/tidb/stable/certificate-authentication#configure-the-user-certificate-information-for-login-verification), the user is implicitly required to enable the encrypted connection to TiDB.
## Configure TiDB server to use secure connections

See the following descriptions about the related parameters to enable secure connections:

- [`auto-tls`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#auto-tls): enables automatic certificate generation (since v5.2.0)
- [`ssl-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-cert): specifies the file path of the SSL certificate
- [`ssl-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-key): specifies the private key that matches the certificate
- [`ssl-ca`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-ca): (optional) specifies the file path of the trusted CA certificate
- [`tls-version`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tls-version): (optional) specifies the minimum TLS version, e.g. "TLSv1.2"

`auto-tls` allows secure connections but does not provide client certificate validation. For certificate validation, and to control how certificates are generated, see the advice on configuring the `ssl-cert`, `ssl-key` and `ssl-ca` variables below.

To enable secure connections with your own certificates in the TiDB server, you must specify both of the `ssl-cert` and `ssl-key` parameters in the configuration file when you start the TiDB server. You can also specify the `ssl-ca` parameter for client authentication (see [Enable authentication](#enable-authentication)).

All the files specified by the parameters are in PEM (Privacy Enhanced Mail) format. Currently, TiDB does not support the import of a password-protected private key, so it is required to provide a private key file without a password. If the certificate or private key is invalid, the TiDB server starts as usual, but the client cannot connect to the TiDB server through a TLS connection.

If the certificate parameters are correct, TiDB outputs `mysql protocol server secure connection is enabled` to the logs on `"INFO"` level when started.
## Configure the MySQL client to use TLS connections

The client of MySQL 5.7 or later versions attempts to establish a TLS connection by default. If the server does not support TLS connections, it automatically returns to unencrypted connections. The client of MySQL earlier than version 5.7 uses the non-TLS connections by default.

You can change the connection behavior of the client using the following `--ssl-mode` parameters:

- `--ssl-mode=REQUIRED`: The client requires a TLS connection. The connection cannot be established if the server side does not support TLS connections.
- In the absence of the `--ssl-mode` parameter: The client attempts to use a TLS connection, but the encrypted connection cannot be established if the server side does not support encrypted connections. Then the client uses an unencrypted connection.
- `--ssl-mode=DISABLED`: The client uses an unencrypted connection.

MySQL 8.x clients have two SSL modes in addition to this parameter:

- `--ssl-mode=VERIFY_CA`: Validates the certificate from the server against the CA that requires `--ssl-ca`.
- `--ssl-mode=VERIFY_IDENTITY`: The same as `VERIFY_CA`, but also validating whether the hostname you are connecting to matches the certificate.

For MySQL 5.7 and MariaDB clients and earlier you can use `--ssl-verify-server-cert` to enable validation of the server certificate.

For more information, see [Client-Side Configuration for Encrypted Connections](https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html#using-encrypted-connections-client-side-configuration) in MySQL.
## Enable authentication

If the `ssl-ca` parameter is not specified in the TiDB server or MySQL client, the client or the server does not perform authentication by default and cannot prevent man-in-the-middle attack. For example, the client might "securely" connect to a disguised client. You can configure the `ssl-ca` parameter for authentication in the server and client. Generally, you only need to authenticate the server, but you can also authenticate the client to further enhance the security.

+ To authenticate the TiDB server from the MySQL client:
  1. Specify the `ssl-cert` and `ssl-key` parameters in the TiDB server.
  2. Specify the `--ssl-ca` parameter in the MySQL client.
  3. Specify the `--ssl-mode` to `VERIFY_CA` at least in the MySQL client.
  4. Make sure that the certificate (`ssl-cert`) configured in the TiDB server is signed by the CA specified by the client `--ssl-ca` parameter; otherwise, the authentication fails.

+ To authenticate the MySQL client from the TiDB server:
  1. Specify the `ssl-cert`, `ssl-key`, and `ssl-ca` parameters in the TiDB server.
  2. Specify the `--ssl-cert` and `--ssl-key` parameters in the client.
  3. Make sure the server-configured certificate and the client-configured certificate are both signed by the `ssl-ca` specified by the server.

- To perform mutual authentication, meet both of the above requirements.

By default, the server-to-client authentication is optional. Even if the client does not present its certificate of identification during the TLS handshake, the TLS connection can be still established. You can also require the client to be authenticated by specifying `REQUIRE x509` when creating a user (`CREATE USER`), or modifying an existing user (`ALTER USER`). The following is an example of creating a user:

```sql
CREATE USER 'u1'@'%'  REQUIRE X509;
```

> **Note:**
>
> If the login user has configured using the [TiDB Certificate-Based Authentication for Login](https://docs.pingcap.com/tidb/stable/certificate-authentication#configure-the-user-certificate-information-for-login-verification), the user is implicitly required to enable the TLS connection to TiDB.
## Check whether the current connection uses encryption

Use the `SHOW STATUS LIKE "%Ssl%";` statement to get the details of the current connection, including whether encryption is used, the encryption protocol used by encrypted connections and the TLS version number.

See the following example of the result in an encrypted connection. The results change according to different TLS versions or encryption protocols supported by the client.

```sql
SHOW STATUS LIKE "Ssl%";
```

```
+-----------------------+------------------------------------------------------->
| Variable_name         | Value                                                 >
+-----------------------+------------------------------------------------------->
| Ssl_cipher            | TLS_AES_128_GCM_SHA256                                >
| Ssl_cipher_list       | RC4-SHA:DES-CBC3-SHA:AES128-SHA:AES256-SHA:AES128-SHA2>
| Ssl_server_not_after  | Apr 23 07:59:47 2024 UTC                              >
| Ssl_server_not_before | Jan 24 07:59:47 2024 UTC                              >
| Ssl_verify_mode       | 5                                                     >
| Ssl_version           | TLSv1.3                                               >
+-----------------------+------------------------------------------------------->
6 rows in set (0.0062 sec)
```

If the `Ssl_cipher` value is not empty, the connection is encrypted.

For the official MySQL client, you can also use the `STATUS` or `\s` statement to view the connection status:

```
mysql> \s
...
SSL: Cipher in use is TLS_AES_128_GCM_SHA256
...
```
## Supported TLS versions, key exchange protocols, and encryption algorithms

The TLS versions, key exchange protocols and encryption algorithms supported by TiDB are determined by the official Go libraries.

The crypto policy for your operating system and the client library you are using might also impact the list of supported protocols and cipher suites.
### Supported TLS versions

- TLSv1.2
- TLSv1.3

You can use the [`tls-version`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tls-version) configuration option to limit the TLS versions that can be used.

The actual TLS versions that can be used depend on the OS crypto policy, MySQL client version and the SSL/TLS library that is used by the client.
