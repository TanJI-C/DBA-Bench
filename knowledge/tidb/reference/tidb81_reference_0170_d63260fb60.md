# peewee tutorial overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-python-peewee.md`
- Source Title: `Connect to TiDB with peewee`
- Source Heading Path: `Connect to TiDB with peewee | Connect to TiDB with peewee > Prerequisites`
- Source Line Ranges: `5-44`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `python`, `peewee`, `prerequisites`, `cluster-setup`, `environment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0170_d63260fb60`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-python-peewee.md#connect-to-tidb-with-peewee`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4fa262d1c1c0d1502cd7deba4c44390df826d0e28d6928edbed6e6a0e03e04ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-peewee#connect-to-tidb-with-peewee
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-python-peewee.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an overview of connecting TiDB with peewee and needs the stated prerequisites or cluster setup options for the tutorial.
- Retrieval Keywords: Connect to TiDB with peewee, Prerequisites, Python 3.8 or higher, Git, A TiDB cluster, TiDB Cloud Dedicated, TiDB Self-Managed, Creating a Starter cluster, Deploy a local test TiDB cluster, Deploy a production TiDB cluster, production-deployment-using-tiup
- Follow-up Guidance: The tutorial says you can next connect to your TiDB cluster using peewee, build and run your application, and optionally use sample CRUD code snippets.
- Classification Note: This is reference content because it summarizes the tutorial scope, supported cluster types named in the page, and prerequisite tools and environment requirements.

## Official Source Content

# Connect to TiDB with peewee

TiDB is a MySQL-compatible database, and [peewee](https://docs.peewee-orm.com/) is a popular Object Relational Mapper (ORM) for Python.

In this tutorial, you can learn how to use TiDB and peewee to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using peewee.
- Build and run your application. Optionally, you can find sample code snippets for basic CRUD operations.

> **Note:**
>
> This tutorial works with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed clusters.
## Prerequisites

To complete this tutorial, you need:

- [Python 3.8 or higher](https://www.python.org/downloads/).
- [Git](https://git-scm.com/downloads).
- A TiDB cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.
