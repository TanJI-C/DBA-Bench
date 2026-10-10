# Import a TiDB Cloud Dedicated network container into Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-network-container-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Network Container Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Network Container Resource > Import a TiDB Cloud Dedicated network container`
- Source Line Ranges: `139-182`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `terraform`, `network-container`, `import`, `generated-configuration`, `plan`, `apply`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0387_13ecc699ea`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-network-container-resource.md#import-a-tidb-cloud-dedicated-network-container`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `affb7e28f420ca37a3f51812709327b723bf3d39741b17494fec84b6da2b4e8e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-network-container-resource#import-a-tidb-cloud-dedicated-network-container
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-network-container-resource.md

## Retrieval Guidance

- Use When: Use this when you need the Terraform import workflow for a TiDB Cloud Dedicated network container that is not already managed by Terraform.
- Retrieval Keywords: Import a TiDB Cloud Dedicated network container, tidbcloud_dedicated_network_container, import block, terraform plan -generate-config-out=generated.tf, generated.tf, cluster_id,network_container_id, terraform apply, Resources: 1 imported
- Follow-up Guidance: The source notes that you should not specify an existing `.tf` filename with `terraform plan -generate-config-out=generated.tf`, or Terraform will return an error.
- Classification Note: This is classified as an operation chunk because it documents the import, generated configuration, review, and apply flow for managing an existing cloud resource with Terraform.

## Official Source Content

## Import a TiDB Cloud Dedicated network container

For a TiDB Cloud Dedicated network container that is not managed by Terraform, you can use Terraform to manage it just by importing it.

For example, you can import a network container that is not created by Terraform.

1. Add an import block for the new TiDB Cloud Dedicated network container resource.

    Add the following import block to your `.tf` file, replace `example` with a desired resource name, and replace `${id}` with the format of `cluster_id,network_container_id`:

    ```
    import {
      to = tidbcloud_dedicated_network_container.example
      id = "${id}"
    }
    ```

2. Generate the new configuration file.

    Generate the new configuration file for the new TiDB Cloud Dedicated network container resource according to the import block:

    ```shell
    terraform plan -generate-config-out=generated.tf
    ```

    Do not specify an existing `.tf` filename in the preceding command. Otherwise, Terraform will return an error.

    Then the `generated.tf` file is created in the current directory, which contains the configuration of the imported resource.

3. Review and apply the generated configuration.

    Review the generated configuration file to ensure that it meets your needs. Optionally, you can move the contents of this file to your preferred location.

    Then, run `terraform apply` to import your infrastructure. After applying, the example output is as follows: 

    ```shell
    tidbcloud_dedicated_network_container.example: Importing... [id=10423692645683000000,example]
    tidbcloud_dedicated_network_container.example: Import complete [id=10423692645683000000,example]

    Apply complete! Resources: 1 imported, 0 added, 0 changed, 0 destroyed.
    ```

Now you can manage the imported TiDB Cloud Dedicated network container with Terraform.
