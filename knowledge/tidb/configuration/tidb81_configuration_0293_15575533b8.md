# Get and configure TiDB Cloud Terraform Provider

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-get-tidbcloud-provider.md`
- Source Title: `Get TiDB Cloud Terraform Provider`
- Source Heading Path: `Get TiDB Cloud Terraform Provider | Get TiDB Cloud Terraform Provider > Prerequisites | Get TiDB Cloud Terraform Provider > Step 1. Install Terraform | Get TiDB Cloud Terraform Provider > Step 2. Create an API key | Get TiDB Cloud Terraform Provider > Step 3. Download TiDB Cloud Terraform Provider | Get TiDB Cloud Terraform Provider > Step 4. Configure TiDB Cloud Terraform Provider with the API key | Get TiDB Cloud Terraform Provider > Step 5. Configure TiDB Cloud Terraform Provider with sync configuration | Get TiDB Cloud Terraform Provider > Next step`
- Source Line Ranges: `5-129`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `terraform`, `provider-installation`, `api-key`, `authentication`, `terraform-registry`, `provider-configuration`, `environment-variables`, `sync-configuration`, `cluster-resource`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0293_15575533b8`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-get-tidbcloud-provider.md#get-tidb-cloud-terraform-provider`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `74e0205906e547eadc4fd54433e41f17bd2018101723d93abb0f959f5c20d4fd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-get-tidbcloud-provider#get-tidb-cloud-terraform-provider
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-get-tidbcloud-provider.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to install, download, and configure the TiDB Cloud Terraform Provider, including API key authentication, Terraform Registry setup, and the optional sync configuration.
- Retrieval Keywords: TiDB Cloud Terraform Provider, terraform registry, source = "tidbcloud/tidbcloud", version = "~> 0.3.0", required_version = ">= 1.0.0", terraform init, HTTP Digest Authentication, API key, public_key, private_key, TIDBCLOUD_PUBLIC_KEY, TIDBCLOUD_PRIVATE_KEY, provider "tidbcloud", sync, cluster resource, TiDB Cloud console
- Follow-up Guidance: The next step in the source is to manage a cluster with the cluster resource.
- Classification Note: This is classified as configuration because the content explains prerequisites, provider installation, API key setup, provider block configuration, environment variables, and the optional sync parameter for the TiDB Cloud Terraform Provider.

## Official Source Content

# Get TiDB Cloud Terraform Provider

You will learn how to get TiDB Cloud Terraform Provider in this document.
## Prerequisites

Make sure that the requirements in [TiDB Cloud Terraform Provider Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-tidbcloud-provider-overview#requirements) are met.
## Step 1. Install Terraform

TiDB Cloud Terraform Provider has been released to [Terraform Registry](https://registry.terraform.io/). All you need to do is install Terraform (>=1.0).

For macOS, you can install Terraform with Homebrew according to the following steps.

1. Install the HashiCorp tap, a repository with all the required Homebrew packages.

    ```shell
    brew tap hashicorp/tap
    ```

2. Install Terraform with `hashicorp/tap/terraform`.

    ```shell
    brew install hashicorp/tap/terraform
    ```

For other operating systems, see [Terraform documentation](https://learn.hashicorp.com/tutorials/terraform/install-cli) for instructions.
## Step 2. Create an API key

TiDB Cloud API uses HTTP Digest Authentication. It protects your private key from being sent over the network.

Currently, TiDB Cloud Terraform Provider does not support managing API keys. So you need to create an API key in the [TiDB Cloud console](https://tidbcloud.com/project/clusters).

For detailed steps, see [TiDB Cloud API documentation](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Authentication/API-Key-Management).
## Step 3. Download TiDB Cloud Terraform Provider

1. Create a `main.tf` file:

   ```
   terraform {
     required_providers {
       tidbcloud = {
         source = "tidbcloud/tidbcloud"
         version = "~> 0.3.0"
       }
     }
     required_version = ">= 1.0.0"
   }
   ```

   - The `source` attribute specifies the target Terraform provider to be downloaded from [Terraform Registry](https://registry.terraform.io/).
   - The `version` attribute is optional, which specifies the version of the Terraform provider. If it is not specified, the latest provider version is used by default.
   - The `required_version` is optional, which specifies the version of Terraform. If it is not specified, the latest Terraform version is used by default.

2. Run the `terraform init` command to download TiDB Cloud Terraform Provider from Terraform Registry.

   ```
   $ terraform init

   Initializing the backend...

   Initializing provider plugins...
   - Reusing previous version of tidbcloud/tidbcloud from the dependency lock file
   - Using previously-installed tidbcloud/tidbcloud v0.1.0

   Terraform has been successfully initialized!

   You may now begin working with Terraform. Try running "terraform plan" to see
   any changes that are required for your infrastructure. All Terraform commands
   should now work.

   If you ever set or change modules or backend configuration for Terraform,
   rerun this command to reinitialize your working directory. If you forget, other
   commands will detect it and remind you to do so if necessary.
   ```
## Step 4. Configure TiDB Cloud Terraform Provider with the API key

You can configure the `main.tf` file as follows:

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
```

`public_key` and `private_key` are the API key's public key and private key. You can also pass them through the environment variables:

```
export TIDBCLOUD_PUBLIC_KEY=${public_key}
export TIDBCLOUD_PRIVATE_KEY=${private_key}
```

Now, you can use the TiDB Cloud Terraform Provider.
## Step 5. Configure TiDB Cloud Terraform Provider with sync configuration

Terraform provider (>= 0.3.0) supports an optional parameter `sync`.

By setting `sync` to `true`, you can create, update, or delete resources synchronously. Here is an example:

```
provider "tidbcloud" {
  public_key = "your_public_key"
  private_key = "your_private_key"
}
```

Setting `sync` to `true` is recommended, but note that `sync` currently only works with the cluster resource. If you need synchronous operations for other resources, [contact TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
## Next step

Get started by managing a cluster with the [cluster resource](https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-cluster-resource).
