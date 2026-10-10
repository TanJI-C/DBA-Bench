# Pulsar authentication and authorization configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-pulsar.md`
- Source Title: `Replicate Data to Pulsar`
- Source Heading Path: `Replicate Data to Pulsar > Use Sink URI and changefeed config to configure Pulsar > TiCDC authentication and authorization for Pulsar`
- Source Line Ranges: `170-250`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `pulsar`, `authentication`, `authorization`, `token`, `mtls`, `oauth2`, `sink-uri`, `changefeed-config`, `tls`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0192_a6fb29abd5`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-pulsar.md#ticdc-authentication-and-authorization-for-pulsar`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf5303cc0faff98f058857e3dbb045452003ad3927bf83f44512b3c6b4baf6b3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-pulsar#ticdc-authentication-and-authorization-for-pulsar
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-pulsar.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiCDC Pulsar sink authentication configuration examples in sink URI and changefeed config for token, token-from-file, mTLS, or OAuth2.
- Retrieval Keywords: TiCDC authentication and authorization for Pulsar, --sink-uri, [sink.pulsar-config], authentication-token, token-from-file, auth-tls-certificate-path, auth-tls-private-key-path, tls-trust-certs-file-path, oauth2.oauth2-issuer-url, oauth2.oauth2-audience, oauth2.oauth2-private-key, oauth2.oauth2-client-id, oauth2.oauth2-scope, pulsar+ssl://127.0.0.1:6651, protocol=canal-json, OAuth2 authentication for Pulsar
- Follow-up Guidance: The chunk includes sample sink URIs and the exact `sink.pulsar-config` parameters for each authentication method.
- Classification Note: This is classified as configuration because the content consists of concrete TiCDC Pulsar sink authentication parameters and sink URI examples.

## Official Source Content

### TiCDC authentication and authorization for Pulsar

The following is a sample configuration when you use token authentication with Pulsar:

- Token

    Sink URI: 

    ```shell
    --sink-uri="pulsar://127.0.0.1:6650/persistent://public/default/yktest?protocol=canal-json"
    ```

    Config parameter: 

    ```shell
    [sink.pulsar-config]
    authentication-token = "xxxxxxxxxxxxx"
    ```

- Token from file

    Sink URI: 

    ```shell
    --sink-uri="pulsar://127.0.0.1:6650/persistent://public/default/yktest?protocol=canal-json"
    ```

    Config parameter: 

    ```toml
    [sink.pulsar-config]
    # Pulsar uses tokens for authentication on the Pulsar server. Specify the path to the token file, which will be read from the TiCDC server.
    token-from-file="/data/pulsar/token-file.txt"
    ```

- mTLS authentication

    Sink URI: 

    ```shell
    --sink-uri="pulsar+ssl://127.0.0.1:6651/persistent://public/default/yktest?protocol=canal-json"
    ```

    Config parameters: 

    ```toml
    [sink.pulsar-config]
    # Certificate path of the Pulsar mTLS authentication
    auth-tls-certificate-path="/data/pulsar/certificate"
    # Private key path of the Pulsar mTLS authentication
    auth-tls-private-key-path="/data/pulsar/certificate.key"
    # Path to the trusted certificate file of the Pulsar mTLS authentication
    tls-trust-certs-file-path="/data/pulsar/tls-trust-certs-file"
    ```

- OAuth2 authentication

    Starting from v7.5.1 and v8.0.0, TiCDC supports the OAuth2 authentication for Pulsar.

    Sink URI: 

    ```shell
    --sink-uri="pulsar://127.0.0.1:6650/persistent://public/default/yktest?protocol=canal-json"
    ```

    Config parameters: 

    ```toml
    [sink.pulsar-config]
    # Pulsar oauth2 issuer-url. For more information, see the Pulsar website: https://pulsar.apache.org/docs/2.10.x/client-libraries-go/#oauth2-authentication
    oauth2.oauth2-issuer-url="https://xxxx.auth0.com"
    # Pulsar oauth2 audience
    oauth2.oauth2-audience="https://xxxx.auth0.com/api/v2/"
    # Pulsar oauth2 private-key
    oauth2.oauth2-private-key="/data/pulsar/privateKey"
    # Pulsar oauth2 client-id
    oauth2.oauth2-client-id="0Xx...Yyxeny"
    # Pulsar oauth2 oauth2-scope
    oauth2.oauth2-scope="xxxx"
    ```
