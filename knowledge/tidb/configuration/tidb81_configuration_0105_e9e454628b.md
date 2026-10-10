# Enable and verify TLS between TiDB cluster components

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/enable-tls-between-components.md`
- Source Title: `Enable TLS Between TiDB Components`
- Source Heading Path: `Enable TLS Between TiDB Components | Enable TLS Between TiDB Components > Configure and enable encrypted data transmission | Enable TLS Between TiDB Components > Configure and enable encrypted data transmission > Verify component caller's identity | Enable TLS Between TiDB Components > Reload certificates | Enable TLS Between TiDB Components > Certificate validity | Enable TLS Between TiDB Components > See also`
- Source Line Ranges: `5-219`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`, `tiup`
- Topic Tags: `tls`, `certificates`, `mutual-authentication`, `https`, `certificate-rotation`, `common-name`, `client-authentication`, `encrypted-transmission`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0105_e9e454628b`
- Source ID: `tidb-docs-8.1:enable-tls-between-components.md#enable-tls-between-tidb-components`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e83fd8e0040bc7415389036604cce77ebf723118e51a3c6bce43860c4c888f5d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/enable-tls-between-components#enable-tls-between-tidb-components
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/enable-tls-between-components.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official TLS configuration, Common Name verification settings, or certificate reload behavior for encrypted transmission between TiDB cluster components.
- Retrieval Keywords: Enable TLS Between TiDB Components, cluster-ssl-ca, cluster-ssl-cert, cluster-ssl-key, ca-path, cert-path, key-path, cacert-path, cluster-verify-cn, cert-allowed-cn, cert_allowed_cn, Common Name, Verify component caller's identity, Reload certificates, TiCDC security, tiflash.toml, tiflash-learner.toml, https URL, tidb-ctl --ssl-cert, tiup ctl:v<CLUSTER_VERSION> pd --cacert, tikv-ctl --ca-path
- Follow-up Guidance: The source also includes example client certificate flags for tidb-ctl, tiup ctl pd, and tikv-ctl after encrypted transmission is enabled, plus notes on certificate validity and automatic rereading or rotation without restarting the TiDB cluster.
- Classification Note: This is classified as configuration because the content provides component TLS certificate settings, HTTPS endpoint requirements, caller identity verification options, and certificate reload details for self-managed TiDB cluster components.

## Official Source Content

# Enable TLS Between TiDB Components

This document describes how to enable encrypted data transmission between components within a TiDB cluster. Once enabled, encrypted transmission is used between the following components:

- Communication between TiDB, TiKV, PD, and TiFlash
- TiDB Control and TiDB; TiKV Control and TiKV; PD Control and PD
- Internal communication within each TiDB, TiKV, PD, and TiFlash cluster

Currently, it is not supported to only enable encrypted transmission of some specific components.
## Configure and enable encrypted data transmission

