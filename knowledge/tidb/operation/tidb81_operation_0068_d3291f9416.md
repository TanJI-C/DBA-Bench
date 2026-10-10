# Node.js mysql2 sample app setup and connection runbook

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-mysql2.md`
- Source Title: `Connect to TiDB with node-mysql2`
- Source Heading Path: `Connect to TiDB with node-mysql2 | Connect to TiDB with node-mysql2 > Prerequisites | Connect to TiDB with node-mysql2 > Run the sample app to connect to TiDB | Connect to TiDB with node-mysql2 > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with node-mysql2 > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with node-mysql2 > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with node-mysql2 > Run the sample app to connect to TiDB > Step 4: Run the code and check the result`
- Source Line Ranges: `5-203`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `nodejs`, `mysql2`, `prerequisites`, `sample-app`, `git`, `npm`, `dotenv`, `connection-configuration`, `tls`, `ca-certificate`, `ip-access-list`, `public-endpoint`, `self-managed`, `tidb-cloud`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0068_d3291f9416`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-mysql2.md#connect-to-tidb-with-node-mysql2`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a49c5c065919facc6e443e0da97432266c1f231708f3e32ca58dbf80b9c76a72`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-mysql2#connect-to-tidb-with-node-mysql2
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-mysql2.md

## Retrieval Guidance

- Use When: Use this chunk when you need the setup and run steps for connecting a Node.js application to TiDB with node-mysql2, including prerequisites, cloning the sample repository, configuring a .env file, and verifying connection output.
- Retrieval Keywords: Connect to TiDB with node-mysql2, node-mysql2, Node.js >= 16.x, Git, git clone https://github.com/tidb-samples/tidb-nodejs-mysql2-quickstart.git, npm install, cp .env.example .env, TIDB_HOST, TIDB_PORT=4000, TIDB_USER, TIDB_PASSWORD, TIDB_DATABASE=test, TIDB_ENABLE_SSL, TIDB_CA_PATH, Public, Branch main, Connect With General, CA cert, Configure IP Access List, TiDB Cloud Dedicated, TiDB Self-Managed, npm start, Connected to TiDB cluster
- Follow-up Guidance: If the connection is successful, the console outputs a message starting with "🔌 Connected to TiDB cluster!" followed by sample CRUD output.
- Classification Note: This is classified as an operation chunk because the official content provides a procedural runbook with prerequisites, environment configuration, and execution steps for the sample app.

## Official Source Content

# Connect to TiDB with node-mysql2

TiDB is a MySQL-compatible database, and [node-mysql2](https://github.com/sidorares/node-mysql2) is a fast [mysqljs/mysql](https://github.com/mysqljs/mysql) compatible MySQL driver for Node.js.

In this tutorial, you can learn how to use TiDB and node-mysql2 to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using node-mysql2.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.

> **Note:**
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
git clone https://github.com/tidb-samples/tidb-nodejs-mysql2-quickstart.git
cd tidb-nodejs-mysql2-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including `mysql2` and `dotenv`) for the sample app:

```shell
npm install
```

<details>
<summary><b>Install dependencies to existing project</b></summary>

For your existing project, run the following command to install the packages:

```shell
npm install mysql2 dotenv --save
```

</details>
### Step 3: Configure connection information

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`.
    - **Branch** is set to `main`.
    - **Connect With** is set to `General`.
    - **Operating System** matches the operating system where you run the application.

4. If you have not set a password yet, click **Generate Password** to generate a random password.

5. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

6. Edit the `.env` file, set up the environment variables as follows, replace the corresponding placeholders `{}` with connection parameters on the connection dialog:

    ```dotenv
    TIDB_HOST={host}
    TIDB_PORT=4000
    TIDB_USER={user}
    TIDB_PASSWORD={password}
    TIDB_DATABASE=test
    TIDB_ENABLE_SSL=true
    ```

    > **Note**
    >
    > For {{{ .starter }}}, TLS connection **MUST** be enabled via `TIDB_ENABLE_SSL` when using public endpoint.

7. Save the `.env` file.

</div>
<div label="TiDB Cloud Dedicated">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list, and then click **CA cert** to download the CA certificate.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidbcloud/configure-ip-access-list) to configure it before your first connection.

    In addition to the **Public** connection type, TiDB Cloud Dedicated supports **Private Endpoint** and **VPC Peering** connection types. For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).

4. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

5. Edit the `.env` file, set up the environment variables as follows, replace the corresponding placeholders `{}` with connection parameters on the connection dialog:

    ```dotenv
    TIDB_HOST={host}
    TIDB_PORT=4000
    TIDB_USER={user}
    TIDB_PASSWORD={password}
    TIDB_DATABASE=test
    TIDB_ENABLE_SSL=true
    TIDB_CA_PATH={downloaded_ssl_ca_path}
    ```

    > **Note**
    >
    > It is recommended to enable TLS connection when using the public endpoint to connect to TiDB Cloud Dedicated.
    >
    > To enable TLS connection, modify `TIDB_ENABLE_SSL` to `true` and using `TIDB_CA_PATH` to specify the file path of CA certificate downloaded from the connection dialog.

6. Save the `.env` file.

</div>
<div label="TiDB Self-Managed">

1. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

2. Edit the `.env` file, set up the environment variables as follows, replace the corresponding placeholders `{}` with connection parameters on the connection dialog:

    ```dotenv
    TIDB_HOST={host}
    TIDB_PORT=4000
    TIDB_USER=root
    TIDB_PASSWORD={password}
    TIDB_DATABASE=test
    ```

   If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `.env` file.

</div>
### Step 4: Run the code and check the result

Run the following command to execute the sample code:

```shell
npm start
```

If the connection is successful, the console will output the version of the TiDB cluster as follows:

```
🔌 Connected to TiDB cluster! (TiDB version: 8.0.11-TiDB-v8.1.2)
⏳ Loading sample game data...
✅ Loaded sample game data.

🆕 Created a new player with ID 12.
ℹ️ Got Player 12: Player { id: 12, coins: 100, goods: 100 }
🔢 Added 50 coins and 50 goods to player 12, updated 1 row.
🚮 Deleted 1 player data.
```
