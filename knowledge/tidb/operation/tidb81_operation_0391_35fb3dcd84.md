# Delete dedicated private endpoint connection with Terraform apply

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Private Endpoint Connection Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Private Endpoint Connection Resource > Delete a TiDB Cloud Dedicated private endpoint connection`
- Source Line Ranges: `189-241`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `private-endpoint`, `resource-deletion`, `destroy-plan`, `state-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0391_35fb3dcd84`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md#delete-a-tidb-cloud-dedicated-private-endpoint-connection`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8af718169a2df43c17bad4e39fcf098d4b5189c38e069d37e2633c20a0d8ebee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource#delete-a-tidb-cloud-dedicated-private-endpoint-connection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about deleting a TiDB Cloud Dedicated private endpoint connection managed by Terraform and confirming the resource is removed from state after apply.
- Retrieval Keywords: tidbcloud_dedicated_private_endpoint_connection, Delete a TiDB Cloud Dedicated private endpoint connection, terraform apply, - destroy, not in configuration, terraform show, Apply complete! Resources: 0 added, 0 changed, 1 destroyed., Destroying..., Destruction complete after 1s
- Follow-up Guidance: After deletion, running the `terraform show` command returns nothing because the resource has been cleared.
- Classification Note: This is classified as an operation chunk because it shows the Terraform deletion workflow and state verification for the `tidbcloud_dedicated_private_endpoint_connection` resource.

## Official Source Content

## Delete a TiDB Cloud Dedicated private endpoint connection

To delete a TiDB Cloud Dedicated private endpoint connection, you can delete the configuration of the `tidbcloud_dedicated_private_endpoint_connection` resource, and then use the `terraform apply` command to destroy the resource:

```shell
  $ terraform apply
  tidbcloud_dedicated_private_endpoint_connection.example: Refreshing state...

  Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

  Terraform will perform the following actions:

  # tidbcloud_dedicated_private_endpoint_connection.example will be destroyed
  # (because tidbcloud_dedicated_private_endpoint_connection.example is not in configuration)
  - resource "tidbcloud_dedicated_private_endpoint_connection" "example" {
      - cloud_provider                 = "aws" -> null
      - cluster_display_name           = "test-tf" -> null
      - cluster_id                     = "10757937805044000000" -> null
      - endpoint_id                    = "vpce-03367e96180000000" -> null
      - endpoint_state                 = "ACTIVE" -> null
      - host                           = "privatelink-19341000.ubkypd1sx000.clusters.tidb-cloud.com" -> null
      - labels                         = {
          - "tidb.cloud/project" = "1372813089454000000"
          } -> null
      - message                        = "The VPC Endpoint Id '{vpce-03367e961805e35b6 []}' does not exist" -> null
      - node_group_id                  = "1934178998036000000" -> null
      - port                           = 4000 -> null
      - private_endpoint_connection_id = "1934214559409000000" -> null
      - private_link_service_name      = "com.amazonaws.vpce.us-west-2.vpce-svc-07468b31cc9000000" -> null
      - region_display_name            = "Oregon (us-west-2)" -> null
      - region_id                      = "aws-us-west-2" -> null
      }

  Plan: 0 to add, 0 to change, 1 to destroy.

  Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

  tidbcloud_dedicated_private_endpoint_connection.example: Destroying...
  tidbcloud_dedicated_private_endpoint_connection.example: Destruction complete after 1s

  Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

Now, if you run the `terraform show` command, you will get nothing because the resource has been cleared:

```
$ terraform show
```
