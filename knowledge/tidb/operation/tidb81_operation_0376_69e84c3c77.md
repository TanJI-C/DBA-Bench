# Dedicated cluster overview, prerequisites, and project ID lookup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource | Use TiDB Cloud Dedicated Cluster Resource > Prerequisites | Use TiDB Cloud Dedicated Cluster Resource > Get project IDs using the `tidbcloud_projects` data source`
- Source Line Ranges: `5-121`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `projects`, `project-id`, `data-source`, `prerequisites`, `cluster-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0376_69e84c3c77`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#use-tidb-cloud-dedicated-cluster-resource`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0e3343beea1d6faec7d9e4bce3be6dfb6612b8fa7db0d6c2e92af67b878c1449`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#use-tidb-cloud-dedicated-cluster-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this when you need Terraform-based overview and prerequisites for managing a TiDB Cloud Dedicated cluster, or when you need to retrieve project IDs with the `tidbcloud_projects` data source before creating a cluster.
- Retrieval Keywords: tidbcloud_dedicated_cluster, TiDB Cloud Dedicated cluster, tidbcloud_projects, project_id, default project, Get project IDs, terraform apply --auto-approve, data "tidbcloud_projects", output "projects", page, page_size, TiDB Cloud Terraform Provider v0.4.0 or later
- Follow-up Guidance: After applying the `tidbcloud_projects` data source configuration, you can get all available projects from the output and copy the project ID you need.
- Classification Note: This chunk is classified as an operation because it describes prerequisites and the procedure for using Terraform resources and data sources to manage TiDB Cloud Dedicated clusters and retrieve project IDs.

## Official Source Content

# Use TiDB Cloud Dedicated Cluster Resource

This document describes how to manage a [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster with the `tidbcloud_dedicated_cluster` resource.

In addition, you will also learn how to get the necessary information with the `tidbcloud_projects` data source and use the `tidbcloud_dedicated_node_group` resource to manage TiDB node groups of your TiDB Cloud Dedicated cluster.

The features of the `tidbcloud_dedicated_cluster` resource include the following:

- Create TiDB Cloud Dedicated clusters.
- Modify TiDB Cloud Dedicated clusters.
- Import TiDB Cloud Dedicated clusters.
- Delete TiDB Cloud Dedicated clusters.
## Prerequisites

- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider) v0.4.0 or later.
## Get project IDs using the `tidbcloud_projects` data source

Each TiDB Cloud Dedicated cluster belongs to a project. Before creating a TiDB Cloud Dedicated cluster, you need to obtain the ID of the project where you want to create the cluster. If no `project_id` is specified, the default project will be used.

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

        The `output` block works similarly to returned values in programming languages. For more information, see the [Terraform documentation](https://www.terraform.io/language/values/outputs).

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
