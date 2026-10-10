# PSC port mapping method introduction and Kafka cluster setup entry

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md`
- Source Title: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect service by PSC port mapping | Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > Set up self-hosted Kafka Private Service Connect service by PSC port mapping > Step 1. Set up the Kafka cluster`
- Source Line Ranges: `62-73`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `shared`
- Topic Tags: `private-service-connect`, `kafka`, `port-mapping`, `brokers`, `networking`, `cluster-setup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0287_2016bfa27d`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-self-hosted-kafka-private-service-connect.md#set-up-self-hosted-kafka-private-service-connect-service-by-psc-port-mapping`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c016f2fafc45365b02f47383d19427efc91537dbb4edf69651288bf580b218ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect#set-up-self-hosted-kafka-private-service-connect-service-by-psc-port-mapping
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks what the PSC port mapping method is or where to start when exposing a new or existing Kafka cluster to TiDB Cloud VPC.
- Retrieval Keywords: PSC port mapping, Set up self-hosted Kafka Private Service Connect service by PSC port mapping, Expose each Kafka broker, unique port, TiDB Cloud VPC, Step 1. Set up the Kafka cluster, Deploy a new Kafka cluster, Reconfigure a running Kafka cluster
- Follow-up Guidance: The source says Step 1 is to set up the Kafka cluster, either by deploying a new Kafka cluster or by reconfiguring a running Kafka cluster.
- Classification Note: This is classified as configuration because the content introduces the PSC port mapping approach and routes the reader to the appropriate Kafka cluster setup path for new or existing clusters.

## Official Source Content

## Set up self-hosted Kafka Private Service Connect service by PSC port mapping

Expose each Kafka broker to TiDB Cloud VPC with a unique port by using the PSC port mapping mechanism. The following diagram shows how it works.

![Connect to Google Cloud self-hosted Kafka Private Service Connect by port mapping](/media/tidb-cloud/changefeed/connect-to-google-cloud-self-hosted-kafka-private-service-connect-by-portmapping.jpeg)
### Step 1. Set up the Kafka cluster

If you need to deploy a new cluster, follow the instructions in [Deploy a new Kafka cluster](#deploy-a-new-kafka-cluster).

If you need to expose an existing cluster, follow the instructions in [Reconfigure a running Kafka cluster](#reconfigure-a-running-kafka-cluster).
