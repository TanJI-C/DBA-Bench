# Modify dedicated cluster capacity and pause state with Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-cluster-resource.md`
- Source Title: `Use Cluster Resource (Deprecated)`
- Source Heading Path: `Use Cluster Resource (Deprecated) > Modify a TiDB Cloud Dedicated cluster > Scale a TiDB cluster | Use Cluster Resource (Deprecated) > Modify a TiDB Cloud Dedicated cluster > Pause or resume a cluster`
- Source Line Ranges: `608-838`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `terraform`, `cluster-scaling`, `pause`, `resume`, `dedicated-cluster`, `state-verification`, `component-configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0373_230dcc680e`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-cluster-resource.md#scale-a-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5a8c939421d91c4cbb6cef77e02e196fc6fa81076d0797419d7aa9e6320739f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-cluster-resource#scale-a-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform procedure and status transitions for scaling a TiDB Cloud Dedicated cluster or pausing and resuming it with the cluster resource.
- Retrieval Keywords: tidbcloud_cluster, cluster.tf, terraform apply, terraform state show tidbcloud_cluster.${resource-name}, components, paused = true, paused = false, status AVAILABLE, status MODIFYING, status PAUSED, status RESUMING, TiDB Cloud Dedicated cluster, node_quantity, TiKV nodes needs to be a multiple of 3, tidb, tikv, tiflash
- Follow-up Guidance: The content also points to the backup resource after cluster management and mentions using the cluster specification information from the tidbcloud_cluster_specs data source for TiKV node step details.
- Classification Note: This is classified as an operation chunk because the official content gives step-by-step Terraform update workflows for changing component capacity and toggling the cluster paused state, including status verification.

## Official Source Content

### Scale a TiDB cluster

You can scale a TiDB cluster when its status is `AVAILABLE`.

1. In the `cluster.tf` file that is used when you [create the cluster](#create-a-cluster-using-the-cluster-resource), edit the `components` configurations.

    For example, to add one more node for TiDB, 3 more nodes for TiKV (The number of TiKV nodes needs to be a multiple of 3 for its step is 3. You can [get this information from the cluster specification](#get-cluster-specification-information-using-the-tidbcloud_cluster_specs-data-source)), and one more node for TiFlash, you can edit the configurations as follows:

   ```
       components = {
         tidb = {
           node_size : "8C16G"
           node_quantity : 2
         }
         tikv = {
           node_size : "8C32G"
           storage_size_gib : 500
           node_quantity : 6
         }
         tiflash = {
           node_size : "8C64G"
           storage_size_gib : 500
           node_quantity : 2
         }
       }
   ```

2. Run the `terraform apply` command and type `yes` for confirmation:

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
                 ~ tidb    = {
                     ~ node_quantity = 1 -> 2
                       # (1 unchanged attribute hidden)
                   }
                 ~ tiflash = {
                     ~ node_quantity    = 1 -> 2
                       # (2 unchanged attributes hidden)
                   }
                 ~ tikv    = {
                     ~ node_quantity    = 3 -> 6
                       # (2 unchanged attributes hidden)
                   }
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

     Enter a value: yes

   tidbcloud_cluster.example_cluster: Modifying... [id=1379661944630234067]
   tidbcloud_cluster.example_cluster: Modifications complete after 2s [id=1379661944630234067]

   Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
   ```

Wait for the status to turn from `MODIFYING` to `AVAILABLE`.
### Pause or resume a cluster

You can pause a cluster when its status is `AVAILABLE` or resume a cluster when its status is `PAUSED`.

- Set `paused = true` to pause a cluster.
- Set `paused = false` to resume a cluster.

1. In the `cluster.tf` file that is used when you [create the cluster](#create-a-cluster-using-the-cluster-resource), add `pause = true` to the `config` configurations:

   ```
   config = {
       paused = true
       root_password = "Your_root_password1."
       port          = 4000
       ...
     }
   ```

2. Run the `terraform apply` command and type `yes` after check:

   ```
   $ terraform apply

   tidbcloud_cluster.example_cluster: Refreshing state... [id=1379661944630234067]

   Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
     ~ update in-place

   Terraform will perform the following actions:

     # tidbcloud_cluster.example_cluster will be updated in-place
     ~ resource "tidbcloud_cluster" "example_cluster" {
         ~ config         = {
             + paused         = true
               # (4 unchanged attributes hidden)
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

     Enter a value: yes

   tidbcloud_cluster.example_cluster: Modifying... [id=1379661944630234067]
   tidbcloud_cluster.example_cluster: Modifications complete after 2s [id=1379661944630234067]

   Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
   ```

3. Use the `terraform state show tidbcloud_cluster.${resource-name}` command to check the status:

   ```
   $ terraform state show tidbcloud_cluster.example_cluster

   # tidbcloud_cluster.example_cluster:
   resource "tidbcloud_cluster" "example_cluster" {
       cloud_provider = "AWS"
       cluster_type   = "DEDICATED"
       config         = {
           components     = {
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
           ip_access_list = [
               # (1 unchanged element hidden)
           ]
           paused         = true
           port           = 4000
           root_password  = "Your_root_password1."
       }
       id             = "1379661944630234067"
       name           = "firstCluster"
       project_id     = "1372813089189561287"
       region         = "eu-central-1"
       status         = "PAUSED"
   }
   ```

4. When you need to resume the cluster, set `paused = false`:

   ```
   config = {
       paused = false
       root_password = "Your_root_password1."
       port          = 4000
       ...
     }
   ```

5. Run the `terraform apply` command and type `yes` for confirmation. If you use the `terraform state show tidbcloud_cluster.${resource-name}` command to check the status, you will find it turns to `RESUMING`:

   ```
   # tidbcloud_cluster.example_cluster:
   resource "tidbcloud_cluster" "example_cluster" {
       cloud_provider = "AWS"
       cluster_type   = "DEDICATED"
       config         = {
           components     = {
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
           ip_access_list = [
               # (1 unchanged element hidden)
           ]
           paused         = false
           port           = 4000
           root_password  = "Your_root_password1."
       }
       id             = "1379661944630234067"
       name           = "firstCluster"
       project_id     = "1372813089189561287"
       region         = "eu-central-1"
       status         = "RESUMING"
   }
   ```

6. Wait for a moment, then use the `terraform refersh` command to update the state. The status will be changed to `AVAILABLE` finally.

Now, you have created and managed a TiDB Cloud Dedicated cluster with Terraform. Next, you can try creating a backup of the cluster by our [backup resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-backup-resource).
