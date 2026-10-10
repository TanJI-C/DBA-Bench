# Add TiFlash to a TiDB Cloud Dedicated cluster with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource > Modify a TiDB Cloud Dedicated cluster > Add a TiFlash component`
- Source Line Ranges: `395-565`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tiflash`, `tidb`, `tikv`
- Topic Tags: `terraform`, `cluster-modification`, `tiflash`, `apply`, `state-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0380_258ac29c4d`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#add-a-tiflash-component`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9bb4a1a2acf77b55bfeb65ea3d4ee3b65432b62dd4ca2928b7708a823e29fed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#add-a-tiflash-component
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this when you need the Terraform steps and state output for adding a TiFlash component to a TiDB Cloud Dedicated cluster.
- Retrieval Keywords: Add a TiFlash component, tiflash_node_setting, cluster.tf, terraform apply, terraform state show tidbcloud_dedicated_cluster.${resource-name}, tidbcloud_dedicated_cluster.example_cluster, node_spec_key, node_count, storage_size_gi, MODIFYING, ACTIVE
- Follow-up Guidance: After applying, you can use `terraform state show tidbcloud_dedicated_cluster.${resource-name}` to verify the `tiflash_node_setting`, and the state changes from `MODIFYING` to `ACTIVE` when the modification is complete.
- Classification Note: This is an operation chunk because the content shows how to modify a TiDB Cloud Dedicated cluster by adding `tiflash_node_setting`, applying the change, and checking resource state.

## Official Source Content

### Add a TiFlash component

1. In the `cluster.tf` file that is used when you [create the cluster](#create-a-tidb-cloud-dedicated-cluster), add the `tiflash_node_setting` configuration.

    For example:

    ```
    tiflash_node_setting = {
      node_spec_key = "2C4G"
      node_count = 3
      storage_size_gi = 60
    }
    ```

2. Run the `terraform apply` command:

    ```shell
    $ terraform apply

    tidbcloud_dedicated_cluster.example_cluster: Refreshing state...

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      ~ update in-place

    Terraform will perform the following actions:

      # tidbcloud_dedicated_cluster.example_cluster will be updated in-place
      ~ resource "tidbcloud_dedicated_cluster" "example_cluster" {
          ~ annotations          = {
              - "tidb.cloud/available-features" = "DELEGATE_USER,DISABLE_PUBLIC_LB,PRIVATELINK"
              - "tidb.cloud/has-set-password"   = "false"
            } -> (known after apply)
          ~ labels               = {
              - "tidb.cloud/organization" = "60000"
              - "tidb.cloud/project"      = "3190000"
            } -> (known after apply)
          + pause_plan           = (known after apply)
          ~ state                = "ACTIVE" -> (known after apply)
          ~ tidb_node_setting    = {
              ~ endpoints               = [
                  - {
                      - connection_type = "PUBLIC"
                      - host            = "tidb.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                      - port            = 4000
                    },
                  - {
                      - connection_type = "VPC_PEERING"
                      - host            = "private-tidb.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                      - port            = 4000
                    },
                  - {
                      - connection_type = "PRIVATE_ENDPOINT"
                      - host            = "privatelink-19320029.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                      - port            = 4000
                    },
                ] -> (known after apply)
              ~ node_spec_display_name  = "2 vCPU, 4 GiB" -> (known after apply)
              ~ state                   = "ACTIVE" -> (known after apply)
                # (6 unchanged attributes hidden)
            }
          + tiflash_node_setting = {
              + node_count             = 3
              + node_spec_display_name = (known after apply)
              + node_spec_key          = "2C4G"
              + storage_size_gi        = 60
              + storage_type           = (known after apply)
            }
          ~ tikv_node_setting    = {
              ~ node_spec_display_name = "2 vCPU, 4 GiB" -> (known after apply)
              ~ storage_type           = "Standard" -> (known after apply)
                # (3 unchanged attributes hidden)
            }
          ~ update_time          = "2025-06-06 09:19:01.548 +0000 UTC" -> (known after apply)
          ~ version              = "v7.5.6" -> (known after apply)
            # (9 unchanged attributes hidden)
        }

    Plan: 0 to add, 1 to change, 0 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes
    ```

    In the preceding execution plan, TiFlash will be added, and one resource will be changed.

3. If everything in your plan looks fine, type `yes` to continue:

    ```shell
      Enter a value: yes

    tidbcloud_dedicated_cluster.example_cluster: Modifying...
    tidbcloud_dedicated_cluster.example_cluster: Still modifying... [10s elapsed]

    Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
    ```

4. Use `terraform state show tidbcloud_dedicated_cluster.${resource-name}` to check the state:

    ```
    $ terraform state show tidbcloud_dedicated_cluster.example_cluster

    # tidbcloud_dedicated_cluster.example_cluster:
    resource "tidbcloud_dedicated_cluster" "example_cluster" {
        annotations         = {
            "tidb.cloud/available-features" = "DISABLE_PUBLIC_LB,PRIVATELINK,DELEGATE_USER"
            "tidb.cloud/has-set-password"   = "false"
        }
        cloud_provider      = "aws"
        cluster_id          = "1379661944600000000"
        create_time         = "2025-06-06 06:25:29.878 +0000 UTC"
        created_by          = "apikey-XXXXXXXX"
        display_name        = "test-tf"
        labels              = {
            "tidb.cloud/organization" = "60000"
            "tidb.cloud/project"      = "3100000"
        }
        port                = 4000
        project_id          = "3100000"
        region_display_name = "Oregon (us-west-2)"
        region_id           = "aws-us-west-2"
        state               = "ACTIVE"
        tidb_node_setting   = {
            endpoints               = [
                {
                    connection_type = "PUBLIC"
                    host            = "tidb.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                    port            = 4000
                },
                {
                    connection_type = "VPC_PEERING"
                    host            = "private-tidb.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                    port            = 4000
                },
                {
                    connection_type = "PRIVATE_ENDPOINT"
                    host            = null
                    port            = 4000
                },
            ]
            is_default_group        = true
            node_count              = 1
            node_group_display_name = "DefaultGroup"
            node_group_id           = "1931960832833000000"
            node_spec_display_name  = "2 vCPU, 4 GiB beta"
            node_spec_key           = "2C4G"
            state                   = "ACTIVE"
        }
        tiflash_node_setting = {
            node_count             = 3
            node_spec_display_name = "2 vCPU, 4 GiB"
            node_spec_key          = "2C4G"
            storage_size_gi        = 60
            storage_type           = "Basic"
        }
        tikv_node_setting   = {
            node_count             = 3
            node_spec_display_name = "2 vCPU, 4 GiB"
            node_spec_key          = "2C4G"
            storage_size_gi        = 60
            storage_type           = "Standard"
        }
        update_time         = "2025-06-06 08:31:42.974 +0000 UTC"
        version             = "v7.5.6"
    }
    ```

The `MODIFYING` state indicates that the cluster is being modified. The state will change to `ACTIVE` once the modification is complete.
