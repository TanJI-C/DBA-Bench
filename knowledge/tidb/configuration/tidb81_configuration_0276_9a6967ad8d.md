# Reconfigure running Kafka cluster AZ placement

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md`
- Source Title: `Set Up Self-Hosted Kafka Private Link Service in AWS`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Link Service in AWS > Step 1. Set up a Kafka cluster > Reconfigure a running Kafka cluster`
- Source Line Ranges: `524-527`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `ticdc`
- Topic Tags: `kafka`, `region-alignment`, `availability-zones`, `cluster-reconfiguration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0276_9a6967ad8d`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md#reconfigure-a-running-kafka-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8a7072a473f00417b4c075e01efdb98be6d61a0ed80f22d5f51ce939ca00a0db`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service#reconfigure-a-running-kafka-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-aws-self-hosted-kafka-private-link-service.md

## Retrieval Guidance

- Use When: Use this chunk when you need the stated requirement for reconfiguring a running Kafka cluster so its brokers align with the TiDB cluster region and availability zones.
- Retrieval Keywords: Reconfigure a running Kafka cluster, same region and AZs as the TiDB cluster, brokers are in different AZs, move them to the correct ones, availability zones, region alignment
- Follow-up Guidance: 
- Classification Note: This is configuration content because it states the required placement of Kafka brokers relative to the TiDB cluster during cluster reconfiguration.

## Official Source Content

### Reconfigure a running Kafka cluster

Ensure that your Kafka cluster is deployed in the same region and AZs as the TiDB cluster. If any brokers are in different AZs, move them to the correct ones.
