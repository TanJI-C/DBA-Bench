# TiDB Cloud Serverless branch prerequisites and creation with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-branch-resource.md`
- Source Title: `Use TiDB Cloud Serverless Branch Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Branch Resource | Use TiDB Cloud Serverless Branch Resource > Prerequisites | Use TiDB Cloud Serverless Branch Resource > Create a TiDB Cloud Serverless branch`
- Source Line Ranges: `5-160`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless-branch`, `prerequisites`, `resource-creation`, `apply`, `state-inspection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0396_8ba7f73d1c`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-branch-resource.md#use-tidb-cloud-serverless-branch-resource`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `95a7a904838e1b8cca4912ab68990ab53a8b9367f98d499d0bd1662ae2bb77cd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-branch-resource#use-tidb-cloud-serverless-branch-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-branch-resource.md

## Retrieval Guidance

- Use When: Use this content when you need the prerequisites, example `branch.tf` configuration, `terraform apply` flow, or state inspection commands for creating a `tidbcloud_serverless_branch` in TiDB Cloud Serverless.
- Retrieval Keywords: tidbcloud_serverless_branch, TiDB Cloud Serverless branch, Terraform Provider v0.4.0 or later, branch.tf, provider "tidbcloud", resource "tidbcloud_serverless_branch" "example", cluster_id, display_name, parent_id, terraform apply, known after apply, terraform show, terraform state show tidbcloud_serverless_branch.example
- Follow-up Guidance: The source also notes that the TiDB Cloud Serverless branch resource cannot be modified and that changing its configuration requires deleting the existing resource and creating a new one.
- Classification Note: This is classified as an operation chunk because the official content gives prerequisites, a resource definition example, apply output, and state inspection steps for creating and viewing a serverless branch.

## Official Source Content

# Use TiDB Cloud Serverless Branch Resource

This document describes how to manage a [TiDB Cloud Serverless branch](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-manage) using the `tidbcloud_serverless_branch` resource.

The features of the `tidbcloud_serverless_branch` resource include the following:

- Create TiDB Cloud Serverless branches.
- Import TiDB Cloud Serverless branches.
- Delete TiDB Cloud Serverless branches.

> **Note:**
>
> TiDB Cloud Serverless branch resource cannot be modified. If you want to change the configuration of a serverless branch resource, you need to delete the existing one and create a new one.
## Prerequisites

- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider) v0.4.0 or later.
- [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless).
## Create a TiDB Cloud Serverless branch

You can create a TiDB Cloud Serverless branch using the `tidbcloud_serverless_branch` resource.

The following example shows how to create a TiDB Cloud Serverless branch.

1. Create a directory for the branch and enter it.

2. Create a `branch.tf` file:

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

    resource "tidbcloud_serverless_branch" "example" {
      cluster_id   = 10581524018573000000
      display_name = "example"
      parent_id = 10581524018573000000
    }
    ```

    Use the `resource` block to define the resource of TiDB Cloud, including the resource type, resource name, and resource details.

    - To use the serverless branch resource, set the resource type as `tidbcloud_serverless_branch`.
    - For the resource name, you can define it as needed. For example, `example`.
    - For the resource details, you can configure them according to the serverless branch specification information.
    - To get the serverless branch specification information, see [tidbcloud_serverless_branch (Resource)](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs/resources/serverless_branch).

3. Run the `terraform apply` command. It is not recommended to use `terraform apply --auto-approve` when you apply a resource.

    ```shell
    $ terraform apply

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      + create

    Terraform will perform the following actions:

      # tidbcloud_serverless_branch.example will be created
      + resource "tidbcloud_serverless_branch" "example" {
          + annotations         = (known after apply)
          + branch_id           = (known after apply)
          + cluster_id          = "10581524018573000000"
          + create_time         = (known after apply)
          + created_by          = (known after apply)
          + display_name        = "example"
          + endpoints           = (known after apply)
          + parent_display_name = (known after apply)
          + parent_id           = "10581524018573000000"
          + parent_timestamp    = (known after apply)
          + state               = (known after apply)
          + update_time         = (known after apply)
          + user_prefix         = (known after apply)
        }

    Plan: 1 to add, 0 to change, 0 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value:
    ```

    In the preceding result, Terraform generates an execution plan for you, which describes the actions that Terraform will take:

    - You can check the differences between the configurations and the states.
    - You can also see the results of this `apply`. It will add a new resource, and no resource will be changed or destroyed.
    - `known after apply` indicates that you will get the corresponding value after `apply`.

4. If everything in your plan looks fine, type `yes` to continue:

    ```shell
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_serverless_branch.example: Creating...
    tidbcloud_serverless_branch.example: Still creating... [10s elapsed]
    tidbcloud_serverless_branch.example: Creation complete after 10s

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

5. Use the `terraform show` or `terraform state show tidbcloud_serverless_branch.${resource-name}` command to inspect the state of your resource. The former command shows the states of all resources and data sources.

    ```shell
    $ terraform state show tidbcloud_serverless_branch.example 
    # tidbcloud_serverless_branch.example:
    resource "tidbcloud_serverless_branch" "example" {
        annotations         = {
            "tidb.cloud/has-set-password" = "false"
        }
        branch_id           = "bran-qt3fij6jufcf5pluot5h000000"
        cluster_id          = "10581524018573000000"
        create_time         = "2025-06-16T07:55:51Z"
        created_by          = "apikey-S2000000"
        display_name        = "example"
        endpoints           = {
            private = {
                aws  = {
                    availability_zone = [
                        "use1-az6",
                    ]
                    service_name      = "com.amazonaws.vpce.us-east-1.vpce-svc-0062ecf0683000000"
                }
                host = "gateway01-privatelink.us-east-1.prod.aws.tidbcloud.com"
                port = 4000
            }
            public  = {
                disabled = false
                host     = "gateway01.us-east-1.prod.aws.tidbcloud.com"
                port     = 4000
            }
        }
        parent_display_name = "test-tf"
        parent_id           = "10581524018573000000"
        parent_timestamp    = "2025-06-16T07:55:51Z"
        state               = "ACTIVE"
        update_time         = "2025-06-16T07:56:49Z"
        user_prefix         = "4ER5SbndR000000"
    }
    ```
