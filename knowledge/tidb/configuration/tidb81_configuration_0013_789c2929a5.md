# Create and verify CA, server, and client certificates

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/certificate-authentication.md`
- Source Title: `Certificate-Based Authentication for Login`
- Source Heading Path: `Certificate-Based Authentication for Login | Certificate-Based Authentication for Login > Create security keys and certificates | Certificate-Based Authentication for Login > Create security keys and certificates > Generate CA key and certificate | Certificate-Based Authentication for Login > Create security keys and certificates > Generate server key and certificate | Certificate-Based Authentication for Login > Create security keys and certificates > Generate client key and certificate | Certificate-Based Authentication for Login > Create security keys and certificates > Verify certificate`
- Source Line Ranges: `5-222`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `sql`
- Topic Tags: `certificate-authentication`, `tls`, `openssl`, `ca`, `server-certificate`, `client-certificate`, `verification`, `x509`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0013_789c2929a5`
- Source ID: `tidb-docs-8.1:certificate-authentication.md#certificate-based-authentication-for-login`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0054c385357724fc85985bebd13c1d873a39d6554c7176e3538735204524247c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/certificate-authentication#certificate-based-authentication-for-login
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/certificate-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact OpenSSL commands and verification output for generating a CA key and certificate, a server key and certificate, a client key and certificate, and checking them for certificate-based login.
- Retrieval Keywords: certificate-based authentication for login, Create security keys and certificates, Generate CA key and certificate, Generate server key and certificate, Generate client key and certificate, Verify certificate, openssl genrsa 2048 > ca-key.pem, openssl req -new -x509 -nodes -days 365000 -key ca-key.pem -out ca-cert.pem, openssl req -newkey rsa:2048 -days 365000 -nodes -keyout server-key.pem -out server-req.pem, openssl x509 -req -in server-req.pem -days 365000 -CA ca-cert.pem -CAkey ca-key.pem -set_serial 01 -out server-cert.pem, openssl req -newkey rsa:2048 -days 365000 -nodes -keyout client-key.pem -out client-req.pem, openssl x509 -req -in client-req.pem -days 365000 -CA ca-cert.pem -CAkey ca-key.pem -set_serial 01 -out client-cert.pem, openssl verify -CAfile ca-cert.pem server-cert.pem client-cert.pem, server-cert.pem: OK, client-cert.pem: OK, subject section, x509
- Follow-up Guidance: The `subject` information shown in the generated certificate output is referenced later for login verification configuration in the `require` section.
- Classification Note: This chunk is classified as configuration because it provides the concrete certificate creation and verification commands and explains that TiDB checks the certificate `subject` information during login.

## Official Source Content

# Certificate-Based Authentication for Login

TiDB supports a certificate-based authentication method for users to log into TiDB. With this method, TiDB issues certificates to different users, uses encrypted connections to transfer data, and verifies certificates when users log in. This approach is more secure than the traditional password-based authentication method commonly used by MySQL users and is thus adopted by an increasing number of users.

To use certificate-based authentication, you might need to perform the following operations:

+ Create security keys and certificates
+ Configure certificates for TiDB and the client
+ Configure the user certificate information to be verified when the user logs in
+ Update and replace certificates

The rest of the document introduces in detail how to perform these operations.
## Create security keys and certificates

