# Delete a TiDB Cloud Dedicated network container with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-network-container-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Network Container Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Network Container Resource > Delete a TiDB Cloud Dedicated network container`
- Source Line Ranges: `183-232`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `network-container`, `deletion`, `destroy`, `inactive-state`, `apply`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0388_8d91ec54b8`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-network-container-resource.md#delete-a-tidb-cloud-dedicated-network-container`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f2958205c695c220425cedd932a64765aec111992cd5ed66a4ac470e25a9295f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-network-container-resource#delete-a-tidb-cloud-dedicated-network-container
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-network-container-resource.md

## Retrieval Guidance

- Use When: Use this when you need the documented conditions and Terraform apply output for deleting a TiDB Cloud Dedicated network container.
- Retrieval Keywords: Delete a TiDB Cloud Dedicated network container, tidbcloud_dedicated_network_container, terraform apply, destroy, INACTIVE, ACTIVE, terraform show, Destruction complete, Plan: 0 to add, 0 to change, 1 to destroy
- Follow-up Guidance: The source also says that after destruction, `terraform show` displays no managed resources because the resource has been cleared.
- Classification Note: This is classified as an operation chunk because it describes the deletion condition based on resource state and the Terraform destroy procedure for the cloud resource.

## Official Source Content

## Delete a TiDB Cloud Dedicated network container

To delete a TiDB Cloud Dedicated cluster, you can delete the configuration of the `tidbcloud_dedicated_cluster` resource, then use the `terraform apply` command to destroy the resource. However, you must ensure that the status of the TiDB Cloud Dedicated network container is not `ACTIVE`. If it is `ACTIVE`, you cannot delete it.

If the status is `INACTIVE`, you can delete it by running the following command:

```shell
  $ terraform apply
  tidbcloud_dedicated_network_container.example: Refreshing state...

  Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
    - destroy

  Terraform will perform the following actions:

    # tidbcloud_dedicated_network_container.example will be destroyed
    # (because tidbcloud_dedicated_network_container.example is not in configuration)
    - resource "tidbcloud_dedicated_network_container" "example" {
        - cidr_notation        = "172.16.16.0/21" -> null
        - cloud_provider       = "aws" -> null
        - labels               = {
            - "tidb.cloud/project" = "1372813089454000000"
          } -> null
        - network_container_id = "1934235512696000000" -> null
        - project_id           = "1372813089454000000" -> null
        - region_display_name  = "Seoul (ap-northeast-2)" -> null
        - region_id            = "aws-ap-northeast-2" -> null
        - state                = "INACTIVE" -> null
          # (1 unchanged attribute hidden)
      }

  Plan: 0 to add, 0 to change, 1 to destroy.

  Do you want to perform these actions?
    Terraform will perform the actions described above.
    Only 'yes' will be accepted to approve.

    Enter a value: yes

  tidbcloud_dedicated_network_container.example: Destroying...
  tidbcloud_dedicated_network_container.example: Destruction complete after 2s

  Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

Now, if you run the `terraform show` command, it will show no managed resources because the resource has been cleared:

```
$ terraform show
```
