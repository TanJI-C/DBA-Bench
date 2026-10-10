# PoC overview, goals, and workload identification

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-poc.md`
- Source Title: `Perform a Proof of Concept (PoC) with TiDB Cloud`
- Source Heading Path: `Perform a Proof of Concept (PoC) with TiDB Cloud | Perform a Proof of Concept (PoC) with TiDB Cloud > Overview of the PoC procedures | Perform a Proof of Concept (PoC) with TiDB Cloud > Step 1. Define success criteria and create a test plan | Perform a Proof of Concept (PoC) with TiDB Cloud > Step 2. Identify characteristics of your workload`
- Source Line Ranges: `5-58`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `poc`, `evaluation`, `test-plan`, `success-criteria`, `workload-characteristics`, `high-availability`, `strong-consistency`, `htap`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0419_a20282cc42`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-poc.md#perform-a-proof-of-concept-poc-with-tidb-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7332e2c37e0754e66f740f31042d3feb6a129f18e9b676d1a10a8ca41375da73`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-poc#perform-a-proof-of-concept-poc-with-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-poc.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official TiDB Cloud PoC overview, the typical PoC steps, or guidance for defining success criteria and identifying workload characteristics.
- Retrieval Keywords: Perform a Proof of Concept (PoC) with TiDB Cloud, Overview of the PoC procedures, Define success criteria and create a test plan, Identify characteristics of your workload, typical TiDB Cloud PoC consists of the following steps, 14 days, high availability, strong consistency, real-time HTAP, MySQL protocol and MySQL ecosystem, TiFlash, workload scenario, dataset size, growth rate, throughput, latency, planned or unplanned downtime, security and compliance requirements
- Follow-up Guidance: The next documented PoC steps are to create a TiDB Cloud Dedicated cluster, adapt schemas and SQL, import data, run the workload and evaluate results, explore more features, and clean up the environment.
- Classification Note: This chunk is classified as an operation topic because the official content describes PoC planning procedures, success criteria, and workload evaluation steps for TiDB Cloud.

## Official Source Content

# Perform a Proof of Concept (PoC) with TiDB Cloud

TiDB Cloud is a Database-as-a-Service (DBaaS) product that delivers everything great about TiDB in a fully managed cloud database. It helps you focus on your applications, instead of the complexities of your database. TiDB Cloud is currently available on Amazon Web Services (AWS), Google Cloud, and Microsoft Azure.

Initiating a proof of concept (PoC) is the best way to determine whether TiDB Cloud is the best fit for your business needs. It will also get you familiar with the key features of TiDB Cloud in a short time. By running performance tests, you can see whether your workload can run efficiently on TiDB Cloud. You can also evaluate the efforts required to migrate your data and adapt configurations.

This document describes the typical PoC procedures and aims to help you quickly complete a TiDB Cloud PoC. It is a best practice that has been validated by TiDB experts and a large customer base.

If you are interested in doing a PoC, feel free to contact <a href="mailto:tidbcloud-support@pingcap.com">PingCAP</a> before you get started. The support team can help you create a test plan and walk you through the PoC procedures smoothly.

Alternatively, you can [create a TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart#step-1-create-a-tidb-cluster) to get familiar with TiDB Cloud for a quick evaluation. Note that the TiDB Cloud Serverless has some [special terms and conditions](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless-special-terms-and-conditions).
## Overview of the PoC procedures

The purpose of a PoC is to test whether TiDB Cloud meets your business requirements. A typical PoC usually lasts 14 days, during which you are expected to focus on completing the PoC.

A typical TiDB Cloud PoC consists of the following steps:

1. Define success criteria and create a test plan
2. Identify characteristics of your workload
3. Sign up and create a TiDB Cloud Dedicated cluster for the PoC
4. Adapt your schemas and SQL
5. Import data
6. Run your workload and evaluate results
7. Explore more features
8. Clean up the environment and finish the PoC
## Step 1. Define success criteria and create a test plan

When evaluating TiDB Cloud through a PoC, it is recommended to decide your points of interest and the corresponding technical evaluation criteria based on your business needs, and then clarify your expectations and goals for the PoC. Clear and measurable technical criteria with a detailed test plan can help you focus on the key aspects, cover the business level requirements, and ultimately get answers through the PoC procedures.

Use the following questions to help identify the goals of your PoC:

- What is the scenario of your workload?
- What is the dataset size or workload of your business? What is the growth rate?
- What are the performance requirements, including the business-critical throughput or latency requirements?
- What are the availability and stability requirements, including the minimum acceptable planned or unplanned downtime?
- What are the necessary metrics for operational efficiency? How do you measure them?
- What are the security and compliance requirements for your workload?

For more information about the success criteria and how to create a test plan, feel free to contact <a href="mailto:tidbcloud-support@pingcap.com">PingCAP</a>.
## Step 2. Identify characteristics of your workload

TiDB Cloud is suitable for various use cases that require high availability and strong consistency with a large volume of data. [TiDB Introduction](https://docs.pingcap.com/tidb/stable/overview) lists the key features and scenarios. You can check whether they apply to your business scenarios:

- Horizontally scaling out or scaling in
- Financial-grade high availability
- Real-time HTAP
- Compatible with the MySQL protocol and MySQL ecosystem

You might also be interested in using [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash-overview), a columnar storage engine that helps speed up analytical processing. During the PoC, you can use the TiFlash feature at any time.
