# Create a TiDB Cloud Dedicated cluster with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource > Create a TiDB Cloud Dedicated cluster`
- Source Line Ranges: `122-251`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`
- Topic Tags: `terraform`, `cluster-creation`, `resource-definition`, `apply`, `state-inspection`, `cidr`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0377_4bc930ee0a`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#create-a-tidb-cloud-dedicated-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01bd6eecabcc0b20cde6dc1302d227266533f0e64236b2cc92d767991a03b007`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#create-a-tidb-cloud-dedicated-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this when you need the Terraform resource example and apply workflow for creating a TiDB Cloud Dedicated cluster, including CIDR prerequisites and state inspection commands.
- Retrieval Keywords: Create a TiDB Cloud Dedicated cluster, tidbcloud_dedicated_cluster, cluster.tf, terraform apply, terraform show, terraform state show tidbcloud_dedicated_cluster.${resource-name}, Set a CIDR, dedicated_network_container resource, display_name, region_id, root_password, tidb_node_setting, tikv_node_setting, node_spec_key, storage_size_gi, storage_type
- Follow-up Guidance: After creation, you can use `terraform show` or `terraform state show tidbcloud_dedicated_cluster.${resource-name}` to inspect the state of the resource.
- Classification Note: This chunk is classified as an operation because it provides the procedural steps and Terraform configuration needed to create a TiDB Cloud Dedicated cluster.

## Official Source Content

## Create a TiDB Cloud Dedicated cluster

> **Note:**
>
> - Before you begin, make sure that you have set a CIDR in the [TiDB Cloud console](https://tidbcloud.com). For more information, see [Set a CIDR](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#prerequisite-set-a-cidr-for-a-region). 
> - You can also [create a `dedicated_network_container` resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-network-container-resource) to manage your CIDR.

You can create a TiDB Cloud Dedicated cluster using the `tidbcloud_dedicated_cluster` resource as follows:

1. Create a directory for the cluster and enter it.

2. Create a `cluster.tf` file:

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

    resource "tidbcloud_dedicated_cluster" "example_cluster" {
      display_name  = "your_display_name"
      region_id     = "your_region_id"
      port          = 4000
      root_password = "your_root_password"
      tidb_node_setting = {
       node_spec_key = "2C4G"
       node_count    = 1
      }
      tikv_node_setting = {
       node_spec_key   = "2C4G"
       node_count      = 3
       storage_size_gi = 60
       storage_type    = "Standard"
      }
    }
    ```

    Use the `resource` block to define the resource of TiDB Cloud, including the resource type, resource name, and resource details.

    - To use the TiDB Cloud Dedicated cluster resource, set the resource type as `tidbcloud_dedicated_cluster`.
    - For the resource name, you can define it as needed. For example, `example_cluster`.
    - For the resource details, you can configure them according to the Project ID and the TiDB Cloud Dedicated cluster specification information. 
    - To get the TiDB Cloud Dedicated cluster specification information, see [tidbcloud_dedicated_cluster (Resource)](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs/resources/dedicated_cluster).

3. Run the `terraform apply` command. It is not recommended to use `terraform apply --auto-approve` when you apply a resource.

    ```shell
    $ terraform apply

    Terraform will perform the following actions:

      # tidbcloud_dedicated_cluster.example_cluster will be created
      + resource "tidbcloud_dedicated_cluster" "example_cluster" {
          + annotations         = (known after apply)
          + cloud_provider      = (known after apply)
          + cluster_id          = (known after apply)
          + create_time         = (known after apply)
          + created_by          = (known after apply)
          + display_name        = "test-tf"
          + labels              = (known after apply)
          + pause_plan          = (known after apply)
          + port                = 4000
          + project_id          = (known after apply)
          + region_display_name = (known after apply)
          + region_id           = "aws-us-west-2"
          + state               = (known after apply)
          + tidb_node_setting   = {
              + endpoints               = (known after apply)
              + is_default_group        = (known after apply)
              + node_count              = 1
              + node_group_display_name = (known after apply)
              + node_group_id           = (known after apply)
              + node_spec_display_name  = (known after apply)
              + node_spec_key           = "2C4G"
              + public_endpoint_setting = (known after apply)
              + state                   = (known after apply)
            }
          + tikv_node_setting   = {
              + node_count             = 3
              + node_spec_display_name = (known after apply)
              + node_spec_key          = "2C4G"
              + storage_size_gi        = 60
              + storage_type           = "Standard"
            }
          + update_time         = (known after apply)
          + version             = (known after apply)
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
    - The `known after apply` shows that you will get the value after `apply`.

4. If everything in your plan looks fine, type `yes` to continue:

    ```shell
    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_dedicated_cluster.example_cluster: Creating...
    tidbcloud_dedicated_cluster.example_cluster: Still creating... [10s elapsed]

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

    It usually takes at least 10 minutes to create a TiDB Cloud Dedicated cluster.

5. Use the `terraform show` or `terraform state show tidbcloud_dedicated_cluster.${resource-name}` command to inspect the state of your resource. The former command shows the states of all resources and data sources.
