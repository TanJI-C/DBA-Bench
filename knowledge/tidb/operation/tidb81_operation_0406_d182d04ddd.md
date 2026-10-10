# Delete a TiDB Cloud SQL user with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-sql-user-resource.md`
- Source Title: `Use SQL User Resource`
- Source Heading Path: `Use SQL User Resource > Delete a SQL user`
- Source Line Ranges: `242-282`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `terraform`, `sql-user`, `delete`, `destroy`, `apply`, `state`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0406_d182d04ddd`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-sql-user-resource.md#delete-a-sql-user`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7b76ac7bd726ac560e78be543a5da90a588c37147f843b1ffd3e9c26478cd3b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-sql-user-resource#delete-a-sql-user
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-sql-user-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform workflow and expected plan output for deleting a TiDB Cloud SQL user managed by `tidbcloud_sql_user`.
- Retrieval Keywords: Delete a SQL user, tidbcloud_sql_user, terraform apply, - destroy, because tidbcloud_sql_user.example is not in configuration, tidbcloud_sql_user.example will be destroyed, terraform show, Destruction complete, Apply complete! Resources: 0 added, 0 changed, 1 destroyed
- Follow-up Guidance: After the resource is destroyed, running `terraform show` returns nothing because the resource has been cleared.
- Classification Note: This is classified as an operation chunk because the official content describes the procedure and Terraform output for destroying a SQL user resource.

## Official Source Content

## Delete a SQL user

To delete a SQL user, you can delete the configuration of the `tidbcloud_sql_user` resource, then use the `terraform apply` command to destroy the resource:

```shell
  $ terraform apply
  tidbcloud_sql_user.example: Refreshing state...

  Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
    - destroy

  Terraform will perform the following actions:

    # tidbcloud_sql_user.example will be destroyed
    # (because tidbcloud_sql_user.example is not in configuration)
    - resource "tidbcloud_sql_user" "example" {
        - builtin_role = "role_readonly" -> null
        - cluster_id   = "10423692645600000000" -> null
        - password     = (sensitive value) -> null
        - user_name    = "example_user" -> null
      }

  Plan: 0 to add, 0 to change, 1 to destroy.

  Do you want to perform these actions?
    Terraform will perform the actions described above.
    Only 'yes' will be accepted to approve.

    Enter a value: yes

  tidbcloud_sql_user.example: Destroying...
  tidbcloud_sql_user.example: Destruction complete after 3s

  Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

Now, if you run the `terraform show` command, you will get nothing because the resource has been cleared:

```
$ terraform show
```
