# JDBC tutorial overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-jdbc.md`
- Source Title: `Connect to TiDB with JDBC`
- Source Heading Path: `Connect to TiDB with JDBC | Connect to TiDB with JDBC > Prerequisites`
- Source Line Ranges: `5-63`
- Source Scope: `all`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `sql`, `tiup`
- Topic Tags: `jdbc`, `java`, `mysql-connector-j`, `prerequisites`, `tls`, `verify_identity`, `san-certificates`, `collation`, `cluster-setup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0143_25e8111f1e`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-jdbc.md#connect-to-tidb-with-jdbc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e85e4c7941ba87cbf605b81890aa4bc15abe54d5bfe04f70c8e250f37f69d1e4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-jdbc#connect-to-tidb-with-jdbc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-jdbc.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the JDBC tutorial scope, supported deployment options, prerequisite software, TiDB cluster setup links, or the note about JDBC collation and TLS VERIFY_IDENTITY requirements.
- Retrieval Keywords: Connect to TiDB with JDBC, Prerequisites, Java Development Kit (JDK) 17, Maven 3.8, Git, MySQL Connector/J, VERIFY_IDENTITY, SAN certificates, 8.0.22, connectionCollation, characterEncoding, UTF-8, Collation used in JDBC connections, TiDB Cloud Dedicated, TiDB Self-Managed, Deploy a local test TiDB cluster, production-deployment-using-tiup
- Follow-up Guidance: The source also points to cluster creation paths such as Creating a cluster in TiDB Cloud, Deploy a local test TiDB cluster, and Deploy a production TiDB cluster.
- Classification Note: This is reference content because it summarizes what the JDBC tutorial covers, lists prerequisites, and states compatibility and connection notes rather than giving the main execution steps.

## Official Source Content

# Connect to TiDB with JDBC

TiDB is a MySQL-compatible database, and JDBC (Java Database Connectivity) is the data access API for Java. [MySQL Connector/J](https://dev.mysql.com/downloads/connector/j/) is MySQL's implementation of JDBC.

In this tutorial, you can learn how to use TiDB and JDBC to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using JDBC.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.

> **Note:**
>
> - This tutorial works with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
> - Starting from TiDB v7.4, if `connectionCollation` is not configured, and `characterEncoding` is either not configured or set to `UTF-8` in the JDBC URL, the collation used in a JDBC connection depends on the JDBC driver version. For more information, see [Collation used in JDBC connections](https://docs.pingcap.com/tidb/stable/faq/sql-faq#collation-used-in-jdbc-connections).

> **Note:**
>
> - This tutorial works with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
> - Starting from TiDB v7.4, if `connectionCollation` is not configured, and `characterEncoding` is either not configured or set to `UTF-8` in the JDBC URL, the collation used in a JDBC connection depends on the JDBC driver version. For more information, see [Collation used in JDBC connections](https://docs.pingcap.com/tidb/stable/sql-faq#collation-used-in-jdbc-connections).
## Prerequisites

To complete this tutorial, you need:

- **Java Development Kit (JDK) 17** or higher. You can choose [OpenJDK](https://openjdk.org/) or [Oracle JDK](https://www.oracle.com/hk/java/technologies/downloads/) based on your business and personal requirements.
- [Maven](https://maven.apache.org/install.html) **3.8** or higher.
- [Git](https://git-scm.com/downloads).
- A TiDB cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

> **Note:**
>
> For security considerations, it is recommended that you use `VERIFY_IDENTITY` to establish TLS connections to TiDB clusters when connecting over the internet. {{{ .starter }}}, {{{ .essential }}}, and TiDB Cloud Dedicated use Subject Alternative Name (SAN) certificates, which require MySQL Connector/J version to be greater than or equal to [8.0.22](https://dev.mysql.com/doc/relnotes/connector-j/en/news-8-0-22.html).

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.
