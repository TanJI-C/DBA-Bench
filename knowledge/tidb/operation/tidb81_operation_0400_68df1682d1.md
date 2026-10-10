# Import an existing TiDB Cloud Serverless cluster into Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-cluster-resource.md`
- Source Title: `Use TiDB Cloud Serverless Cluster Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Cluster Resource > Import a TiDB Cloud Serverless cluster`
- Source Line Ranges: `421-462`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless`, `cluster`, `resource`, `import`, `generate-config`, `plan`, `apply`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0400_68df1682d1`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-cluster-resource.md#import-a-tidb-cloud-serverless-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `736347c2dc59d646c59b295ca75990dc98b95dfaac791984264d06da21daecb6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-cluster-resource#import-a-tidb-cloud-serverless-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Terraform import workflow for a TiDB Cloud Serverless cluster that is not managed by Terraform.
- Retrieval Keywords: import block, tidbcloud_serverless_cluster.example, cluster ID, terraform plan -generate-config-out=generated.tf, terraform apply, Import a TiDB Cloud Serverless cluster
- Follow-up Guidance: Review the generated configuration file, then run terraform apply to import the infrastructure.
- Classification Note: This chunk is an operation guide for importing an existing TiDB Cloud Serverless cluster into Terraform and generating configuration from the import block.

## Official Source Content

## Import a TiDB Cloud Serverless cluster

For a TiDB Cloud Serverless cluster that is not managed by Terraform, you can use Terraform to manage it just by importing it.

Import a TiDB Cloud Serverless cluster that is not created by Terraform as follows:

1. Add an import block for the new TiDB Cloud Serverless cluster resource.

    Add the following import block to your `.tf` file, replace `example` with a desired resource name, and replace `${id}` with the cluster ID:

    ```
    import {
      to = tidbcloud_serverless_cluster.example
      id = "${id}"
    }
    ```

2. Generate the new configuration file.

    Generate the new configuration file for the new TiDB Cloud Serverless cluster resource according to the import block:

      ```shell
      terraform plan -generate-config-out=generated.tf
      ```

    Do not specify an existing `.tf` filename in the preceding command. Otherwise, Terraform will return an error.

3. Review and apply the generated configuration.

    Review the generated configuration file to ensure that it meets your needs. Optionally, you can move the contents of this file to your preferred location.

    Then, run `terraform apply` to import your infrastructure. After applying, the example output is as follows: 

    ```shell
    tidbcloud_serverless_cluster.example: Importing... 
    tidbcloud_serverless_cluster.example: Import complete 

    Apply complete! Resources: 1 imported, 0 added, 0 changed, 0 destroyed.
    ```

Now you can manage the imported cluster with Terraform.
