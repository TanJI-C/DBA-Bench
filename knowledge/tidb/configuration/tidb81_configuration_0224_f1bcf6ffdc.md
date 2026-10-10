# Data App integrations with GPTs and Dify

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-integrations.md`
- Source Title: `Integrate a Data App with Third-Party Tools`
- Source Heading Path: `Integrate a Data App with Third-Party Tools | Integrate a Data App with Third-Party Tools > Integrate your Data App with GPTs | Integrate a Data App with Third-Party Tools > Integrate your Data App with Dify`
- Source Line Ranges: `5-40`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `data app`, `data service`, `integrations`, `gpts`, `dify`, `openapi`, `api key`, `base64`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0224_f1bcf6ffdc`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-integrations.md#integrate-a-data-app-with-third-party-tools`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ef61f2578242e7bb3a0027aef9ccfba272b115cebdb59dd9485df4d471c22e20`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-integrations#integrate-a-data-app-with-third-party-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-integrations.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to get Data App integration configuration for GPTs or Dify in the TiDB Cloud console, including the OpenAPI specification URL, API key, and encoded API key.
- Retrieval Keywords: Data App integrations, Integrate your Data App with GPTs, Integrate your Data App with Dify, TiDB Cloud console, Data Service, Integrations tab, Get Configuration, API Specification URL, OpenAPI Specification, API Key, Create API Key, API Key Encoded, base64 encoded string, Dify, GPTs
- Follow-up Guidance: For Dify, the source says to follow the same steps as GPTs integration, but click Get Configuration in the Integrate with Dify area on the Integrations tab.
- Classification Note: This is classified as configuration because the content describes obtaining and using integration configuration values for a Data App in TiDB Cloud.

## Official Source Content

# Integrate a Data App with Third-Party Tools

Integrating third-party tools with your Data App enhances your applications with advanced natural language processing and artificial intelligence (AI) capabilities provided by third-party tools. This integration enables your applications to perform more complex tasks and deliver intelligent solutions.

This document describes how to integrate a Data App with third-party tools, such as GPTs and Dify, in the TiDB Cloud console.
## Integrate your Data App with GPTs

You can integrate your Data App with [GPTs](https://openai.com/blog/introducing-gpts) to enhance your applications with intelligent capabilities.

To integrate your Data App with GPTs, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, locate your target Data App, click the name of your target Data App, and then click the **Integrations** tab.
3. In the **Integrate with GPTs** area, click **Get Configuration**.

    ![Get Configuration](/media/tidb-cloud/data-service/GPTs1.png)

4. In the displayed dialog box, you can see the following fields:

    a. **API Specification URL**: copy the URL of the OpenAPI Specification of your Data App. For more information, see [Use the OpenAPI Specification](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#use-the-openapi-specification).

    b. **API Key**: enter the API key of your Data App. If you do not have an API key yet, click **Create API Key** to create one. For more information, see [Create an API key](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key#create-an-api-key).

    c. **API Key Encoded**: copy the base64 encoded string equivalent to the API key you have provided.

    ![GPTs Dialog Box](/media/tidb-cloud/data-service/GPTs2.png)

5. Use the copied API Specification URL and the encoded API key in your GPT configuration.
## Integrate your Data App with Dify

You can integrate your Data App with [Dify](https://docs.dify.ai/guides/tools) to enhance your applications with intelligent capabilities, such as vector distance calculations, advanced similarity searches, and vector analysis.

To integrate your Data App with Dify, follow the same steps as for [GPTs integration](#integrate-your-data-app-with-gpts). The only difference is that on the **Integrations** tab, you need to click **Get Configuration** in the **Integrate with Dify** area.
