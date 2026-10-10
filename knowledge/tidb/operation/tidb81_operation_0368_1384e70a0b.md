# Create and verify a TiDB Cloud Terraform backup resource

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-backup-resource.md`
- Source Title: `Use Backup Resource`
- Source Heading Path: `Use Backup Resource | Use Backup Resource > Prerequisites | Use Backup Resource > Create a backup with the backup resource | Use Backup Resource > Update a backup`
- Source Line Ranges: `5-155`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `backup`, `resource-creation`, `prerequisites`, `verification`, `state-refresh`, `dedicated-cluster`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0368_1384e70a0b`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-backup-resource.md#use-backup-resource`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a76c3435d72f58b6393209c8294eeacb9ce917d1f66e35a932d81226bd0168ff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-backup-resource#use-backup-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-backup-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented Terraform workflow to create and verify a `tidbcloud_backup` resource for a TiDB Cloud Dedicated cluster, including status checks and refresh behavior.
- Retrieval Keywords: tidbcloud_backup, TiDB Cloud Dedicated clusters, backup and restore feature is unavailable to TiDB Cloud Serverless clusters, backup.tf, terraform apply, terraform state show tidbcloud_backup.example_backup, terraform refresh, status PENDING, status SUCCESS, type MANUAL, project_id, cluster_id, Backups cannot be updated, use the restore resources
- Follow-up Guidance: After the backup status turns to `SUCCESS`, the document links to `use the restore resources` if you want to use the backup to restore the cluster.
- Classification Note: This is classified as an operation chunk because the official content provides prerequisites, Terraform configuration examples, `terraform apply`, state inspection, refresh, and verification steps for creating a backup resource.

## Official Source Content

# Use Backup Resource

You can learn how to create a backup of a TiDB Cloud cluster with the `tidbcloud_backup` resource in this document.

The features of the `tidbcloud_backup` resource include the following:

- Create backups for TiDB Cloud Dedicated clusters.
- Delete backups for TiDB Cloud Dedicated clusters.
## Prerequisites

- [Get TiDB Cloud Terraform Provider](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider).
- The backup and restore feature is unavailable to TiDB Cloud Serverless clusters. To use backup resources, make sure that you have created a TiDB Cloud Dedicated cluster.
## Create a backup with the backup resource

1. Create a directory for the backup and enter it.

2. Create a `backup.tf` file.

    For example:

    ```
    terraform {
     required_providers {
       tidbcloud = {
         source = "tidbcloud/tidbcloud"
       }
     }
   }

   provider "tidbcloud" {
     public_key = "your_public_key"
     private_key = "your_private_key"
   }
    resource "tidbcloud_backup" "example_backup" {
      project_id  = "1372813089189561287"
      cluster_id  = "1379661944630234067"
      name        = "firstBackup"
      description = "create by terraform"
    }
    ```

    You need to replace resource values (such as project ID and cluster ID) in the file with your own.

    If you have maintained a cluster resource (for example, `example_cluster`) using Terraform, you can also configure the backup resource as follows, without specifying the actual project ID and cluster ID.

    ```
    resource "tidbcloud_backup" "example_backup" {
      project_id  = tidbcloud_cluster.example_cluster.project_id
      cluster_id  = tidbcloud_cluster.example_cluster.id
      name        = "firstBackup"
      description = "create by terraform"
    }
    ```

3. Run the `terraform apply` command:

    ```
    $ terraform apply

    tidbcloud_cluster.example_cluster: Refreshing state... [id=1379661944630234067]

    Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
      + create

    Terraform will perform the following actions:

      # tidbcloud_backup.example_backup will be created
      + resource "tidbcloud_backup" "example_backup" {
          + cluster_id       = "1379661944630234067"
          + create_timestamp = (known after apply)
          + description      = "create by terraform"
          + id               = (known after apply)
          + name             = "firstBackup"
          + project_id       = "1372813089189561287"
          + size             = (known after apply)
          + status           = (known after apply)
          + type             = (known after apply)
        }

    Plan: 1 to add, 0 to change, 0 to destroy.

    Do you want to perform these actions?
      Terraform will perform the actions described above.
      Only 'yes' will be accepted to approve.

      Enter a value:
    ```

4. Type `yes` to create a backup:

    ```
      Enter a value: yes

    tidbcloud_backup.example_backup: Creating...
    tidbcloud_backup.example_backup: Creation complete after 2s [id=1350048]

    Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

    ```

5. Use `terraform state show tidbcloud_backup.${resource-name}` to check the status of the backup:

    ```
    $ terraform state show tidbcloud_backup.example_backup

    # tidbcloud_backup.example_backup:
    resource "tidbcloud_backup" "example_backup" {
        cluster_id       = "1379661944630234067"
        create_timestamp = "2022-08-26T07:56:10Z"
        description      = "create by terraform"
        id               = "1350048"
        name             = "firstBackup"
        project_id       = "1372813089189561287"
        size             = "0"
        status           = "PENDING"
        type             = "MANUAL"
    }
    ```

6. Wait for some minutes. Then use `terraform refersh` to update the status:

    ```
    $ terraform refresh
    tidbcloud_cluster.example_cluster: Refreshing state... [id=1379661944630234067]
    tidbcloud_backup.example_backup: Refreshing state... [id=1350048]
    $ terraform state show tidbcloud_backup.example_backup
    # tidbcloud_backup.example_backup:
    resource "tidbcloud_backup" "example_backup" {
        cluster_id       = "1379661944630234067"
        create_timestamp = "2022-08-26T07:56:10Z"
        description      = "create by terraform"
        id               = "1350048"
        name             = "firstBackup"
        project_id       = "1372813089189561287"
        size             = "198775"
        status           = "SUCCESS"
        type             = "MANUAL"
    }
    ```

When the status turns to `SUCCESS`, it indicates that you have created a backup for your cluster. Pay attention that the backup cannot be updated after the creation.

Now, you have created a backup for the cluster. If you want to use the backup to restore the cluster, you can [use the restore resources](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-restore-resource).
## Update a backup

Backups cannot be updated.
