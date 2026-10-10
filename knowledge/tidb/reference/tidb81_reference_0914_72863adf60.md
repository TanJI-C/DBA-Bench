# Root certificate authority and TLS support FAQs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md`
- Source Title: `TLS Connections to TiDB Cloud Dedicated`
- Source Heading Path: `TLS Connections to TiDB Cloud Dedicated > Manage root certificates for TiDB Cloud Dedicated | TLS Connections to TiDB Cloud Dedicated > FAQs | TLS Connections to TiDB Cloud Dedicated > FAQs > Which TLS versions are supported to connect to my TiDB Cloud Dedicated cluster? | TLS Connections to TiDB Cloud Dedicated > FAQs > Is two-way TLS authentication between my client and TiDB Cloud Dedicated supported?`
- Source Line Ranges: `285-299`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `root-certificates`, `certificate-authority`, `aws-acm`, `tls-versions`, `one-way-authentication`, `two-way-authentication`, `faq`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0914_72863adf60`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md#manage-root-certificates-for-tidb-cloud-dedicated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d83b36d39bd7824e563051729669994c78f55759dba969867a9809721ab22fde`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-tls-connect-to-dedicated#manage-root-certificates-for-tidb-cloud-dedicated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md

## Retrieval Guidance

- Use When: Use this chunk when checking which certificate authority and TLS versions are used by TiDB Cloud Dedicated or whether two-way TLS authentication is supported.
- Retrieval Keywords: AWS Certificate Manager (ACM), Certificate Authority (CA), AWS-managed hardware security modules (HSMs), FIPS 140-2 Level 3, TLS 1.2, TLS 1.3, TLS 1.0 and TLS 1.1 not supported, one-way TLS authentication, two-way TLS authentication, TiDB Cloud Dedicated FAQs, Deprecating TLS 1.0 and TLS 1.1
- Follow-up Guidance: If two-way TLS authentication is needed, the content says to contact TiDB Cloud Support.
- Classification Note: This is classified as reference because the content states support constraints and factual FAQ answers about certificates, TLS versions, and authentication mode.

## Official Source Content

## Manage root certificates for TiDB Cloud Dedicated

TiDB Cloud Dedicated uses certificates from [AWS Certificate Manager (ACM)](https://aws.amazon.com/certificate-manager/) as a Certificate Authority (CA) for TLS connections between clients and TiDB Cloud Dedicated clusters. Usually, the root certificates of ACM are stored securely in AWS-managed hardware security modules (HSMs) that meet [FIPS 140-2 Level 3](https://csrc.nist.gov/projects/cryptographic-module-validation-program/Certificate/3139) security standards.
## FAQs
### Which TLS versions are supported to connect to my TiDB Cloud Dedicated cluster?

For security reasons, TiDB Cloud Dedicated only supports TLS 1.2 and TLS 1.3, and does not support TLS 1.0 and TLS 1.1 versions. See IETF [Deprecating TLS 1.0 and TLS 1.1](https://datatracker.ietf.org/doc/rfc8996/) for details.
### Is two-way TLS authentication between my client and TiDB Cloud Dedicated supported?

No.

TiDB Cloud Dedicated only supports one-way TLS authentication, and does not support two-way TLS authentication currently. If you need two-way TLS authentication, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
