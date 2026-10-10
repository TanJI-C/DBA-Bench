# Run sample app and configure TiDB connection

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-golang-gorm.md`
- Source Title: `Connect to TiDB with GORM`
- Source Heading Path: `Connect to TiDB with GORM > Run the sample app to connect to TiDB | Connect to TiDB with GORM > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with GORM > Run the sample app to connect to TiDB > Step 2: Configure connection information | Connect to TiDB with GORM > Run the sample app to connect to TiDB > Step 3: Run the code and check the result`
- Source Line Ranges: `45-179`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `sample-app`, `repository-clone`, `connection-configuration`, `env-file`, `ssl`, `password`, `ip-access-list`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0053_cdf27ef524`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-golang-gorm.md#run-the-sample-app-to-connect-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84987cf1a119860c1d4f678102e0056a58cef83ba9d6933c3b777f16fb308cf0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-gorm#run-the-sample-app-to-connect-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-golang-gorm.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the exact steps to clone the tidb-golang-gorm-quickstart repository, fill in the .env connection settings, and run the sample app against different TiDB deployment options.
- Retrieval Keywords: Run the sample app to connect to TiDB, tidb-golang-gorm-quickstart, git clone https://github.com/tidb-samples/tidb-golang-gorm-quickstart.git, cp .env.example .env, .env, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, USE_SSL, Connect, Generate Password, Reset Password, Connection Type Public, Branch main, Connect With General, CA cert, Configure IP Access List, make, Expected-Output.txt, 127.0.0.1
- Follow-up Guidance: After configuration, the chunk says to run make and compare the program output with Expected-Output.txt.
- Classification Note: This is classified as configuration content because it focuses on setting connection parameters in .env and selecting connection dialog options for TiDB Cloud and TiDB Self-Managed.

## Official Source Content

## Run the sample app to connect to TiDB

This section demonstrates how to run the sample application code and connect to TiDB.
### Step 1: Clone the sample app repository

Run the following commands in your terminal window to clone the sample code repository:

```shell
git clone https://github.com/tidb-samples/tidb-golang-gorm-quickstart.git
cd tidb-golang-gorm-quickstart
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

2. Check the [Expected-Output.txt](https://github.com/tidb-samples/tidb-golang-gorm-quickstart/blob/main/Expected-Output.txt) to see if the output matches.
