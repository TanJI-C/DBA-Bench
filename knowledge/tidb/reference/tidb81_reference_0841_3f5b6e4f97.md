# TiDB Cloud Terraform provider overview and supported capabilities

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-tidbcloud-provider-overview.md`
- Source Title: `Terraform Integration Overview`
- Source Heading Path: `Terraform Integration Overview | Terraform Integration Overview > Requirements | Terraform Integration Overview > Supported resources and data sources | Terraform Integration Overview > Next step`
- Source Line Ranges: `5-55`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `terraform`, `provider`, `requirements`, `resources`, `data-sources`, `clusters`, `backups`, `restores`, `import`, `provisioning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0841_3f5b6e4f97`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-tidbcloud-provider-overview.md#terraform-integration-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6dfc953318976dd1387c3f9b0337ee2c2a9fdfa8f85219393056a0e8fc848e0b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-tidbcloud-provider-overview#terraform-integration-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-tidbcloud-provider-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an overview of TiDB Cloud Terraform Provider capabilities, prerequisites, and the supported Terraform resources and data sources for managing TiDB Cloud.
- Retrieval Keywords: TiDB Cloud Terraform Provider, Terraform Integration Overview, Terraform version >= 1.0, Go version >= 1.18, tidbcloud_cluster, tidbcloud_backup, tidbcloud_restore, tidbcloud_import, tidbcloud_projects, tidbcloud_cluster_specs, tidbcloud_clusters, tidbcloud_restores, tidbcloud_backups, clusters backups restores, supported resources and data sources
- Follow-up Guidance: The source points to configuration documentation and next-step pages for getting the provider and using the Cluster, Backup, and Restore resources.
- Classification Note: This is reference content because it summarizes requirements, supported resources and data sources, and linked next steps for the TiDB Cloud Terraform provider.

## Official Source Content

# Terraform Integration Overview

[Terraform](https://www.terraform.io/) is an infrastructure as code tool that lets you define both cloud and self-hosted resources in human-readable configuration files that you can version, reuse, and share.

[TiDB Cloud Terraform Provider](https://registry.terraform.io/providers/tidbcloud/tidbcloud) is a plugin that allows you to use Terraform to manage TiDB Cloud resources, such as clusters, backups, and restores.

If you are looking for a simple way to automate resource provisioning and your infrastructure workflow, you can try out TiDB Cloud Terraform Provider, which provides you with the following capacities:

- Get your project information.
- Get cluster specification information, such as supported cloud providers, regions, and node sizes.
- Manage your TiDB cluster, including creating, scaling, pausing, and resuming a cluster.
- Create and delete a backup for your cluster.
- Create a restore task for your cluster.
## Requirements

- [A TiDB Cloud account](https://tidbcloud.com/free-trial)
- [Terraform version](https://www.terraform.io/downloads.html) >= 1.0
- [Go version](https://golang.org/doc/install) >= 1.18 (required only if you want to build [TiDB Cloud Terraform Provider](https://github.com/tidbcloud/terraform-provider-tidbcloud) locally)
## Supported resources and data sources

[Resources](https://www.terraform.io/language/resources) and [Data sources](https://www.terraform.io/language/data-sources) are the two most important elements in the Terraform language.

TiDB Cloud supports the following resources and data sources:

- Resources

    - `tidbcloud_cluster`
    - `tidbcloud_backup`
    - `tidbcloud_restore`
    - `tidbcloud_import`

- Data sources

    - `tidbcloud_projects`
    - `tidbcloud_cluster_specs`
    - `tidbcloud_clusters`
    - `tidbcloud_restores`
    - `tidbcloud_backups`

To get all the available configurations for the resources and data sources, see this [configuration documentation](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs).
## Next step

- [Learn more about Terraform](https://www.terraform.io/docs)
- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider)
- [Use Cluster Resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-cluster-resource)
- [Use Backup Resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-backup-resource)
- [Use Restore Resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-restore-resource)
