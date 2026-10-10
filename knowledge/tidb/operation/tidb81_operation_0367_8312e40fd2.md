# Migrate Terraform cluster resource to serverless or dedicated resources

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-migrate-cluster-resource.md`
- Source Title: `Migrate Cluster Resource to Serverless or Dedicated Cluster Resource`
- Source Heading Path: `Migrate Cluster Resource to Serverless or Dedicated Cluster Resource | Migrate Cluster Resource to Serverless or Dedicated Cluster Resource > Prerequisites | Migrate Cluster Resource to Serverless or Dedicated Cluster Resource > Step 1. Identify the `tidbcloud_cluster` resource to migrate | Migrate Cluster Resource to Serverless or Dedicated Cluster Resource > Step 2. Remove the existing resource from the Terraform state | Migrate Cluster Resource to Serverless or Dedicated Cluster Resource > Step 3. Delete the configuration of your target cluster resource | Migrate Cluster Resource to Serverless or Dedicated Cluster Resource > Step 4. Add an import block for the new serverless or dedicated cluster resource | Migrate Cluster Resource to Serverless or Dedicated Cluster Resource > Step 5. Generate the new configuration file | Migrate Cluster Resource to Serverless or Dedicated Cluster Resource > Step 6. Review and apply the generated configuration`
- Source Line Ranges: `5-87`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `resource-migration`, `import`, `state-management`, `configuration-generation`, `serverless`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0367_8312e40fd2`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-migrate-cluster-resource.md#migrate-cluster-resource-to-serverless-or-dedicated-cluster-resource`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0145d6bab6dc3b99d568edd9372decd7e7047611b2d5b8f325b495d7099dca7a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-migrate-cluster-resource#migrate-cluster-resource-to-serverless-or-dedicated-cluster-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-migrate-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented Terraform migration flow from `tidbcloud_cluster` to `tidbcloud_serverless_cluster` or `tidbcloud_dedicated_cluster`, including state removal, import blocks, and generated configuration.
- Retrieval Keywords: TiDB Cloud Terraform Provider v0.4.0, tidbcloud_cluster, tidbcloud_serverless_cluster, tidbcloud_dedicated_cluster, terraform state list | grep "tidbcloud_cluster", terraform state show ${your_target_cluster_resource} | grep ' id ', terraform state rm ${your_target_cluster_resource}, import { to = tidbcloud_serverless_cluster.example id = "${id}" }, import { to = tidbcloud_dedicated_cluster.example id = "${id}" }, terraform plan -generate-config-out=generated.tf, Do not specify an existing `.tf` file name, terraform apply, Resources: 1 imported, 0 added, 0 changed, 0 destroyed
- Follow-up Guidance: The content also points to reviewing the generated configuration and then running `terraform apply`, with an example import-complete output for `tidbcloud_serverless_cluster.example`.
- Classification Note: This is classified as an operation topic because the content provides a step-by-step migration procedure for Terraform resource state, configuration deletion, import, configuration generation, and apply steps in TiDB Cloud.

## Official Source Content

# Migrate Cluster Resource to Serverless or Dedicated Cluster Resource

Starting from TiDB Cloud Terraform Provider v0.4.0, the `tidbcloud_cluster` resource is replaced by two new resources: `tidbcloud_serverless_cluster` and `tidbcloud_dedicated_cluster`. If you are using TiDB Cloud Terraform Provider v0.4.0 or a later version, you can follow this document to migrate your `tidbcloud_cluster` resource to the `tidbcloud_serverless_cluster` or `tidbcloud_dedicated_cluster` resource. 

> **Tip:**
>
> The steps in this document use the configuration generation feature of Terraform to simplify the migration process by automatically recreating the `.tf` configuration for your cluster resource. To learn more about it, see [Generating configuration](https://developer.hashicorp.com/terraform/language/import/generating-configuration) in Terraform documentation.
## Prerequisites

- Upgrade to [TiDB Cloud Terraform Provider v0.4.0 or later](https://registry.terraform.io/providers/tidbcloud/tidbcloud/latest)
## Step 1. Identify the `tidbcloud_cluster` resource to migrate

1. List all `tidbcloud_cluster` resources:

    ```shell
    terraform state list | grep "tidbcloud_cluster"
    ```

2. Choose a target cluster resource to migrate and get its cluster `id` for later use:

    ```shell
    terraform state show ${your_target_cluster_resource} | grep ' id '
    ```
## Step 2. Remove the existing resource from the Terraform state

Remove your target cluster resource from the Terraform state:

```shell
terraform state rm ${your_target_cluster_resource}
```
## Step 3. Delete the configuration of your target cluster resource

In your `.tf` file, find the configuration of your target cluster resource and delete the corresponding code.
## Step 4. Add an import block for the new serverless or dedicated cluster resource

- If your target cluster is TiDB Cloud Serverless, add the following import block to your `.tf` file, replace `example` with a desired resource name, and replace `${id}` with the cluster ID you get from [Step 1](#step-1-identify-the-tidbcloud_cluster-resource-to-migrate):

    ```
    # TiDB Cloud Serverless
    import {
      to = tidbcloud_serverless_cluster.example
      id = "${id}"
    }
    ```

- If your target cluster is TiDB Cloud Dedicated, add the following import block to your `.tf` file, replace `example` with a desired resource name, and replace `${id}` with the cluster ID you get from [Step 1](#step-1-identify-the-tidbcloud_cluster-resource-to-migrate):

    ```
    # TiDB Cloud Dedicated
    import {
      to = tidbcloud_dedicated_cluster.example
      id = "${id}"
    }
    ```
## Step 5. Generate the new configuration file

Generate the new configuration file for the new serverless or dedicated cluster resource according to the import block:

```shell
terraform plan -generate-config-out=generated.tf
```

Do not specify an existing `.tf` file name in the preceding command. Otherwise, Terraform will return an error.
## Step 6. Review and apply the generated configuration

Review the generated configuration file to ensure it meets your needs. Optionally, you can move the contents of this file to your preferred location.

Then, run `terraform apply` to import your infrastructure. After applying, the example output is as follows: 

```shell
tidbcloud_serverless_cluster.example: Importing... 
tidbcloud_serverless_cluster.example: Import complete 

Apply complete! Resources: 1 imported, 0 added, 0 changed, 0 destroyed.
```
