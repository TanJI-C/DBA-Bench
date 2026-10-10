# Delete a TiDB Cloud Terraform backup resource

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-backup-resource.md`
- Source Title: `Use Backup Resource`
- Source Heading Path: `Use Backup Resource > Delete a backup`
- Source Line Ranges: `156-176`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `backup`, `resource-deletion`, `destroy`, `state-cleanup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0369_ced5d7740e`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-backup-resource.md#delete-a-backup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4c29eeac75841ced5336b276cd559dadfae5f41716808f12dfcbf3250b513d2c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-backup-resource#delete-a-backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-backup-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented Terraform command flow for deleting a backup resource and confirming that the managed resource has been cleared from state.
- Retrieval Keywords: Delete a backup, terraform destroy, backup directory, backup.tf, Plan: 0 to add, 0 to change, 1 to destroy, Do you really want to destroy all resources?, Only 'yes' will be accepted to confirm, terraform show, resource has been cleared
- Follow-up Guidance: After `terraform destroy`, running `terraform show` returns nothing because the resource has been cleared.
- Classification Note: This is classified as an operation chunk because the official content gives the command and expected output for destroying a backup resource and verifying its removal.

## Official Source Content

## Delete a backup

To delete a backup, go to the backup directory where the corresponding `backup.tf` file is located, and then run the `terraform destroy` command to destroy the backup resource.

```
$ terraform destroy

Plan: 0 to add, 0 to change, 1 to destroy.

Do you really want to destroy all resources?
Terraform will destroy all your managed infrastructure, as shown above.
There is no undo. Only 'yes' will be accepted to confirm.

Enter a value: yes
```

Now, if you run the `terraform show` command, you will get nothing because the resource has been cleared:

```
$ terraform show
```
