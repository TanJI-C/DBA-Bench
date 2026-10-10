# Quick start with authentication and serverless cluster creation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/get-started-with-cli.md`
- Source Title: `TiDB Cloud CLI Quick Start`
- Source Heading Path: `TiDB Cloud CLI Quick Start > Quick start | TiDB Cloud CLI Quick Start > Quick start > Create a user profile or log into TiDB Cloud | TiDB Cloud CLI Quick Start > Quick start > Create a TiDB Cloud Serverless cluster`
- Source Line Ranges: `88-125`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `quick-start`, `authentication`, `api-key`, `oauth`, `profile`, `serverless`, `cluster-creation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0325_552cc8266f`
- Source ID: `tidb-docs-8.1:tidb-cloud/get-started-with-cli.md#quick-start`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ee83c20e7575082403bab7546f52c96a6dc7681624429de54ac48853e0e9f406`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/get-started-with-cli#quick-start
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/get-started-with-cli.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to authenticate with TiDB Cloud CLI, create a profile with an API key or OAuth login, understand credential precedence, or create a TiDB Cloud Serverless cluster.
- Retrieval Keywords: Quick start, Create a user profile or log into TiDB Cloud, ticloud config create, TiDB Cloud API key, profile name MUST NOT contain ., ticloud auth login, OAuth token, default profile, API key takes precedence over the OAuth token, Create a TiDB Cloud Serverless cluster, ticloud serverless create
- Follow-up Guidance: After authentication, the documented next step is to run ticloud serverless create and follow the CLI prompts to provide the required information.
- Classification Note: This is classified as a cloud operation chunk because the official content covers CLI authentication and serverless cluster creation commands.

## Official Source Content

## Quick start

[TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) is the best way to get started with TiDB Cloud. In this section, you will learn how to create a TiDB Cloud Serverless cluster with TiDB Cloud CLI.
### Create a user profile or log into TiDB Cloud

Before creating a cluster with TiDB Cloud CLI, you need to either create a user profile or log into TiDB Cloud.

- Create a user profile with your [TiDB Cloud API key](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Authentication/API-Key-Management):

    ```shell
    ticloud config create
    ```

    > **Warning:**
    >
    > The profile name **MUST NOT** contain `.`.

- Log into TiDB Cloud with authentication:

    ```shell
    ticloud auth login
    ```

    After successful login, an OAuth token will be assigned to the current profile. If no profiles exist, the token will be assigned to a profile named `default`.

> **Note:**
>
> In the preceding two methods, the TiDB Cloud API key takes precedence over the OAuth token. If both are available, the API key will be used.
### Create a TiDB Cloud Serverless cluster

To create a TiDB Cloud Serverless cluster, enter the following command, and then follow the CLI prompts to provide the required information:

```shell
ticloud serverless create
```
