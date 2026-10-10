# Create TiDB Cloud Serverless export resource with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-export-resource.md`
- Source Title: `Use TiDB Cloud Serverless Export Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Export Resource | Use TiDB Cloud Serverless Export Resource > Prerequisites | Use TiDB Cloud Serverless Export Resource > Create a TiDB Cloud Serverless data export task`
- Source Line Ranges: `5-144`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless`, `export`, `resource-creation`, `prerequisites`, `state-inspection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0402_9bd9790788`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-export-resource.md#use-tidb-cloud-serverless-export-resource`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bc38bb6865fd4614187658786ad7b467640deb2cae9bac366f6c3026fbea6fb9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-export-resource#use-tidb-cloud-serverless-export-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-export-resource.md

## Retrieval Guidance

- Use When: Use this when looking for how to create, inspect, or refresh a TiDB Cloud Serverless export managed by Terraform.
- Retrieval Keywords: tidbcloud_serverless_export, TiDB Cloud Serverless data export task, terraform apply, terraform refresh, terraform show, terraform state show
- Follow-up Guidance: Use terraform show or terraform state show tidbcloud_serverless_export.${resource-name} to inspect the resource state after apply.
- Classification Note: This chunk documents creation and state inspection of the tidbcloud_serverless_export resource, including the prerequisite provider version v0.4.0 or later and a TiDB Cloud Serverless cluster.

## Official Source Content

# Use TiDB Cloud Serverless Export Resource

This document describes how to manage a [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) data export task using the `tidbcloud_serverless_export` resource.

The features of the `tidbcloud_serverless_export` resource include the following:

- Create TiDB Cloud Serverless data export tasks.
- Import TiDB Cloud Serverless data export tasks.
- Delete TiDB Cloud Serverless data export tasks.

> **Note:**
>
> TiDB Cloud Serverless export resource cannot be modified. If you want to change the configuration of a TiDB Cloud Serverless export resource, you need to delete the existing one, and then create a new one.
## Prerequisites

- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider) v0.4.0 or later.
- [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless).
## Create a TiDB Cloud Serverless data export task

You can create a TiDB Cloud Serverless data export task using the `tidbcloud_serverless_export` resource.

The following example shows how to create a TiDB Cloud Serverless data export task.

1. Create a directory for the export and enter it.

2. Create a `export.tf` file:

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

    resource "tidbcloud_serverless_export" "example" {
      cluster_id   = 10476959660988000000
    }
    ```

    Use the `resource` block to define the resource of TiDB Cloud, including the resource type, resource name, and resource details.

    - To use the serverless export resource, set the resource type as `tidbcloud_serverless_export`.
    - For the resource name, you can define it as needed. For example, `example`.
    - For the resource details, you can configure them according to the serverless export specification information.
    - To get the serverless export specification information, see [tidbcloud_serverless_export (Resource)](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs/resources/serverless_export).

3. Run the `terraform apply` command. It is not recommended to use `terraform apply --auto-approve` when you apply a resource.

    ```shell
    $ terraform apply

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
        + create

    Terraform will perform the following actions:

        # tidbcloud_serverless_export.example will be created
        + resource "tidbcloud_serverless_export" "example" {
            + cluster_id     = "10476959660988000000"
            + complete_time  = (known after apply)
            + create_time    = (known after apply)
            + created_by     = (known after apply)
            + display_name   = (known after apply)
            + expire_time    = (known after apply)
            + export_id      = (known after apply)
            + export_options = (known after apply)
            + reason         = (known after apply)
            + snapshot_time  = (known after apply)
            + state          = (known after apply)
            + target         = (known after apply)
            + update_time    = (known after apply)
        }

    Plan: 1 to add, 0 to change, 0 to destroy.

    Do you want to perform these actions?
        Terraform will perform the actions described above.
        Only 'yes' will be accepted to approve.

        Enter a value:
    ```

    In the preceding result, Terraform generates an execution plan for you, which describes the actions that Terraform will take:

    - You can check the difference between the configurations and the states.
    - You can also see the results of this `apply`. It will add a new resource, and no resource will be changed or destroyed.
    - `known after apply` indicates that you will get the corresponding value after `apply`.

4. If everything in your plan looks fine, type `yes` to continue:

    ```shell
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_serverless_export.example: Creating...
    tidbcloud_serverless_export.example: Creation complete after 1s

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

    In this example, the `tidbcloud_serverless_export.example` resource will create an export task to export data from the entire cluster. 
    
    This resource is not synchronized. You can use `terraform refresh` to retrieve its latest state.

5. Use the `terraform show` or `terraform state show tidbcloud_serverless_export.${resource-name}` command to inspect the state of your resource. The former command shows the states of all resources and data sources.

    ```shell
    $ terraform state show tidbcloud_serverless_export.example
    # tidbcloud_serverless_export.example:
    resource "tidbcloud_serverless_export" "example" {
        cluster_id     = "10476959660988000000"
        create_time    = "2025-06-16T08:54:10Z"
        created_by     = "apikey-S2000000"
        display_name   = "SNAPSHOT_2025-06-16T08:54:10Z"
        export_id      = "exp-ezsli6ugtzg2nkmzaitt000000"
        export_options = {
            compression = "GZIP"
            file_type   = "CSV"
        }
        snapshot_time  = "2025-06-16T08:54:10Z"
        state          = "RUNNING"
        target         = {
            type = "LOCAL"
        }
    }
    ```