1. Prepare certificates.

    It is recommended to prepare a server certificate for TiDB, TiKV, and PD separately. Make sure that these components can authenticate each other. The Control tools of TiDB, TiKV, and PD can choose to share one client certificate.

    You can use tools like `openssl`, `easy-rsa` and `cfssl` to generate self-signed certificates.

    If you choose `openssl`, you can refer to [generating self-signed certificates](https://docs.pingcap.com/tidb/stable/generate-self-signed-certificates).

    If you choose `openssl`, you can refer to [generating self-signed certificates](https://docs.pingcap.com/tidb/stable/generate-self-signed-certificates).

2. Configure certificates.

    To enable mutual authentication among TiDB components, configure the certificates of TiDB, TiKV, and PD as follows.

    - TiDB

        Configure in the configuration file or command-line arguments:

        ```toml
        [security]
        # Path of the file that contains list of trusted SSL CAs for connection with cluster components.
        cluster-ssl-ca = "/path/to/ca.pem"
        # Path of the file that contains X509 certificate in PEM format for connection with cluster components.
        cluster-ssl-cert = "/path/to/tidb-server.pem"
        # Path of the file that contains X509 key in PEM format for connection with cluster components.
        cluster-ssl-key = "/path/to/tidb-server-key.pem"
        ```

    - TiKV

        Configure in the configuration file or command-line arguments, and set the corresponding URL to `https`:

        ```toml
        [security]
        ## The path for certificates. An empty string means that secure connections are disabled.
        # Path of the file that contains a list of trusted SSL CAs. If it is set, the following settings `cert_path` and `key_path` are also needed.
        ca-path = "/path/to/ca.pem"
        # Path of the file that contains X509 certificate in PEM format.
        cert-path = "/path/to/tikv-server.pem"
        # Path of the file that contains X509 key in PEM format.
        key-path = "/path/to/tikv-server-key.pem"
        ```

    - PD

        Configure in the configuration file or command-line arguments, and set the corresponding URL to `https`:

        ```toml
        [security]
        ## The path for certificates. An empty string means that secure connections are disabled.
        # Path of the file that contains a list of trusted SSL CAs. If it is set, the following settings `cert_path` and `key_path` are also needed.
        cacert-path = "/path/to/ca.pem"
        # Path of the file that contains X509 certificate in PEM format.
        cert-path = "/path/to/pd-server.pem"
        # Path of the file that contains X509 key in PEM format.
        key-path = "/path/to/pd-server-key.pem"
        ```

    - TiFlash (New in v4.0.5)

        Configure in the `tiflash.toml` file:

        ```toml
        [security]
        ## The path for certificates. An empty string means that secure connections are disabled.
        # Path of the file that contains a list of trusted SSL CAs. If it is set, the following settings `cert_path` and `key_path` are also needed.
        ca_path = "/path/to/ca.pem"
        # Path of the file that contains X509 certificate in PEM format.
        cert_path = "/path/to/tiflash-server.pem"
        # Path of the file that contains X509 key in PEM format.
        key_path = "/path/to/tiflash-server-key.pem"
        ```

        Configure in the `tiflash-learner.toml` file:

        ```toml
        [security]
        # Path of the file that contains a list of trusted SSL CAs. If it is set, the following settings `cert_path` and `key_path` are also needed.
        ca-path = "/path/to/ca.pem"
        # Path of the file that contains X509 certificate in PEM format.
        cert-path = "/path/to/tiflash-server.pem"
        # Path of the file that contains X509 key in PEM format.
        key-path = "/path/to/tiflash-server-key.pem"
        ```

    - TiCDC

        Configure in the configuration file:

        ```toml
        [security]
        ca-path = "/path/to/ca.pem"
        cert-path = "/path/to/cdc-server.pem"
        key-path = "/path/to/cdc-server-key.pem"
        ```

        Alternatively, configure in the command-line arguments and set the corresponding URL to `https`:

        ```bash
        cdc server --pd=https://127.0.0.1:2379 --log-file=ticdc.log --addr=0.0.0.0:8301 --advertise-addr=127.0.0.1:8301 --ca=/path/to/ca.pem --cert=/path/to/ticdc-cert.pem --key=/path/to/ticdc-key.pem
        ```

        Now, encrypted transmission among TiDB components is enabled.

    > **Note:**
    >
    > After enabling encrypted transmission in a TiDB cluster, if you need to connect to the cluster using tidb-ctl, tikv-ctl, or pd-ctl, specify the client certificate. For example:

    ```bash
    ./tidb-ctl -u https://127.0.0.1:10080 --ca /path/to/ca.pem --ssl-cert /path/to/client.pem --ssl-key /path/to/client-key.pem
    ```

    ```bash
    tiup ctl:v<CLUSTER_VERSION> pd -u https://127.0.0.1:2379 --cacert /path/to/ca.pem --cert /path/to/client.pem --key /path/to/client-key.pem
    ```

    ```bash
    ./tikv-ctl --host="127.0.0.1:20160" --ca-path="/path/to/ca.pem" --cert-path="/path/to/client.pem" --key-path="/path/to/clinet-key.pem"
    ```
### Verify component caller's identity

The Common Name is used for caller verification. In general, the callee needs to verify the caller's identity, in addition to verifying the key, the certificates, and the CA provided by the caller. For example, TiKV can only be accessed by TiDB, and other visitors are blocked even though they have legitimate certificates.

To verify component caller's identity, you need to mark the certificate user identity using `Common Name` when generating the certificate, and to check the caller's identity by configuring the `Common Name` list for the callee.

> **Note:**
>
> Currently the `cert-allowed-cn` configuration item of the PD can only be set to one value. Therefore, the `commonName` of all authentication objects must be set to the same value.

- TiDB

    Configure in the configuration file or command-line arguments:

    ```toml
    [security]
    cluster-verify-cn = ["TiDB"]
    ```

- TiKV

    Configure in the configuration file or command-line arguments:

    ```toml
    [security]
    cert-allowed-cn = ["TiDB"]
    ```

- PD

    Configure in the configuration file or command-line arguments:

    ```toml
    [security]
    cert-allowed-cn = ["TiDB"]
    ```

- TiFlash (New in v4.0.5)

    Configure in the `tiflash.toml` file or command-line arguments:

    ```toml
    [security]
    cert_allowed_cn = ["TiDB"]
    ```

    Configure in the `tiflash-learner.toml` file:

    ```toml
    [security]
    cert-allowed-cn = ["TiDB"]
    ```
## Reload certificates

- If your TiDB cluster is deployed in a local data center, to reload the certificates and keys, TiDB, PD, TiKV, TiFlash, TiCDC, and all kinds of clients reread the current certificates and key files each time a new connection is created, without restarting the TiDB cluster.

- If your TiDB cluster is deployed on your own managed cloud, make sure that the issuance of TLS certificates is integrated with the certificate management service of the cloud provider. The TLS certificates of the TiDB, PD, TiKV, TiFlash, and TiCDC components can be automatically rotated without restarting the TiDB cluster.
## Certificate validity

You can customize the validity period of TLS certificates for each component in a TiDB cluster. For example, when using OpenSSL to issue and generate TLS certificates, you can set the validity period via the **days** parameter. For more information, see [Generate self-signed certificates](https://docs.pingcap.com/tidb/stable/generate-self-signed-certificates).
## See also

- [Enable TLS Between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers)
