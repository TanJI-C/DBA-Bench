# TiDB Cloud API overview and access model

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/api-overview.md`
- Source Title: `TiDB Cloud API Overview`
- Source Heading Path: `TiDB Cloud API Overview (Beta)`
- Source Line Ranges: `5-32`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `api`, `rest`, `json`, `https`, `tls`, `authentication`, `digest-authentication`, `api-keys`, `projects`, `clusters`, `backups`, `restores`, `imports`, `billing`, `data-service`, `beta`, `changelog`, `rate-limiting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0782_b0c34d77e5`
- Source ID: `tidb-docs-8.1:tidb-cloud/api-overview.md#tidb-cloud-api-overview-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f01a852a8f0f2a9527c0c1d54fa28748dac7aba713045fdd8ad7b51096638c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/api-overview#tidb-cloud-api-overview-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/api-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for a high-level overview of the TiDB Cloud API, including its access model, supported resource areas, or where to find authentication, rate limiting, and full API references.
- Retrieval Keywords: TiDB Cloud API Overview (Beta), REST interface, JSON entities, HTTPS-only, TLS, HTTP Digest Authentication, API key, API Key Management, Get Started, Authentication, Rate Limiting, API Changelog, Projects, Clusters, Backups, Restores, Imports, Billings, Data Service, v1beta, v1beta1
- Follow-up Guidance: The source points to TiDB Cloud API Documentation sections for Get Started, Authentication, Rate Limiting, API Full References for v1beta and v1beta1, and the API Changelog.
- Classification Note: This is reference content because it describes the TiDB Cloud API scope, access characteristics, authentication model, and documentation entry points without providing a procedural workflow.

## Official Source Content

# TiDB Cloud API Overview (Beta)

> **Note:**
>
> TiDB Cloud API is in beta.

The TiDB Cloud API is a [REST interface](https://en.wikipedia.org/wiki/Representational_state_transfer) that provides you with programmatic access to manage administrative objects within TiDB Cloud. Through this API, you can automatically and efficiently manage resources such as Projects, Clusters, Backups, Restores, Imports, Billings, and resources in the [Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview).

The API has the following features:

- **JSON entities.** All entities are expressed in JSON.
- **HTTPS-only.** You can only access the API via HTTPS, ensuring all the data sent over the network is encrypted with TLS.
- **Key-based access and digest authentication.** Before you access TiDB Cloud API, you must generate an API key, refer to [API Key Management](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Authentication/API-key-management). All requests are authenticated through [HTTP Digest Authentication](https://en.wikipedia.org/wiki/Digest_access_authentication), ensuring the API key is never sent over the network.

To start using TiDB Cloud API, refer to the following resources in TiDB Cloud API Documentation:

- [Get Started](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Get-Started)
- [Authentication](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Authentication)
- [Rate Limiting](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Rate-Limiting)
- API Full References
    - v1beta1
        - [Billing](https://docs.pingcap.com/tidbcloud/api/v1beta1/billing)
        - [Data Service](https://docs.pingcap.com/tidbcloud/api/v1beta1/dataservice)
        - [IAM](https://docs.pingcap.com/tidbcloud/api/v1beta1/iam)
        - [MSP (Deprecated)](https://docs.pingcap.com/tidbcloud/api/v1beta1/msp)
    - [v1beta](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Project)
- [Changelog](https://docs.pingcap.com/tidbcloud/api/v1beta#section/API-Changelog)
