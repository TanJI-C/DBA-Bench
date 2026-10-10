# Vector Search integration overview and supported ecosystem integrations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integration-overview.md`
- Source Title: `Vector Search Integration Overview`
- Source Heading Path: `Vector Search Integration Overview | Vector Search Integration Overview > AI frameworks | Vector Search Integration Overview > AI services | Vector Search Integration Overview > Embedding models and services | Vector Search Integration Overview > Object Relational Mapping (ORM) libraries`
- Source Line Ranges: `5-77`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `tidb`
- Topic Tags: `vector-search`, `ai-frameworks`, `ai-services`, `embedding-models`, `embedding-providers`, `orm`, `python`, `langchain`, `llamaindex`, `amazon-bedrock`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0929_c33032158d`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integration-overview.md#vector-search-integration-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `80f6e8d9aae06a669cb15043cd816f75fd053664561628a220d965f69d483f72`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integration-overview#vector-search-integration-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integration-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of TiDB Vector Search ecosystem integrations, supported AI frameworks, AI services, embedding providers, ORM libraries, and availability scope.
- Retrieval Keywords: Vector Search Integration Overview, TiDB Vector Search, Langchain, LlamaIndex, Amazon Bedrock, Jina AI, embedding models and services, up to 16383 dimensions, Object Relational Mapping (ORM) libraries, TiDB Vector Client, SQLAlchemy, peewee, Django, pip install tidb-vector[client], pip install tidb-vector, pip install django-tidb[vector], TiDB Cloud Serverless, TiDB Self-Managed, TiDB Cloud Dedicated
- Follow-up Guidance: The source links to integration tutorials for Langchain, LlamaIndex, Amazon Bedrock, Jina AI Embeddings API, TiDB Vector Client, SQLAlchemy, peewee, and Django.
- Classification Note: This is reference content because it summarizes supported TiDB Vector Search integrations, availability notes, and related installation/tutorial entry points rather than a single step-by-step procedure.

## Official Source Content

# Vector Search Integration Overview

This document provides an overview of TiDB Vector Search integration, including supported AI frameworks, embedding models, and Object Relational Mapping (ORM) libraries.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## AI frameworks

TiDB provides official support for the following AI frameworks, enabling you to easily integrate AI applications developed based on these frameworks with TiDB Vector Search.

| AI frameworks | Tutorial                                                                                          |
| ------------- | ------------------------------------------------------------------------------------------------- |
| Langchain     | [Integrate Vector Search with LangChain](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-langchain)   |
| LlamaIndex    | [Integrate Vector Search with LlamaIndex](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-llamaindex) |

Moreover, you can also use TiDB for various purposes, such as document storage and knowledge graph storage for AI applications.
## AI services

TiDB Vector Search supports integration with the following AI service, enabling you to easily build Retrieval-Augmented Generation (RAG) based applications.

- [Amazon Bedrock](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-amazon-bedrock)
## Embedding models and services

TiDB Vector Search supports storing vectors of up to 16383 dimensions, which accommodates most embedding models.

You can either use self-deployed open-source embedding models or third-party embedding APIs provided by third-party embedding providers to generate vectors.

The following table lists some mainstream embedding service providers and the corresponding integration tutorials.

| Embedding service providers | Tutorial                                                                                                            |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Jina AI                     | [Integrate Vector Search with Jina AI Embeddings API](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-jinaai-embedding) |
## Object Relational Mapping (ORM) libraries

You can integrate TiDB Vector Search with your ORM library to interact with the TiDB database.

The following table lists the supported ORM libraries and the corresponding integration tutorials:

<table>
  <tr>
    <th>Language</th>
    <th>ORM/Client</th>
    <th>How to install</th>
    <th>Tutorial</th>
  </tr>
  <tr>
    <td rowspan="4">Python</td>
    <td>TiDB Vector Client</td>
    <td><code>pip install tidb-vector[client]</code></td>
    <td><a href="/tidbcloud/vector-search-get-started-using-python">Get Started with Vector Search Using Python</a></td>
  </tr>
  <tr>
    <td>SQLAlchemy</td>
    <td><code>pip install tidb-vector</code></td>
    <td><a href="/tidbcloud/vector-search-integrate-with-sqlalchemy">Integrate TiDB Vector Search with SQLAlchemy</a></td>
  </tr>
  <tr>
    <td>peewee</td>
    <td><code>pip install tidb-vector</code></td>
    <td><a href="/tidbcloud/vector-search-integrate-with-peewee">Integrate TiDB Vector Search with peewee</a></td>
  </tr>
  <tr>
    <td>Django</td>
    <td><code>pip install django-tidb[vector]</code></td>
    <td><a href="/tidbcloud/vector-search-integrate-with-django-orm">Integrate TiDB Vector Search with Django</a></td>
  </tr>
</table>
