# Import an existing TiDB Cloud cluster into Terraform state

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-cluster-resource.md`
- Source Title: `Use Cluster Resource (Deprecated)`
- Source Heading Path: `Use Cluster Resource (Deprecated) > Import a cluster`
- Source Line Ranges: `839-964`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `terraform`, `import`, `state-management`, `cluster-management`, `configuration`, `validation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0374_f0a1560974`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-cluster-resource.md#import-a-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2874cb848bf4b43ac5cd97082a4c6c3100b097a2838f43fe3bab57de8a3e863`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-cluster-resource#import-a-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented Terraform import workflow for an existing TiDB Cloud cluster and want to validate the imported state against the configuration.
- Retrieval Keywords: Import a cluster, terraform import tidbcloud_cluster.import_cluster projectId,clusterId, tidbcloud_cluster, import_cluster.tf, terraform state show tidbcloud_cluster.import_cluster, terraform fmt, terraform plan, terraform apply, No changes, projectId,clusterId, id, status
- Follow-up Guidance: After importing, the content shows checking the cluster with `terraform state show tidbcloud_cluster.import_cluster`, copying the output into the configuration after removing `id` and `status`, and then running `terraform plan` or `terraform apply` to confirm `No changes`.
- Classification Note: This is an operation chunk because the content provides a step-by-step procedure to import an unmanaged TiDB Cloud cluster into Terraform state and verify the result.

## Official Source Content

## Import a cluster

For a TiDB cluster that is not managed by Terraform, you can use Terraform to manage it just by importing it.

For example, you can import a cluster that is not created by Terraform or import a cluster that is [created with the restore resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-restore-resource#create-a-restore-task).

1. Create a `import_cluster.tf` file as follows:

    ```
    terraform {
     required_providers {
       tidbcloud = {
         source = "tidbcloud/tidbcloud"
       }
     }
   }
    resource "tidbcloud_cluster" "import_cluster" {}
    ```

2. Import the cluster by `terraform import tidbcloud_cluster.import_cluster projectId,clusterId`:

   For example:

    ```
    $ terraform import tidbcloud_cluster.import_cluster 1372813089189561287,1379661944630264072

    tidbcloud_cluster.import_cluster: Importing from ID "1372813089189561287,1379661944630264072"...
    tidbcloud_cluster.import_cluster: Import prepared!
      Prepared tidbcloud_cluster for import
    tidbcloud_cluster.import_cluster: Refreshing state... [id=1379661944630264072]

    Import successful!

    The resources that were imported are shown above. These resources are now in
    your Terraform state and will henceforth be managed by Terraform.
    ```

3. Run the `terraform state show tidbcloud_cluster.import_cluster` command to check the status of the cluster:

    ```
    $ terraform state show tidbcloud_cluster.import_cluster

    # tidbcloud_cluster.import_cluster:
    resource "tidbcloud_cluster" "import_cluster" {
        cloud_provider = "AWS"
        cluster_type   = "DEDICATED"
        config         = {
            components = {
                tidb    = {
                    node_quantity = 2
                    node_size     = "8C16G"
                }
                tiflash = {
                    node_quantity    = 2
                    node_size        = "8C64G"
                    storage_size_gib = 500
                }
                tikv    = {
                    node_quantity    = 6
                    node_size        = "8C32G"
                    storage_size_gib = 500
                }
            }
            port       = 4000
        }
        id             = "1379661944630264072"
        name           = "restoreCluster"
        project_id     = "1372813089189561287"
        region         = "eu-central-1"
        status         = "AVAILABLE"
    }
    ```

4. To manage the cluster using Terraform, you can copy the output of the previous step to your configuration file. Note that you need to delete the lines of `id` and `status`, because they will be controlled by Terraform instead:

    ```
    resource "tidbcloud_cluster" "import_cluster" {
          cloud_provider = "AWS"
          cluster_type   = "DEDICATED"
          config         = {
              components = {
                  tidb    = {
                      node_quantity = 2
                      node_size     = "8C16G"
                  }
                  tiflash = {
                      node_quantity    = 2
                      node_size        = "8C64G"
                      storage_size_gib = 500
                  }
                  tikv    = {
                      node_quantity    = 6
                      node_size        = "8C32G"
                      storage_size_gib = 500
                  }
              }
              port       = 4000
          }
          name           = "restoreCluster"
          project_id     = "1372813089189561287"
          region         = "eu-central-1"
    }
    ```

5. You can use `terraform fmt` to format your configuration file:

    ```
    $ terraform fmt
    ```

6. To ensure the consistency of the configuration and state, you can execute `terraform plan` or `terraform apply`. If you see `No changes`, the import is successful.

    ```
    $ terraform apply

    tidbcloud_cluster.import_cluster: Refreshing state... [id=1379661944630264072]

    No changes. Your infrastructure matches the configuration.

    Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.

    Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
    ```

Now you can use Terraform to manage the cluster.
