# Configure Pulsar sink URI auth and TLS

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-pulsar.md`
- Source Title: `Replicate Data to Pulsar`
- Source Heading Path: `Replicate Data to Pulsar > Use Sink URI and changefeed config to configure Pulsar | Replicate Data to Pulsar > Use Sink URI and changefeed config to configure Pulsar > Sink URI | Replicate Data to Pulsar > Use Sink URI and changefeed config to configure Pulsar > Changefeed config parameters | Replicate Data to Pulsar > Use Sink URI and changefeed config to configure Pulsar > Best practice | Replicate Data to Pulsar > Use Sink URI and changefeed config to configure Pulsar > TLS encrypted transmission`
- Source Line Ranges: `38-169`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `sink-uri`, `pulsar`, `changefeed-config`, `authentication`, `tls`, `mtls`, `oauth2`, `protocol`, `producer-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0191_4de9647f61`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-pulsar.md#use-sink-uri-and-changefeed-config-to-configure-pulsar`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ec28bc39a4b8a624beff8ef798b3cd207908e1c4a53801cb96ba35d0e4686b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-pulsar#use-sink-uri-and-changefeed-config-to-configure-pulsar
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-pulsar.md

## Retrieval Guidance

- Use When: Use this content when you need the exact Pulsar Sink URI format, Pulsar-related changefeed configuration keys, authentication options, producer cache settings, or TLS settings for a TiCDC Pulsar changefeed.
- Retrieval Keywords: pulsar://, pulsar+ssl://, [scheme]://[userinfo@][host]:[port][/path]?[query_parameters], protocol=canal-json, persistent://public/default/yktest, sink.pulsar-config, authentication-token, token-from-file, basic-user-name, basic-password, auth-tls-certificate-path, auth-tls-private-key-path, tls-trust-certs-file-path, tls-key-file-path, tls-certificate-file, oauth2.oauth2-issuer-url, oauth2.oauth2-audience, oauth2.oauth2-private-key, oauth2.oauth2-client-id, oauth2.oauth2-scope, pulsar-producer-cache-size, compression-type, connection-timeout, operation-timeout, batching-max-messages, batching-max-publish-delay, send-timeout, dispatchers, partition, TLS encrypted transmission
- Follow-up Guidance: It includes a TLS encrypted transmission example using `pulsar+ssl://127.0.0.1:6651/...` and notes that if `tlsRequireTrustedClientCertOnConnect=true` is configured on the Pulsar server, `tls-key-file-path` and `tls-certificate-file` also need to be set.
- Classification Note: This is classified as configuration because the content defines the Sink URI structure, lists changefeed configuration parameters under `[sink.pulsar-config]`, and documents authentication, routing, protocol, producer cache, and TLS-related settings.

## Official Source Content

## Use Sink URI and changefeed config to configure Pulsar

You can use Sink URI to specify the connection information for the TiCDC target system, and use changefeed config to configure parameters related to Pulsar.
### Sink URI

A Sink URI follows the following format:

```shell
[scheme]://[userinfo@][host]:[port][/path]?[query_parameters]
```

Configuration example 1:

```shell
--sink-uri="pulsar://127.0.0.1:6650/persistent://abc/def/yktest?protocol=canal-json"
```

Configuration example 2:

```shell
--sink-uri="pulsar://127.0.0.1:6650/yktest?protocol=canal-json"
```

The configurable parameters in a URI are as follows:

| Parameter           | Description                                                   |
| :------------------ | :------------------------------------------------------------ |
| `pulsar`             | The scheme for the downstream Pulsar. The value can be `pulsar` or `pulsar+ssl`.                        |
| `127.0.0.1`          | The IP address by which the downstream Pulsar provides service.             |
| `6650`               | The connection port for the downstream Pulsar.                              |
| `persistent://abc/def/yktest`   |  As shown in the preceding configuration example 1, this parameter is used to specify the tenant, namespace, and topic of Pulsar.   |
| `yktest`    | As shown in the preceding configuration example 2, if the topic you want to specify is in the default namespace `default` of the default tenant `public` in Pulsar, you can configure the URI with just the topic name, for example, `yktest`. This is equivalent to specifying the topic as `persistent://public/default/yktest`. |
### Changefeed config parameters

The following are examples of changefeed config parameters:

