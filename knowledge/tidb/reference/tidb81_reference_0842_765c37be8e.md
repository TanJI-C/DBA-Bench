# Retrieve cluster specifications with the tidbcloud_cluster_specs data source

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-cluster-resource.md`
- Source Title: `Use Cluster Resource (Deprecated)`
- Source Heading Path: `Use Cluster Resource (Deprecated) > Get cluster specification information using the `tidbcloud_cluster_specs` data source`
- Source Line Ranges: `126-271`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `terraform`, `deprecated`, `data-source`, `cluster-specs`, `cloud-provider`, `region`, `node-size`, `storage-size`, `scaling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0842_765c37be8e`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-cluster-resource.md#get-cluster-specification-information-using-the-tidbcloud-cluster-specs-data-source`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e7f31c0ab1d98290d8372c5e341aa2f209a8a41379d310d28370010e49bb938f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-cluster-resource#get-cluster-specification-information-using-the-tidbcloud-cluster-specs-data-source
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-cluster-resource.md

## Retrieval Guidance

- Use When: Use this when looking for how to retrieve available cluster configuration values with the `tidbcloud_cluster_specs` data source before creating a TiDB Cloud cluster.
- Retrieval Keywords: tidbcloud_cluster_specs, cluster specification information, data "tidbcloud_cluster_specs", output "cluster_spec", terraform apply --auto-approve, cloud_provider, region, cluster_type, node_quantity_range, node_size, storage_size_gib_range, tidb, tikv, tiflash, supported cloud providers, regions, node sizes
- Follow-up Guidance: The content says the output provides available configuration values such as `cloud_provider`, `region`, `node_quantity_range`, `node_size`, and `storage_size_gib_range`.
- Classification Note: This is classified as a reference chunk because it documents the `tidbcloud_cluster_specs` data source output fields and example specification values for cluster configuration.

## Official Source Content

## Get cluster specification information using the `tidbcloud_cluster_specs` data source

Before you create a cluster, you need to get the cluster specification information, which contains all available configuration values (such as supported cloud providers, regions, and node sizes).

To get the cluster specification information, you can use the `tidbcloud_cluster_specs` data source as follows:

1. Edit the `main.tf` file as follows:

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
      sync = true
    }
    data "tidbcloud_cluster_specs" "example_cluster_spec" {
    }
    output "cluster_spec" {
      value = data.tidbcloud_cluster_specs.example_cluster_spec.items
    }
    ```

2. Run the `terraform apply --auto-approve` command and you will get the cluster specification information.

    Click the following line to get a part of the example results for your reference.

    <details>
      <summary>Cluster specification</summary>

    ```
    {
        "cloud_provider" = "AWS"
        "cluster_type" = "DEDICATED"
        "region" = "eu-central-1"
        "tidb" = tolist([
          {
            "node_quantity_range" = {
              "min" = 1
              "step" = 1
            }
            "node_size" = "4C16G"
          },
          {
            "node_quantity_range" = {
              "min" = 1
              "step" = 1
            }
            "node_size" = "8C16G"
          },
          {
            "node_quantity_range" = {
              "min" = 1
              "step" = 1
            }
            "node_size" = "16C32G"
          },
        ])
        "tiflash" = tolist([
          {
            "node_quantity_range" = {
              "min" = 0
              "step" = 1
            }
            "node_size" = "8C64G"
            "storage_size_gib_range" = {
              "max" = 2048
              "min" = 500
            }
          },
          {
            "node_quantity_range" = {
              "min" = 0
              "step" = 1
            }
            "node_size" = "16C128G"
            "storage_size_gib_range" = {
              "max" = 2048
              "min" = 500
            }
          },
        ])
        "tikv" = tolist([
          {
            "node_quantity_range" = {
              "min" = 3
              "step" = 3
            }
            "node_size" = "4C16G"
            "storage_size_gib_range" = {
              "max" = 2048
              "min" = 200
            }
          },
          {
            "node_quantity_range" = {
              "min" = 3
              "step" = 3
            }
            "node_size" = "8C32G"
            "storage_size_gib_range" = {
              "max" = 4096
              "min" = 500
            }
          },
          {
            "node_quantity_range" = {
              "min" = 3
              "step" = 3
            }
            "node_size" = "8C64G"
            "storage_size_gib_range" = {
              "max" = 4096
              "min" = 500
            }
          },
          {
            "node_quantity_range" = {
              "min" = 3
              "step" = 3
            }
            "node_size" = "16C64G"
            "storage_size_gib_range" = {
              "max" = 4096
              "min" = 500
            }
          },
        ])
      }
    ```

    </details>

In the results:

- `cloud_provider` is the cloud provider on which a TiDB cluster can be hosted.
- `region` is the region of `cloud_provider`.
- `node_quantity_range` shows the minimum node number and the step to scale a node.
- `node_size` is the size of a node.
- `storage_size_gib_range` shows the minimum and maximum storage size you can set for a node.
