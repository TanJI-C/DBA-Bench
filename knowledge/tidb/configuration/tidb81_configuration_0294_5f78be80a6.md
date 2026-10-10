# Serverless cluster resource overview, prerequisites, and project ID lookup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-cluster-resource.md`
- Source Title: `Use TiDB Cloud Serverless Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Cluster Resource | Use TiDB Cloud Serverless Cluster Resource > Prerequisites | Use TiDB Cloud Serverless Cluster Resource > Get project IDs using the `tidbcloud_projects` data source`
- Source Line Ranges: `5-121`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `terraform`, `serverless`, `project-id`, `data-source`, `provider`, `prerequisites`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0294_5f78be80a6`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-cluster-resource.md#use-tidb-cloud-serverless-cluster-resource`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c799e2a1f025fc3ae03113cc4bfe27e0ddf7cf852dcb37ba54fba775779b17b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-cluster-resource#use-tidb-cloud-serverless-cluster-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-cluster-resource.md

## Retrieval Guidance

- Use When: Use this when you need Terraform documentation for TiDB Cloud Serverless prerequisites or to retrieve a project ID with the `tidbcloud_projects` data source before creating a cluster.
- Retrieval Keywords: tidbcloud_serverless_cluster, tidbcloud_projects, Get project IDs, project_id, default project, terraform apply --auto-approve, output "projects", data "tidbcloud_projects", page, page_size, TiDB Cloud Terraform Provider v0.4.0 or later
- Follow-up Guidance: After applying the `tidbcloud_projects` data source configuration, the output lists available projects and their `id` values for use as `project_id`.
- Classification Note: This is classified as configuration because the content defines provider, data source, and output blocks used to obtain project information for Terraform configurations.

## Official Source Content

# Use TiDB Cloud Serverless Cluster Resource

This document describes how to manage a [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster with the `tidbcloud_serverless_cluster` resource.

In addition, you will also learn how to get the necessary information with the `tidbcloud_projects` data source.

The features of the `tidbcloud_serverless_cluster` resource include the following:

- Create TiDB Cloud Serverless clusters.
- Modify TiDB Cloud Serverless clusters.
- Import TiDB Cloud Serverless clusters.
- Delete TiDB Cloud Serverless clusters.
## Prerequisites

- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider) v0.4.0 or later.
## Get project IDs using the `tidbcloud_projects` data source

Each TiDB cluster belongs to a project. Before creating a TiDB Cloud Serverless cluster, you need to obtain the ID of the project where you want to create the cluster. If no `project_id` is specified, the default project will be used.

To retrieve the information about all available projects, use the `tidbcloud_projects` data source as follows:

1. In the `main.tf` file created when you [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider), add the `data` and `output` blocks as follows:

    ```
    terraform {
      required_providers {
        tidbcloud = {
          source = "tidbcloud/tidbcloud"
        }
      }
    }

    provider "tidbcloud" {
      public_key = "your_public_key"
      private_key = "your_private_key"
    }

    data "tidbcloud_projects" "example_project" {
      page      = 1
      page_size = 10
    }

    output "projects" {
      value = data.tidbcloud_projects.example_project.items
    }
    ```

    - Use the `data` block to define the data source of TiDB Cloud, including the data source type and the data source name.

        - To use the projects data source, set the data source type as `tidbcloud_projects`.
        - For the data source name, you can define it as needed. For example, `"example_project"`.
        - For the `tidbcloud_projects` data source, you can use the `page` and `page_size` attributes to limit the maximum number of projects you want to check.

    - Use the `output` block to define the data source information to be displayed in the output, and expose the information for other Terraform configurations to use.

        The `output` block works similarly to returned values in programming languages. See [Terraform documentation](https://www.terraform.io/language/values/outputs) for more details.

    To get all the available configurations for the resources and data sources, see the [Terraform provider configuration documentation](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs).

2. Run the `terraform apply` command to apply the configurations. You need to type `yes` at the confirmation prompt to proceed.

    To skip the prompt, use `terraform apply --auto-approve`:

    ```shell
    $ terraform apply --auto-approve

    Changes to Outputs:
      + projects = [
          + {
              + cluster_count    = 0
              + create_timestamp = "1649154426"
              + id               = "1372813089191000000"
              + name             = "test1"
              + org_id           = "1372813089189000000"
              + user_count       = 1
            },
          + {
              + cluster_count    = 1
              + create_timestamp = "1640602740"
              + id               = "1372813089189000000"
              + name             = "default project"
              + org_id           = "1372813089189000000"
              + user_count       = 1
            },
        ]

    You can apply this plan to save these new output values to the Terraform state, without changing any real infrastructure.

    Apply complete! Resources: 0 added, 0 changed, 0 destroyed.

    Outputs:

    projects = tolist([
      {
        "cluster_count" = 0
        "create_timestamp" = "1649154426"
        "id" = "1372813089100000000"
        "name" = "test1"
        "org_id" = "1372813089100000000"
        "user_count" = 1
      },
      {
        "cluster_count" = 1
        "create_timestamp" = "1640602740"
        "id" = "1372813089100000001"
        "name" = "default project"
        "org_id" = "1372813089100000000"
        "user_count" = 1
      },
    ])
    ```

Now, you can get all the available projects from the output. Copy one of the project IDs that you need.
