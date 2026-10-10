# Python MySQL Connector quickstart setup and sample app run

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-python-mysql-connector.md`
- Source Title: `Connect to TiDB with MySQL Connector/Python`
- Source Heading Path: `Connect to TiDB with MySQL Connector/Python | Connect to TiDB with MySQL Connector/Python > Prerequisites | Connect to TiDB with MySQL Connector/Python > Run the sample app to connect to TiDB | Connect to TiDB with MySQL Connector/Python > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with MySQL Connector/Python > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with MySQL Connector/Python > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with MySQL Connector/Python > Run the sample app to connect to TiDB > Step 4: Run the code and check the result`
- Source Line Ranges: `5-184`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `python`, `mysql-connector-python`, `prerequisites`, `sample-app`, `git`, `dependencies`, `connection-configuration`, `env-file`, `tls`, `cloud-connectivity`, `self-managed`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0059_05091bbbfa`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-python-mysql-connector.md#connect-to-tidb-with-mysql-connector-python`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c074509415cdace601104df836984dd0da0a52c5a3e4bf06168da713b34b6e69`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-mysql-connector#connect-to-tidb-with-mysql-connector-python
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-python-mysql-connector.md

## Retrieval Guidance

- Use When: Use this chunk when you need the MySQL Connector/Python quickstart steps to clone the sample repository, install dependencies, configure a `.env` file, and run the sample app against a TiDB cluster.
- Retrieval Keywords: MySQL Connector/Python, mysql-connector-python, tidb-python-mysqlconnector-quickstart, git clone https://github.com/tidb-samples/tidb-python-mysqlconnector-quickstart.git, pip install -r requirements.txt, cp .env.example .env, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, CA_PATH, python mysql_connector_example.py, Expected-Output.txt, TiDB Cloud Dedicated, TiDB Self-Managed, Connection Type Public, Branch main, Connect With General
- Follow-up Guidance: The source also points to the `Expected-Output.txt` file to verify whether the sample app output matches the expected result.
- Classification Note: This is classified as configuration because the content is primarily about prerequisites, environment setup, connection parameters in `.env`, and running the sample application.

## Official Source Content

# Connect to TiDB with MySQL Connector/Python

TiDB is a MySQL-compatible database, and [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/) is the official MySQL driver for Python.

In this tutorial, you can learn how to use TiDB and MySQL Connector/Python to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using MySQL Connector/Python.
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
## Run the sample app to connect to TiDB

This section demonstrates how to run the sample application code and connect to TiDB.
### Step 1: Clone the sample app repository

Run the following commands in your terminal window to clone the sample code repository:

```shell
git clone https://github.com/tidb-samples/tidb-python-mysqlconnector-quickstart.git
cd tidb-python-mysqlconnector-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including mysql-connector-python) for the sample app:

```shell
pip install -r requirements.txt
```
### Step 3: Configure connection information

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
    CA_PATH='{ssl_ca}'  # e.g. /etc/ssl/certs/ca-certificates.crt (Debian / Ubuntu / Arch)
    ```

    Be sure to replace the placeholders `{}` with the connection parameters obtained from the connection dialog.

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
    CA_PATH='{your-downloaded-ca-path}'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters obtained from the connection dialog, and configure `CA_PATH` with the certificate path downloaded in the previous step.

6. Save the `.env` file.

</div>
<div label="TiDB Self-Managed">

1. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

2. Copy and paste the corresponding connection string into the `.env` file. The example result is as follows:

    ```dotenv
    TIDB_HOST='{tidb_server_host}'
    TIDB_PORT='4000'
    TIDB_USER='root'
    TIDB_PASSWORD='{password}'
    TIDB_DB_NAME='test'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters, and remove the `CA_PATH` line. If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `.env` file.

</div>
### Step 4: Run the code and check the result

1. Execute the following command to run the sample code:

    ```shell
    python mysql_connector_example.py
    ```

2. Check the [Expected-Output.txt](https://github.com/tidb-samples/tidb-python-mysqlconnector-quickstart/blob/main/Expected-Output.txt) to see if the output matches.
