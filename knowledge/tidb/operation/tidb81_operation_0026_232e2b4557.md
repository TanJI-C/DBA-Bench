# Update and replace CA, client, and server certificates

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/certificate-authentication.md`
- Source Title: `Certificate-Based Authentication for Login`
- Source Heading Path: `Certificate-Based Authentication for Login > Update and replace certificate | Certificate-Based Authentication for Login > Update and replace certificate > Update CA key and certificate | Certificate-Based Authentication for Login > Update and replace certificate > Update client key and certificate | Certificate-Based Authentication for Login > Update and replace certificate > Update the server key and certificate`
- Source Line Ranges: `393-501`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `sql`
- Topic Tags: `tls`, `ssl`, `certificate-rotation`, `ca-certificate`, `client-certificate`, `server-certificate`, `openssl`, `restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0026_232e2b4557`
- Source ID: `tidb-docs-8.1:certificate-authentication.md#update-and-replace-certificate`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e7b93722353e067bb0230c05c2b3ef537e4a60ba74734b14101565f04c9b496`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/certificate-authentication#update-and-replace-certificate
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/certificate-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when searching how to rotate or replace CA, client, and server certificates for TiDB with combined CA certificate handling.
- Retrieval Keywords: Update and replace certificate, Update CA key and certificate, Update client key and certificate, Update the server key and certificate, combined CA certificate, ca-key.pem, ca-cert.pem, ca-cert.new.pem, ca-cert.old.pem, client-key.new.pem, client-cert.new.pem, server-key.new.pem, server-cert.new.pem, openssl genrsa 2048, openssl req -new -x509 -nodes -days 365000, openssl x509 -req, restart the TiDB server, require issuer, require subject, mysql --ssl-cert --ssl-key --ssl-ca
- Follow-up Guidance: The source says to restart the TiDB server after creating the combined CA certificate, replace the CA certificate on both client and server first, and then replace the client or server key and certificate.
- Classification Note: This is classified as operation because it describes the certificate update and replacement procedure, including command sequences and restart timing.

## Official Source Content

## Update and replace certificate

The key and certificate are updated regularly. The following sections introduce how to update the key and certificate.

The CA certificate is the basis for mutual verification between the client and server. To replace the CA certificate, generate a combined certificate that supports the authentication for both old and new certificates. On the client and server, first replace the CA certificate, then replace the client/server key and certificate.
### Update CA key and certificate

1. Back up the old CA key and certificate (suppose that `ca-key.pem` is stolen):

    ```bash
    mv ca-key.pem ca-key.old.pem && \
    mv ca-cert.pem ca-cert.old.pem
    ```

2. Generate the new CA key:

    ```bash
    sudo openssl genrsa 2048 > ca-key.pem
    ```

3. Generate the new CA certificate using the newly generated CA key:

    ```bash
    sudo openssl req -new -x509 -nodes -days 365000 -key ca-key.pem -out ca-cert.new.pem
    ```

    > **Note:**
    >
    > Generating the new CA certificate is to replace the keys and certificates on the client and server, and to ensure that online users are not affected. Therefore, the appended information in the above command must be consistent with the `require issuer` information.

4. Generate the combined CA certificate:

    ```bash
    cat ca-cert.new.pem ca-cert.old.pem > ca-cert.pem
    ```

After the above operations, restart the TiDB server with the newly created combined CA certificate. Then the server accepts both the new and old CA certificates.

Also replace the old CA certificate with the combined certificate so that the client accepts both the old and new CA certificates.
### Update client key and certificate

> **Note:**
>
> Perform the following steps **only after** you have replaced the old CA certificate on the client and server with the combined CA certificate.

1. Generate the new RSA key of the client:

    ```bash
    sudo openssl req -newkey rsa:2048 -days 365000 -nodes -keyout client-key.new.pem -out client-req.new.pem && \
    sudo openssl rsa -in client-key.new.pem -out client-key.new.pem
    ```

    > **Note:**
    >
    > The above command is to replace the client key and certificate, and to ensure that the online users are not affected. Therefore, the appended information in the above command must be consistent with the `require subject` information.

2. Use the combined certificate and the new CA key to generate the new client certificate:

    ```bash
    sudo openssl x509 -req -in client-req.new.pem -days 365000 -CA ca-cert.pem -CAkey ca-key.pem -set_serial 01 -out client-cert.new.pem
    ```

3. Make the client (for example, MySQL) connect TiDB with the new client key and certificate:

    ```bash
    mysql -utest -h0.0.0.0 -P4000 --ssl-cert /path/to/client-cert.new.pem --ssl-key /path/to/client-key.new.pem --ssl-ca /path/to/ca-cert.pem
    ```

    > **Note:**
    >
    > `/path/to/client-cert.new.pem`, `/path/to/client-key.new.pem`, and `/path/to/ca-cert.pem` specify the directory of the CA certificate, client key, and client certificate. You can replace them with your own directory.
### Update the server key and certificate

1. Generate the new RSA key of the server:

    ```bash
    sudo openssl req -newkey rsa:2048 -days 365000 -nodes -keyout server-key.new.pem -out server-req.new.pem && \
    sudo openssl rsa -in server-key.new.pem -out server-key.new.pem
    ```

2. Use the combined CA certificate and the new CA key to generate the new server certificate:

    ```bash
    sudo openssl x509 -req -in server-req.new.pem -days 365000 -CA ca-cert.pem -CAkey ca-key.pem -set_serial 01 -out server-cert.new.pem
    ```

3. Configure the TiDB server to use the new server key and certificate. See [Configure TiDB server](#configure-tidb-and-the-client-to-use-certificates) for details.
