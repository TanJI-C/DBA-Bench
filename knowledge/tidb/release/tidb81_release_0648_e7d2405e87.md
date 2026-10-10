# January 2024 TiDB Cloud release updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2024.md`
- Source Title: `TiDB Cloud Release Notes in 2024`
- Source Heading Path: `TiDB Cloud Release Notes in 2024 > January 16, 2024 | TiDB Cloud Release Notes in 2024 > January 3, 2024`
- Source Line Ranges: `432-471`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `shared`
- Topic Tags: `release-notes`, `cidr`, `networking`, `serverless`, `public-endpoint`, `data-service`, `custom-domain`, `sso`, `saml`, `oidc`, `dedicated`, `version-upgrade`, `backup`, `disaster-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0648_e7d2405e87`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2024.md#january-16-2024`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6adc9b5c4b6ee19f1fe7fc9ab93f7f533068f3ccb280cf10ddeb463d3fd7f7dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2024#january-16-2024
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2024.md

## Retrieval Guidance

- Use When: Use this chunk when looking for January 2024 TiDB Cloud release notes about CIDR configuration, disabling public endpoints for TiDB Cloud Serverless, Data Service custom domain, Organization SSO, default TiDB version changes for new TiDB Cloud Dedicated clusters, or dual region backup GA.
- Retrieval Keywords: January 16 2024, January 3 2024, TiDB Cloud Release Notes in 2024, CIDR configuration for projects, region-level CIDR, global-level CIDR settings retired, Set a CIDR for a region, disable public endpoints, Disable a Public Endpoint, TiDB Cloud Serverless, Data Service (beta), custom domain, <region>.data.tidbcloud.com, Custom domain in Data Service, Organization SSO, SAML, OIDC, Organization SSO Authentication, TiDB Cloud Dedicated, default TiDB version, v7.1.1, v7.5.0, dual region backup, General Availability, backup and restore, disaster recovery
- Follow-up Guidance: The content points to related documents for Set a CIDR for a region, Disable a Public Endpoint, Custom domain in Data Service, Organization SSO Authentication, and Dual region backup.
- Classification Note: This is a TiDB Cloud release-notes chunk covering cloud general changes across networking, access, Data Service, authentication, dedicated cluster defaults, and backup capabilities announced in January 2024.

## Official Source Content

## January 16, 2024

**General changes**

- Enhance CIDR configuration for projects.

    - You can directly set a region-level CIDR for each project.
    - You can choose your CIDR configurations from a broader range of CIDR values.

    Note: The previous global-level CIDR settings for projects are retired, but all existing regional CIDR in active state remain unaffected. There will be no impact on the network of existing clusters.

    For more information, see [Set a CIDR for a region](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#prerequisite-set-a-cidr-for-a-region).

- TiDB Cloud Serverless users now have the capability to disable public endpoints for your clusters.

    For more information, see [Disable a Public Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless#disable-a-public-endpoint).

- [Data Service (beta)](https://tidbcloud.com/project/data-service) supports configuring a custom domain to access endpoints in a Data App.

    By default, TiDB Cloud Data Service provides a domain `<region>.data.tidbcloud.com` to access each Data App's endpoints. For enhanced personalization and flexibility, you can now configure a custom domain for your Data App instead of using the default domain. This feature enables you to use branded URLs for your database services and enhances security.

    For more information, see [Custom domain in Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-custom-domain).
## January 3, 2024

**General changes**

- Support [Organization SSO](https://tidbcloud.com/org-settings/authentication) to streamline enterprise authentication processes.

    With this feature, you can seamlessly integrate TiDB Cloud with any identity provider (IdP) using [Security Assertion Markup Language (SAML)](https://en.wikipedia.org/wiki/Security_Assertion_Markup_Language) or [OpenID Connect (OIDC)](https://openid.net/developers/how-connect-works/).

    For more information, see [Organization SSO Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-org-sso-authentication).

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v7.1.1](https://docs.pingcap.com/tidb/v7.1/release-7.1.1) to [v7.5.0](https://docs.pingcap.com/tidb/v7.5/release-7.5.0).

- The dual region backup feature for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) is now in General Availability (GA).

    By using this feature, you can replicate backups across geographic regions within AWS or Google Cloud. This feature provides an additional layer of data protection and disaster recovery capabilities.

    For more information, see [Dual region backup](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-dual-region-backup).
