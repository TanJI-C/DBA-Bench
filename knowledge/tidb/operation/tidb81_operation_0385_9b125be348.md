# Delete a TiDB Cloud Dedicated cluster with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource > Delete a TiDB Cloud Dedicated cluster`
- Source Line Ranges: `1093-1198`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `cluster-deletion`, `resource-destroy`, `apply`, `state-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0385_9b125be348`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#delete-a-tidb-cloud-dedicated-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9542f4171d36710d8e29e6db4c0b4d2251344ce65bb3a82cee8b4911fcbbe80`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#delete-a-tidb-cloud-dedicated-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about deleting a TiDB Cloud Dedicated cluster managed by Terraform and verifying that the resource was removed from Terraform state.
- Retrieval Keywords: Delete a TiDB Cloud Dedicated cluster, tidbcloud_dedicated_cluster, terraform apply, destroy, terraform show, no managed resources, resource has been cleared, tidbcloud_dedicated_cluster.example_cluster
- Follow-up Guidance: After destruction, running `terraform show` shows no managed resources because the resource has been cleared.
- Classification Note: This is an operation chunk because the official content describes deleting the `tidbcloud_dedicated_cluster` resource with `terraform apply` and checking the cleared state with `terraform show`.

## Official Source Content

## Delete a TiDB Cloud Dedicated cluster

To delete a TiDB Cloud Dedicated cluster, you can delete the configuration of the `tidbcloud_dedicated_cluster` resource, then use the `terraform apply` command to destroy the resource:

```shell
  $ terraform apply
  tidbcloud_dedicated_cluster.example_cluster: Refreshing state...

  Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
    - destroy
   Terraform will perform the following actions:

    # tidbcloud_dedicated_cluster.example_cluster will be destroyed
    # (because tidbcloud_dedicated_cluster.example_cluster is not in configuration)
    - resource "tidbcloud_dedicated_cluster" "example_cluster" {
        - annotations          = {
            - "tidb.cloud/available-features" = "DELEGATE_USER,DISABLE_PUBLIC_LB,PRIVATELINK"
            - "tidb.cloud/has-set-password"   = "false"
          } -> null
        - cloud_provider       = "aws" -> null
        - cluster_id           = "10526169210000000000" -> null
        - create_time          = "2025-06-06 09:12:55.396 +0000 UTC" -> null
        - created_by           = "apikey-K1R3JIC0" -> null
        - display_name         = "test-tf" -> null
        - labels               = {
            - "tidb.cloud/organization" = "60000"
            - "tidb.cloud/project"      = "3100000"
          } -> null
        - paused               = false -> null
        - port                 = 4000 -> null
        - project_id           = "3100000" -> null
        - region_display_name  = "Oregon (us-west-2)" -> null
        - region_id            = "aws-us-west-2" -> null
        - state                = "ACTIVE" -> null
        - tidb_node_setting    = {
            - endpoints               = [
                - {
                    - connection_type = "PUBLIC"
                    - host            = "tidb.nwdkyhxxxxxx.clusters.dev.tidb-cloud.com"
                    - port            = 4000
                  },
                - {
                    - connection_type = "VPC_PEERING"
                    - host            = "private-tidb.nwdkyhxxxxxx.clusters.dev.tidb-cloud.com"
                    - port            = 4000
                  },
                - {
                    - connection_type = "PRIVATE_ENDPOINT"
                    - host            = "privatelink-19320000.nwdkyhxxxxxx.clusters.dev.tidb-cloud.com"
                    - port            = 4000
                  },
              ] -> null
            - is_default_group        = true -> null
            - node_count              = 2 -> null
            - node_group_display_name = "DefaultGroup" -> null
            - node_group_id           = "1932002964533000000" -> null
            - node_spec_display_name  = "8 vCPU, 16 GiB" -> null
            - node_spec_key           = "8C16G" -> null
            - public_endpoint_setting = {
                - enabled        = true -> null
                - ip_access_list = [
                    - {
                        - cidr_notation = "0.0.0.0/32"
                          # (1 unchanged attribute hidden)
                      },
                  ] -> null
              } -> null
            - state                   = "ACTIVE" -> null
          } -> null
        - tiflash_node_setting = {
            - node_count             = 4 -> null
            - node_spec_display_name = "8 vCPU, 64 GiB" -> null
            - node_spec_key          = "8C64G" -> null
            - storage_size_gi        = 200 -> null
            - storage_type           = "Basic" -> null
          } -> null
        - tikv_node_setting    = {
            - node_count             = 6 -> null
            - node_spec_display_name = "8 vCPU, 32 GiB" -> null
            - node_spec_key          = "8C32G" -> null
            - storage_size_gi        = 200 -> null
            - storage_type           = "Standard" -> null
          } -> null
        - update_time          = "2025-06-06 14:15:29.609 +0000 UTC" -> null
        - version              = "v7.5.6" -> null
      }

    Plan: 0 to add, 0 to change, 1 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_dedicated_cluster.example_cluster: Destroying...
    tidbcloud_dedicated_cluster.example_cluster: Destruction complete after 3s

    Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
  ```

Now, if you run the `terraform show` command, it will show no managed resources because the resource has been cleared:

```
$ terraform show
```
