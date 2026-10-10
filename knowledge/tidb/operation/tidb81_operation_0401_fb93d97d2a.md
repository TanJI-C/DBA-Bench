# Delete a TiDB Cloud Serverless cluster with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-cluster-resource.md`
- Source Title: `Use TiDB Cloud Serverless Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Cluster Resource > Delete a TiDB Cloud Serverless cluster`
- Source Line Ranges: `463-549`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless`, `cluster`, `resource`, `delete`, `destroy`, `apply`, `state`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0401_fb93d97d2a`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-cluster-resource.md#delete-a-tidb-cloud-serverless-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `835fdb937019b895977f63943110f8d2980f4e3d10421b07fc33189379059511`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-cluster-resource#delete-a-tidb-cloud-serverless-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform destroy flow for removing a TiDB Cloud Serverless cluster from configuration.
- Retrieval Keywords: tidbcloud_serverless_cluster, terraform apply, destroy, not in configuration, terraform show, Delete a TiDB Cloud Serverless cluster
- Follow-up Guidance: Delete the resource configuration and run terraform apply to destroy the resource; terraform show will then show no managed resources.
- Classification Note: This chunk is an operation guide for deleting a TiDB Cloud Serverless cluster by removing its Terraform configuration and applying the destroy plan.

## Official Source Content

## Delete a TiDB Cloud Serverless cluster

To delete a TiDB Cloud Serverless cluster, you can delete the configuration of the `tidbcloud_serverless_cluster` resource, then use the `terraform apply` command to destroy the resource:

```shell
$ terraform apply
tidbcloud_serverless_cluster.example: Refreshing state...

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

Terraform will perform the following actions:

  # tidbcloud_serverless_cluster.example will be destroyed
  # (because tidbcloud_serverless_cluster.example is not in configuration)
  - resource "tidbcloud_serverless_cluster" "example" {
      - annotations             = {
          - "tidb.cloud/available-features" = "DISABLE_PUBLIC_LB,DELEGATE_USER"
          - "tidb.cloud/has-set-password"   = "false"
        } -> null
      - automated_backup_policy = {
          - retention_days = 14 -> null
          - start_time     = "07:00" -> null
        } -> null
      - cluster_id              = "10145794214536000000" -> null
      - create_time             = "2025-06-16T07:04:41Z" -> null
      - created_by              = "apikey-S2000000" -> null
      - display_name            = "test-tf-modified" -> null
      - encryption_config       = {
          - enhanced_encryption_enabled = false -> null
        } -> null
      - endpoints               = {
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
      - labels                  = {
          - "tidb.cloud/organization" = "1372813089187000000"
          - "tidb.cloud/project"      = "1372813089454000000"
        } -> null
      - project_id              = "1372813089454000000" -> null
      - region                  = {
          - cloud_provider = "aws" -> null
          - display_name   = "N. Virginia (us-east-1)" -> null
          - name           = "regions/aws-us-east-1" -> null
          - region_id      = "us-east-1" -> null
        } -> null
      - spending_limit          = {
          - monthly = 2 -> null
        } -> null
      - state                   = "ACTIVE" -> null
      - update_time             = "2025-06-16T07:04:57Z" -> null
      - user_prefix             = "KhSDGqQ3P000000" -> null
      - version                 = "v7.5.2" -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

tidbcloud_serverless_cluster.example: Destroying...
tidbcloud_serverless_cluster.example: Destruction complete after 1s

Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

Now, if you run the `terraform show` command, it will show no managed resources because the resource has been cleared:

```
$ terraform show
```
