# TiDB Cloud Dedicated private endpoint connection prerequisites and creation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Private Endpoint Connection Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Private Endpoint Connection Resource | Use TiDB Cloud Dedicated Private Endpoint Connection Resource > Prerequisites | Use TiDB Cloud Dedicated Private Endpoint Connection Resource > Create a TiDB Cloud Dedicated private endpoint connection`
- Source Line Ranges: `5-146`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `terraform`, `private-endpoint`, `dedicated-cluster`, `resource-creation`, `prerequisites`, `state-inspection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0389_926109dac5`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md#use-tidb-cloud-dedicated-private-endpoint-connection-resource`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d530100d4795e4d160285b92d988a4e831ae7afe6d1e521eca169468370c865b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource#use-tidb-cloud-dedicated-private-endpoint-connection-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md

## Retrieval Guidance

- Use When: Use this content when you need the prerequisites, Terraform resource name, creation flow, or state inspection commands for a TiDB Cloud Dedicated private endpoint connection.
- Retrieval Keywords: tidbcloud_dedicated_private_endpoint_connection, TiDB Cloud Dedicated private endpoint connection, Get TiDB Cloud Terraform Provider v0.4.0 or later, Create a TiDB Cloud Dedicated Cluster, private_endpoint_connection.tf, terraform apply, terraform show, terraform state show tidbcloud_dedicated_private_endpoint_connection.example, cluster_id, node_group_id, endpoint_id, known after apply, private_endpoint_connection_id, endpoint_state, private_link_service_name
- Follow-up Guidance: The source also shows that the resource cannot be modified and that changing a TiDB Cloud Dedicated private endpoint connection requires deleting the existing one and creating a new one.
- Classification Note: This is classified as an operation chunk because the official content provides prerequisites, a Terraform resource definition, apply output, and commands to inspect the created resource state.

## Official Source Content

# Use TiDB Cloud Dedicated Private Endpoint Connection Resource

This document describes how to manage a [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) private endpoint connection using the `tidbcloud_dedicated_private_endpoint_connection` resource.

The features of the `tidbcloud_dedicated_private_endpoint_connection` resource include the following:

- Create TiDB Cloud Dedicated private endpoint connections.
- Import TiDB Cloud Dedicated private endpoint connections.
- Delete TiDB Cloud Dedicated private endpoint connections.

> **Note:**
>
> TiDB Cloud Dedicated private endpoint connection resource cannot be modified. If you want to modify a TiDB Cloud Dedicated private endpoint connection, you need to delete the existing one, and then create a new one.
## Prerequisites

- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider) v0.4.0 or later.
- [Create a TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster).
## Create a TiDB Cloud Dedicated private endpoint connection

You can create a TiDB Cloud Dedicated private endpoint connection using the `tidbcloud_dedicated_private_endpoint_connection` resource.

The following example shows how to create a TiDB Cloud Dedicated private endpoint connection.

1. Create a directory for the TiDB Cloud Dedicated private endpoint connection and enter it.

2. Create a `private_endpoint_connection.tf` file:

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

    resource "tidbcloud_dedicated_private_endpoint_connection" "example" {
      cluster_id = "your_cluster_id"
      node_group_id = "your_node_group_id"
      endpoint_id = "your_endpoint_id"
    }
    ```

    Use the `resource` block to define the resource of TiDB Cloud, including the resource type, resource name, and resource details.

    - To use the TiDB Cloud Dedicated private endpoint connection resource, set the resource type as `tidbcloud_dedicated_private_endpoint_connection`.
    - For the resource name, you can define it as needed. For example, `example`.
    - If you do not know how to get the values of the required arguments, see [Connect to a TiDB Cloud Dedicated Cluster via Private Endpoint with AWS](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections).
    - To get the TiDB Cloud Dedicated private endpoint connection specification information, see [tidbcloud_private_endpoint_connection (Resource)](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs/resources/dedicated_private_endpoint_connection).

3. Run the `terraform apply` command. It is not recommended to use `terraform apply --auto-approve` when you apply a resource.

    ```shell
    $ terraform apply

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      + create

    Terraform will perform the following actions:

        # tidbcloud_dedicated_private_endpoint_connection.example will be created
        + resource "tidbcloud_dedicated_private_endpoint_connection" "example" {
            + account_id                     = (known after apply)
            + cloud_provider                 = (known after apply)
            + cluster_display_name           = (known after apply)
            + cluster_id                     = "10757937805044000000"
            + endpoint_id                    = "vpce-03367e9618000000"
            + endpoint_state                 = (known after apply)
            + host                           = (known after apply)
            + labels                         = (known after apply)
            + message                        = (known after apply)
            + node_group_id                  = "1934178998036000000"
            + port                           = (known after apply)
            + private_endpoint_connection_id = (known after apply)
            + private_link_service_name      = (known after apply)
            + region_display_name            = (known after apply)
            + region_id                      = (known after apply)
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

    tidbcloud_dedicated_private_endpoint_connection.example: Creating...
    tidbcloud_dedicated_private_endpoint_connection.example: Creation complete after 10s

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

5. Use the `terraform show` or `terraform state show tidbcloud_dedicated_private_endpoint_connection.${resource-name}` command to inspect the state of your resource. The former command shows the states of all resources and data sources.

    ```shell
    $ terraform state show tidbcloud_dedicated_private_endpoint_connection.example
    # tidbcloud_dedicated_private_endpoint_connection.example:
    resource "tidbcloud_dedicated_private_endpoint_connection" "example" {
        cloud_provider                 = "aws"
        cluster_display_name           = "test-tf"
        cluster_id                     = "10757937805044000000"
        endpoint_id                    = "vpce-03367e96180000000"
        endpoint_state                 = "ACTIVE"
        host                           = "privatelink-19341000.ubkypd000000.clusters.tidb-cloud.com"
        labels                         = {
            "tidb.cloud/project" = "1372813089454000000"
        }
        message                        = "The VPC Endpoint Id '{vpce-03367e961805e35b6 []}' does not exist"
        node_group_id                  = "1934178998036000000"
        port                           = 4000
        private_endpoint_connection_id = "1934214559409000000"
        private_link_service_name      = "com.amazonaws.vpce.us-west-2.vpce-svc-07468b31cc9000000"
        region_display_name            = "Oregon (us-west-2)"
        region_id                      = "aws-us-west-2"
    }
    ```