It is recommended that you use [OpenSSL](https://www.openssl.org/) to create keys and certificates. The certificate generation process is similar to the process described in [Enable TLS Between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers). The following paragraphs demonstrate how to configure more attribute fields that need to be verified in the certificate.

It is recommended that you use [OpenSSL](https://www.openssl.org/) to create keys and certificates. The certificate generation process is similar to the process described in [Enable TLS Between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers). The following paragraphs demonstrate how to configure more attribute fields that need to be verified in the certificate.
### Generate CA key and certificate

1. Execute the following command to generate the CA key:

    ```bash
    sudo openssl genrsa 2048 > ca-key.pem
    ```

    The output of the above command:

    ```
    Generating RSA private key, 2048 bit long modulus (2 primes)
    ....................+++++
    ...............................................+++++
    e is 65537 (0x010001)
    ```

2. Execute the following command to generate the certificate corresponding to the CA key:

    ```bash
    sudo openssl req -new -x509 -nodes -days 365000 -key ca-key.pem -out ca-cert.pem
    ```

3. Enter detailed certificate information. For example:

    ```bash
    Country Name (2 letter code) [AU]:US
    State or Province Name (full name) [Some-State]:California
    Locality Name (e.g. city) []:San Francisco
    Organization Name (e.g. company) [Internet Widgits Pty Ltd]:PingCAP Inc.
    Organizational Unit Name (e.g. section) []:TiDB
    Common Name (e.g. server FQDN or YOUR name) []:TiDB admin
    Email Address []:s@pingcap.com
    ```

    > **Note:**
    >
    > In the above certificate details, texts after `:` are the entered information.
### Generate server key and certificate

1. Execute the following command to generate the server key:

    ```bash
    sudo openssl req -newkey rsa:2048 -days 365000 -nodes -keyout server-key.pem -out server-req.pem
    ```

2. Enter detailed certificate information. For example:

    ```bash
    Country Name (2 letter code) [AU]:US
    State or Province Name (full name) [Some-State]:California
    Locality Name (e.g. city) []:San Francisco
    Organization Name (e.g. company) [Internet Widgits Pty Ltd]:PingCAP Inc.
    Organizational Unit Name (e.g. section) []:TiKV
    Common Name (e.g. server FQDN or YOUR name) []:TiKV Test Server
    Email Address []:k@pingcap.com

    Please enter the following 'extra' attributes
    to be sent with your certificate request
    A challenge password []:
    An optional company name []:
    ```

3. Execute the following command to generate the RSA key of the server:

    ```bash
    sudo openssl rsa -in server-key.pem -out server-key.pem
    ```

    The output of the above command:

    ```bash
    writing RSA key
    ```

4. Use the CA certificate signature to generate the signed server certificate:

    ```bash
    sudo openssl x509 -req -in server-req.pem -days 365000 -CA ca-cert.pem -CAkey ca-key.pem -set_serial 01 -out server-cert.pem
    ```

    The output of the above command (for example):

    ```bash
    Signature ok
    subject=C = US, ST = California, L = San Francisco, O = PingCAP Inc., OU = TiKV, CN = TiKV Test Server, emailAddress = k@pingcap.com
    Getting CA Private Key
    ```

    > **Note:**
    >
    > When you log in, TiDB checks whether the information in the `subject` section of the above output is consistent or not.
### Generate client key and certificate

After generating the server key and certificate, you need to generate the key and certificate for the client. It is often necessary to generate different keys and certificates for different users.

1. Execute the following command to generate the client key:

    ```bash
    sudo openssl req -newkey rsa:2048 -days 365000 -nodes -keyout client-key.pem -out client-req.pem
    ```

2. Enter detailed certificate information. For example:

    ```bash
    Country Name (2 letter code) [AU]:US
    State or Province Name (full name) [Some-State]:California
    Locality Name (e.g. city) []:San Francisco
    Organization Name (e.g. company) [Internet Widgits Pty Ltd]:PingCAP Inc.
    Organizational Unit Name (e.g. section) []:TiDB
    Common Name (e.g. server FQDN or YOUR name) []:tpch-user1
    Email Address []:zz@pingcap.com

    Please enter the following 'extra' attributes
    to be sent with your certificate request
    A challenge password []:
    An optional company name []:
    ```

3. Execute the following command to generate the RSA key of the client:

    ```bash
    sudo openssl rsa -in client-key.pem -out client-key.pem
    ```

    The output of the above command:

    ```bash
    writing RSA key
    ```

4. Use the CA certificate signature to generate the client certificate:

    ```bash
    sudo openssl x509 -req -in client-req.pem -days 365000 -CA ca-cert.pem -CAkey ca-key.pem -set_serial 01 -out client-cert.pem
    ```

    The output of the above command (for example):

    ```bash
    Signature ok
    subject=C = US, ST = California, L = San Francisco, O = PingCAP Inc., OU = TiDB, CN = tpch-user1, emailAddress = zz@pingcap.com
    Getting CA Private Key
    ```

    > **Note:**
    >
    > The information of the `subject` section in the above output is used for [certificate configuration for login verification](#configure-the-user-certificate-information-for-login-verification) in the `require` section.
### Verify certificate

Execute the following command to verify certificate:

```bash
openssl verify -CAfile ca-cert.pem server-cert.pem client-cert.pem
```

If the certificate is verified, you will see the following result:

```
server-cert.pem: OK
client-cert.pem: OK
```
