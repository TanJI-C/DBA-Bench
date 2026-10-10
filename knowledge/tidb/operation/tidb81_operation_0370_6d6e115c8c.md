# Deprecated cluster resource overview, prerequisites, and project ID lookup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-cluster-resource.md`
- Source Title: `Use Cluster Resource (Deprecated)`
- Source Heading Path: `Use Cluster Resource (Deprecated) | Use Cluster Resource (Deprecated) > Prerequisites | Use Cluster Resource (Deprecated) > Get project IDs using the `tidbcloud_projects` data source`
- Source Line Ranges: `5-125`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `deprecated`, `prerequisites`, `projects`, `data-source`, `project-id`, `cluster-creation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0370_6d6e115c8c`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-cluster-resource.md#use-cluster-resource-deprecated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8aff30a2a00a6633644343365bbe4a64a6a1e8434ec827eabdd109363603a1b6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-cluster-resource#use-cluster-resource-deprecated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-cluster-resource.md

## Retrieval Guidance

- Use When: Use this when looking for deprecated `tidbcloud_cluster` Terraform resource context, prerequisites, or how to get a TiDB Cloud project ID with the `tidbcloud_projects` data source before cluster creation.
- Retrieval Keywords: tidbcloud_cluster deprecated, Use Cluster Resource (Deprecated), TiDB Cloud Terraform Provider v0.4.0, tidbcloud_dedicated_cluster, tidbcloud_serverless_cluster, Prerequisites, Get TiDB Cloud Terraform Provider, tidbcloud_projects, project IDs, data "tidbcloud_projects", output "projects", terraform apply --auto-approve, project id lookup
- Follow-up Guidance: The content points to `tidbcloud_dedicated_cluster` and `tidbcloud_serverless_cluster` resources for more information, and shows using `terraform apply` to output available projects and copy a project ID.
- Classification Note: This is classified as an operation chunk because it gives prerequisite and Terraform workflow steps for listing projects and obtaining a project ID in TiDB Cloud.

## Official Source Content

# Use Cluster Resource (Deprecated)

> **Warning:**
>
> Starting from [TiDB Cloud Terraform Provider](https://registry.terraform.io/providers/tidbcloud/tidbcloud) v0.4.0, the `tidbcloud_cluster` resource is deprecated. It is recommended to use the `tidbcloud_dedicated_cluster` or `tidbcloud_serverless_cluster` resource instead. For more information, see [Use TiDB Cloud Dedicated Cluster Resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource) or [Use TiDB Cloud Serverless Cluster Resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-cluster-resource).

You can learn how to manage a TiDB Cloud cluster with the `tidbcloud_cluster` resource in this document.

In addition, you will also learn how to get the necessary information with the `tidbcloud_projects` and `tidbcloud_cluster_specs` data sources.

The features of the `tidbcloud_cluster` resource include the following:

- Create TiDB Cloud Serverless and TiDB Cloud Dedicated clusters.
- Modify TiDB Cloud Dedicated clusters.
- Delete TiDB Cloud Serverless and TiDB Cloud Dedicated clusters.
## Prerequisites

- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider).
## Get project IDs using the `tidbcloud_projects` data source

Each TiDB cluster is in a project. Before you create a TiDB cluster, you need to get the ID of the project in which you want to create a cluster.

To view the information of all available projects, you can use the `tidbcloud_projects` data source as follows:

1. In the `main.tf` file that is created when you [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider), add the `data` and `output` blocks as follows:

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
     sync = true
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
      - For the data source name, you can define it according to your need. For example, "example_project".
      - For the `tidbcloud_projects` data source, you can use the `page` and `page_size` attributes to limit the maximum number of projects you want to check.

   - Use the `output` block to define the data source information to be displayed in the output, and expose the information for other Terraform configurations to use.

      The `output` block works similarly to returned values in programming languages. See [Terraform documentation](https://www.terraform.io/language/values/outputs) for more details.

   To get all the available configurations for the resources and data sources, see this [configuration documentation](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs).

2. Run the `terraform apply` command to apply the configurations. You need to type `yes` at the confirmation prompt to proceed.

   To skip the prompt, use `terraform apply --auto-approve`:

   ```
   $ terraform apply --auto-approve

   Changes to Outputs:
     + projects = [
         + {
             + cluster_count    = 0
             + create_timestamp = "1649154426"
             + id               = "1372813089191121286"
             + name             = "test1"
             + org_id           = "1372813089189921287"
             + user_count       = 1
           },
         + {
             + cluster_count    = 1
             + create_timestamp = "1640602740"
             + id               = "1372813089189561287"
             + name             = "default project"
             + org_id           = "1372813089189921287"
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
       "id" = "1372813089191121286"
       "name" = "test1"
       "org_id" = "1372813089189921287"
       "user_count" = 1
     },
     {
       "cluster_count" = 1
       "create_timestamp" = "1640602740"
       "id" = "1372813089189561287"
       "name" = "default project"
       "org_id" = "1372813089189921287"
       "user_count" = 1
     },
   ])
   ```

Now, you can get all the available projects from the output. Copy one of the project IDs that you need.
