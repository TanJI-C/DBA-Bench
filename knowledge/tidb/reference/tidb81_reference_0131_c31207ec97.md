# AWS Lambda mysql2 tutorial overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-aws-lambda.md`
- Source Title: `Connect to TiDB with mysql2 in AWS Lambda Function`
- Source Heading Path: `Connect to TiDB with mysql2 in AWS Lambda Function | Connect to TiDB with mysql2 in AWS Lambda Function > Prerequisites`
- Source Line Ranges: `5-50`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `aws-lambda`, `mysql2`, `prerequisites`, `nodejs`, `git`, `aws-cli`, `sam-cli`, `cluster-setup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0131_c31207ec97`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-aws-lambda.md#connect-to-tidb-with-mysql2-in-aws-lambda-function`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7bf67165c90b5fd2e872e3c8bf7946c22572e2370d22aaaa030d5a19ab6a6979`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-aws-lambda#connect-to-tidb-with-mysql2-in-aws-lambda-function
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-aws-lambda.md

## Retrieval Guidance

- Use When: Use this chunk when you need the tutorial overview and prerequisites for connecting TiDB with mysql2 in an AWS Lambda Function.
- Retrieval Keywords: Connect to TiDB with mysql2 in AWS Lambda Function, Prerequisites, AWS Lambda Function, mysql2, Node.js 18 or later, Git, AWS CLI, AWS SAM CLI, TiDB cluster, AWS user with administrator permissions, Creating a TiDB Cloud cluster, Deploy a local test TiDB cluster, Deploy a production TiDB cluster, Getting Started with Lambda
- Follow-up Guidance: The tutorial then covers running the sample app, connecting to the TiDB cluster, building and running the application, and deploying the AWS Lambda Function.
- Classification Note: This is reference content because it summarizes the tutorial scope and lists required tools, accounts, and cluster prerequisites.

## Official Source Content

# Connect to TiDB with mysql2 in AWS Lambda Function

TiDB is a MySQL-compatible database, [AWS Lambda Function](https://aws.amazon.com/lambda/) is a compute service, and [mysql2](https://github.com/sidorares/node-mysql2) is a popular open-source driver for Node.js.

In this tutorial, you can learn how to use TiDB and mysql2 in AWS Lambda Function to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using mysql2.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.
- Deploy your AWS Lambda Function.

> **Note**
>
> This tutorial works with {{{ .starter }}}, {{{ .essential }}}, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [Node.js **18**](https://nodejs.org/en/download/) or later.
- [Git](https://git-scm.com/downloads).
- A TiDB cluster.
- An [AWS user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html) with administrator permissions.
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

If you don't have an AWS account or a user, you can create them by following the steps in the [Getting Started with Lambda](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html) guide.
