# DataGrip TiDB overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-datagrip.md`
- Source Title: `Connect to TiDB with JetBrains DataGrip`
- Source Heading Path: `Connect to TiDB with JetBrains DataGrip | Connect to TiDB with JetBrains DataGrip > Prerequisites`
- Source Line Ranges: `5-44`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `datagrip`, `jetbrains`, `prerequisites`, `cluster`, `connection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0041_0543ae085d`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-datagrip.md#connect-to-tidb-with-jetbrains-datagrip`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bb604176fc1a3fb796098b54c2a805ba7de95886d43568e67b165138f15171eb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-datagrip#connect-to-tidb-with-jetbrains-datagrip
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-datagrip.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an overview of connecting TiDB with JetBrains DataGrip and needs the documented prerequisites or supported environments.
- Retrieval Keywords: Connect to TiDB with JetBrains DataGrip, Prerequisites, DataGrip 2023.2.1 or later, JetBrains IDE, Database Tools and SQL plugin, TiDB cluster, TiDB Cloud Dedicated, TiDB Self-Managed, MySQL-compatible database
- Follow-up Guidance: The source also points to creating a TiDB Cloud cluster, deploying a local test TiDB cluster, or deploying a production TiDB cluster if no TiDB cluster exists.
- Classification Note: This is classified as configuration because the content defines the connection context, supported tooling, and prerequisite software and cluster requirements.

## Official Source Content

# Connect to TiDB with JetBrains DataGrip

TiDB is a MySQL-compatible database, and [JetBrains DataGrip](https://www.jetbrains.com/help/datagrip/getting-started.html) is a powerful integrated development environment (IDE) for database and SQL. This tutorial walks you through the process of connecting to your TiDB cluster using DataGrip.

> **Note:**
>
> This tutorial is compatible with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.

You can use DataGrip in two ways:

- As the [DataGrip IDE](https://www.jetbrains.com/datagrip/download) standalone tool.
- As the [Database Tools and SQL plugin](https://www.jetbrains.com/help/idea/relational-databases.html) in JetBrains IDEs, such as IntelliJ, PhpStorm, and PyCharm.

This tutorial mainly focuses on the standalone DataGrip IDE. The steps of connecting to TiDB using the JetBrains Database Tools and SQL plugin in JetBrains IDEs are similar. You can also follow the steps in this document for reference when connecting to TiDB from any JetBrains IDE.
## Prerequisites

To complete this tutorial, you need:

- [DataGrip **2023.2.1** or later](https://www.jetbrains.com/datagrip/download/) or a non-community edition [JetBrains](https://www.jetbrains.com/) IDE.
- A TiDB cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.
