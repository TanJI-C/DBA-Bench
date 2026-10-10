# mysql2 sample app setup and connection workflow

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-ruby-mysql2.md`
- Source Title: `Connect to TiDB with mysql2`
- Source Heading Path: `Connect to TiDB with mysql2 | Connect to TiDB with mysql2 > Prerequisites | Connect to TiDB with mysql2 > Run the sample app to connect to TiDB | Connect to TiDB with mysql2 > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with mysql2 > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with mysql2 > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with mysql2 > Run the sample app to connect to TiDB > Step 4: Run the code and check the result`
- Source Line Ranges: `5-204`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `shared`
- Topic Tags: `ruby`, `mysql2`, `prerequisites`, `sample-app`, `repository-clone`, `dependency-installation`, `environment-variables`, `connection-configuration`, `tls`, `ca-certificate`, `ip-access-list`, `public-endpoint`, `self-managed`, `cloud-dedicated`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0061_26fd434c00`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-ruby-mysql2.md#connect-to-tidb-with-mysql2`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `27f587b49c2cc5506e2971559ca1a6d6c5753fc4db59747063399188c73cc1a0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-ruby-mysql2#connect-to-tidb-with-mysql2
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-ruby-mysql2.md

## Retrieval Guidance

- Use When: Use this chunk when you need the mysql2 Ruby sample app setup flow, including prerequisites, repository clone, dependency installation, .env configuration, deployment-specific connection settings, and the expected successful connection output.
- Retrieval Keywords: Connect to TiDB with mysql2, Prerequisites, git clone https://github.com/tidb-samples/tidb-ruby-mysql2-quickstart.git, bundle install, bundle add mysql2 dotenv, cp .env.example .env, DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME, DATABASE_ENABLE_SSL, DATABASE_SSL_CA, Public, Branch main, Connect With General, CA cert, Configure IP Access List, TiDB Cloud Dedicated, TiDB Self-Managed, ruby app.rb, Connected to TiDB cluster
- Follow-up Guidance: The sample code snippets section provides the mysql2 connection options code and CRUD examples referenced by this setup tutorial.
- Classification Note: This is classified as configuration because the content is primarily a step-by-step setup and connection guide using environment variables, deployment-specific connection parameters, and commands to run the sample application.

## Official Source Content

# Connect to TiDB with mysql2

TiDB is a MySQL-compatible database, and [mysql2](https://github.com/brianmario/mysql2) is one of the most popular MySQL drivers for Ruby.

In this tutorial, you can learn how to use TiDB and mysql2 to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using mysql2.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.

> **Note:**
>
> This tutorial works with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [Ruby](https://www.ruby-lang.org/en/) >= 3.0 installed on your machine
- [Bundler](https://bundler.io/) installed on your machine
- [Git](https://git-scm.com/downloads) installed on your machine
- A TiDB cluster running

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
git clone https://github.com/tidb-samples/tidb-ruby-mysql2-quickstart.git
cd tidb-ruby-mysql2-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including `mysql2` and `dotenv`) for the sample app:

```shell
bundle install
```

<details>
<summary><b>Install dependencies for existing projects</b></summary>

For your existing project, run the following command to install the packages:

```shell
bundle add mysql2 dotenv
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

6. Edit the `.env` file, set up the environment variables as follows, and replace the corresponding placeholders `{}` with connection parameters in the connection dialog:

    ```dotenv
    DATABASE_HOST={host}
    DATABASE_PORT=4000
    DATABASE_USER={user}
    DATABASE_PASSWORD={password}
    DATABASE_NAME=test
    DATABASE_ENABLE_SSL=true
    ```

   > **Note**
   >
   > For [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential), TLS connection **MUST** be enabled via `DATABASE_ENABLE_SSL` when using public endpoint.

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

5. Edit the `.env` file, set up the environment variables as follows, and replace the corresponding placeholders `{}` with connection parameters in the connection dialog:

    ```dotenv
    DATABASE_HOST={host}
    DATABASE_PORT=4000
    DATABASE_USER={user}
    DATABASE_PASSWORD={password}
    DATABASE_NAME=test
    DATABASE_ENABLE_SSL=true
    DATABASE_SSL_CA={downloaded_ssl_ca_path}
    ```

   > **Note**
   >
   > It is recommended to enable TLS connection when using the public endpoint to connect to a TiDB Cloud Dedicated cluster.
   >
   > To enable TLS connection, modify `DATABASE_ENABLE_SSL` to `true` and use `DATABASE_SSL_CA` to specify the file path of CA certificate downloaded from the connection dialog.

6. Save the `.env` file.

</div>
<div label="TiDB Self-Managed">

1. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

2. Edit the `.env` file, set up the environment variables as follows, and replace the corresponding placeholders `{}` with your own TiDB connection information:

    ```dotenv
    DATABASE_HOST={host}
    DATABASE_PORT=4000
    DATABASE_USER={user}
    DATABASE_PASSWORD={password}
    DATABASE_NAME=test
    ```

   If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `.env` file.

</div>
### Step 4: Run the code and check the result

Run the following command to execute the sample code:

```shell
ruby app.rb
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
