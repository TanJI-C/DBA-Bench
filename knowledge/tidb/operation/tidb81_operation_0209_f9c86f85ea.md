# Kafka and Flink integration overview and environment setup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/replicate-data-to-kafka.md`
- Source Title: `Integrate Data with Apache Kafka and Apache Flink`
- Source Heading Path: `Integrate Data with Apache Kafka and Apache Flink | Integrate Data with Apache Kafka and Apache Flink > Step 1. Set up the environment`
- Source Line Ranges: `5-41`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tiup`, `ecosystem`, `tidb`
- Topic Tags: `overview`, `environment-setup`, `lab-environment`, `production-environment`, `deployment`, `kafka`, `flink`, `ticdc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0209_f9c86f85ea`
- Source ID: `tidb-docs-8.1:replicate-data-to-kafka.md#integrate-data-with-apache-kafka-and-apache-flink`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ba5e6597f64d2462a4d950e64f95994b6c7b5382612f456098f6cdf75e8d695d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/replicate-data-to-kafka#integrate-data-with-apache-kafka-and-apache-flink
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/replicate-data-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview and environment setup for replicating TiDB data to Apache Kafka and Apache Flink with TiCDC in a lab or production environment.
- Retrieval Keywords: Integrate Data with Apache Kafka and Apache Flink, Step 1. Set up the environment, TiCDC, TiUP Playground, tiup playground --host 0.0.0.0 --db 1 --pd 1 --kv 1 --tiflash 0 --ticdc 1, tiup status, Deploy TiCDC, Apache Kafka Quickstart, Running Kafka in Production, Apache Flink First steps, Flink deployment overview
- Follow-up Guidance: The next steps in the document are to create a changefeed that replicates data from TiDB to Kafka, write data using go-tpc, verify the Kafka topic, and optionally configure Flink to consume Kafka data.
- Classification Note: This is classified as an operation chunk because it describes deployment and environment setup steps for TiDB, Kafka, and optional Flink with TiCDC.

## Official Source Content

# Integrate Data with Apache Kafka and Apache Flink

This document describes how to replicate TiDB data to Apache Kafka and Apache Flink using [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview). The organization of this document is as follows:

1. Quickly deploy a TiDB cluster with TiCDC included, and create a Kafka cluster and a Flink cluster.
2. Create a changefeed that replicates data from TiDB to Kafka.
3. Write data to TiDB using go-tpc.
4. Observe data on Kafka console consumer and check that the data is replicated to a specified Kafka topic.
5. (Optional) Configure the Flink cluster to consume Kafka data.

The preceding steps are performed in a lab environment. You can also deploy a cluster in a production environment by referring to these steps.
## Step 1. Set up the environment

1. Deploy a TiDB cluster with TiCDC included.

    In a lab or testing environment, you can deploy a TiDB cluster with TiCDC included quickly by using TiUP Playground.

    ```shell
    tiup playground --host 0.0.0.0 --db 1 --pd 1 --kv 1 --tiflash 0 --ticdc 1
    # View cluster status
    tiup status
    ```

    If TiUP is not installed yet, refer to [Install TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview#install-tiup). In a production environment, you can deploy a TiCDC as instructed in [Deploy TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc).

2. Create a Kafka cluster.

    - Lab environment: refer to [Apache Kafka Quickstart](https://kafka.apache.org/quickstart) to start a Kafka cluster.
    - Production environment: refer to [Running Kafka in Production](https://docs.confluent.io/platform/current/kafka/deployment.html) to deploy a Kafka production cluster.

3. (Optional) Create a Flink cluster.

    - Lab environment: refer to [Apache Flink First steps](https://nightlies.apache.org/flink/flink-docs-release-1.15/docs/try-flink/local_installation/) to start a Flink cluster.
    - Production environment: refer to [Apache Kafka Deployment](https://nightlies.apache.org/flink/flink-docs-release-1.15/docs/deployment/overview/) to deploy a Flink production cluster.
