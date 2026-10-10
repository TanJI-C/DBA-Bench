# Modify a TiDB Cloud Serverless cluster with Terraform

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-cluster-resource.md`
- Source Title: `Use TiDB Cloud Serverless Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Cluster Resource > Modify a TiDB Cloud Serverless cluster`
- Source Line Ranges: `292-420`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless`, `cluster`, `resource`, `modify`, `display-name`, `spending-limit`, `public-endpoint`, `backup-policy`, `state-inspection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0295_e2ca0895bb`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-cluster-resource.md#modify-a-tidb-cloud-serverless-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8058c7b1d2b4050fe567d3b886191efdf177d67399db120d0639496f4b809572`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-cluster-resource#modify-a-tidb-cloud-serverless-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform fields and commands for changing a TiDB Cloud Serverless cluster resource.
- Retrieval Keywords: tidbcloud_serverless_cluster, display_name, spending_limit, endpoints.public.disabled, automated_backup_policy.start_time, terraform apply, terraform show, terraform state show tidbcloud_serverless_cluster.${resource-name}
- Follow-up Guidance: Run terraform apply to apply the changes, then use terraform show or terraform state show tidbcloud_serverless_cluster.${resource-name} to inspect the resource state.
- Classification Note: This chunk is a configuration guide for modifying a TiDB Cloud Serverless cluster with Terraform and shows the editable arguments and state inspection commands.

## Official Source Content

## Modify a TiDB Cloud Serverless cluster

For a TiDB Cloud Serverless cluster, you can use Terraform to manage resources. The arguments that you can modify include:

- `display_name`: The display name of the cluster.
- `spending_limit`: The spending limit of the cluster.
- `endpoints.public.disabled`: Whether to disable the public endpoint.
- `automated_backup_policy.start_time`: The UTC time of day in `HH:mm` format when the automated backup starts.

To modify a TiDB Cloud Serverless cluster, you can modify the configuration of the `tidbcloud_serverless_cluster` resource, then use the `terraform apply` command to apply the changes. For example, you can modify the `display_name` and `spending_limit` as follows:

```
resource "tidbcloud_serverless_cluster" "example" {
  project_id = "1372813089454000000"
  display_name = "test-tf-modified"
  spending_limit = {
    monthly = 2
  }
  region = {
    name = "regions/aws-us-east-1"
  }
}
```

Then, run the `terraform apply` command to apply the changes:

```shell
$ terraform apply

tidbcloud_serverless_cluster.example: Refreshing state...

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  ~ update in-place

Terraform will perform the following actions:

  # tidbcloud_serverless_cluster.example will be updated in-place
  ~ resource "tidbcloud_serverless_cluster" "example" {
      ~ annotations             = {
          - "tidb.cloud/available-features" = "DISABLE_PUBLIC_LB,DELEGATE_USER"
          - "tidb.cloud/has-set-password"   = "false"
        } -> (known after apply)
      ~ display_name            = "test-tf" -> "test-tf-modified"
      ~ labels                  = {
          - "tidb.cloud/organization" = "1372813089187041280"
          - "tidb.cloud/project"      = "1372813089454543324"
        } -> (known after apply)
      ~ spending_limit          = {
          ~ monthly = 1 -> 2
        }
      ~ state                   = "ACTIVE" -> (known after apply)
      ~ update_time             = "2025-06-16T07:04:57Z" -> (known after apply)
      ~ version                 = "v7.5.2" -> (known after apply)
        # (9 unchanged attributes hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

tidbcloud_serverless_cluster.example: Modifying...
tidbcloud_serverless_cluster.example: Modifications complete after 8s

Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
```

Then, you can use the `terraform show` or `terraform state show tidbcloud_serverless_cluster.${resource-name}` command to inspect the state of your resource. The former command shows the states of all resources and data sources.

```shell
$ terraform state show tidbcloud_serverless_cluster.example
# tidbcloud_serverless_cluster.example:
resource "tidbcloud_serverless_cluster" "example" {
    annotations             = {
        "tidb.cloud/available-features" = "DISABLE_PUBLIC_LB,DELEGATE_USER"
        "tidb.cloud/has-set-password"   = "false"
    }
    automated_backup_policy = {
        retention_days = 14
        start_time     = "07:00"
    }
    cluster_id              = "10145794214536000000"
    create_time             = "2025-06-16T07:04:41Z"
    created_by              = "apikey-S2000000"
    display_name            = "test-tf-modified"
    encryption_config       = {
        enhanced_encryption_enabled = false
    }
    endpoints               = {
        private = {
            aws  = {
                availability_zone = [
                    "use1-az6",
                ]
                service_name      = "com.amazonaws.vpce.us-east-1.vpce-svc-0062ecf0683000000"
            }
            host = "gateway01-privatelink.us-east-1.prod.aws.tidbcloud.com"
            port = 4000
        }
        public  = {
            disabled = false
            host     = "gateway01.us-east-1.prod.aws.tidbcloud.com"
            port     = 4000
        }
    }
    labels                  = {
        "tidb.cloud/organization" = "1372813089187000000"
        "tidb.cloud/project"      = "1372813089454000000"
    }
    project_id              = "1372813089454000000"
    region                  = {
        cloud_provider = "aws"
        display_name   = "N. Virginia (us-east-1)"
        name           = "regions/aws-us-east-1"
        region_id      = "us-east-1"
    }
    spending_limit          = {
        monthly = 2
    }
    state                   = "ACTIVE"
    update_time             = "2025-06-16T07:04:57Z"
    user_prefix             = "KhSDGqQ3P000000"
    version                 = "v7.5.2"
}
```
