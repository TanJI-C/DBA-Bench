# General TiDB Cloud FAQs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-faq.md`
- Source Title: `TiDB Cloud FAQs`
- Source Heading Path: `TiDB Cloud FAQs | TiDB Cloud FAQs > General FAQs | TiDB Cloud FAQs > General FAQs > What is TiDB Cloud? | TiDB Cloud FAQs > General FAQs > What is the relationship between TiDB and TiDB Cloud? | TiDB Cloud FAQs > General FAQs > Is TiDB Cloud compatible with MySQL? | TiDB Cloud FAQs > General FAQs > What programming languages can I use to work with TiDB Cloud? | TiDB Cloud FAQs > General FAQs > Where can I run TiDB Cloud? | TiDB Cloud FAQs > General FAQs > Does TiDB Cloud support VPC peering between different cloud service providers? | TiDB Cloud FAQs > General FAQs > What versions of TiDB are supported on TiDB Cloud? | TiDB Cloud FAQs > General FAQs > What companies are using TiDB or TiDB Cloud in production? | TiDB Cloud FAQs > General FAQs > What does the SLA look like? | TiDB Cloud FAQs > General FAQs > What does BETA mean in TiDB Cloud? | TiDB Cloud FAQs > General FAQs > How can I learn more about TiDB Cloud? | TiDB Cloud FAQs > General FAQs > What does `XXX's Org/default project/Cluster0` refer to when deleting a cluster?`
- Source Line Ranges: `5-72`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`
- Topic Tags: `overview`, `mysql-compatibility`, `programming-languages`, `cloud-providers`, `vpc-peering`, `supported-versions`, `sla`, `beta`, `learning-resources`, `cluster-identification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0908_06f947977a`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-faq.md#tidb-cloud-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `333d9a8b91bbad49b70b4ad48dcb17d0bc1df0bb6a38711ce71279061e112960`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-faq#tidb-cloud-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering general TiDB Cloud FAQ questions about what TiDB Cloud is, how it relates to TiDB, MySQL compatibility, supported languages, cloud providers, VPC peering across providers, supported TiDB versions, SLA, BETA meaning, learning resources, or the fully qualified cluster name shown during deletion.
- Retrieval Keywords: TiDB Cloud FAQs, What is TiDB Cloud, relationship between TiDB and TiDB Cloud, compatible with MySQL, MySQL 5.7, MySQL 8.0, triggers, stored procedures, user-defined functions, programming languages, MySQL client or driver, Amazon Web Services (AWS), Google Cloud, Microsoft Azure, VPC peering between different cloud service providers, default TiDB version for new TiDB Cloud Dedicated clusters, v8.1.2, TiDB Cloud Serverless clusters, v7.1.3, TiDB Cloud Release Notes, 99.99% SLA, BETA, TiDB Cloud Introduction, Get Started, Create a TiDB Cloud Serverless Cluster, XXX's Org/default project/Cluster0, organization name project name and cluster name
- Follow-up Guidance: For more details, the content points to Compatibility with MySQL, TiDB Cloud Release Notes, TiDB Cloud Introduction, Get Started, and Create a TiDB Cloud Serverless Cluster.
- Classification Note: This chunk is reference content because it is a general FAQ that states product scope, compatibility, availability, version information, SLA, and identifier meaning for TiDB Cloud.

## Official Source Content

# TiDB Cloud FAQs

This document lists the most frequently asked questions about TiDB Cloud.
## General FAQs
### What is TiDB Cloud?

TiDB Cloud makes deploying, managing, and maintaining your TiDB clusters even simpler with a fully managed cloud instance that you control through an intuitive console. You are able to easily deploy on Amazon Web Services (AWS), Google Cloud, or Microsoft Azure to quickly build mission-critical applications.

TiDB Cloud allows developers and DBAs with little or no training to handle once-complex tasks such as infrastructure management and cluster deployment with ease, to focus on your applications, not the complexities of your database. And by scaling TiDB clusters in or out with a simple click of a button, you no longer waste costly resources because you are able to provision your databases for exactly how much and how long you need them.
### What is the relationship between TiDB and TiDB Cloud?

TiDB is an open-source database and is the best option for organizations who want to run TiDB Self-Managed in their own data centers, in a self-managed cloud environment, or in a hybrid of the two.

TiDB Cloud is a fully managed cloud Database as a Service of TiDB. It has an easy-to-use web-based management console to let you manage TiDB clusters for mission-critical production environments.
### Is TiDB Cloud compatible with MySQL?

Currently, TiDB Cloud supports the majority of MySQL 5.7 and MySQL 8.0 syntax with the exception of triggers, stored procedures, and user-defined functions. For more details, see [Compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility).
### What programming languages can I use to work with TiDB Cloud?

You can use any language supported by the MySQL client or driver.
### Where can I run TiDB Cloud?

TiDB Cloud is currently available on Amazon Web Services (AWS), Google Cloud, and Microsoft Azure.
### Does TiDB Cloud support VPC peering between different cloud service providers?

No.
### What versions of TiDB are supported on TiDB Cloud?

- Starting from January 2, 2025, the default TiDB version for new TiDB Cloud Dedicated clusters is [v8.1.2](https://docs.pingcap.com/tidb/v8.1/release-8.1.2).
- Starting from February 21, 2024, the TiDB version for TiDB Cloud Serverless clusters is [v7.1.3](https://docs.pingcap.com/tidb/v7.1/release-7.1.3).

For more information, see [TiDB Cloud Release Notes](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-release-notes).
### What companies are using TiDB or TiDB Cloud in production?

TiDB is trusted by over 1500 global enterprises across a variety of industries, such as financial services, gaming, and e-commerce. Our users include Square (US), Shopee (Singapore), and China UnionPay (China). See our [case studies](https://www.pingcap.com/customers/) for specific details.
### What does the SLA look like?

TiDB Cloud provides 99.99% SLA. For details, see [Service Level Agreement for TiDB Cloud Services](https://www.pingcap.com/legal/service-level-agreement-for-tidb-cloud-services/).
### What does BETA mean in TiDB Cloud?

BETA is the public preview stage of a TiDB Cloud feature or offering before it becomes generally available (GA).
### How can I learn more about TiDB Cloud?

The best way to learn about TiDB Cloud is to follow our step-by-step tutorial. Check out the following topics to get started:

- [TiDB Cloud Introduction](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-intro)
- [Get Started](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart)
- [Create a TiDB Cloud Serverless Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless)
### What does `XXX's Org/default project/Cluster0` refer to when deleting a cluster?

In TiDB Cloud, a cluster is uniquely identified by the combination of the organization name, project name, and cluster name. To ensure that you are deleting the intended cluster, you need to provide the fully qualified name of that cluster, such as `XXX's Org/default project/Cluster0`.
