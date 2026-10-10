# Import TiDB Cloud Serverless export resource into Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-export-resource.md`
- Source Title: `Use TiDB Cloud Serverless Export Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Export Resource > Import a TiDB Cloud Serverless data export task`
- Source Line Ranges: `145-186`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless`, `export`, `resource-import`, `generated-configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0403_51912ced53`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-export-resource.md#import-a-tidb-cloud-serverless-data-export-task`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2ed28f56d3cfb7ecbff8b255f0116b39e1471da17c9f8790134e55f7774af5c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-export-resource#import-a-tidb-cloud-serverless-data-export-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-export-resource.md

## Retrieval Guidance

- Use When: Use this when you need to import an existing TiDB Cloud Serverless export task into Terraform management.
- Retrieval Keywords: tidbcloud_serverless_export, import block, cluster_id,export_id, terraform plan -generate-config-out=generated.tf, terraform apply, generated.tf
- Follow-up Guidance: Generate the new configuration file with terraform plan -generate-config-out=generated.tf, then review and apply it.
- Classification Note: This chunk describes importing a TiDB Cloud Serverless data export task that was not created by Terraform and generating configuration from the import block.

## Official Source Content

## Import a TiDB Cloud Serverless data export task

For a TiDB Serverless data export task that is not managed by Terraform, you can use Terraform to manage it just by importing it.

Import a TiDB Cloud Serverless data export task that is not created by Terraform as follows:

1. Add an import block for the new TiDB Cloud Serverless export resource.

    Add the following import block to your `.tf` file, replace `example` with a desired resource name, and replace `${id}` with the format of `cluster_id,export_id`:

    ```
    import {
      to = tidbcloud_serverless_export.example
      id = "${id}"
    }
    ```

2. Generate the new configuration file.

    Generate the new configuration file for the new serverless export resource according to the import block:

      ```shell
      terraform plan -generate-config-out=generated.tf
      ```

    Do not specify an existing `.tf` filename in the preceding command. Otherwise, Terraform will return an error.

3. Review and apply the generated configuration.

    Review the generated configuration file to ensure that it meets your needs. Optionally, you can move the contents of this file to your preferred location.

    Then, run `terraform apply` to import your infrastructure. After applying, the example output is as follows: 

    ```shell
    tidbcloud_serverless_export.example: Importing... 
    tidbcloud_serverless_export.example: Import complete 

    Apply complete! Resources: 1 imported, 0 added, 0 changed, 0 destroyed.
    ```

Now you can manage the imported export with Terraform.