```toml
[sink]
# `dispatchers` is used to specify matching rules.
# Note: When the downstream MQ is Pulsar, if the routing rule for `partition` is not specified as any of `ts`, `index-value`, `table`, or `default`, each Pulsar message will be routed using the string you set as the key.
# For example, if you specify the routing rule for a matcher as the string `code`, then all Pulsar messages that match that matcher will be routed with `code` as the key.
# dispatchers = [
#    {matcher = ['test1.*', 'test2.*'], topic = "Topic expression 1", partition = "ts" },
#    {matcher = ['test3.*', 'test4.*'], topic = "Topic expression 2", partition = "index-value" },
#    {matcher = ['test1.*', 'test5.*'], topic = "Topic expression 3", partition = "table"},
#    {matcher = ['test6.*'], partition = "default"},
#    {matcher = ['test7.*'], partition = "test123"}
# ]

# `protocol` is used to specify the protocol format for encoding messages.
# When the downstream is Pulsar, the protocol can only be canal-json.
# protocol = "canal-json"

# The following parameters only take effect when the downstream is Pulsar.
[sink.pulsar-config]
# Authentication on the Pulsar server is done using a token. Specify the value of the token.
authentication-token = "xxxxxxxxxxxxx"
# When you use a token for Pulsar server authentication, specify the path to the file where the token is located.
token-from-file="/data/pulsar/token-file.txt"
# Pulsar uses the basic account and password to authenticate the identity. Specify the account.
basic-user-name="root"
# Pulsar uses the basic account and password to authenticate the identity. Specify the password.
basic-password="password"
# The certificate path on the client, which is required when Pulsar enables the mTLS authentication.
auth-tls-certificate-path="/data/pulsar/certificate"
# The private key path on the client, which is required when Pulsar enables the mTLS authentication.
auth-tls-private-key-path="/data/pulsar/certificate.key"
# The path to the trusted certificate file of the Pulsar TLS authentication, which is required when Pulsar enables the mTLS authentication or TLS encrypted transmission.
tls-trust-certs-file-path="/data/pulsar/tls-trust-certs-file"
# The path to the encrypted private key on the client, which is required when Pulsar enables TLS encrypted transmission.
tls-key-file-path="/data/pulsar/tls-key-file"
# The path to the encrypted certificate file on the client, which is required when Pulsar enables TLS encrypted transmission.
tls-certificate-file="/data/pulsar/tls-certificate-file"
# Pulsar oauth2 issuer-url. For more information, see the Pulsar website: https://pulsar.apache.org/docs/2.10.x/client-libraries-go/#tls-encryption-and-authentication
oauth2.oauth2-issuer-url="https://xxxx.auth0.com"
# Pulsar oauth2 audience
oauth2.oauth2-audience="https://xxxx.auth0.com/api/v2/"
# Pulsar oauth2 private-key
oauth2.oauth2-private-key="/data/pulsar/privateKey"
# Pulsar oauth2 client-id
oauth2.oauth2-client-id="0Xx...Yyxeny"
# Pulsar oauth2 oauth2-scope
oauth2.oauth2-scope="xxxx"
# The number of cached Pulsar producers in TiCDC. The value is 10240 by default. Each Pulsar producer corresponds to one topic. If the number of topics you need to replicate is larger than the default value, you need to increase the number.
pulsar-producer-cache-size=10240
# Pulsar data compression method. No compression is used by default. Optional values are "lz4", "zlib", and "zstd".
compression-type=""
# The timeout for the Pulsar client to establish a TCP connection with the server. The value is 5 seconds by default.
connection-timeout=5
# The timeout for Pulsar clients to initiate operations such as creating and subscribing to a topic. The value is 30 seconds by default.
operation-timeout=30
# The maximum number of messages in a single batch for a Pulsar producer to send. The value is 1000 by default.
batching-max-messages=1000
# The interval at which Pulsar producer messages are saved for batching. The value is 10 milliseconds by default.
batching-max-publish-delay=10
# The timeout for a Pulsar producer to send a message. The value is 30 seconds by default.
send-timeout=30
```
### Best practice

* You need to specify the `protocol` parameter when creating a changefeed. Currently, only the `canal-json` protocol is supported for replicating data to Pulsar.
* The `pulsar-producer-cache-size` parameter indicates the number of producers cached in the Pulsar client. Because each producer in Pulsar can only correspond to one topic, TiCDC adopts the LRU method to cache producers, and the default limit is 10240. If the number of topics you need to replicate is larger than the default value, you need to increase the number.
### TLS encrypted transmission

Starting from v7.5.1 and v8.0.0, TiCDC supports TLS encrypted transmission for Pulsar. The configuration example is as follows:

Sink URI:

```shell
--sink-uri="pulsar+ssl://127.0.0.1:6651/persistent://public/default/yktest?protocol=canal-json"
```

Configuration:

```toml
[sink.pulsar-config]
tls-trust-certs-file-path="/data/pulsar/tls-trust-certs-file"
```

If the `tlsRequireTrustedClientCertOnConnect=true` parameter is configured for your Pulsar server, you also need to configure the `tls-key-file-path` and `tls-certificate-file` parameters in the changefeed configuration file. For example:

```toml
[sink.pulsar-config]
tls-trust-certs-file-path="/data/pulsar/tls-trust-certs-file"
tls-certificate-file="/data/pulsar/tls-certificate-file"
tls-key-file-path="/data/pulsar/tls-key-file"
```
