# Generate self-signed certificates for DM components

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-generate-self-signed-certificates.md`
- Source Title: `Generate Self-signed Certificates for TiDB Data Migration`
- Source Heading Path: `Generate Self-signed Certificates for TiDB Data Migration | Generate Self-signed Certificates for TiDB Data Migration > Install OpenSSL | Generate Self-signed Certificates for TiDB Data Migration > Generate the CA certificate | Generate Self-signed Certificates for TiDB Data Migration > Issue certificates for individual components | Generate Self-signed Certificates for TiDB Data Migration > Issue certificates for individual components > Certificates that might be used in the cluster | Generate Self-signed Certificates for TiDB Data Migration > Issue certificates for individual components > Issue certificates for DM-master | Generate Self-signed Certificates for TiDB Data Migration > Issue certificates for individual components > Issue certificates for the client (dmctl)`
- Source Line Ranges: `5-185`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `shared`
- Topic Tags: `tls`, `openssl`, `self-signed-certificates`, `ca`, `san`, `dm-master`, `dm-worker`, `dmctl`, `client-authentication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0075_790d17828d`
- Source ID: `tidb-docs-8.1:dm/dm-generate-self-signed-certificates.md#generate-self-signed-certificates-for-tidb-data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `81a14c891e4c6eec1ecad85b051cd5e5a93c0f055db2907f825c272b452c1469`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-generate-self-signed-certificates#generate-self-signed-certificates-for-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-generate-self-signed-certificates.md

## Retrieval Guidance

- Use When: Use this chunk when searching for how to generate self-signed TLS certificates with OpenSSL for DM components such as DM-master, DM-worker, and dmctl, including CA creation and SAN configuration.
- Retrieval Keywords: Generate Self-signed Certificates for TiDB Data Migration, openssl, Install OpenSSL, apt install openssl, yum install openssl, CA certificate, openssl genrsa -out ca-key.pem 4096, openssl req -new -x509 -days 1000 -key ca-key.pem -out ca.pem, openssl x509 -text -in ca.pem -noout, DM-master, DM-worker, dmctl, master certificate, worker certificate, client certificate, master-key.pem, master-cert.pem, client-key.pem, client-cert.pem, openssl.cnf, req_extensions = v3_req, subjectAltName = @alt_names, SAN, Subject Alternative Name, [ alt_names ], IP, DNS, URI, 0.0.0.0, openssl req -new -key master-key.pem -out master-cert.pem -config openssl.cnf, openssl x509 -req -days 365 -CA ca.pem -CAkey ca-key.pem -CAcreateserial -in master-cert.pem -out master-cert.pem -extensions v3_req -extfile openssl.cnf, openssl req -new -key client-key.pem -out client-cert.pem, openssl x509 -req -days 365 -CA ca.pem -CAkey ca-key.pem -CAcreateserial -in client-cert.pem -out client-cert.pem
- Follow-up Guidance: The source also notes that issuing certificates for the DM-worker instance is similar to the DM-master process and that each component does not enable Common Name validation by default but it can be enabled in the configuration file.
- Classification Note: This chunk is classified as configuration because it provides the certificate generation procedure and the related OpenSSL configuration entries such as openssl.cnf, req_extensions, and subjectAltName for DM TLS setup.

## Official Source Content

# Generate Self-signed Certificates for TiDB Data Migration

This document provides an example of using `openssl` to generate a self-signed certificate for TiDB Data Migration (DM). You can also generate certificates and keys that meet requirements according to your demands.

Assume that the topology of the instance cluster is as follows:

| Name  | Host IP      | Services   |
| ----- | -----------  | ---------- |
| node1 | 172.16.10.11 | DM-master1 |
| node2 | 172.16.10.12 | DM-master2 |
| node3 | 172.16.10.13 | DM-master3 |
| node4 | 172.16.10.14 | DM-worker1 |
| node5 | 172.16.10.15 | DM-worker2 |
| node6 | 172.16.10.16 | DM-worker3 |
## Install OpenSSL

- For Debian or Ubuntu OS:

    ```bash
    apt install openssl
    ```

