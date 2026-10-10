# DBeaver TiDB prerequisites

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-dbeaver.md`
- Source Title: `Connect to TiDB with DBeaver`
- Source Heading Path: `Connect to TiDB with DBeaver | Connect to TiDB with DBeaver > Prerequisites`
- Source Line Ranges: `5-39`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `cloud`
- Topic Tags: `dbeaver`, `prerequisites`, `cluster`, `connection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0056_2b4c5e15dc`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-dbeaver.md#connect-to-tidb-with-dbeaver`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0e26303687b3a8f4e4fe9d2f972b8892b50b852dac6fc57cef85ef982881b6cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-dbeaver#connect-to-tidb-with-dbeaver
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-dbeaver.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the prerequisites for connecting a TiDB cluster with DBeaver Community.
- Retrieval Keywords: DBeaver Community 23.0.3 or higher, TiDB cluster prerequisites, Connect to TiDB with DBeaver, Creating a TiDB Cloud cluster, Deploy a local test TiDB cluster, Deploy a production TiDB cluster
- Follow-up Guidance: If no TiDB cluster exists, the content points to creating a TiDB Cloud cluster or deploying a local test or production cluster.
- Classification Note: This is classified as an operation chunk because it lists prerequisite software and cluster requirements before making a DBeaver connection.

## Official Source Content

# Connect to TiDB with DBeaver

TiDB is a MySQL-compatible database, and [DBeaver Community](https://dbeaver.io/download/) is a free cross-platform database tool for developers, database administrators, analysts, and everyone working with data.

In this tutorial, you can learn how to connect to your TiDB cluster using DBeaver Community.

> **Note:**
>
> This tutorial is compatible with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [DBeaver Community **23.0.3** or higher](https://dbeaver.io/download/).
- A TiDB cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.
