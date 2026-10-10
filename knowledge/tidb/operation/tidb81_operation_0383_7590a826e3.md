# Add a TiDB node group to a TiDB Cloud Dedicated cluster

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource > Modify a TiDB Cloud Dedicated cluster > Add a TiDB node group to the cluster`
- Source Line Ranges: `829-915`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `terraform`, `node-group`, `cluster-scaling`, `resource-creation`, `state-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0383_7590a826e3`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#add-a-tidb-node-group-to-the-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aa0b4fdc751ca7c41aac41604606d31b371d92ad6e93a121d5e3e17c3b290b11`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#add-a-tidb-node-group-to-the-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform steps to add a `tidbcloud_dedicated_node_group` to a TiDB Cloud Dedicated cluster and verify the created node group state when the cluster is `ACTIVE`.
- Retrieval Keywords: Add a TiDB node group to a TiDB Cloud Dedicated cluster, tidbcloud_dedicated_node_group, cluster_id = tidbcloud_dedicated_cluster.example_cluster.cluster_id, node_count = 3, display_name = "test-node-group", terraform apply, terraform state show tidbcloud_dedicated_node_group.${resource-name}, state = "ACTIVE"
- Follow-up Guidance: After creation, the content shows using `terraform state show tidbcloud_dedicated_node_group.${resource-name}` to check fields such as `node_group_id`, `node_spec_key`, `endpoints`, and `state`.
- Classification Note: This is classified as an operation because the content walks through creating a new node group resource in Terraform and validating the resulting resource state.

## Official Source Content

### Add a TiDB node group to the cluster

You can add a TiDB node group to the cluster when its state is `ACTIVE`.

1. In the `cluster.tf` file that is used when you [create the cluster](#create-a-tidb-cloud-dedicated-cluster), add the `tidbcloud_dedicated_node_group` configuration.

    For example, to add a TiDB node group with 3 nodes, you can edit the configurations as follows:

    ```
    resource "tidbcloud_dedicated_node_group" "example_group" {
        cluster_id = tidbcloud_dedicated_cluster.example_cluster.cluster_id
        node_count = 3
        display_name = "test-node-group"
    }
    ```

2. Run the `terraform apply` command and type `yes` for confirmation:

    ```shell
    $ terraform apply
    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
     + create

    Terraform will perform the following actions:

     # tidbcloud_dedicated_node_group.example_group will be created
     + resource "tidbcloud_dedicated_node_group" "example_group" {
         + cluster_id              = "10526169210080596964"
         + display_name            = "test-node-group2"
         + endpoints               = (known after apply)
         + is_default_group        = (known after apply)
         + node_count              = 3
         + node_group_id           = (known after apply)
         + node_spec_display_name  = (known after apply)
         + node_spec_key           = (known after apply)
         + public_endpoint_setting = (known after apply)
         + state                   = (known after apply)
       }

    Plan: 1 to add, 0 to change, 0 to destroy.

    Do you want to perform these actions?
     Terraform will perform the actions described above.
     Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_dedicated_node_group.example_group: Creating...
    tidbcloud_dedicated_node_group.example_group: Still creating... [10s elapsed]

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
    ```

3. Use the `terraform state show tidbcloud_dedicated_node_group.${resource-name}` command to check the state:

    ```shell
    $ terraform state show tidbcloud_dedicated_node_group.example_group
    tidbcloud_dedicated_node_group.example_group:
    resource "tidbcloud_dedicated_node_group" "example_group" {
        cluster_id             = "10526169210000000000"
        display_name           = "test-node-group"
        endpoints              = [
            {
                connection_type = "PUBLIC"
                host            = null
                port            = 0
            },
            {
                connection_type = "VPC_PEERING"
                host            = "private-tidb.pvqmzrxxxxxx.clusters.dev.tidb-cloud.com"
                port            = 4000
            },
            {
                connection_type = "PRIVATE_ENDPOINT"
                host            = "privatelink-19320383.pvqmzrxxxxxx.clusters.dev.tidb-cloud.com"
                port            = 4000
            },
        ]
        is_default_group       = false
        node_count             = 3
        node_group_id          = "1932038361900000000"
        node_spec_display_name = "8 vCPU, 16 GiB"
        node_spec_key          = "8C16G"
        state                  = "ACTIVE"
    }
    ```
