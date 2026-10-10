# Terraform delete TiDB Cloud Dedicated VPC peering

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-vpc-peering-resource.md`
- Source Title: `Use TiDB Cloud Dedicated VPC Peering Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated VPC Peering Resource > Delete a TiDB Cloud Dedicated VPC peering`
- Source Line Ranges: `191-243`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `terraform`, `vpc-peering`, `dedicated`, `delete`, `destroy`, `apply`, `state-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0393_283ed8e8af`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-vpc-peering-resource.md#delete-a-tidb-cloud-dedicated-vpc-peering`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `465619e0dd378b9c463d72463f1b46809b757d0862bc65939bd9ed6c2cdd3531`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-vpc-peering-resource#delete-a-tidb-cloud-dedicated-vpc-peering
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-vpc-peering-resource.md

## Retrieval Guidance

- Use When: Use this when you need the Terraform procedure and expected output for deleting a TiDB Cloud Dedicated VPC peering by removing the `tidbcloud_dedicated_vpc_peering` configuration and running `terraform apply`.
- Retrieval Keywords: Delete a TiDB Cloud Dedicated VPC peering, tidbcloud_dedicated_vpc_peering, terraform apply, - destroy, terraform show, Destruction complete, because tidbcloud_dedicated_vpc_peering.example is not in configuration
- Follow-up Guidance: After the destruction completes, running `terraform show` returns nothing because the resource has been cleared.
- Classification Note: This is classified as an operation document because it shows the operational Terraform destroy flow and resulting state output for a TiDB Cloud Dedicated VPC peering resource.

## Official Source Content

## Delete a TiDB Cloud Dedicated VPC peering

To delete a TiDB Cloud Dedicated VPC peering, you can delete the configuration of the `tidbcloud_dedicated_vpc_peering` resource, and then use the `terraform apply` command to destroy the resource:

```shell
  $ terraform apply
  tidbcloud_dedicated_vpc_peering.example: Refreshing state...

  Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

  Terraform will perform the following actions:

  # tidbcloud_dedicated_vpc_peering.example will be destroyed
  # (because tidbcloud_dedicated_vpc_peering.example is not in configuration)
  - resource "tidbcloud_dedicated_vpc_peering" "example" {
      - aws_vpc_peering_connection_id = "pcx-0b2e5211d48000000" -> null
      - customer_account_id           = "986330900000" -> null
      - customer_region_id            = "aws-us-west-2" -> null
      - customer_vpc_cidr             = "172.16.32.0/21" -> null
      - customer_vpc_id               = "vpc-0c0c7d59702000000" -> null
      - labels                        = {
          - "tidb.cloud/project" = "1372813089187000000"
          } -> null
      - project_id                    = "1372813089187000000" -> null
      - state                         = "ACTIVE" -> null
      - tidb_cloud_account_id         = "380838000000" -> null
      - tidb_cloud_cloud_provider     = "aws" -> null
      - tidb_cloud_region_id          = "aws-us-west-2" -> null
      - tidb_cloud_vpc_cidr           = "10.250.0.0/16" -> null
      - tidb_cloud_vpc_id             = "vpc-0b9fa4b78ef000000" -> null
      - vpc_peering_id                = "aws-1934187953894000000" -> null
      }

  Plan: 0 to add, 0 to change, 1 to destroy.

  Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

  tidbcloud_dedicated_vpc_peering.example: Destroying...
  tidbcloud_dedicated_vpc_peering.example: Destruction complete after 1s

  Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

Now, if you run the `terraform show` command, you will get nothing because the resource has been cleared:

```
$ terraform show
```
