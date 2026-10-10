# Delete a TiDB Cloud Serverless branch with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-branch-resource.md`
- Source Title: `Use TiDB Cloud Serverless Branch Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Branch Resource > Delete a TiDB Cloud Serverless branch`
- Source Line Ranges: `203-270`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless-branch`, `deletion`, `destroy`, `apply`, `state`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0398_86d0633fd3`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-branch-resource.md#delete-a-tidb-cloud-serverless-branch`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `644a007d6b02eaea90d607d7a12688e2db954556318244b4fa773ad98e11a4e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-branch-resource#delete-a-tidb-cloud-serverless-branch
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-branch-resource.md

## Retrieval Guidance

- Use When: Use this content when you need the Terraform destroy workflow for removing a TiDB Cloud Serverless branch by deleting the `tidbcloud_serverless_branch` configuration and running `terraform apply`.
- Retrieval Keywords: Delete a TiDB Cloud Serverless branch, tidbcloud_serverless_branch, terraform apply, - destroy, because tidbcloud_serverless_branch.example is not in configuration, Plan: 0 to add, 0 to change, 1 to destroy, Destroying..., Destruction complete, terraform show, no managed resources
- Follow-up Guidance: The source adds that after the resource is cleared, running `terraform show` shows no managed resources.
- Classification Note: This is classified as an operation chunk because the official content provides the destroy plan, confirmation prompt, and post-deletion state behavior for a serverless branch resource.

## Official Source Content

## Delete a TiDB Cloud Serverless branch

To delete a TiDB Cloud Serverless branch, you can delete the configuration of the `tidbcloud_serverless_branch` resource, then use the `terraform apply` command to destroy the resource:

```shell
$ terraform apply
tidbcloud_serverless_branch.example: Refreshing state...

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

Terraform will perform the following actions:

  # tidbcloud_serverless_branch.example will be destroyed
  # (because tidbcloud_serverless_branch.example is not in configuration)
  - resource "tidbcloud_serverless_branch" "example" {
      - annotations         = {
          - "tidb.cloud/has-set-password" = "false"
        } -> null
      - branch_id           = "bran-qt3fij6jufcf5pluot5h000000" -> null
      - cluster_id          = "10581524018573000000" -> null
      - create_time         = "2025-06-16T07:55:51Z" -> null
      - created_by          = "apikey-S2000000" -> null
      - display_name        = "example" -> null
      - endpoints           = {
          - private = {
              - aws  = {
                  - availability_zone = [
                      - "use1-az6",
                    ] -> null
                  - service_name      = "com.amazonaws.vpce.us-east-1.vpce-svc-0062ecf0683000000" -> null
                } -> null
              - host = "gateway01-privatelink.us-east-1.prod.aws.tidbcloud.com" -> null
              - port = 4000 -> null
            } -> null
          - public  = {
              - disabled = false -> null
              - host     = "gateway01.us-east-1.prod.aws.tidbcloud.com" -> null
              - port     = 4000 -> null
            } -> null
        } -> null
      - parent_display_name = "test-tf" -> null
      - parent_id           = "10581524018573000000" -> null
      - parent_timestamp    = "2025-06-16T07:55:51Z" -> null
      - state               = "ACTIVE" -> null
      - update_time         = "2025-06-16T07:56:49Z" -> null
      - user_prefix         = "4ER5SbndR000000" -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

tidbcloud_serverless_branch.example: Destroying...
tidbcloud_serverless_branch.example: Destruction complete after 1s

Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

Now, if you run the `terraform show` command, it will show no managed resources because the resource has been cleared:

```
$ terraform show
```
