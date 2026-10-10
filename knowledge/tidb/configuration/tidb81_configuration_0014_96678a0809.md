# Configure TiDB, client certificates, and X.509 login requirements

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/certificate-authentication.md`
- Source Title: `Certificate-Based Authentication for Login`
- Source Heading Path: `Certificate-Based Authentication for Login > Configure TiDB and the client to use certificates | Certificate-Based Authentication for Login > Configure TiDB and the client to use certificates > Configure TiDB to use server certificate | Certificate-Based Authentication for Login > Configure TiDB and the client to use certificates > Configure the client to use client certificate | Certificate-Based Authentication for Login > Configure the user certificate information for login verification | Certificate-Based Authentication for Login > Configure the user certificate information for login verification > Get user certificate information`
- Source Line Ranges: `223-321`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `certificate-authentication`, `tls`, `server-certificate`, `client-certificate`, `x509`, `require-subject`, `require-issuer`, `require-san`, `require-cipher`, `user-authentication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0014_96678a0809`
- Source ID: `tidb-docs-8.1:certificate-authentication.md#configure-tidb-and-the-client-to-use-certificates`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `00ad30a79c355dd8c0b6ef75f97fce494ea223b324ef1052587f94db88486e9c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/certificate-authentication#configure-tidb-and-the-client-to-use-certificates
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/certificate-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact TiDB `[security]` settings, MySQL client TLS options, and X.509 `REQUIRE SUBJECT`, `REQUIRE ISSUER`, `REQUIRE SAN`, or `REQUIRE CIPHER` details for certificate-based login verification.
- Retrieval Keywords: Configure TiDB and the client to use certificates, [security], ssl-cert, ssl-key, ssl-ca, mysql protocol server secure connection is enabled, client verification enabled, mysql --ssl-cert --ssl-key --ssl-ca, Configure the user certificate information for login verification, Get user certificate information, REQUIRE SUBJECT, REQUIRE ISSUER, REQUIRE SAN, REQUIRE CIPHER, openssl x509 -noout -subject -in client-cert.pem, openssl x509 -noout -subject -in ca-cert.pem, openssl x509 -noout -extensions subjectAltName -in client.crt, SHOW SESSION STATUS LIKE 'Ssl_cipher_list';, CREATE USER 'u1'@'%' REQUIRE SAN, Subject Alternative Name, URI, IP, DNS, x509
- Follow-up Guidance: This chunk includes the commands to extract the client certificate subject, CA subject, and `subjectAltName`, plus the SQL statement to check `Ssl_cipher_list` and an example `CREATE USER ... REQUIRE SAN` statement.
- Classification Note: This chunk is classified as configuration because it defines the TiDB server TLS file settings, client certificate connection parameters, and the SQL and OpenSSL inputs used for X.509 login verification rules.

## Official Source Content

## Configure TiDB and the client to use certificates

After generating the certificates, you need to configure the TiDB server and the client to use the corresponding server certificate or client certificate.
### Configure TiDB to use server certificate

Modify the `[security]` section in the TiDB configuration file. This step specifies the directory in which the CA certificate, the server key, and the server certificate are stored. You can replace `path/to/server-cert.pem`, `path/to/server-key.pem`, `path/to/ca-cert.pem` with your own directory.

```
[security]
ssl-cert ="path/to/server-cert.pem"
ssl-key ="path/to/server-key.pem"
ssl-ca="path/to/ca-cert.pem"
```

Start TiDB and check logs. If the following information is displayed in the log, the configuration is successful:

```
[INFO] [server.go:286] ["mysql protocol server secure connection is enabled"] ["client verification enabled"=true]
```
### Configure the client to use client certificate

Configure the client so that the client uses the client key and certificate for login.

Taking the MySQL client as an example, you can use the newly created client certificate, client key and CA by specifying `ssl-cert`, `ssl-key`, and `ssl-ca`:

```bash
mysql -utest -h0.0.0.0 -P4000 --ssl-cert /path/to/client-cert.new.pem --ssl-key /path/to/client-key.new.pem --ssl-ca /path/to/ca-cert.pem
```

> **Note:**
>
> `/path/to/client-cert.new.pem`, `/path/to/client-key.new.pem`, and `/path/to/ca-cert.pem` are the directory of the CA certificate, client key, and client certificate. You can replace them with your own directory.
## Configure the user certificate information for login verification

First, connect TiDB using the client to configure the login verification. Then, you can get and configure the user certificate information to be verified.
### Get user certificate information

The user certificate information can be specified by `REQUIRE SUBJECT`, `REQUIRE ISSUER`, `REQUIRE SAN`, and `REQUIRE CIPHER`, which are used to check the X.509 certificate attributes.

+ `REQUIRE SUBJECT`: Specifies the subject information of the client certificate when you log in. With this option specified, you do not need to configure `require ssl` or x509. The information to be specified is consistent with the entered subject information in [Generate client keys and certificates](#generate-client-key-and-certificate).

    To get this option, execute the following command:

    ```bash
    openssl x509 -noout -subject -in client-cert.pem | sed 's/.\{8\}//'  | sed 's/, /\//g' | sed 's/ = /=/g' | sed 's/^/\//'
    ```

+ `require issuer`: Specifies the `subject` information of the CA certificate that issues the user certificate. The information to be specified is consistent with the entered `subject` information in [Generate CA key and certificate](#generate-ca-key-and-certificate).

    To get this option, execute the following command:

    ```bash
    openssl x509 -noout -subject -in ca-cert.pem | sed 's/.\{8\}//'  | sed 's/, /\//g' | sed 's/ = /=/g' | sed 's/^/\//'
    ```

+ `require san`: Specifies the `Subject Alternative Name` information of the CA certificate that issues the user certificate. The information to be specified is consistent with the [`alt_names` of the `openssl.cnf` configuration file](https://docs.pingcap.com/tidb/stable/generate-self-signed-certificates) used to generate the client certificate.

    + Execute the following command to get the information of the `REQUIRE SAN` item in the generated certificate:

        ```shell
        openssl x509 -noout -extensions subjectAltName -in client.crt
        ```

    + `REQUIRE SAN` currently supports the following `Subject Alternative Name` check items:

        - URI
        - IP
        - DNS

    + Multiple check items can be configured after they are connected by commas. For example, configure `REQUIRE SAN` as follows for the `u1` user:

        ```sql
        CREATE USER 'u1'@'%' REQUIRE SAN 'DNS:d1,URI:spiffe://example.org/myservice1,URI:spiffe://example.org/myservice2';
        ```

        The above configuration only allows the `u1` user to log in to TiDB using the certificate with the URI item `spiffe://example.org/myservice1` or `spiffe://example.org/myservice2` and the DNS item `d1`.

+ `REQUIRE CIPHER`: Checks the cipher method supported by the client. Use the following statement to check the list of supported cipher methods:

    ```sql
    SHOW SESSION STATUS LIKE 'Ssl_cipher_list';
    ```
