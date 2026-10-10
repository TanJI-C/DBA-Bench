# TiDB Cloud release notes Sep 2024 CLI and partner updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2024.md`
- Source Title: `TiDB Cloud Release Notes in 2024`
- Source Heading Path: `TiDB Cloud Release Notes in 2024 > September 24, 2024 | TiDB Cloud Release Notes in 2024 > September 10, 2024`
- Source Line Ranges: `101-142`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tiup`, `tiflash`, `sql`
- Topic Tags: `release-notes`, `cli`, `serverless`, `sql-user-management`, `public-endpoint`, `oauth`, `export`, `import`, `s3`, `gcs`, `azure-blob`, `branching`, `logging`, `partner-console`, `billing-management`, `tiflash-sizing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0645_0359f164de`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2024.md#september-24-2024`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c831b182d4ae6c76ce3125f8aa4d0d97fbb1c8b8a5bdbe175f42c5bee2e21a0a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2024#september-24-2024
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2024.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about September 2024 TiDB Cloud updates for the CLI, Partner Web Console and Open API, or TiFlash sizing on AWS Dedicated clusters.
- Retrieval Keywords: September 24 2024, September 10 2024, TiDB Cloud CLI v1.0.0-beta.2, ticloud serverless sql-user, ticloud serverless create, ticloud serverless update, disable public endpoint, ticloud auth whoami, OAuth authentication, ticloud serverless export create, --sql, --where, --filter, CSV, Parquet, Amazon S3, role ARN, Google Cloud Storage, Azure Blob Storage, importing data, create a branch from a branch and a specific timestamp, debug logging, credentials and user-agent, --s3.uri, --s3.bucket-uri, annotations field, TiDB Cloud Partner Web Console, Open API, resource and billing management, MSP, AWS Marketplace Channel Partner Private Offer, CPPO, TiFlash 32 vCPU 128 GiB
- Follow-up Guidance: The source links to command-specific CLI documentation and the TiDB Cloud Partner Web Console page for more detailed usage information.
- Classification Note: This is a release-notes chunk covering September 2024 TiDB Cloud general changes and CLI feature additions, replacements, removals, and partner updates.

## Official Source Content

## September 24, 2024

**General changes**

- Provide a new [TiFlash vCPU and RAM size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tiflash-vcpu-and-ram) for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS: `32 vCPU, 128 GiB`

**CLI changes**

- Release [TiDB Cloud CLI v1.0.0-beta.2](https://github.com/tidbcloud/tidbcloud-cli/releases/tag/v1.0.0-beta.2).

    TiDB Cloud CLI provides the following new features:

    - Support SQL user management for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters via [`ticloud serverless sql-user`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-sql-user-create).
    - Allow disabling the public endpoint for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters in [`ticloud serverless create`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-cluster-create) and [`ticloud serverless update`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-update).
    - Add the [`ticloud auth whoami`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auth-whoami) command to get information about the current user when using OAuth authentication.
    - Support `--sql`, `--where`, and `--filter` flags in [`ticloud serverless export create`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-create) to choose source tables flexibly.
    - Support exporting data to CSV and Parquet files.
    - Support exporting data to Amazon S3 using role ARN as credentials, and also support exporting to Google Cloud Storage and Azure Blob Storage.
    - Support importing data from Amazon S3, Google Cloud Storage, and Azure Blob Storage.
    - Support creating a branch from a branch and a specific timestamp.

  TiDB Cloud CLI enhances the following features:

    - Improve debug logging. Now it can log credentials and user-agent.
    - Speed up local export file downloads from tens of KiB per second to tens of MiB per second.

  TiDB Cloud CLI replaces or removes the following features:

    - The `--s3.bucket-uri` flag is replaced by `--s3.uri` in [`ticloud serverless export create`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-create).
    - The `--database` and `--table` flags are removed in [`ticloud serverless export create`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-export-create). Instead, you can use `--sql`, `--where`, and `--filter` flags.
    - [`ticloud serverless update`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-serverless-update) cannot update the annotations field anymore.
## September 10, 2024

**General changes**

- Launch the TiDB Cloud Partner Web Console and Open API to enhance resource and billing management for TiDB Cloud partners.

    Managed Service Providers (MSPs) and resellers through AWS Marketplace Channel Partner Private Offer (CPPO) can now leverage the [TiDB Cloud Partner Web Console](https://partner-console.tidbcloud.com/) and Open API to streamline their daily operations.

    For more information, see [TiDB Cloud Partner Web Console](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-partners).
