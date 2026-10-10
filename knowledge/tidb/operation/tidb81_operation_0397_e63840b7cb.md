# Import a TiDB Cloud Serverless branch into Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-serverless-branch-resource.md`
- Source Title: `Use TiDB Cloud Serverless Branch Resource`
- Source Heading Path: `Use TiDB Cloud Serverless Branch Resource > Import a TiDB Cloud Serverless branch`
- Source Line Ranges: `161-202`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `serverless-branch`, `import`, `generate-config`, `apply`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0397_e63840b7cb`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-serverless-branch-resource.md#import-a-tidb-cloud-serverless-branch`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9592be1dada1af409ef4ee01da0b7697ffeee9418427aa6a83d48f9ade7db80c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-serverless-branch-resource#import-a-tidb-cloud-serverless-branch
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-serverless-branch-resource.md

## Retrieval Guidance

- Use When: Use this content when you need the Terraform import workflow for a TiDB Cloud Serverless branch that was not originally created by Terraform.
- Retrieval Keywords: Import a TiDB Cloud Serverless branch, import block, to = tidbcloud_serverless_branch.example, id = "${id}", cluster_id,branch_id, terraform plan -generate-config-out=generated.tf, generated.tf, Import complete, Resources: 1 imported, 0 added, 0 changed, 0 destroyed
- Follow-up Guidance: The source says not to specify an existing `.tf` filename in `terraform plan -generate-config-out=generated.tf`, otherwise Terraform returns an error.
- Classification Note: This is classified as an operation chunk because the official content describes the import block, generated configuration step, and apply result for bringing an existing serverless branch under Terraform management.

## Official Source Content

## Import a TiDB Cloud Serverless branch

For a TiDB Cloud Serverless branch that is not managed by Terraform, you can use Terraform to manage it just by importing it.

Import a TiDB Cloud Serverless branch that is not created by Terraform as follows:

1. Add an import block for the new TiDB Cloud Serverless branch resource.

    Add the following import block to your `.tf` file, replace `example` with a desired resource name, and replace `${id}` with the format of `cluster_id,branch_id`:

    ```
    import {
      to = tidbcloud_serverless_branch.example
      id = "${id}"
    }
    ```

2. Generate the new configuration file.

    Generate the new configuration file for the new TiDB Cloud Serverless branch resource according to the import block:

      ```shell
      terraform plan -generate-config-out=generated.tf
      ```

    Do not specify an existing `.tf` filename in the preceding command. Otherwise, Terraform will return an error.

3. Review and apply the generated configuration.

    Review the generated configuration file to ensure that it meets your needs. Optionally, you can move the contents of this file to your preferred location.

    Then, run `terraform apply` to import your infrastructure. After applying, the example output is as follows: 

    ```shell
    tidbcloud_serverless_branch.example: Importing... 
    tidbcloud_serverless_branch.example: Import complete 

    Apply complete! Resources: 1 imported, 0 added, 0 changed, 0 destroyed.
    ```

Now you can manage the imported branch with Terraform.
