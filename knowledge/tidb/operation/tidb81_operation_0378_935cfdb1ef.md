# Terraform state refresh and state show for Dedicated cluster

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource > Create a TiDB Cloud Dedicated cluster`
- Source Line Ranges: `252-383`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`
- Topic Tags: `terraform`, `state-refresh`, `state-show`, `cluster-creation`, `resource-state`, `endpoints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0378_935cfdb1ef`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#create-a-tidb-cloud-dedicated-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6c856aa372103cb00a080631299b47e14d4814bfea00d891e7021dd6f902a2e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#create-a-tidb-cloud-dedicated-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform commands and example output for refreshing and displaying the state of a TiDB Cloud Dedicated cluster resource, including endpoint and node setting fields.
- Retrieval Keywords: terraform refresh, terraform state show tidbcloud_dedicated_cluster.${resource-name}, terraform state show tidbcloud_dedicated_cluster.example_cluster, tidbcloud_dedicated_cluster, Dedicated cluster state, state show, state refresh, tidb_node_setting.endpoints, connection_type PUBLIC, connection_type VPC_PEERING, connection_type PRIVATE_ENDPOINT, public_endpoint_setting.enabled, cluster_id, project_id, region_id aws-us-west-2, state ACTIVE, version v7.5.6
- Follow-up Guidance: The source says that if you want to synchronize the state from the remote, run `terraform refresh` and then run `terraform state show tidbcloud_dedicated_cluster.${resource-name}` to display the state.
- Classification Note: This is classified as an operation because the official content shows the `terraform refresh` and `terraform state show` commands and their resulting resource state for a Dedicated cluster.

## Official Source Content

```shell
    $ terraform state show tidbcloud_dedicated_cluster.example_cluster

    # tidbcloud_dedicated_cluster.example_cluster:
    resource "tidbcloud_dedicated_cluster" "example_cluster" {
        annotations         = {
            "tidb.cloud/available-features" = "DISABLE_PUBLIC_LB,PRIVATELINK,DELEGATE_USER"
            "tidb.cloud/has-set-password"   = "false"
        }
        cloud_provider      = "aws"
        cluster_id          = "1379661944600000000"
        create_time         = "2025-06-06 06:25:29.878 +0000 UTC"
        created_by          = "apikey-XXXXXXXX"
        display_name        = "test-tf"
        labels              = {
            "tidb.cloud/organization" = "60000"
            "tidb.cloud/project"      = "3100000"
        }
        port                = 4000
        project_id          = "3100000"
        region_display_name = "Oregon (us-west-2)"
        region_id           = "aws-us-west-2"
        state               = "ACTIVE"
        tidb_node_setting   = {
            endpoints               = [
                {
                    connection_type = "PUBLIC"
                    host            = "tidb.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                    port            = 4000
                },
                {
                    connection_type = "VPC_PEERING"
                    host            = "private-tidb.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                    port            = 4000
                },
                {
                    connection_type = "PRIVATE_ENDPOINT"
                    host            = null
                    port            = 4000
                },
            ]
            is_default_group        = true
            node_count              = 1
            node_group_display_name = "DefaultGroup"
            node_group_id           = "1931960832833000000"
            node_spec_display_name  = "2 vCPU, 4 GiB beta"
            node_spec_key           = "2C4G"
            state                   = "ACTIVE"
        }
        tikv_node_setting   = {
            node_count             = 3
            node_spec_display_name = "2 vCPU, 4 GiB"
            node_spec_key          = "2C4G"
            storage_size_gi        = 60
            storage_type           = "Standard"
        }
        update_time         = "2025-06-06 06:31:42.974 +0000 UTC"
        version             = "v7.5.6"
    }
    ```

6. If you want to synchronize the state from the remote, run the `terraform refresh` command to update the state, and then run the `terraform state show tidbcloud_dedicated_cluster.${resource-name}` command to display the state.

    ```shell
    $ terraform refresh

    tidbcloud_dedicated_cluster.example_cluster: Refreshing state...

    $ terraform state show tidbcloud_dedicated_cluster.example_cluster

    # tidbcloud_dedicated_cluster.example_cluster:
    resource "tidbcloud_dedicated_cluster" "example_cluster" {
        annotations         = {
            "tidb.cloud/available-features" = "DISABLE_PUBLIC_LB,PRIVATELINK,DELEGATE_USER"
            "tidb.cloud/has-set-password"   = "false"
        }
        cloud_provider      = "aws"
        cluster_id          = "10528940229200000000"
        create_time         = "2025-06-06 06:25:29.878 +0000 UTC"
        created_by          = "apikey-XXXXXXXX"
        display_name        = "test-tf"
        labels              = {
            "tidb.cloud/organization" = "60000"
            "tidb.cloud/project"      = "3190000"
        }
        port                = 4000
        project_id          = "3190000"
        region_display_name = "Oregon (us-west-2)"
        region_id           = "aws-us-west-2"
        state               = "ACTIVE"
        tidb_node_setting   = {
            endpoints               = [
                {
                    connection_type = "PUBLIC"
                    host            = "tidb.taiqixxxxxxx.clusters.tidb-cloud.com"
                    port            = 4000
                },
                {
                    connection_type = "VPC_PEERING"
                    host            = "private-tidb.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                    port            = 4000
                },
                {
                    connection_type = "PRIVATE_ENDPOINT"
                    host            = "privatelink-19319608.taiqixxxxxxx.clusters.dev.tidb-cloud.com"
                    port            = 4000
                },
            ]
            is_default_group        = true
            node_count              = 1
            node_group_display_name = "DefaultGroup"
            node_group_id           = "1931960832800000000"
            node_spec_display_name  = "2 vCPU, 4 GiB beta"
            node_spec_key           = "2C4G"
            public_endpoint_setting = {
                enabled        = false
                ip_access_list = []
            }
            state                   = "ACTIVE"
        }
        tikv_node_setting   = {
            node_count             = 3
            node_spec_display_name = "2 vCPU, 4 GiB"
            node_spec_key          = "2C4G"
            storage_size_gi        = 60
            storage_type           = "Standard"
        }
        update_time         = "2025-06-06 06:31:42.974 +0000 UTC"
        version             = "v7.5.6"
    }
    ```
