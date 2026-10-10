# ProxySQL overview, benefits, and deployment architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-proxysql-integration.md`
- Source Title: `ProxySQL Integration Guide`
- Source Heading Path: `Integrate TiDB with ProxySQL | Integrate TiDB with ProxySQL > What is ProxySQL? | Integrate TiDB with ProxySQL > Why ProxySQL integration? | Integrate TiDB with ProxySQL > Deployment architecture`
- Source Line Ranges: `5-37`
- Source Scope: `all`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `cloud`
- Topic Tags: `proxysql`, `overview`, `benefits`, `deployment-architecture`, `sidecar`, `query-routing`, `connection-pooling`, `query-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0015_a710fa3a67`
- Source ID: `tidb-docs-8.1:develop/dev-guide-proxysql-integration.md#integrate-tidb-with-proxysql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2913c8a91a022902062cd986c3435feb096f1dc8bd8aecf7a459bd51b56a75e6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-proxysql-integration#integrate-tidb-with-proxysql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-proxysql-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for a high-level overview of ProxySQL with TiDB, its integration benefits, or the deployment architecture including standalone intermediary and sidecar patterns.
- Retrieval Keywords: ProxySQL, What is ProxySQL?, Why ProxySQL integration?, Deployment architecture, sidecar, standalone intermediary, connection pooling, caching frequently-used queries, query cache, query rules, SQL injection, open-source SQL proxy, MySQL compatible, zero vendor lock-in, additional latency due to network hop
- Follow-up Guidance: The document also provides development environment and production environment integration guidance and a typical scenario of query routing.
- Classification Note: This is classified as architecture because the content explains ProxySQL capabilities, integration benefits, and deployment architecture choices with TiDB.

## Official Source Content

# Integrate TiDB with ProxySQL

This document provides a high-level introduction to ProxySQL, describes how to integrate ProxySQL with TiDB in a [development environment](#development-environment) and a [production environment](#production-environment), and demonstrates the key integration benefits through the [scenario of query routing](#typical-scenario).

If you are interested in learning more about TiDB and ProxySQL, you can find some useful links as follows:

- [TiDB Cloud](https://docs.pingcap.com/tidbcloud)
- [TiDB Developer Guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview)
- [ProxySQL Documentation](https://proxysql.com/documentation/)
## What is ProxySQL?

[ProxySQL](https://proxysql.com/) is a high-performance, open-source SQL proxy. It has a flexible architecture and can be deployed in several different ways, making it ideal for a variety of use cases. For example, ProxySQL can be used to improve performance by caching frequently-accessed data.

ProxySQL is designed from the ground up to be fast, efficient, and easy to use. It is fully compatible with MySQL, and supports all of the features you would expect from a high quality SQL proxy. In addition, ProxySQL comes with a number of unique features that make it an ideal choice for a wide range of applications.
## Why ProxySQL integration?

- ProxySQL can help boost application performance by reducing latency when interacting with TiDB. Irrespective of what you are building, whether it is a scalable application using serverless functions like Lambda, where the workload is nondeterministic and can spike, or if you are building an application to execute queries that load tons of data. By leveraging powerful capabilities of ProxySQL such as [connection pooling](https://proxysql.com/documentation/detailed-answers-on-faq/) and [caching frequently-used queries](https://proxysql.com/documentation/query-cache/), applications can gain immediate benefits.
- ProxySQL can act as an additional layer of application security protection against SQL vulnerabilities such as SQL injection with the help of [query rules](#query-rules), an easy-to-configure feature available in ProxySQL.
- As both [ProxySQL](https://github.com/sysown/proxysql) and [TiDB](https://github.com/pingcap/tidb) are open-source projects, you can get the benefits of zero vendor lock-in.
## Deployment architecture

The most obvious way to deploy ProxySQL with TiDB is to add ProxySQL as a standalone intermediary between the application layer and TiDB. However, the scalability and failure tolerance are not guaranteed, and it also adds additional latency due to network hop. To avoid these problems, an alternate deployment architecture is to deploy ProxySQL as a sidecar as below:

![proxysql-client-side-tidb-cloud](/media/develop/proxysql-client-side-tidb-cloud.png)

> **Note:**
>
> The preceding illustration is only for reference. You must adapt it according to your actual deployment architecture.
