# TiCDC client authentication methods and configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-client-authentication.md`
- Source Title: `TiCDC Client Authentication`
- Source Heading Path: `TiCDC Client Authentication | TiCDC Client Authentication > Use mTLS for client authentication | TiCDC Client Authentication > Use TiDB username and password for client authentication`
- Source Line Ranges: `5-122`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `shared`
- Topic Tags: `client-authentication`, `mtls`, `tls`, `user-authentication`, `credentials`, `openapi`, `command-line`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0175_ba8b9e9699`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-client-authentication.md#ticdc-client-authentication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `49361ba358bc35a0c47fa9bfe74b6d5836da480e403f1871781c9c8c5d36698e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-client-authentication#ticdc-client-authentication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-client-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiCDC client authentication options, related security settings, and how to pass mTLS certificates or TiDB username and password in the command-line tool or OpenAPI.
- Retrieval Keywords: TiCDC Client Authentication, mTLS, Mutual Transport Layer Security, security.mtls, security.client-user-required, security.client-allowed-user, TLS is enabled, TiCDC command-line tool, TiCDC OpenAPI, --cert, --key, --ca, --cacert, --user, --password, TICDC_CERT_PATH, TICDC_KEY_PATH, TICDC_CA_PATH, TICDC_USER, TICDC_PASSWORD, ~/.ticdc/credentials, cdc cli configure-credentials, cdc cli changefeed list, CREATE USER 'test'@'ticdc_ip_address' IDENTIFIED BY 'password', /api/v2/status
- Follow-up Guidance: The content also shows the credential lookup methods and examples for both `cdc cli changefeed list` and `curl -X GET http://127.0.0.1:8300/api/v2/status`.
- Classification Note: This is classified as configuration because the content defines TiCDC server security parameters and the exact client-side flags, environment variables, and credential file locations for authentication.

## Official Source Content

# TiCDC Client Authentication

Starting from v8.1.0, TiCDC supports client authentication using Mutual Transport Layer Security (mTLS) or TiDB username and password. 

- mTLS authentication provides security control at the transport layer, enabling TiCDC to verify the client identity.
- TiDB username and password authentication provides security control at the application layer, ensuring that only authorized users can log in through the TiCDC node.

These two authentication methods can be used either independently or in combination to meet different scenarios and security requirements. 

> **Note:**
>
> To ensure the security of network access, it is strongly recommended to use TiCDC client authentication only when [TLS is enabled](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers). If TLS is not enabled, the username and password are transmitted as plaintext over the network, which can lead to serious credential leaks.
## Use mTLS for client authentication

1. In the TiCDC server, configure the `security.mtls` parameter as `true` to enable mTLS authentication:

    ```toml
    [security]
    # This parameter controls whether to enable the TLS client authentication. The default value is false.
    mtls = true
    ```

2. Configure the client certificate.

    <div label="TiCDC command-line tool" value="cdc-cli">

    When using the [TiCDC command-line tool](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed), you can specify the client certificate using the following methods. TiCDC will attempt to read the client certificate in the following order:

    1. Specify the certificate and private key using the command-line parameters `--cert` and `--key`. If the server uses a self-signed certificate, you also need to specify the trusted CA certificate using the `--ca` parameter.

        ```bash
        cdc cli changefeed list --cert client.crt --key client.key --ca ca.crt
        ```

    2. Specify the paths to the certificate, private key, and CA certificate using the environment variables `TICDC_CERT_PATH`, `TICDC_KEY_PATH`, and `TICDC_CA_PATH`.

        ```bash
        export TICDC_CERT_PATH=client.crt
        export TICDC_KEY_PATH=client.key
        export TICDC_CA_PATH=ca.crt
        ```

    3. Specify the certificate using the shared credential file `~/.ticdc/credentials`. You can modify the configuration using the `cdc cli configure-credentials` command.

    </div>

    <div label="TiCDC OpenAPI" value="cdc-api">

    When using [TiCDC OpenAPI](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2), you can specify the client certificate and private key using `--cert` and `--key`. If the server uses a self-signed certificate, you also need to specify the trusted CA certificate using the `--cacert` parameter. For example:

    ```bash
    curl -X GET http://127.0.0.1:8300/api/v2/status --cert client.crt --key client.key --cacert ca.crt
    ```

    </div>
## Use TiDB username and password for client authentication

1. [Create a user](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user) in TiDB and grant the user permission to log in from the TiCDC node.

    ```sql
    CREATE USER 'test'@'ticdc_ip_address' IDENTIFIED BY 'password';
    ```

2. In the TiCDC server, configure `security.client-user-required` and `security.client-allowed-user` to enable username and password authentication:

    ```toml
    [security]
    # This parameter controls whether to use username and password for client authentication. The default value is false.
    client-user-required = true
    # This parameter lists the usernames that are allowed for client authentication. Authentication requests with usernames not in this list will be rejected. The default value is null.
    client-allowed-user = ["test"]
    ```

3. Specify the username and password of the user created in step 1.

    <div label="TiCDC command-line tool" value="cdc-cli">

    When using the [TiCDC command-line tool](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed), you can specify the username and password using the following methods. TiCDC will attempt to read the client certificate in the following order:

    1. Specify the username and password using the command-line parameters `--user` and `--password`:

        ```bash
        cdc cli changefeed list --user test --password password
        ```

    2. Specify the username using the command-line parameter `--user`. Then, enter the password in the terminal:

        ```bash
        cdc cli changefeed list --user test
        ```

    3. Specify the username and password using the environment variables `TICDC_USER` and `TICDC_PASSWORD`:

        ```bash
        export TICDC_USER=test
        export TICDC_PASSWORD=password
        ```

    4. Specify the username and password using the shared credential file  `~/.ticdc/credentials`. You can modify the configuration using the `cdc cli configure-credentials` command.

    </div>

    <div label="TiCDC OpenAPI" value="cdc-api">

    When using [TiCDC OpenAPI](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2), you can specify the username and password using `--user <user>:<password>`. For example:

    ```bash
    curl -X GET http://127.0.0.1:8300/api/v2/status --user test:password
    ```

    </div>
