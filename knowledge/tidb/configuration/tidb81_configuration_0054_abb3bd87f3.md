# Go-MySQL-Driver quickstart prerequisites and sample app setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-golang-sql-driver.md`
- Source Title: `Connect to TiDB with Go-MySQL-Driver`
- Source Heading Path: `Connect to TiDB with Go-MySQL-Driver | Connect to TiDB with Go-MySQL-Driver > Prerequisites | Connect to TiDB with Go-MySQL-Driver > Run the sample app to connect to TiDB | Connect to TiDB with Go-MySQL-Driver > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with Go-MySQL-Driver > Run the sample app to connect to TiDB > Step 2: Configure connection information | Connect to TiDB with Go-MySQL-Driver > Run the sample app to connect to TiDB > Step 3: Run the code and check the result`
- Source Line Ranges: `5-179`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `golang`, `mysql-driver`, `prerequisites`, `sample-app`, `repository-clone`, `connection-configuration`, `cloud-connection`, `self-managed-connection`, `environment-file`, `ssl`, `run-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0054_abb3bd87f3`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-golang-sql-driver.md#connect-to-tidb-with-go-mysql-driver`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e8ab6e39c4de873fb329ad9b0f29a3afb53641c59dba73661a169ea95072a980`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-sql-driver#connect-to-tidb-with-go-mysql-driver
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-golang-sql-driver.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the Go-MySQL-Driver quickstart prerequisites, sample repository clone commands, or deployment-specific `.env` connection settings to run the sample app against TiDB.
- Retrieval Keywords: Go-MySQL-Driver, database/sql, Go 1.20 or higher, Git, TiDB cluster, git clone https://github.com/tidb-samples/tidb-golang-sql-driver-quickstart.git, cp .env.example .env, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, USE_SSL, make, Expected-Output.txt, TiDB Cloud Dedicated, TiDB Self-Managed, Connect dialog, Connection Type Public, Branch main, Connect With General, CA cert, Configure IP Access List, 127.0.0.1
- Follow-up Guidance: The source then shows running `make` and checking `Expected-Output.txt` to verify the sample output, and later provides sample code snippets for CRUD operations.
- Classification Note: This is classified as configuration because the content is primarily about prerequisites, cloning the sample repository, and filling `.env` connection parameters such as `TIDB_HOST`, `TIDB_PORT`, and `USE_SSL` for different TiDB deployment options.

## Official Source Content

# Connect to TiDB with Go-MySQL-Driver

TiDB is a MySQL-compatible database, and [Go-MySQL-Driver](https://github.com/go-sql-driver/mysql) is a MySQL implementation for the [database/sql](https://pkg.go.dev/database/sql) interface.

In this tutorial, you can learn how to use TiDB and Go-MySQL-Driver to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using Go-MySQL-Driver.
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
## Run the sample app to connect to TiDB

This section demonstrates how to run the sample application code and connect to TiDB.
### Step 1: Clone the sample app repository

Run the following commands in your terminal window to clone the sample code repository:

```shell
git clone https://github.com/tidb-samples/tidb-golang-sql-driver-quickstart.git
cd tidb-golang-sql-driver-quickstart
```
### Step 2: Configure connection information

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`
    - **Branch** is set to `main`
    - **Connect With** is set to `General`
    - **Operating System** matches your environment.

    > **Tip:**
    >
    > If your program is running in Windows Subsystem for Linux (WSL), switch to the corresponding Linux distribution.

4. Click **Generate Password** to create a random password.

    > **Tip:**
    > 
    > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

5. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

6. Copy and paste the corresponding connection string into the `.env` file. The example result is as follows:

    ```dotenv
    TIDB_HOST='{host}'  # e.g. gateway01.ap-northeast-1.prod.aws.tidbcloud.com
    TIDB_PORT='4000'
    TIDB_USER='{user}'  # e.g. xxxxxx.root
    TIDB_PASSWORD='{password}'
    TIDB_DB_NAME='test'
    USE_SSL='true'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters obtained from the connection dialog.

    {{{ .starter }}} requires a secure connection. Therefore, you need to set the value of `USE_SSL` to `true`.

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

5. Copy and paste the corresponding connection string into the `.env` file. The example result is as follows:

    ```dotenv
    TIDB_HOST='{host}'  # e.g. tidb.xxxx.clusters.tidb-cloud.com
    TIDB_PORT='4000'
    TIDB_USER='{user}'  # e.g. root
    TIDB_PASSWORD='{password}'
    TIDB_DB_NAME='test'
    USE_SSL='false'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters obtained from the connection dialog.

6. Save the `.env` file.

</div>
<div label="TiDB Self-Managed">

1. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

2. Copy and paste the corresponding connection string into the `.env` file. The example result is as follows:

    ```dotenv
    TIDB_HOST='{host}'
    TIDB_PORT='4000'
    TIDB_USER='root'
    TIDB_PASSWORD='{password}'
    TIDB_DB_NAME='test'
    USE_SSL='false'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters, and set `USE_SSL` to `false`. If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `.env` file.

</div>
### Step 3: Run the code and check the result

1. Execute the following command to run the sample code:

    ```shell
    make
    ```

2. Check the [Expected-Output.txt](https://github.com/tidb-samples/tidb-golang-sql-driver-quickstart/blob/main/Expected-Output.txt) to see if the output matches.