- For RedHat or CentOS OS:

    ```bash
    yum install openssl
    ```

You can also refer to OpenSSL's official [download document](https://www.openssl.org/source/) for installation.
## Generate the CA certificate

A certificate authority (CA) is a trusted entity that issues digital certificates. In practice, contact your administrator to issue the certificate or use a trusted CA. CA manages multiple certificate pairs. Here you only need to generate an original pair of certificates as follows.

1. Generate the CA key:

    ```bash
    openssl genrsa -out ca-key.pem 4096
    ```

2. Generate the CA certificates:

    ```bash
    openssl req -new -x509 -days 1000 -key ca-key.pem -out ca.pem
    ```

3. Validate the CA certificates:

    ```bash
    openssl x509 -text -in ca.pem -noout
    ```
## Issue certificates for individual components
### Certificates that might be used in the cluster

- The `master` certificate used by DM-master to authenticate DM-master for other components.
- The `worker` certificate used by DM-worker to authenticate DM-worker for other components.
- The `client` certificate used by dmctl to authenticate clients for DM-master and DM-worker.
### Issue certificates for DM-master

To issue a certificate to a DM-master instance, perform the following steps:

1. Generate the private key corresponding to the certificate:

    ```bash
    openssl genrsa -out master-key.pem 2048
    ```

2. Make a copy of the OpenSSL configuration template file (Refer to the actual location of your template file because it might have more than one location):

    ```bash
    cp /usr/lib/ssl/openssl.cnf .
    ```

    If you do not know the actual location, look for it in the root directory:

    ```bash
    find / -name openssl.cnf
    ```

3. Edit `openssl.cnf`, add `req_extensions = v3_req` under the `[ req ]` field, and add `subjectAltName = @alt_names` under the `[ v3_req ]` field. Finally, create a new field and edit the information of `Subject Alternative Name` (SAN) according to the cluster topology description above.

    ```
    [ alt_names ]
    IP.1 = 127.0.0.1
    IP.2 = 172.16.10.11
    IP.3 = 172.16.10.12
    IP.4 = 172.16.10.13
    ```

    The following checking items of SAN are currently supported:

    - `IP`
    - `DNS`
    - `URI`

    > **Note:**
    >
    > If a special IP such as `0.0.0.0` is to be used for connection or communication, you must also add it to `alt_names`.

4. Save the `openssl.cnf` file, and generate the certificate request file: (When giving input to `Common Name (e.g. server FQDN or YOUR name) []:`, you assign a Common Name (CN) to the certificate, such as `dm`. It is used by the server to validate the identity of the client. Each component does not enable the validation by default. You can enable it in the configuration file.)

    ```bash
    openssl req -new -key master-key.pem -out master-cert.pem -config openssl.cnf
    ```

5. Issue and generate the certificate:

    ```bash
    openssl x509 -req -days 365 -CA ca.pem -CAkey ca-key.pem -CAcreateserial -in master-cert.pem -out master-cert.pem -extensions v3_req -extfile openssl.cnf
    ```

6. Verify that the certificate includes the SAN field (optional):

    ```bash
    openssl x509 -text -in master-cert.pem -noout
    ```

7. Confirm that the following files exist in your current directory:

    ```
    ca.pem
    master-cert.pem
    master-key.pem
    ```

> **Note:**
>
> The process of issuing certificates for the DM-worker instance is similar and will not be repeated in this document.
### Issue certificates for the client (dmctl)

To issue a certificate to the client (dmctl), perform the following steps:

1. Generate the private key corresponding to the certificate:

    ```bash
    openssl genrsa -out client-key.pem 2048
    ```

2. Generate the certificate request file (in this step, you can also assign a Common Name to the certificate, which is used to allow the server to validate the identity of the client. Each component does not enable the validation by default, and you can enable it in the configuration file):

    ```bash
    openssl req -new -key client-key.pem -out client-cert.pem
    ```

3. Issue and generate the certificate:

    ```bash
    openssl x509 -req -days 365 -CA ca.pem -CAkey ca-key.pem -CAcreateserial -in client-cert.pem -out client-cert.pem
    ```
