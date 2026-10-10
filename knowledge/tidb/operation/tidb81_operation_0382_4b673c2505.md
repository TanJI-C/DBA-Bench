# Pause or resume a TiDB Cloud Dedicated cluster with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource > Modify a TiDB Cloud Dedicated cluster > Pause or resume a cluster`
- Source Line Ranges: `669-828`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `cluster-lifecycle`, `pause`, `resume`, `state-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0382_4b673c2505`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#pause-or-resume-a-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d36fe326c474232af7a3cf7a554540ec899a33c0373a332004a06955176e662`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#pause-or-resume-a-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform procedure and state verification details for pausing or resuming a TiDB Cloud Dedicated cluster based on `paused` and cluster state values such as `ACTIVE` or `PAUSED`.
- Retrieval Keywords: Pause or resume a TiDB Cloud Dedicated cluster with Terraform, paused = true, paused = false, terraform apply, terraform state show tidbcloud_dedicated_cluster.${resource-name}, state = "PAUSED", state = "ACTIVE", tidbcloud_dedicated_cluster
- Follow-up Guidance: After applying the change, the content shows checking the result with `terraform state show tidbcloud_dedicated_cluster.${resource-name}`, and for resume it states the cluster state will finally change to `ACTIVE`.
- Classification Note: This is classified as an operation because the content describes modifying the cluster lifecycle in Terraform, running `terraform apply`, and verifying the resulting cluster state.

## Official Source Content

### Pause or resume a cluster

You can pause a cluster when its state is `ACTIVE` or resume a cluster when its state is `PAUSED`.

- Set `paused = true` to pause a cluster.
- Set `paused = false` to resume a cluster.

1. In the `cluster.tf` file that is used when you [create the cluster](#create-a-tidb-cloud-dedicated-cluster), add `pause = true` to the configurations:

    ```
    paused = true
    ```

2. Run the `terraform apply` command and type `yes` after checking the plan:

    ```shell
    $ terraform apply

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
           + paused               = true
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
               ~ node_spec_display_name  = "8 vCPU, 16 GiB" -> (known after apply)
               ~ state                   = "ACTIVE" -> (known after apply)
                 # (6 unchanged attributes hidden)
             }
           ~ tiflash_node_setting = {
               ~ node_spec_display_name = "8 vCPU, 64 GiB" -> (known after apply)
               ~ storage_type           = "Basic" -> (known after apply)
                 # (3 unchanged attributes hidden)
             }
           ~ tikv_node_setting    = {
               ~ node_spec_display_name = "8 vCPU, 32 GiB" -> (known after apply)
               ~ storage_type           = "Standard" -> (known after apply)
                 # (3 unchanged attributes hidden)
             }
           ~ update_time          = "2025-06-09 10:01:59.65 +0000 UTC" -> (known after apply)
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

3. Use the `terraform state show tidbcloud_dedicated_cluster.${resource-name}` command to check the state:

    ```
    $ terraform state show tidbcloud_dedicate_cluster.example_cluster

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
         paused              = true
         port                = 4000
         project_id          = "3100000"
         region_display_name = "Oregon (us-west-2)"
         region_id           = "aws-us-west-2"
         state               = "PAUSED"
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
         tikv_node_setting   = {
             node_count             = 3
             node_spec_display_name = "2 vCPU, 4 GiB"
             node_spec_key          = "2C4G"
             storage_size_gi        = 60
             storage_type           = "Standard"
         }
         update_time         = "2025-06-06 06:31:42.974 +0000 UTC"
         version             = "v7.5.6"
     }
    ```

4. When you need to resume the cluster, set `paused = false`:

    ```
    paused = false
    ```

5. Run the `terraform apply` command and type `yes` for confirmation. Wait for a moment, the state will be changed to `ACTIVE` finally.
