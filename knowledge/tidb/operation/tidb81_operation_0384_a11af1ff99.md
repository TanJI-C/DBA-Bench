# Update, delete, and import TiDB Cloud Dedicated Terraform resources

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-cluster-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Cluster Resource > Modify a TiDB Cloud Dedicated cluster > Update a TiDB node group of the cluster | Use TiDB Cloud Dedicated Cluster Resource > Modify a TiDB Cloud Dedicated cluster > Delete a TiDB node group of the cluster | Use TiDB Cloud Dedicated Cluster Resource > Import a cluster`
- Source Line Ranges: `916-1092`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `terraform`, `dedicated-cluster`, `node-group`, `update`, `delete`, `import`, `apply`, `plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0384_a11af1ff99`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-cluster-resource.md#update-a-tidb-node-group-of-the-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `68fa38b217c4c53bd582193b30f48fa6c8c1fe2100706a568418b545867126a1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-cluster-resource#update-a-tidb-node-group-of-the-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when working with Terraform lifecycle operations for a TiDB Cloud Dedicated cluster resource, including updating or deleting a `tidbcloud_dedicated_node_group` and importing an existing `tidbcloud_dedicated_cluster` into Terraform management.
- Retrieval Keywords: tidbcloud_dedicated_node_group, tidbcloud_dedicated_cluster, Update a TiDB node group of the cluster, Delete a TiDB node group of the cluster, Import a cluster, terraform apply, terraform plan -generate-config-out=generated.tf, terraform show, cluster.tf, node_count, state ACTIVE, destroy, import block, generated.tf, example_cluster, example_group
- Follow-up Guidance: The content notes that updating a TiDB node group is supported when its state is `ACTIVE`, deleting the resource configuration and running `terraform apply` destroys the node group resource, and importing requires an import block followed by `terraform plan -generate-config-out=generated.tf` and `terraform apply`.
- Classification Note: This is classified as an operation chunk because the official content describes procedural Terraform operations to update, destroy, and import TiDB Cloud Dedicated resources.

## Official Source Content

### Update a TiDB node group of the cluster

You can update a TiDB node group of the cluster when its state is `ACTIVE`.

1. In the `cluster.tf` file that is used when you [create the cluster](#create-a-tidb-cloud-dedicated-cluster), edit the configurations of `tidbcloud_dedicated_node_group`.

    For example, to change the node count to `1`, edit the configurations as follows:

    ```
    resource "tidbcloud_dedicated_node_group" "example_group" {
        cluster_id = tidbcloud_dedicated_cluster.example_cluster.cluster_id
        node_count = 1
        display_name = "test-node-group"
    }
    ```

2. Run the `terraform apply` command and type `yes` for confirmation:

    ```shell
    $ terraform apply
    tidbcloud_dedicated_node_group.example_group: Refreshing state...

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      ~ update in-place

    Terraform will perform the following actions:

      # tidbcloud_dedicated_node_group.example_group will be updated in-place
      ~ resource "tidbcloud_dedicated_node_group" "example_group" {
          ~ endpoints               = [
              - {
                  - connection_type = "PUBLIC"
                  - port            = 0
                    # (1 unchanged attribute hidden)
                },
              - {
                  - connection_type = "VPC_PEERING"
                  - host            = "private-tidb.pvqmzrxxxxxx.clusters.dev.tidb-cloud.com"
                  - port            = 4000
                },
              - {
                  - connection_type = "PRIVATE_ENDPOINT"
                  - host            = "privatelink-19320383.pvqmzrxxxxxx.clusters.dev.tidb-cloud.com"
                  - port            = 4000
                },
            ] -> (known after apply)
          ~ node_count              = 3 -> 1
          ~ node_spec_display_name  = "8 vCPU, 16 GiB" -> (known after apply)
          ~ node_spec_key           = "8C16G" -> (known after apply)
          ~ state                   = "ACTIVE" -> (known after apply)
            # (5 unchanged attributes hidden)
        }

    Plan: 0 to add, 1 to change, 0 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_dedicated_node_group.example_group: Modifying...
    tidbcloud_dedicated_node_group.example_group: Still modifying... [10s elapsed]
    tidbcloud_dedicated_node_group.example_group: Modifications complete after 24s

    Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
    ```
### Delete a TiDB node group of the cluster

To delete a TiDB node group of the cluster, you can delete the configuration of the `dedicated_node_group` resource, then use the `terraform apply` command to destroy the resource:

  ```shell
    $ terraform apply
    tidbcloud_dedicated_node_group.example_group: Refreshing state...

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      - destroy

    Terraform will perform the following actions:

      # tidbcloud_dedicated_node_group.example_group will be destroyed
      # (because tidbcloud_dedicated_node_group.example_group is not in configuration)
      - resource "tidbcloud_dedicated_node_group" "example_group" {
          - cluster_id              = "10526169210000000000" -> null
          - display_name            = "test-node-group" -> null
          - endpoints               = [
              - {
                  - connection_type = "PUBLIC"
                  - port            = 0
                    # (1 unchanged attribute hidden)
                },
              - {
                  - connection_type = "VPC_PEERING"
                  - host            = "private-tidb.pvqmzrxxxxxx.clusters.dev.tidb-cloud.com"
                  - port            = 4000
                },
              - {
                  - connection_type = "PRIVATE_ENDPOINT"
                  - host            = "privatelink-19320383.pvqmzrxxxxxx.clusters.dev.tidb-cloud.com"
                  - port            = 4000
                },
            ] -> null
          - is_default_group        = false -> null
          - node_count              = 1 -> null
          - node_group_id           = "1932038361900000000" -> null
          - node_spec_display_name  = "8 vCPU, 16 GiB" -> null
          - node_spec_key           = "8C16G" -> null
          - public_endpoint_setting = {
              - enabled        = false -> null
              - ip_access_list = [] -> null
            } -> null
          - state                   = "PAUSED" -> null
        }

    Plan: 0 to add, 0 to change, 1 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value: yes

    tidbcloud_dedicated_node_group.example_group: Destroying...
    tidbcloud_dedicated_node_group.example_group: Destruction complete after 3s

    Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
  ```

Now, if you run the `terraform show` command, you will get nothing because the resource has been cleared:

```
$ terraform show
```
## Import a cluster

For a TiDB cluster that is not managed by Terraform, you can use Terraform to manage it just by importing it.

Import a cluster that is not created by Terraform as follows:

1. Add an import block for the new TiDB Cloud Dedicated cluster resource.

    Add the following import block to your `.tf` file, replace `example` with a desired resource name, and replace `${id}` with the cluster ID:

    ```
    import {
      to = tidbcloud_dedicated_cluster.example_cluster
      id = "${id}"
    }
    ```

2. Generate the new configuration file.

    Generate the new configuration file for the new TiDB Cloud Dedicated cluster resource according to the import block:

      ```shell
      terraform plan -generate-config-out=generated.tf
      ```

    Do not specify an existing `.tf` file name in the preceding command. Otherwise, Terraform will return an error.

3. Review and apply the generated configuration.

    Review the generated configuration file to ensure that it meets your needs. Optionally, you can move the contents of this file to your preferred location.

    Then, run `terraform apply` to import your infrastructure. After applying, the example output is as follows: 

    ```shell
    tidbcloud_dedicated_cluster.example_cluster: Importing... 
    tidbcloud_dedicated_cluster.example_cluster: Import complete 

    Apply complete! Resources: 1 imported, 0 added, 0 changed, 0 destroyed.
    ```

Now you can manage the imported cluster with Terraform.
