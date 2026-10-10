# Create a TiDB Cloud Serverless cluster with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-cluster-resource.md`
- Source Title: `Use TiDB Cloud Serverless Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Cluster Resource > Create a TiDB Cloud Serverless cluster`
- Source Line Ranges: `122-291`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `terraform`, `serverless`, `cluster-creation`, `apply`, `state-inspection`, `resource-definition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0399_f177e8249d`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-cluster-resource.md#create-a-tidb-cloud-serverless-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7fcf7d2fa0513b9a37e5a6ba4e437b7b33b70dc279c5afaa3ac7754d20a2b15e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-cluster-resource#create-a-tidb-cloud-serverless-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-cluster-resource.md

## Retrieval Guidance

- Use When: Use this when you need the Terraform resource example and apply flow for creating a TiDB Cloud Serverless cluster with `tidbcloud_serverless_cluster`.
- Retrieval Keywords: Create a TiDB Cloud Serverless cluster, tidbcloud_serverless_cluster, resource "tidbcloud_serverless_cluster" "example", project_id, display_name, spending_limit, region.name, regions/aws-us-east-1, terraform apply, terraform state show tidbcloud_serverless_cluster.example, terraform show, known after apply
- Follow-up Guidance: After creation, you can inspect the resource state with `terraform show` or `terraform state show tidbcloud_serverless_cluster.${resource-name}` to view fields such as `cluster_id`, `endpoints`, `state`, and `version`.
- Classification Note: This is classified as operation because the content walks through creating a serverless cluster resource, approving the Terraform execution plan, and inspecting the resulting state.

## Official Source Content

## Create a TiDB Cloud Serverless cluster

You can create a TiDB Cloud Serverless cluster using the `tidbcloud_serverless_cluster` resource.

The following example shows how to create a TiDB Cloud Serverless cluster.

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

    resource "tidbcloud_serverless_cluster" "example" {
      project_id = "1372813089454000000"
      display_name = "test-tf"
      spending_limit = {
        monthly = 1
      }
      region = {
        name = "regions/aws-us-east-1"
      }
    }
    ```

    Use the `resource` block to define the resource of TiDB Cloud, including the resource type, resource name, and resource details.

    - To use the TiDB Cloud Serverless cluster resource, set the resource type as `tidbcloud_serverless_cluster`.
    - For the resource name, you can define it as needed. For example, `example`.
    - For the resource details, you can configure them according to the Project ID and the TiDB Cloud Serverless cluster specification information.
    - To get the TiDB Cloud Serverless cluster specification information, see [tidbcloud_serverless_cluster (Resource)](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs/resources/serverless_cluster).

3. Run the `terraform apply` command. It is not recommended to use `terraform apply --auto-approve` when you apply a resource.

    ```shell
    $ terraform apply

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      + create

    Terraform will perform the following actions:

        # tidbcloud_serverless_cluster.example will be created
        + resource "tidbcloud_serverless_cluster" "example" {
            + annotations             = (known after apply)
            + automated_backup_policy = (known after apply)
            + cluster_id              = (known after apply)
            + create_time             = (known after apply)
            + created_by              = (known after apply)
            + display_name            = "test-tf"
            + encryption_config       = (known after apply)
            + endpoints               = (known after apply)
            + labels                  = (known after apply)
            + project_id              = "1372813089454000000"
            + region                  = {
                + cloud_provider = (known after apply)
                + display_name   = (known after apply)
                + name           = "regions/aws-us-east-1"
                + region_id      = (known after apply)
            }
            + spending_limit          = {
                + monthly = 1
            }
            + state                   = (known after apply)
            + update_time             = (known after apply)
            + user_prefix             = (known after apply)
            + version                 = (known after apply)
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

    tidbcloud_serverless_cluster.example: Creating...
    tidbcloud_serverless_cluster.example: Still creating... [10s elapsed]

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

5. Use the `terraform show` or `terraform state show tidbcloud_serverless_cluster.${resource-name}` command to inspect the state of your resource. The former command shows the states of all resources and data sources.

    ```shell
    $ terraform state show tidbcloud_serverless_cluster.example

    # tidbcloud_serverless_cluster.example:
    resource "tidbcloud_serverless_cluster" "example" {
        annotations             = {
            "tidb.cloud/available-features" = "DISABLE_PUBLIC_LB,DELEGATE_USER"
            "tidb.cloud/has-set-password"   = "false"
        }
        automated_backup_policy = {
            retention_days = 14
            start_time     = "07:00"
        }
        cluster_id              = "10145794214536000000"
        create_time             = "2025-06-16T07:04:41Z"
        created_by              = "apikey-S2000000"
        display_name            = "test-tf"
        encryption_config       = {
            enhanced_encryption_enabled = false
        }
        endpoints               = {
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
        labels                  = {
            "tidb.cloud/organization" = "1372813089187000000"
            "tidb.cloud/project"      = "1372813089454000000"
        }
        project_id              = "1372813089454000000"
        region                  = {
            cloud_provider = "aws"
            display_name   = "N. Virginia (us-east-1)"
            name           = "regions/aws-us-east-1"
            region_id      = "us-east-1"
        }
        spending_limit          = {
            monthly = 1
        }
        state                   = "ACTIVE"
        update_time             = "2025-06-16T07:04:48Z"
        user_prefix             = "KhSDGqQ3P000000"
        version                 = "v7.5.2"
    }
    ```
