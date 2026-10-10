# Enable TLS between DM-master, DM-worker, and dmctl

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-enable-tls.md`
- Source Title: `Enable TLS for DM Connections`
- Source Heading Path: `Enable TLS for DM Connections | Enable TLS for DM Connections > Enable encrypted data transmission between DM-master, DM-worker, and dmctl | Enable TLS for DM Connections > Enable encrypted data transmission between DM-master, DM-worker, and dmctl > Configure and enable encrypted data transmission | Enable TLS for DM Connections > Enable encrypted data transmission between DM-master, DM-worker, and dmctl > Verify component caller's identity | Enable TLS for DM Connections > Enable encrypted data transmission between DM-master, DM-worker, and dmctl > Reload certificates`
- Source Line Ranges: `5-87`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `tls`, `certificates`, `encrypted-connections`, `component-authentication`, `common-name`, `certificate-reload`, `dmctl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0073_d118038c3d`
- Source ID: `tidb-docs-8.1:dm/dm-enable-tls.md#enable-tls-for-dm-connections`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b64dce607e71829610ee776792683a6ccdbb8b3fe648e36b0091684a06154e54`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-enable-tls#enable-tls-for-dm-connections
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-enable-tls.md

## Retrieval Guidance

- Use When: Use this content when configuring TLS for connections among DM-master, DM-worker, and dmctl, including certificate paths, Common Name verification, and certificate reload behavior.
- Retrieval Keywords: DM-master, DM-worker, dmctl, Enable TLS for DM Connections, ssl-ca, ssl-cert, ssl-key, cert-allowed-cn, Common Name, CN, caller verification, encrypted data transmission, reload certificates, ./dmctl --master-addr=127.0.0.1:8261 --ssl-ca --ssl-cert --ssl-key
- Follow-up Guidance: The content also states that DM-master, DM-worker, and dmctl reread the current certificates and key files each time a new connection is created, and that restarting DM components reloads updated files specified by `ssl-ca`, `ssl-cert`, or `ssl-key`.
- Classification Note: This is classified as configuration because the official content provides TLS-related configuration items and command-line arguments for DM-master, DM-worker, and dmctl, including `ssl-ca`, `ssl-cert`, `ssl-key`, and `cert-allowed-cn`.

## Official Source Content

# Enable TLS for DM Connections

This document describes how to enable encrypted data transmission for DM connections, including connections between the DM-master, DM-worker, and dmctl components, and connections between DM and the upstream or downstream database.
## Enable encrypted data transmission between DM-master, DM-worker, and dmctl

This section introduces how to enable encrypted data transmission between DM-master, DM-worker, and dmctl.
### Configure and enable encrypted data transmission

1. Prepare certificates.

    It is recommended to prepare a server certificate for DM-master and DM-worker separately. Make sure that the two components can authenticate each other. You can choose to share one client certificate for dmctl.

    To generate self-signed certificates, you can use `openssl`, `cfssl` and other tools based on `openssl`, such as `easy-rsa`.

    If you choose `openssl`, you can refer to [generating self-signed certificates](https://docs.pingcap.com/tidb/stable/dm/dm-generate-self-signed-certificates).

2. Configure certificates.

    > **Note:**
    >
    > You can configure DM-master, DM-worker, and dmctl to use the same set of certificates.

    - DM-master

        Configure in the configuration file or command-line arguments:

        ```toml
        ssl-ca = "/path/to/ca.pem"
        ssl-cert = "/path/to/master-cert.pem"
        ssl-key = "/path/to/master-key.pem"
        ```

    - DM-worker

        Configure in the configuration file or command-line arguments:

        ```toml
        ssl-ca = "/path/to/ca.pem"
        ssl-cert = "/path/to/worker-cert.pem"
        ssl-key = "/path/to/worker-key.pem"
        ```

    - dmctl

        After enabling encrypted transmission in a DM cluster, if you need to connect to the cluster using dmctl, specify the client certificate. For example:

        ```bash
        ./dmctl --master-addr=127.0.0.1:8261 --ssl-ca /path/to/ca.pem --ssl-cert /path/to/client-cert.pem --ssl-key /path/to/client-key.pem
        ```
### Verify component caller's identity

The Common Name is used for caller verification. In general, the callee needs to verify the caller's identity, in addition to verifying the key, the certificates, and the CA provided by the caller. For example, DM-worker can only be accessed by DM-master, and other visitors are blocked even though they have legitimate certificates.

To verify component caller's identity, you need to mark the certificate user identity using `Common Name` (CN) when generating the certificate, and to check the caller's identity by configuring the `Common Name` list for the callee.

- DM-master

    Configure in the configuration file or command-line arguments:

    ```toml
    cert-allowed-cn = ["dm"]
    ```

- DM-worker

    Configure in the configuration file or command-line arguments:

    ```toml
    cert-allowed-cn = ["dm"]
    ```
### Reload certificates

To reload the certificates and the keys, DM-master, DM-worker, and dmctl reread the current certificates and the key files each time a new connection is created.

When the files specified by `ssl-ca`, `ssl-cert` or `ssl-key` are updated, restart DM components to reload the certificates and the key files and reconnect with each other.
