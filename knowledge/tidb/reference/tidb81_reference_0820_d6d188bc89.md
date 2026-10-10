# Serverless TLS FAQs on versions authentication and requirement

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/secure-connections-to-serverless-clusters.md`
- Source Title: `TLS Connections to TiDB Cloud Serverless`
- Source Heading Path: `TLS Connections to TiDB Cloud Serverless > FAQs | TLS Connections to TiDB Cloud Serverless > FAQs > Which TLS versions are supported to connect to my TiDB Cloud Serverless cluster? | TLS Connections to TiDB Cloud Serverless > FAQs > Is two-way TLS authentication between my connection client and TiDB Cloud Serverless supported? | TLS Connections to TiDB Cloud Serverless > FAQs > Does TiDB Cloud Serverless have to configure TLS to establish a secure connection?`
- Source Line Ranges: `91-107`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `tls`, `faq`, `tls-versions`, `authentication`, `one-way-tls`, `non-ssl`, `private-endpoint`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0820_d6d188bc89`
- Source ID: `tidb-docs-8.1:tidb-cloud/secure-connections-to-serverless-clusters.md#faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `83100e557fd1415162c7224e609610f396d290b65524da2174339857e1391909`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters#faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/secure-connections-to-serverless-clusters.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the supported TLS versions, whether two-way TLS authentication is supported, or whether TLS is required for standard and private endpoint connections in TiDB Cloud Serverless.
- Retrieval Keywords: TLS 1.2, TLS 1.3, TLS 1.0 not supported, TLS 1.1 not supported, two-way TLS authentication, one-way TLS authentication, public key verify signature, standard connection only allows TLS, prohibits non-SSL/TLS connections, private endpoint connection TLS optional
- Follow-up Guidance: The content distinguishes that standard connection requires TLS while private endpoint connection makes TLS optional because it provides highly secure and one-way access without exposing data to the public internet.
- Classification Note: This is classified as reference because the content is an FAQ that states support boundaries and security properties for TLS versions, authentication mode, and connection requirements.

## Official Source Content

## FAQs
### Which TLS versions are supported to connect to my TiDB Cloud Serverless cluster?

For security reasons, TiDB Cloud Serverless only supports TLS 1.2 and TLS 1.3, and does not support TLS 1.0 and TLS 1.1 versions. See IETF [Deprecating TLS 1.0 and TLS 1.1](https://datatracker.ietf.org/doc/rfc8996/) for details.
### Is two-way TLS authentication between my connection client and TiDB Cloud Serverless supported?

No.

TiDB Cloud Serverless only supports one-way TLS authentication, which means your client uses the public key to verify the signature of your TiDB Cloud cluster certificate's private key while the cluster does not validate the client.
### Does TiDB Cloud Serverless have to configure TLS to establish a secure connection?

For standard connection, TiDB Cloud Serverless only allows TLS connections and prohibits non-SSL/TLS connections. The reason is that SSL/TLS is one of the most basic security measures for you to reduce the risk of data exposure to the internet when you connect to the TiDB Cloud Serverless cluster through the internet.

For private endpoint connection, because it supports highly secure and one-way access to the TiDB Cloud service and does not expose your data to the public internet, configuring TLS is optional.
