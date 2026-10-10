# VS Code SQLTools overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-gui-vscode-sqltools.md`
- Source Title: `Connect to TiDB with Visual Studio Code`
- Source Heading Path: `Connect to TiDB with Visual Studio Code | Connect to TiDB with Visual Studio Code > Prerequisites`
- Source Line Ranges: `5-44`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `vscode`, `sqltools`, `prerequisites`, `cluster-creation`, `remote-development`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0044_32a7b18e4f`
- Source ID: `tidb-docs-8.1:develop/dev-guide-gui-vscode-sqltools.md#connect-to-tidb-with-visual-studio-code`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b56ddcf82f5f86bcf2d670e88bc4f49b23313ad0e8d27fbe38379036eaaa121a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-gui-vscode-sqltools#connect-to-tidb-with-visual-studio-code
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-gui-vscode-sqltools.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the prerequisites or supported environments for connecting to a TiDB cluster from Visual Studio Code with SQLTools.
- Retrieval Keywords: Connect to TiDB with Visual Studio Code, VS Code SQLTools overview, Prerequisites, Visual Studio Code 1.72.0, SQLTools MySQL/MariaDB/TiDB, mtxr.sqltools-driver-mysql, official driver, remote development environments, GitHub Codespaces, Visual Studio Code Dev Containers, Visual Studio Code WSL, TiDB cluster, Deploy a local test TiDB cluster, production deployment using TiUP
- Follow-up Guidance: If the user does not have a TiDB cluster, this content points to creating a TiDB Cloud cluster or deploying a local test or production TiDB cluster.
- Classification Note: The chunk is classified as configuration because it lists required software, extension identifiers, and environment prerequisites before setting up the VS Code connection.

## Official Source Content

# Connect to TiDB with Visual Studio Code

TiDB is a MySQL-compatible database, and [Visual Studio Code (VS Code)](https://code.visualstudio.com/) is a lightweight but powerful source code editor. This tutorial uses the [SQLTools](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools) extension which supports TiDB as an [official driver](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools-driver-mysql).

In this tutorial, you can learn how to connect to your TiDB cluster using Visual Studio Code.

> **Note:**
>
> - This tutorial is compatible with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
> - This tutorial also works with Visual Studio Code Remote Development environments, such as [GitHub Codespaces](https://github.com/features/codespaces), [Visual Studio Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers), and [Visual Studio Code WSL](https://code.visualstudio.com/docs/remote/wsl).
## Prerequisites

To complete this tutorial, you need:

- [Visual Studio Code](https://code.visualstudio.com/#alt-downloads) **1.72.0** or later versions.
- [SQLTools MySQL/MariaDB/TiDB](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools-driver-mysql) extension for Visual Studio Code. To install it, you can use one of the following methods:
    - Click <a href="vscode:extension/mtxr.sqltools-driver-mysql">this link</a>  to launch VS Code and install the extension directly.
    - Navigate to [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools-driver-mysql) and click **Install**.
    - On the **Extensions** tab of your VS Code, search for `mtxr.sqltools-driver-mysql` to get the **SQLTools MySQL/MariaDB/TiDB** extension, and then click **Install**.
- A TiDB cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.
