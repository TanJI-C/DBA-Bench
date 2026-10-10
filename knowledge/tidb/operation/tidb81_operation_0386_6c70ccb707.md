# TiDB Cloud Dedicated network container prerequisites and creation with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-network-container-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Network Container Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Network Container Resource | Use TiDB Cloud Dedicated Network Container Resource > Prerequisites | Use TiDB Cloud Dedicated Network Container Resource > Create a TiDB Cloud Dedicated network container`
- Source Line Ranges: `5-138`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `network-container`, `cidr`, `vpc-peering`, `prerequisites`, `resource-creation`, `apply`, `state-inspection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0386_6c70ccb707`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-network-container-resource.md#use-tidb-cloud-dedicated-network-container-resource`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `06e2467b892f6b3bf088586aef6cad7156dcdd1b174ec9f40211ee166eb4b4ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-network-container-resource#use-tidb-cloud-dedicated-network-container-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-network-container-resource.md

## Retrieval Guidance

- Use When: Use this when you need the prerequisites, resource definition, apply output, and state inspection details for creating a TiDB Cloud Dedicated network container with Terraform.
- Retrieval Keywords: tidbcloud_dedicated_network_container, TiDB Cloud Dedicated network container, Terraform Provider v0.4.0 or later, network_container.tf, project_id, region_id, cidr_notation, terraform apply, terraform show, terraform state show tidbcloud_dedicated_network_container.example, CIDR block, VPC peering, INACTIVE, ACTIVE, aws-ap-northeast-2, 172.16.16.0/21
- Follow-up Guidance: The source also states that the resource remains `INACTIVE` until you create a TiDB Cloud Dedicated cluster in the same region, after which the status changes to `ACTIVE`.
- Classification Note: This is classified as an operation chunk because it gives prerequisites and step-by-step Terraform creation and inspection procedures for a cloud resource.

## Official Source Content

# Use TiDB Cloud Dedicated Network Container Resource

This document describes how to manage a [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) network container using the `tidbcloud_dedicated_network_container` resource.

A network container is a logical networking resource that lets you define and manage a CIDR block (IP address range) for a specific project and region. This CIDR block is used for creating a VPC for TiDB Cloud Dedicated clusters and is required before setting up VPC peering in that region.

Before adding VPC peering requests to a region, you must first set a CIDR block for that region and create an initial TiDB Cloud Dedicated cluster. Once the first cluster is created, TiDB Cloud automatically creates the associated VPC, enabling you to establish a peering connection with your application's VPC.

The features of the `tidbcloud_dedicated_network_container` resource include the following:

- Create TiDB Cloud Dedicated network containers.
- Import TiDB Cloud Dedicated network containers.
- Delete TiDB Cloud Dedicated network containers.

> **Note:**
>
> TiDB Cloud Dedicated network containers cannot be modified or deleted if the status is `ACTIVE`. Make sure that the configuration of the `tidbcloud_network_container` resource is correct before you apply it.
## Prerequisites

- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider) v0.4.0 or later.
## Create a TiDB Cloud Dedicated network container

You can create a TiDB Cloud Dedicated network container using the `tidbcloud_dedicated_network_container` resource.

The following example shows how to create a TiDB Cloud Dedicated network container.

1. Create a directory for the TiDB Cloud Dedicated network container and enter it.

2. Create a `network_container.tf` file:

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

    resource "tidbcloud_dedicated_network_container" "example" {
      project_id = "1372813089454000000"
      region_id = "aws-ap-northeast-2"
      cidr_notation = "172.16.16.0/21"
    }
    ```

    Use the `resource` block to define the resource of TiDB Cloud, including the resource type, resource name, and resource details.

    - To use the TiDB Cloud Dedicated network container resource, set the resource type as `tidbcloud_dedicated_network_container`.
    - For the resource name, you can define it as needed, for example, `example`.
    - If you do not know how to get the values of the required arguments, see [Set a CIDR for a Region](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#prerequisite-set-a-cidr-for-a-region).
    - For more information about the TiDB Cloud Dedicated network container specification, see [tidbcloud_dedicated_network_container (Resource)](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs/resources/dedicated_network_container).

3. Run the `terraform apply` command. It is not recommended to use `terraform apply --auto-approve` when you apply a resource.

    ```shell
    $ terraform apply

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      + create

    Terraform will perform the following actions:

        # tidbcloud_dedicated_network_container.example will be created
        + resource "tidbcloud_dedicated_network_container" "example" {
            + cidr_notation        = "172.16.16.0/21"
            + cloud_provider       = (known after apply)
            + labels               = (known after apply)
            + network_container_id = (known after apply)
            + project_id           = "1372813089454543324"
            + region_display_name  = (known after apply)
            + region_id            = "aws-ap-northeast-2"
            + state                = (known after apply)
            + vpc_id               = (known after apply)
        }

    Plan: 1 to add, 0 to change, 0 to destroy.

    Do you want to perform these actions?
        Terraform will perform the actions described above.
        Only 'yes' will be accepted to approve.

        Enter a value:
    ```

    In the preceding result, Terraform generates an execution plan for you, which describes the actions Terraform will take:

    - You can check the differences between the configurations and the states.
    - You can also see the results of this `apply`. It will add a new resource, and no resource will be changed or destroyed.
    - `known after apply` indicates that you will get the corresponding value after `apply`.

4. If everything in your plan looks fine, type `yes` to continue:

    ```shell
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_dedicated_network_container.example: Creating...
    tidbcloud_dedicated_network_container.example: Creation complete after 4s
    ```

    The status of the resource will remain `INACTIVE` until you create a TiDB Cloud Dedicated cluster in the region of the TiDB Cloud Dedicated network container. Then, the status will change to `ACTIVE`.

5. Use the `terraform show` or `terraform state show tidbcloud_dedicated_network_container.${resource-name}` command to inspect the state of your resource. The former command shows the states of all resources and data sources.

    ```shell
    $ terraform state show tidbcloud_dedicated_network_container.example          
    # tidbcloud_dedicated_network_container.example:
    resource "tidbcloud_dedicated_network_container" "example" {
        cidr_notation        = "172.16.16.0/21"
        cloud_provider       = "aws"
        labels               = {
            "tidb.cloud/project" = "1372813089454000000"
        }
        network_container_id = "1934235512696000000"
        project_id           = "1372813089454000000"
        region_display_name  = "Seoul (ap-northeast-2)"
        region_id            = "aws-ap-northeast-2"
        state                = "INACTIVE"
        vpc_id               = null
    }
    ```
