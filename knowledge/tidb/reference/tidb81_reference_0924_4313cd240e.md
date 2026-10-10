# Amazon Bedrock integration overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-amazon-bedrock.md`
- Source Title: `Integrate TiDB Vector Search with Amazon Bedrock`
- Source Heading Path: `Integrate TiDB Vector Search with Amazon Bedrock | Integrate TiDB Vector Search with Amazon Bedrock > Prerequisites | Integrate TiDB Vector Search with Amazon Bedrock > Get started`
- Source Line Ranges: `5-46`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `ecosystem`
- Topic Tags: `vector-search`, `amazon-bedrock`, `rag`, `prerequisites`, `serverless`, `models`, `regions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0924_4313cd240e`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-amazon-bedrock.md#integrate-tidb-vector-search-with-amazon-bedrock`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae4ac898eb5a6b4d95b9b300984b4baad01c74c2f7eedefaa1b078775a9d82f8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-amazon-bedrock#integrate-tidb-vector-search-with-amazon-bedrock
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-amazon-bedrock.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview, availability note, prerequisites, supported region requirement, or model identifiers for integrating TiDB Vector Search with Amazon Bedrock for a RAG Q&A bot.
- Retrieval Keywords: Integrate TiDB Vector Search with Amazon Bedrock, RAG Q&A bot, TiDB Vector Search, TiDB Cloud Serverless, TiDB Self-Managed (TiDB >= v8.4), not available for TiDB Cloud Dedicated, Python 3.11 or later, Pip, AWS CLI, aws configure set region <your-region>, Amazon Bedrock Regions, required permissions for Amazon Bedrock, amazon.titan-embed-text-v2:0, us.meta.llama3-2-3b-instruct-v1:0, Request access to an Amazon Bedrock foundation model
- Follow-up Guidance: The next section provides step-by-step instructions to set environment variables and start the integration.
- Classification Note: This is reference content because it states the integration purpose, availability note, prerequisites, and exact Amazon Bedrock model and region identifiers from the tutorial.

## Official Source Content

# Integrate TiDB Vector Search with Amazon Bedrock

This tutorial demonstrates how to integrate the [vector search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview) feature of TiDB with [Amazon Bedrock](https://aws.amazon.com/bedrock/) to build a Retrieval-Augmented Generation (RAG) Q&A bot.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).

> **Tip**
>
> You can view the complete [sample code](https://github.com/aws-samples/aws-generativeai-partner-samples/blob/main/tidb/samples/tidb-bedrock-boto3-rag.ipynb) in Notebook format.
## Prerequisites

To complete this tutorial, you need:

- [Python 3.11 or later](https://www.python.org/downloads/) installed
- [Pip](https://pypi.org/project/pip/) installed
- [AWS CLI](https://aws.amazon.com/cli/) installed

    Ensure your AWS CLI profile is configured to a supported [Amazon Bedrock](https://aws.amazon.com/bedrock/) region for this tutorial. You can find the list of supported regions at [Amazon Bedrock Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html). To switch to a supported region, run the following command:

    ```shell
    aws configure set region <your-region>
    ```

- A TiDB Cloud Serverless cluster

    Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create your own TiDB Cloud cluster if you don't have one.

- An AWS account with the [required permissions for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_id-based-policy-examples.html) and access to the following models:

    - **Amazon Titan Embeddings** (`amazon.titan-embed-text-v2:0`), used for generating text embeddings
    - **Meta Llama 3** (`us.meta.llama3-2-3b-instruct-v1:0`), used for text generation

  If you don't have access, follow the instructions in [Request access to an Amazon Bedrock foundation model](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html#getting-started-model-access).
## Get started

This section provides step-by-step instructions for integrating TiDB Vector Search with Amazon Bedrock to build a RAG-based Q&A bot.
