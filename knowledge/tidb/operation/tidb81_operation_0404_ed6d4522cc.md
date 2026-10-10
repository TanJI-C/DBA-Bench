# Delete TiDB Cloud Serverless export resource with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-export-resource.md`
- Source Title: `Use TiDB Cloud Serverless Export Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Export Resource > Delete a TiDB Cloud Serverless data export task`
- Source Line Ranges: `187-237`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless`, `export`, `resource-deletion`, `destroy-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0404_ed6d4522cc`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-export-resource.md#delete-a-tidb-cloud-serverless-data-export-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a8fa2c4e4e763debc01725e57d306af9f92e8d0f075c5c918ccd349d7ad09113`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-export-resource#delete-a-tidb-cloud-serverless-data-export-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-export-resource.md

## Retrieval Guidance

- Use When: Use this when you need to remove a TiDB Cloud Serverless export by deleting its Terraform configuration and applying the change.
- Retrieval Keywords: tidbcloud_serverless_export, terraform apply, destroy, not in configuration, terraform show
- Follow-up Guidance: After the resource is cleared, terraform show will show no managed resources.
- Classification Note: This chunk explains deleting the tidbcloud_serverless_export resource by removing its configuration and using terraform apply to destroy it.

## Official Source Content

## Delete a TiDB Cloud Serverless data export task

To delete a TiDB Cloud Serverless data export task, you can delete the configuration of the `tidbcloud_serverless_export` resource, then use the `terraform apply` command to destroy the resource:

```shell
$ terraform apply
tidbcloud_serverless_export.example: Refreshing state...

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

Terraform will perform the following actions:

  # tidbcloud_serverless_export.example will be destroyed
  # (because tidbcloud_serverless_export.example is not in configuration)
  - resource "tidbcloud_serverless_export" "example" {
      - cluster_id     = "10476959660988000000" -> null
      - create_time    = "2025-06-16T08:54:10Z" -> null
      - created_by     = "apikey-S2000000" -> null
      - display_name   = "SNAPSHOT_2025-06-16T08:54:10Z" -> null
      - export_id      = "exp-ezsli6ugtzg2nkmzaitt000000" -> null
      - export_options = {
          - compression = "GZIP" -> null
          - file_type   = "CSV" -> null
        } -> null
      - snapshot_time  = "2025-06-16T08:54:10Z" -> null
      - state          = "RUNNING" -> null
      - target         = {
          - type = "LOCAL" -> null
        } -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

tidbcloud_serverless_export.example: Destroying...
tidbcloud_serverless_export.example: Destruction complete after 2s

Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

Now, if you run the `terraform show` command, it will show no managed resources because the resource has been cleared:

```
$ terraform show
```
