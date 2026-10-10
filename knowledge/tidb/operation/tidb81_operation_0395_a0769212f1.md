# TiDB Cloud import resource S3 import, deletion behavior, and configuration reference

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-import-resource.md`
- Source Title: `Use Import Resource`
- Source Heading Path: `Use Import Resource > Create and run an import task > Create and run an Amazon S3 import task | Use Import Resource > Update an import task | Use Import Resource > Delete an import task | Use Import Resource > Configurations`
- Source Line Ranges: `188-301`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `terraform`, `import`, `amazon-s3`, `csv`, `parquet`, `task-status`, `cancellation`, `destroy`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0395_a0769212f1`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-import-resource.md#create-and-run-an-amazon-s3-import-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f013db0d1c100dcdc3d10d845fc13f36607ba5597183484e2d24de2aca12f10`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-import-resource#create-and-run-an-amazon-s3-import-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-import-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need Terraform details for Amazon S3 import tasks with `tidbcloud_import`, or when checking import task update limitations, destroy behavior, cancellation conditions, and the configuration reference link.
- Retrieval Keywords: Amazon S3 import task, type = "S3", data_format = "CSV", data_format = "Parquet", aws_role_arn, source_url, configure Amazon S3 access, terraform apply, terraform refresh, terraform state show tidbcloud_import.${resource-name}, Import tasks cannot be updated, Delete Error, CancelImport, COMPLETED import task, IMPORTING, terraform destroy, configuration documentation, resources/import
- Follow-up Guidance: The chunk states that deleting an import task in Terraform means canceling the corresponding import resource, and cancellation succeeds only for a task whose status is `IMPORTING`.
- Classification Note: This is classified as an operation chunk because the content covers procedural Terraform usage for S3 imports plus the documented operational behavior for update, delete, and configuration lookup.

## Official Source Content

### Create and run an Amazon S3 import task

> **Note:**
>
> To allow TiDB Cloud to access your files in the Amazon S3 bucket, you need to [configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-amazon-s3-access) first.

1. Create an `import` directory, and then create a `main.tf` inside it. For example:

   ```
   terraform {
     required_providers {
       tidbcloud = {
         source = "tidbcloud/tidbcloud"
       }
     }
   }

   provider "tidbcloud" {
     public_key  = "your_public_key"
     private_key = "your_private_key"
   }

   resource "tidbcloud_import" "example_s3_csv" {
     project_id   = "your_project_id"
     cluster_id   = "your_cluster_id"
     type         = "S3"
     data_format  = "CSV"
     aws_role_arn = "your_arn"
     source_url   = "your_url"
   }

   resource "tidbcloud_import" "example_s3_parquet" {
     project_id   = "your_project_id"
     cluster_id   = "your_cluster_id"
     type         = "S3"
     data_format  = "Parquet"
     aws_role_arn = "your_arn"
     source_url   = "your_url"
   }
   ```

2. Run the `terraform apply` command to create an import task, and then type `yes` to confirm the creation and start the import:

   ```
   $ terraform apply
   ...
   Plan: 2 to add, 0 to change, 0 to destroy.

   Do you want to perform these actions?
   Terraform will perform the actions described above.
   Only 'yes' will be accepted to approve.

   Enter a value: yes

   tidbcloud_import.example_s3_csv: Creating...
   tidbcloud_import.example_s3_csv: Creation complete after 3s [id=781075]
   tidbcloud_import.example_s3_parquet: Creating...
   tidbcloud_import.example_s3_parquet: Creation complete after 4s [id=781076]
   ```

3. Use `terraform refresh` and `terraform state show tidbcloud_import.${resource-name}` to update and check the status of the import task.
## Update an import task

Import tasks cannot be updated.
## Delete an import task

For Terraform, deleting an import task means canceling the corresponding import resource.

You cannot cancel a `COMPLETED` import task. Otherwise, you will get a `Delete Error` as in the following example:

```
$ terraform destroy
...
Plan: 0 to add, 0 to change, 1 to destroy.

Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes

tidbcloud_import.example_local: Destroying... [id=781074]
╷
│ Error: Delete Error
│
│ Unable to call CancelImport, got error: [DELETE /api/internal/projects/{project_id}/clusters/{cluster_id}/imports/{id}][500] CancelImport default  &{Code:59900104 Details:[] Message:failed to cancel
│ import}
╵
```

You can cancel an import task whose status is `IMPORTING`. For example:

```
$ terraform destroy
...
Plan: 0 to add, 0 to change, 1 to destroy.

Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes

tidbcloud_import.example_local: Destroying... [id=781074]
tidbcloud_import.example_local: Destruction complete after 0s

Destroy complete! Resources: 1 destroyed.
```
## Configurations

See [configuration documentation](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest/docs/resources/import) to get all the available configurations for the import resource.
