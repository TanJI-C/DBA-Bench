# Import a TiDB Cloud Dedicated private endpoint connection into Terraform

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md`
- Source Title: `Use TiDB Cloud Dedicated Private Endpoint Connection Resource`
- Source Heading Path: `Use TiDB Cloud Dedicated Private Endpoint Connection Resource > Import a TiDB Cloud Dedicated private endpoint connection`
- Source Line Ranges: `147-188`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `terraform`, `private-endpoint`, `resource-import`, `generated-configuration`, `apply`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0390_d72c98ac1f`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md#import-a-tidb-cloud-dedicated-private-endpoint-connection`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `448f7ec2bc72a2530a467c9ea0638293a1e683aa23a417249695062c676d176b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource#import-a-tidb-cloud-dedicated-private-endpoint-connection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-dedicated-private-endpoint-connection-resource.md

## Retrieval Guidance

- Use When: Use this content when you need to import an existing TiDB Cloud Dedicated private endpoint connection into Terraform and generate configuration from the import block.
- Retrieval Keywords: Import a TiDB Cloud Dedicated private endpoint connection, import block, tidbcloud_dedicated_private_endpoint_connection.example, cluster_id,dedicated_private_endpoint_connection_id, terraform plan -generate-config-out=generated.tf, generated.tf, terraform apply, Resources: 1 imported, 0 added, 0 changed, 0 destroyed
- Follow-up Guidance: The source notes that you should not specify an existing .tf filename with terraform plan -generate-config-out=generated.tf because Terraform will return an error.
- Classification Note: This is classified as an operation chunk because the official content describes the procedural import workflow, generated configuration step, and apply result for Terraform-managed resources.

## Official Source Content

## Import a TiDB Cloud Dedicated private endpoint connection

For a TiDB Cloud Dedicated private endpoint connection that is not managed by Terraform, you can start managing it with Terraform by importing it.

1. Add an import block for the new TiDB Cloud Dedicated private endpoint connection resource.

    Add the following import block to your `.tf` file, replace `example` with a desired resource name, and replace `${id}` with the format of `cluster_id,dedicated_private_endpoint_connection_id`:

    ```
    import {
      to = tidbcloud_dedicated_private_endpoint_connection.example
      id = "${id}"
    }
    ```

2. Generate the new configuration file.

    Generate the new configuration file for the new TiDB Cloud Dedicated private endpoint connection resource according to the import block:

    ```shell
    terraform plan -generate-config-out=generated.tf
    ```

    Do not specify an existing `.tf` filename in the preceding command. Otherwise, Terraform will return an error.

    Then the `generated.tf` file is created in the current directory, which contains the configuration of the imported resource.

3. Review and apply the generated configuration.

    Review the generated configuration file to ensure that it meets your needs. Optionally, you can move the contents of this file to your preferred location.

    Then, run `terraform apply` to import your infrastructure. After applying, the example output is as follows: 

    ```shell
    tidbcloud_dedicated_private_endpoint_connection.example: Importing... [id=aws-1934187953894000000,example]
    tidbcloud_dedicated_private_endpoint_connection.example: Import complete [id=aws-19341879538940000000,example]

    Apply complete! Resources: 1 imported, 0 added, 0 changed, 0 destroyed.
    ```

    Now you can manage the imported TiDB Cloud Dedicated private endpoint connection with Terraform.
