# run the peewee sample app and configure connection

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-python-peewee.md`
- Source Title: `Connect to TiDB with peewee`
- Source Heading Path: `Connect to TiDB with peewee > Run the sample app to connect to TiDB | Connect to TiDB with peewee > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with peewee > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with peewee > Run the sample app to connect to TiDB > Step 2: Install dependencies > Why use PyMySQL? | Connect to TiDB with peewee > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with peewee > Run the sample app to connect to TiDB > Step 4: Run the code and check the result`
- Source Line Ranges: `45-188`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `sample-app`, `git-clone`, `dependencies`, `pymysql`, `connection-string`, `env-file`, `tls`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0074_6d4f034962`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-python-peewee.md#run-the-sample-app-to-connect-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a9f83a84c9f0baf5d05126315a1700449a500799c70062784ff97b8ab5b675b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-peewee#run-the-sample-app-to-connect-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-python-peewee.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact steps to clone the peewee sample app, install dependencies, configure the .env connection settings, and run the example against a TiDB cluster.
- Retrieval Keywords: Run the sample app to connect to TiDB, git clone https://github.com/tidb-samples/tidb-python-peewee-quickstart.git, pip install -r requirements.txt, PyMySQL, Why use PyMySQL, cp .env.example .env, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, CA_PATH, Connection Type Public, Branch main, Connect With General, CA cert, Configure IP Access List, python peewee_example.py, Expected-Output.txt
- Follow-up Guidance: The chunk continues with exact .env examples for Starter or Essential, TiDB Cloud Dedicated, and TiDB Self-Managed, then shows running python peewee_example.py and checking Expected-Output.txt.
- Classification Note: This is operational content because it provides ordered execution steps, commands, and environment configuration details for running the sample application.

## Official Source Content

## Run the sample app to connect to TiDB

This section demonstrates how to run the sample application code and connect to TiDB.
### Step 1: Clone the sample app repository

Run the following commands in your terminal window to clone the sample code repository:

```shell
git clone https://github.com/tidb-samples/tidb-python-peewee-quickstart.git
cd tidb-python-peewee-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including peewee and PyMySQL) for the sample app:

```shell
pip install -r requirements.txt
```
#### Why use PyMySQL?

peewee is an ORM library that works with multiple databases. It provides a high-level abstraction of the database, which helps developers write SQL statements in a more object-oriented way. However, peewee does not include a database driver. To connect to a database, you need to install a database driver. This sample application uses PyMySQL as the database driver, which is a pure Python MySQL client library that is compatible with TiDB and can be installed on all platforms. For more information, refer to [peewee official documentation](https://docs.peewee-orm.com/en/latest/peewee/database.html?highlight=mysql#using-mysql).
### Step 3: Configure connection information

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://{{{.console-url}}}/project/clusters) page, and then click the name of your target cluster to go to its overview page.

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
    python peewee_example.py
    ```

2. Check the [Expected-Output.txt](https://github.com/tidb-samples/tidb-python-peewee-quickstart/blob/main/Expected-Output.txt) to see if the output matches.
