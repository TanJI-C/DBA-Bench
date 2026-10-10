# TiSpark configuration for TLS, logging, and time zone

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tispark-overview.md`
- Source Title: `TiSpark User Guide`
- Source Heading Path: `TiSpark User Guide > TiSpark configurations > TLS configurations | TiSpark User Guide > TiSpark configurations > Log4j configuration | TiSpark User Guide > TiSpark configurations > Time zone configuration`
- Source Line Ranges: `311-379`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `tikv`, `pd`, `shared`
- Topic Tags: `tls`, `x509`, `jks`, `jdbc`, `log4j`, `warnings`, `timezone`, `spark-shell`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0394_4335e33246`
- Source ID: `tidb-docs-8.1:tispark-overview.md#tls-configurations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6b9887dc182baeb924edbf241cc7f581001ff8cebf78dbb31454628a50265aaa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tispark-overview#tls-configurations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tispark-overview.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiSpark settings related to TLS for TiKV Client and JDBC, log4j warnings in spark-shell or spark-sql, or time zone configuration for Timestamp behavior.
- Retrieval Keywords: TiSpark TLS configurations, spark.tispark.tikv.tls_enable, spark.tispark.tikv.trust_cert_collection, spark.tispark.tikv.key_cert_chain, spark.tispark.tikv.key_file, spark.tispark.tikv.jks_enable, spark.tispark.tikv.jks_trust_path, spark.tispark.tikv.jks_key_path, spark.tispark.jdbc.tls_enable, spark.tispark.jdbc.server_cert_store, spark.tispark.jdbc.client_cert_store, TLSv1.2, TLSv1.3, JKS higher priority than X.509, Failed to get database returning NoSuchObjectException, log4j.logger.org.apache.hadoop.hive.metastore.ObjectStore=ERROR, ${SPARK_HOME}/conf/log4j.properties, -Duser.timezone, Do not use spark.sql.session.timeZone, spark-shell, spark-sql
- Follow-up Guidance: The source also points to Enable TLS between TiDB Clients and Servers and Connecting Securely Using SSL for more details about TiDB TLS and JAVA key store generation.
- Classification Note: This chunk is classified as configuration because it defines exact TiSpark configuration properties and system properties for TLS, logging, and time zone behavior.

## Official Source Content

### TLS configurations

TiSpark TLS has two parts: TiKV Client TLS and JDBC connector TLS. To enable TLS in TiSpark, you need to configure both. `spark.tispark.tikv.xxx` is used for TiKV Client to create a TLS connection with PD and TiKV server. `spark.tispark.jdbc.xxx` is used for JDBC to connect with TiDB server in TLS connection.

When TiSpark TLS is enabled, you must configure either the X.509 certificate with `tikv.trust_cert_collection`, `tikv.key_cert_chain` and `tikv.key_file` configurations, or the JKS certificate with `tikv.jks_enable`, `tikv.jks_trust_path` and `tikv.jks_key_path`. `jdbc.server_cert_store` and `jdbc.client_cert_store` are optional.

TiSpark only supports TLSv1.2 and TLSv1.3.

* The following is an example of opening TLS configuration with the X.509 certificate in TiKV Client.

```
spark.tispark.tikv.tls_enable                                  true
spark.tispark.tikv.trust_cert_collection                       /home/tispark/root.pem
spark.tispark.tikv.key_cert_chain                              /home/tispark/client.pem
spark.tispark.tikv.key_file                                    /home/tispark/client.key
```

* The following is an example of enabling TLS with JKS configurations in TiKV Client.

```
spark.tispark.tikv.tls_enable                                  true
spark.tispark.tikv.jks_enable                                  true
spark.tispark.tikv.jks_key_path                                /home/tispark/config/tikv-truststore
spark.tispark.tikv.jks_key_password                            tikv_trustore_password
spark.tispark.tikv.jks_trust_path                              /home/tispark/config/tikv-clientstore
spark.tispark.tikv.jks_trust_password                          tikv_clientstore_password
```

When both JKS and X.509 certificates are configured, JKS would have a higher priority. That means TLS builder will use JKS certificate first. Therefore, do not set `spark.tispark.tikv.jks_enable=true` when you just want to use a common PEM certificate.

* The following is an example of enabling TLS in JDBC connector.

```
spark.tispark.jdbc.tls_enable                                  true
spark.tispark.jdbc.server_cert_store                           /home/tispark/jdbc-truststore
spark.tispark.jdbc.server_cert_password                        jdbc_truststore_password
spark.tispark.jdbc.client_cert_store                           /home/tispark/jdbc-clientstore
spark.tispark.jdbc.client_cert_password                        jdbc_clientstore_password
```

- For details about how to open TiDB TLS, see [Enable TLS between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers).
- For details about how to generate a JAVA key store, see [Connecting Securely Using SSL](https://dev.mysql.com/doc/connector-j/en/connector-j-reference-using-ssl.html).
### Log4j configuration

When you start `spark-shell` or `spark-sql` and run query, you might see the following warnings:

```
Failed to get database ****, returning NoSuchObjectException
Failed to get database ****, returning NoSuchObjectException
```

where `****` is the database name.

The warnings are benign and occurs because Spark cannot find `****` in its own catalog. You can just ignore these warnings.

To mute them, append the following text to `${SPARK_HOME}/conf/log4j.properties`.

```
# tispark disable "WARN ObjectStore:568 - Failed to get database"
log4j.logger.org.apache.hadoop.hive.metastore.ObjectStore=ERROR
```
### Time zone configuration

Set time zone by using the `-Duser.timezone` system property (for example, `-Duser.timezone=GMT-7`), which affects the `Timestamp` type.

Do not use `spark.sql.session.timeZone`.
