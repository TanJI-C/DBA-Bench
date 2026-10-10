# Security model, tenancy, and encryption FAQs

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-faqs.md`
- Source Title: `TiDB Cloud Serverless FAQs`
- Source Heading Path: `TiDB Cloud Serverless FAQs > Security FAQs | TiDB Cloud Serverless FAQs > Security FAQs > Is my TiDB Cloud Serverless shared or dedicated? | TiDB Cloud Serverless FAQs > Security FAQs > How does TiDB Cloud Serverless ensure security?`
- Source Line Ranges: `138-148`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `security`, `multi-tenancy`, `shared-resources`, `dedicated-tier`, `tls`, `encryption-at-rest`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0085_f79e52bc72`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-faqs.md#security-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5158d1f199e91c1f94d14e8b8a36efb501bc2a171d1ac06f555bb84c0b186fc7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-faqs#security-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-faqs.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about whether TiDB Cloud Serverless is shared or dedicated, or how it provides TLS encryption and encryption-at-rest.
- Retrieval Keywords: TiDB Cloud Serverless shared or dedicated, multi-tenancy, resources used by all clusters are shared, TiDB Cloud Dedicated isolated infrastructure and resources, Transport Layer Security TLS, TLS Connection to TiDB Cloud Serverless, encrypted-at-rest, cloud provider
- Follow-up Guidance: To get managed TiDB service with isolated infrastructure and resources, you can upgrade it to TiDB Cloud Dedicated, and for TLS connection details see TLS Connection to TiDB Cloud Serverless.
- Classification Note: This is architecture content because it describes the multi-tenancy model, shared resources, and security mechanisms used by TiDB Cloud Serverless.

## Official Source Content

## Security FAQs
### Is my TiDB Cloud Serverless shared or dedicated?

The serverless technology is designed for multi-tenancy and the resources used by all clusters are shared. To get managed TiDB service with isolated infrastructure and resources, you can upgrade it to [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
### How does TiDB Cloud Serverless ensure security?

- Your connections are encrypted by Transport Layer Security (TLS). For more information about using TLS to connect to TiDB Cloud Serverless, see [TLS Connection to TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters).
- All persisted data on TiDB Cloud Serverless is encrypted-at-rest using the tool of the cloud provider that your cluster is running in.
