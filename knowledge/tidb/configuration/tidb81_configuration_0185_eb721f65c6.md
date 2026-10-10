# Kafka sink URI practices, security, and schema registry integration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-kafka.md`
- Source Title: `Replicate Data to Kafka`
- Source Heading Path: `Replicate Data to Kafka > Configure sink URI for Kafka > Best practices | Replicate Data to Kafka > Configure sink URI for Kafka > TiCDC uses the authentication and authorization of Kafka | Replicate Data to Kafka > Configure sink URI for Kafka > Integrate TiCDC with Kafka Connect (Confluent Platform) | Replicate Data to Kafka > Configure sink URI for Kafka > Integrate TiCDC with AWS Glue Schema Registry`
- Source Line Ranges: `109-215`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `kafka`, `sink-uri`, `best-practices`, `sasl`, `tls`, `acl`, `avro`, `schema-registry`, `confluent`, `aws-glue`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0185_eb721f65c6`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-kafka.md#best-practices`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7d3e88a4f7859e4d27adbc8eb34b2b794d802e97acecc5afadae8b6ff5eea250`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when configuring a TiCDC Kafka sink URI and you need official details about topic creation parameters, SASL or TLS settings, ACL permissions, or Avro schema registry integration with Confluent Platform or AWS Glue Schema Registry.
- Retrieval Keywords: TiCDC Kafka sink URI, max-message-bytes, partition-num, replication-factor, canal-json, open-protocol, broken pipe, SASL/PLAIN, sasl-user, sasl-password, sasl-mechanism, SASL/SCRAM, SASL/GSSAPI, sasl-gssapi-auth-type, sasl-gssapi-kerberos-config-path, sasl-gssapi-service-name, sasl-gssapi-user, sasl-gssapi-password, sasl-gssapi-keytab-path, sasl-gssapi-realm, enable-tls, ca, cert, key, ACL authorization, Create, Write, Describe, DescribeConfig, Confluent Schema Registry, schema-registry, protocol=avro, Kafka Connect, AWS Glue Schema Registry, glue-schema-registry-config, region, registry-name, access-key, secret-access-key, token
- Follow-up Guidance: The source also provides sample `--sink-uri` and changefeed configuration examples for SASL, TLS, Confluent Schema Registry, and AWS Glue Schema Registry.
- Classification Note: This chunk is classified as configuration because it defines Kafka sink URI parameters, authentication and authorization options, topic-related settings, and schema registry configuration fields for TiCDC.

## Official Source Content

### Best practices

* It is recommended that you create your own Kafka Topic. At a minimum, you need to set the maximum amount of data of each message that the Topic can send to the Kafka broker, and the number of downstream Kafka partitions. When you create a changefeed, these two settings correspond to `max-message-bytes` and `partition-num`, respectively.
* If you create a changefeed with a Topic that does not yet exist, TiCDC will try to create the Topic using the `partition-num` and `replication-factor` parameters. It is recommended that you specify these parameters explicitly.
* In most cases, it is recommended to use the `canal-json` protocol.
* If the upstream data changes in TiCDC are infrequent, such as there might be no data changes for more than 10 minutes, it is recommended to increase the Kafka connection idle timeout in the Kafka broker configuration file. For more information, see [Why do TiCDC replication tasks to Kafka often fail with `broken pipe` errors](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#why-do-ticdc-replication-tasks-to-kafka-often-fail-with-broken-pipe-errors).

> **Note:**
>
> When `protocol` is `open-protocol`, TiCDC encodes multiple events into one Kafka message and avoids generating messages that exceed the length specified by `max-message-bytes`. 
> If the encoded result of a single row change event exceeds the value of `max-message-bytes`, the changefeed reports an error and prints logs.
### TiCDC uses the authentication and authorization of Kafka

The following are examples when using Kafka SASL authentication:

- SASL/PLAIN

  ```shell
  --sink-uri="kafka://127.0.0.1:9092/topic-name?kafka-version=2.4.0&sasl-user=alice-user&sasl-password=alice-secret&sasl-mechanism=plain"
  ```

- SASL/SCRAM

  SCRAM-SHA-256 and SCRAM-SHA-512 are similar to the PLAIN method. You just need to specify `sasl-mechanism` as the corresponding authentication method.

- SASL/GSSAPI

  SASL/GSSAPI `user` authentication:

  ```shell
  --sink-uri="kafka://127.0.0.1:9092/topic-name?kafka-version=2.4.0&sasl-mechanism=gssapi&sasl-gssapi-auth-type=user&sasl-gssapi-kerberos-config-path=/etc/krb5.conf&sasl-gssapi-service-name=kafka&sasl-gssapi-user=alice/for-kafka&sasl-gssapi-password=alice-secret&sasl-gssapi-realm=example.com"
  ```

  Values of `sasl-gssapi-user` and `sasl-gssapi-realm` are related to the [principle](https://web.mit.edu/kerberos/krb5-1.5/krb5-1.5.4/doc/krb5-user/What-is-a-Kerberos-Principal_003f.html) specified in kerberos. For example, if the principle is set as `alice/for-kafka@example.com`, then `sasl-gssapi-user` and `sasl-gssapi-realm` are specified as `alice/for-kafka` and `example.com` respectively.

  SASL/GSSAPI `keytab` authentication:

  ```shell
  --sink-uri="kafka://127.0.0.1:9092/topic-name?kafka-version=2.4.0&sasl-mechanism=gssapi&sasl-gssapi-auth-type=keytab&sasl-gssapi-kerberos-config-path=/etc/krb5.conf&sasl-gssapi-service-name=kafka&sasl-gssapi-user=alice/for-kafka&sasl-gssapi-keytab-path=/var/lib/secret/alice.key&sasl-gssapi-realm=example.com"
  ```

  For more information about SASL/GSSAPI authentication methods, see [Configuring GSSAPI](https://docs.confluent.io/platform/current/kafka/authentication_sasl/authentication_sasl_gssapi.html).

- TLS/SSL encryption

    If the Kafka broker has TLS/SSL encryption enabled, you need to add the `-enable-tls=true` parameter to `--sink-uri`. If you want to use self-signed certificates, you also need to specify `ca`, `cert` and `key` in `--sink-uri`.

- ACL authorization

    The minimum set of permissions required for TiCDC to function properly is as follows.

    - The `Create`, `Write`, and `Describe` permissions for the Topic [resource type](https://docs.confluent.io/platform/current/kafka/authorization.html#resources).
    - The `DescribeConfig` permission for the Cluster resource type.

  The usage scenarios for each permission are as follows:

    | Resource type | Type of operation      |  Scenario                           |
    | :-------------| :------------- | :--------------------------------|
    | Cluster       | `DescribeConfig`| Gets the cluster metadata while the changefeed is running |
    | Topic         | `Describe`      | Tries to create a topic when the changefeed starts |                
    | Topic         | `Create`        | Tries to create a topic when the changefeed starts  |
    | Topic         | `Write`         | Sends data to the topic                   | 

    When creating or starting a changefeed, you can disable the `Describe` and `Create` permissions if the specified Kafka topic already exists.
### Integrate TiCDC with Kafka Connect (Confluent Platform)

To use the [data connectors](https://docs.confluent.io/current/connect/managing/connectors.html) provided by Confluent to stream data to relational or non-relational databases, you need to use the [`avro` protocol](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-avro-protocol) and provide a URL for [Confluent Schema Registry](https://www.confluent.io/product/confluent-platform/data-compatibility/) in `schema-registry`.

Sample configuration:

```shell
--sink-uri="kafka://127.0.0.1:9092/topic-name?&protocol=avro&replication-factor=3" --schema-registry="http://127.0.0.1:8081" --config changefeed_config.toml
```

```shell
[sink]
dispatchers = [
 {matcher = ['*.*'], topic = "tidb_{schema}_{table}"},
]
```

For detailed integration guide, see [Quick Start Guide on Integrating TiDB with Confluent Platform](https://docs.pingcap.com/tidb/stable/ticdc/integrate-confluent-using-ticdc).
### Integrate TiCDC with AWS Glue Schema Registry

Starting from v7.4.0, TiCDC supports using the [AWS Glue Schema Registry](https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html) as the Schema Registry when users choose the [Avro protocol](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-avro-protocol) for data replication. The configuration example is as follows:

```shell
./cdc cli changefeed create --server=127.0.0.1:8300 --changefeed-id="kafka-glue-test" --sink-uri="kafka://127.0.0.1:9092/topic-name?&protocol=avro&replication-factor=3" --config changefeed_glue.toml
```

```toml
[sink]
[sink.kafka-config.glue-schema-registry-config]
region="us-west-1"  
registry-name="ticdc-test"
access-key="xxxx"
secret-access-key="xxxx"
token="xxxx"
```

In the above configuration, `region` and `registry-name` are required fields, while `access-key`, `secret-access-key`, and `token` are optional fields. The best practice is to set the AWS credentials as environment variables or store them in the `~/.aws/credentials` file instead of setting them in the changefeed configuration file.

For more information, refer to the [official AWS SDK for Go V2 documentation](https://aws.github.io/aws-sdk-go-v2/docs/configuring-sdk/#specifying-credentials).
