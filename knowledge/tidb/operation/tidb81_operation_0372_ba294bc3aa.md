# Modify a dedicated cluster by adding TiFlash

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-cluster-resource.md`
- Source Title: `Use Cluster Resource (Deprecated)`
- Source Heading Path: `Use Cluster Resource (Deprecated) > Modify a TiDB Cloud Dedicated cluster | Use Cluster Resource (Deprecated) > Modify a TiDB Cloud Dedicated cluster > Add a TiFlash component`
- Source Line Ranges: `479-607`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tiflash`, `tidb`, `tikv`
- Topic Tags: `terraform`, `cluster-modification`, `dedicated-cluster`, `tiflash`, `apply`, `state`, `cluster-status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0372_ba294bc3aa`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-cluster-resource.md#modify-a-tidb-cloud-dedicated-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `07a044214a688b2124e8065931616de3dfbcac8f972d60721a9d87029c3cc7e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-cluster-resource#modify-a-tidb-cloud-dedicated-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform steps to modify a TiDB Cloud Dedicated cluster by adding a `tiflash` component and checking the `MODIFYING` to `AVAILABLE` status transition.
- Retrieval Keywords: Modify a TiDB Cloud Dedicated cluster, Add a TiFlash component, tiflash, terraform apply, terraform state show tidbcloud_cluster.${resource-name}, update in-place, status MODIFYING, status AVAILABLE, components field, node_size = "8C64G", storage_size_gib = 500
- Follow-up Guidance: After applying the updated `cluster.tf`, the content shows checking `terraform state show tidbcloud_cluster.${resource-name}` until the cluster status changes from `MODIFYING` to `AVAILABLE`.
- Classification Note: This is classified as an operation because the content describes how to change an existing cloud cluster resource configuration by adding TiFlash through Terraform.

## Official Source Content

## Modify a TiDB Cloud Dedicated cluster

For a TiDB Cloud Dedicated cluster, you can use Terraform to manage cluster resources as follows:

- Add a TiFlash component to the cluster.
- Scale the cluster.
- Pause or resume the cluster.
### Add a TiFlash component

1. In the `cluster.tf` file that is used when you [create the cluster](#create-a-cluster-using-the-cluster-resource), add the `tiflash` configurations to the `components` field.

    For example:

    ```
        components = {
          tidb = {
            node_size : "8C16G"
            node_quantity : 1
          }
          tikv = {
            node_size : "8C32G"
            storage_size_gib : 500
            node_quantity : 3
          }
          tiflash = {
            node_size : "8C64G"
            storage_size_gib : 500
            node_quantity : 1
          }
        }
    ```

2. Run the `terraform apply` command:

    ```
    $ terraform apply

    tidbcloud_cluster.example_cluster: Refreshing state... [id=1379661944630234067]

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      ~ update in-place

    Terraform will perform the following actions:

      # tidbcloud_cluster.example_cluster will be updated in-place
      ~ resource "tidbcloud_cluster" "example_cluster" {
          ~ config         = {
              ~ components     = {
                  + tiflash = {
                      + node_quantity    = 1
                      + node_size        = "8C64G"
                      + storage_size_gib = 500
                    }
                    # (2 unchanged attributes hidden)
                }
                # (3 unchanged attributes hidden)
            }
            id             = "1379661944630234067"
            name           = "firstCluster"
          ~ status         = "AVAILABLE" -> (known after apply)
            # (4 unchanged attributes hidden)
        }

    Plan: 0 to add, 1 to change, 0 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value:

    ```

    As in the above execution plan, TiFlash will be added, and one resource will be changed.

3. If everything in your plan looks fine, type `yes` to continue:

    ```
      Enter a value: yes

    tidbcloud_cluster.example_cluster: Modifying... [id=1379661944630234067]
    tidbcloud_cluster.example_cluster: Modifications complete after 2s [id=1379661944630234067]

    Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
    ```

4. Use `terraform state show tidbcloud_cluster.${resource-name}` to see the status:

    ```
    $ terraform state show tidbcloud_cluster.example_cluster

    # tidbcloud_cluster.example_cluster:
    resource "tidbcloud_cluster" "example_cluster" {
        cloud_provider = "AWS"
        cluster_type   = "DEDICATED"
        config         = {
            components     = {
                tidb    = {
                    node_quantity = 1
                    node_size     = "8C16G"
                }
                tiflash = {
                    node_quantity    = 1
                    node_size        = "8C64G"
                    storage_size_gib = 500
                }
                tikv    = {
                    node_quantity    = 3
                    node_size        = "8C32G"
                    storage_size_gib = 500
                }
            }
            ip_access_list = [
                # (1 unchanged element hidden)
            ]
            port           = 4000
            root_password  = "Your_root_password1."
        }
        id             = "1379661944630234067"
        name           = "firstCluster"
        project_id     = "1372813089189561287"
        region         = "eu-central-1"
        status         = "MODIFYING"
    }
    ```

The `MODIFYING` status indicates that the cluster is changing now. Wait for a moment. The status will be changed to `AVAILABLE`.
