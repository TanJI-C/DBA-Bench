# Quick start overview and deployment options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/quick-start-with-tidb.md`
- Source Title: `Quick Start Guide for the TiDB Database Platform`
- Source Heading Path: `Quick Start Guide for the TiDB Database Platform`
- Source Line Ranges: `5-22`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `cloud`, `operator`, `tiup`
- Topic Tags: `quickstart`, `deployment-methods`, `non-production`, `playground`, `production-guidance`, `kubernetes`, `cloud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0486_f7da5e017d`
- Source ID: `tidb-docs-8.1:quick-start-with-tidb.md#quick-start-guide-for-the-tidb-database-platform`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40a746d77c8986b4f651ad53c32ce3bf1f7ba8501f08c6ae502d988dfa92ba32`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#quick-start-guide-for-the-tidb-database-platform
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/quick-start-with-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when someone asks which quick start deployment methods are available, whether they are for non-production only, or where to go for production, Kubernetes, TiDB Cloud, or TiDB Playground entry points.
- Retrieval Keywords: Quick Start Guide for the TiDB Database Platform, Deploy a local test cluster, Simulate production deployment on a single machine, TiDB Playground, ONLY FOR quick start, NOT FOR production, production installation guide, Get Started with TiDB on Kubernetes, TiDB Cloud Quick Start
- Follow-up Guidance: It points to the production installation guide, Get Started with TiDB on Kubernetes, and TiDB Cloud Quick Start for those deployment paths.
- Classification Note: The classification is reference because the content summarizes available quick start options and scope limitations rather than giving one specific procedure.

## Official Source Content

# Quick Start Guide for the TiDB Database Platform

This guide provides the quickest way to get started with TiDB. For non-production environments, you can deploy your TiDB database using either of the following methods:

- [Deploy a local test cluster](#deploy-a-local-test-cluster) (for macOS and Linux)
- [Simulate production deployment on a single machine](#simulate-production-deployment-on-a-single-machine) (for Linux only)

In addition, you can try out TiDB features on [TiDB Playground](https://play.tidbcloud.com/?utm_source=docs&utm_medium=tidb_quick_start).

> **Note:**
>
> The deployment method provided in this guide is **ONLY FOR** quick start, **NOT FOR** production or comprehensive functionality and stability testing.
>
> - To deploy a self-hosted production cluster, see the [production installation guide](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup).
> - To deploy TiDB on Kubernetes, see [Get Started with TiDB on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/get-started).
> - To manage TiDB in the cloud, see [TiDB Cloud Quick Start](https://docs.pingcap.com/tidbcloud/tidb-cloud-quickstart).
