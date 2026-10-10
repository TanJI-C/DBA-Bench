# Scale a TiDB Cloud Dedicated cluster with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource > Modify a TiDB Cloud Dedicated cluster > Scale a cluster`
- Source Line Ranges: `566-668`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `terraform`, `scaling`, `node-count`, `cluster-modification`, `apply`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0381_49a8c91d75`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#scale-a-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d598d9360e5299547f2ba015cf384ba4d6b52aaa9b8d23ee5e6a35210aec02db`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#scale-a-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this when you need the documented Terraform procedure and constraints for scaling a TiDB Cloud Dedicated cluster.
- Retrieval Keywords: Scale a cluster, TiDB Cloud Dedicated cluster, state is ACTIVE, tidb_node_setting, tikv_node_setting, tiflash_node_setting, terraform apply, node_count, TiKV nodes needs to be a multiple of 3, update in-place, Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
- Follow-up Guidance: The cluster can be scaled when its state is `ACTIVE`, and after `terraform apply` you wait for the process to finish until the state changes back to `ACTIVE`.
- Classification Note: This is an operation chunk because the content describes editing node settings and applying an in-place update to scale TiDB, TiKV, and TiFlash nodes in a cloud cluster.

## Official Source Content

### Scale a cluster

You can scale a TiDB Cloud Dedicated cluster when its state is `ACTIVE`.

1. In the `cluster.tf` file that is used when you [create the cluster](#create-a-tidb-cloud-dedicated-cluster), edit the configurations of `tidb_node_setting`, `tikv_node_setting` and `tiflash_node_setting`.

    For example, to add one more TiDB node, three more TiKV nodes (the number of TiKV nodes needs to be a multiple of 3, because its scaling step is 3), and one more TiFlash node, you can edit the configurations as follows:

    ```
     tidb_node_setting = {
       node_spec_key = "8C16G"
       node_count = 2
     }
     tikv_node_setting = {
       node_spec_key = "8C32G"
       node_count = 6
       storage_size_gi = 200
     }
     tiflash_node_setting = {
       node_spec_key = "8C64G"
       node_count = 4
       storage_size_gi = 200
     }
    ```

2. Run the `terraform apply` command and type `yes` for confirmation:

    ```
    tidbcloud_dedicated_cluster.example_cluster: Refreshing state...

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      ~ update in-place

    Terraform will perform the following actions:

      # tidbcloud_dedicated_cluster.example_cluster will be updated in-place
      ~ resource "tidbcloud_dedicated_cluster" "example_cluster" {
          ~ annotations          = {
              - "tidb.cloud/available-features" = "DISABLE_PUBLIC_LB,PRIVATELINK,DELEGATE_USER"
              - "tidb.cloud/has-set-password"   = "false"
            } -> (known after apply)
          ~ labels               = {
              - "tidb.cloud/organization" = "60205"
              - "tidb.cloud/project"      = "3199728"
            } -> (known after apply)
          + pause_plan           = (known after apply)
          ~ state                = "ACTIVE" -> (known after apply)
          ~ tidb_node_setting    = {
              ~ endpoints               = [
                  - {
                      - connection_type = "PUBLIC"
                      - host            = "tidb.nwdkyh1smmxk.clusters.dev.tidb-cloud.com"
                      - port            = 4000
                    },
                  - {
                      - connection_type = "VPC_PEERING"
                      - host            = "private-tidb.nwdkyh1smmxk.clusters.dev.tidb-cloud.com"
                      - port            = 4000
                    },
                  - {
                      - connection_type = "PRIVATE_ENDPOINT"
                      - host            = "privatelink-19320029.nwdkyh1smmxk.clusters.dev.tidb-cloud.com"
                      - port            = 4000
                    },
                ] -> (known after apply)
              ~ node_count              = 3 -> 2
              ~ node_spec_display_name  = "8 vCPU, 16 GiB" -> (known after apply)
              ~ state                   = "ACTIVE" -> (known after apply)
                # (5 unchanged attributes hidden)
            }
          ~ tiflash_node_setting = {
              ~ node_count             = 3 -> 4
              ~ node_spec_display_name = "8 vCPU, 64 GiB" -> (known after apply)
              ~ storage_type           = "Basic" -> (known after apply)
                # (2 unchanged attributes hidden)
            }
          ~ tikv_node_setting    = {
              ~ node_count             = 3 -> 6
              ~ node_spec_display_name = "8 vCPU, 32 GiB" -> (known after apply)
              ~ storage_type           = "Standard" -> (known after apply)
                # (2 unchanged attributes hidden)
            }
          ~ update_time          = "2025-06-09 09:29:25.678 +0000 UTC" -> (known after apply)
          ~ version              = "v7.5.6" -> (known after apply)
            # (9 unchanged attributes hidden)
        }

    Plan: 0 to add, 1 to change, 0 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_dedicated_cluster.example_cluster: Modifying...
    tidbcloud_dedicated_cluster.example_cluster: Still modifying... [10s elapsed]

    Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
    ```

Wait for the process to finish. The state will change to `ACTIVE` once the scaling is complete.
