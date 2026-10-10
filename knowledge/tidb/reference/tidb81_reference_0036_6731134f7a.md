# Policy-based access control for certificates

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/certificate-authentication.md`
- Source Title: `Certificate-Based Authentication for Login`
- Source Heading Path: `Certificate-Based Authentication for Login > Policy-based access control for certificates`
- Source Line Ranges: `502-504`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`
- Topic Tags: `certificate-authentication`, `pbac`, `access-control`, `key-management`, `security-policy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0036_6731134f7a`
- Source ID: `tidb-docs-8.1:certificate-authentication.md#policy-based-access-control-for-certificates`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `173582dc06fea869a605bdf70e5d023bd7e736c91a04433a01b95975bb145b92`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/certificate-authentication#policy-based-access-control-for-certificates
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/certificate-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when searching whether TiDB supports policy-based access control for certificates and what kinds of policy criteria are mentioned.
- Retrieval Keywords: policy-based access control for certificates, PBAC, key management server policies, time-based policies, location-based policies, certificate management, fine-grained control
- Follow-up Guidance: The source states that PBAC leverages policies defined by the underlying key management server, including time-based, location-based, and other customizable conditions.
- Classification Note: This is classified as reference because it briefly describes TiDB support for certificate PBAC and the policy concepts involved.

## Official Source Content

## Policy-based access control for certificates

TiDB supports policy-based access control (PBAC) for certificates, leveraging policies defined by the underlying key management server. This enables fine-grained control over access based on various criteria, such as time-based policies (for example, certificates only valid during specific hours), location-based policies (for example, restricting access to certain geographic locations), and other customizable conditions, ensuring enhanced security and flexibility in certificate management.
