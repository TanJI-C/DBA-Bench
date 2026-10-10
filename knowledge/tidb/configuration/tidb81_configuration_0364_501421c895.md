# Configure TiSpark to read TiFlash replicas

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/use-tispark-to-read-tiflash.md`
- Source Title: `Use TiSpark to Read TiFlash Replicas`
- Source Heading Path: `Use TiSpark to Read TiFlash Replicas`
- Source Line Ranges: `6-29`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `ecosystem`, `tidb`, `tikv`
- Topic Tags: `tispark`, `spark`, `isolation-read`, `tiflash-replica`, `spark-defaults`, `thrift-server`, `beeline`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0364_501421c895`
- Source ID: `tidb-docs-8.1:tiflash/use-tispark-to-read-tiflash.md#use-tispark-to-read-tiflash-replicas`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `959e500f1469692aa82196109b41c368d8ea708534338f0215dfb817cef6ecb4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/use-tispark-to-read-tiflash#use-tispark-to-read-tiflash-replicas
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/use-tispark-to-read-tiflash.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to configure TiSpark to read TiFlash replicas or control isolation read engines for Spark shell or Thrift server.
- Retrieval Keywords: spark.tispark.isolation_read_engines, TiSpark read TiFlash replicas, isolation read engines, spark-defaults.conf, --conf spark.tispark.isolation_read_engines=tiflash, spark.conf.set("spark.tispark.isolation_read_engines", "tiflash"), set spark.tispark.isolation_read_engines=tiflash, Thrift server, beeline, tikv,tiflash, tiflash, tikv
- Follow-up Guidance: The content also states that when the parameter is set to `tiflash`, all queried tables must have TiFlash replicas or an error is reported, and when set to `tikv`, only the TiKV replica is read.
- Classification Note: This is classified as configuration because the content explains the `spark.tispark.isolation_read_engines` parameter, its values, defaults, and the supported ways to set it in Spark and Thrift server.

## Official Source Content

# Use TiSpark to Read TiFlash Replicas

This document introduces how to use TiSpark to read TiFlash replicas.

Currently, you can use TiSpark to read TiFlash replicas in a method similar to the engine isolation in TiDB. This method is to configure the `spark.tispark.isolation_read_engines` parameter. The parameter value defaults to `tikv,tiflash`, which means that TiDB reads data from TiFlash or from TiKV according to CBO's selection. If you set the parameter value to `tiflash`, it means that TiDB forcibly reads data from TiFlash.

> **Note:**
>
> When this parameter is set to `tiflash`, only the TiFlash replicas of all tables involved in the query are read and these tables must have TiFlash replicas; for tables that do not have TiFlash replicas, an error is reported. When this parameter is set to `tikv`, only the TiKV replica is read.

You can configure this parameter in one of the following ways:

* Add the following item in the `spark-defaults.conf` file:

    ```
    spark.tispark.isolation_read_engines tiflash
    ```

* Add `--conf spark.tispark.isolation_read_engines=tiflash` in the initialization command when initializing Spark shell or Thrift server.

* Set `spark.conf.set("spark.tispark.isolation_read_engines", "tiflash")` in Spark shell in a real-time manner.

* Set `set spark.tispark.isolation_read_engines=tiflash` in Thrift server after the server is connected via beeline.
