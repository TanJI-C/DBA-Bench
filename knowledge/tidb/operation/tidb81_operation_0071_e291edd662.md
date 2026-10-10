# TypeORM tutorial overview, prerequisites, and initial setup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-typeorm.md`
- Source Title: `Connect to TiDB with TypeORM`
- Source Heading Path: `Connect to TiDB with TypeORM | Connect to TiDB with TypeORM > Prerequisites | Connect to TiDB with TypeORM > Run the sample app to connect to TiDB | Connect to TiDB with TypeORM > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with TypeORM > Run the sample app to connect to TiDB > Step 2: Install dependencies`
- Source Line Ranges: `5-82`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `node.js`, `typeorm`, `prerequisites`, `sample-app`, `git`, `npm`, `dependencies`, `setup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0071_e291edd662`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-typeorm.md#connect-to-tidb-with-typeorm`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4985a3c2fff92fcbbe6f2b228d66268fafe1bf519231cf3a974d890f83443f66`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-typeorm#connect-to-tidb-with-typeorm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-typeorm.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TypeORM quickstart overview, prerequisites, or the initial commands to clone the sample repository and install Node.js dependencies for connecting to TiDB.
- Retrieval Keywords: Connect to TiDB with TypeORM, TypeORM, Node.js >= 16.x, Git, A TiDB cluster running, git clone https://github.com/tidb-samples/tidb-nodejs-typeorm-quickstart.git, cd tidb-nodejs-typeorm-quickstart, npm install, typeorm, mysql2, dotenv, typescript, ts-node, @types/node
- Follow-up Guidance: The next steps in the source are to configure connection information in a `.env` file, run `npm run migration:run`, and then run `npm start`.
- Classification Note: This is classified as an operation chunk because it provides prerequisites and step-by-step setup commands for running a sample TypeORM application with TiDB.

## Official Source Content

# Connect to TiDB with TypeORM

TiDB is a MySQL-compatible database, and [TypeORM](https://github.com/TypeORM/TypeORM) is a popular open-source ORM framework for Node.js.

In this tutorial, you can learn how to use TiDB and TypeORM to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using TypeORM.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.

> **Note**
>
> This tutorial works with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [Node.js](https://nodejs.org/en) >= 16.x installed on your machine.
- [Git](https://git-scm.com/downloads) installed on your machine.
- A TiDB cluster running.

**If you don't have a TiDB cluster, you can create one as follows:**

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.

- (Recommended) Follow [Creating a {{{ .starter }}} cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster.
- Follow [Deploy a local test TiDB cluster](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster) or [Deploy a production TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to create a local cluster.
## Run the sample app to connect to TiDB

This section demonstrates how to run the sample application code and connect to TiDB.
### Step 1: Clone the sample app repository

Run the following commands in your terminal window to clone the sample code repository:

```shell
git clone https://github.com/tidb-samples/tidb-nodejs-typeorm-quickstart.git
cd tidb-nodejs-typeorm-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including `typeorm` and `mysql2`) for the sample app:

```shell
npm install
```

<details>
<summary><b>Install dependencies to an existing project</b></summary>

For your existing project, run the following command to install the packages:

- `typeorm`: the ORM framework for Node.js.
- `mysql2`: the MySQL driver for Node.js. You can also use the `mysql` driver.
- `dotenv`: loads environment variables from the `.env` file.
- `typescript`: compiles TypeScript code to JavaScript.
- `ts-node`: runs TypeScript code directly without compiling.
- `@types/node`: provides TypeScript type definitions for Node.js.

```shell
npm install typeorm mysql2 dotenv --save
npm install @types/node ts-node typescript --save-dev
```

</details>
