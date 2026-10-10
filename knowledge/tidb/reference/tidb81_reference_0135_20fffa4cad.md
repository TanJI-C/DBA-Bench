# GORM tutorial overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-golang-gorm.md`
- Source Title: `Connect to TiDB with GORM`
- Source Heading Path: `Connect to TiDB with GORM | Connect to TiDB with GORM > Prerequisites`
- Source Line Ranges: `5-44`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `gorm`, `golang`, `prerequisites`, `cluster-setup`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0135_20fffa4cad`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-golang-gorm.md#connect-to-tidb-with-gorm`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8254280688c4056439d987fc013f155e8acf4444a111b56b84e0027dc03ceade`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-gorm#connect-to-tidb-with-gorm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-golang-gorm.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the overview and prerequisites for connecting to TiDB with GORM, including supported environments and required tools.
- Retrieval Keywords: Connect to TiDB with GORM, Prerequisites, Go 1.20 or higher, Git, TiDB cluster, MySQL-compatible database, GORM, AUTO_RANDOM, supports TiDB as a default database option, Creating a TiDB Cloud cluster, Deploy a local test TiDB cluster, Deploy a production TiDB cluster, TiUP
- Follow-up Guidance: It also points to creating a TiDB Cloud cluster or deploying a local test or production TiDB cluster if you do not already have a TiDB cluster.
- Classification Note: This is classified as reference content because it introduces the GORM tutorial scope, compatibility, and prerequisite environment requirements rather than giving a single operational procedure.

## Official Source Content

# Connect to TiDB with GORM

TiDB is a MySQL-compatible database, and [GORM](https://gorm.io/index.html) is a popular open-source ORM framework for Golang. GORM adapts to TiDB features such as `AUTO_RANDOM` and [supports TiDB as a default database option](https://gorm.io/docs/connecting_to_the_database.html#TiDB).

In this tutorial, you can learn how to use TiDB and GORM to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using GORM.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.

> **Note:**
>
> This tutorial works with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [Go](https://go.dev/) **1.20** or higher.
- [Git](https://git-scm.com/downloads).
- A TiDB cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.
