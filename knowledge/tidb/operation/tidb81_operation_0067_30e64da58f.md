# Prerequisites and run the MyBatis sample app

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-mybatis.md`
- Source Title: `Connect to TiDB with MyBatis`
- Source Heading Path: `Connect to TiDB with MyBatis | Connect to TiDB with MyBatis > Prerequisites | Connect to TiDB with MyBatis > Run the sample app to connect to TiDB | Connect to TiDB with MyBatis > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with MyBatis > Run the sample app to connect to TiDB > Step 2: Configure connection information | Connect to TiDB with MyBatis > Run the sample app to connect to TiDB > Step 3: Run the code and check the result`
- Source Line Ranges: `5-180`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `java`, `mybatis`, `prerequisites`, `sample-app`, `git`, `maven`, `connection-configuration`, `ssl`, `cloud-connectivity`, `self-managed`, `runbook`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0067_30e64da58f`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-mybatis.md#connect-to-tidb-with-mybatis`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `322b6e0b37d740a4ba2727089d0bc2e50e16ef7de35e859005f7e30ed4846f5f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-mybatis#connect-to-tidb-with-mybatis
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-mybatis.md

## Retrieval Guidance

- Use When: Use this chunk when you need the prerequisites, repository clone commands, env.sh connection settings, and run steps for the TiDB Java MyBatis sample application across TiDB Cloud and TiDB Self-Managed.
- Retrieval Keywords: Connect to TiDB with MyBatis, Prerequisites, Java Development Kit (JDK) 17, Maven 3.8, Git, TiDB cluster, git clone https://github.com/tidb-samples/tidb-java-mybatis-quickstart.git, cp env.sh.example env.sh, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, USE_SSL, Connection Type Public, Branch main, Connect With General, CA cert, Configure IP Access List, make, Expected-Output.txt
- Follow-up Guidance: The chunk continues with environment-specific connection dialog settings and example env.sh values for {{{ .starter }}} or Essential, TiDB Cloud Dedicated, and TiDB Self-Managed, then shows running the sample with `make` and checking `Expected-Output.txt`.
- Classification Note: This is classified as operation because the content is a step-by-step runbook for preparing the environment, configuring connectivity, and executing the sample app.

## Official Source Content

# Connect to TiDB with MyBatis

TiDB is a MySQL-compatible database, and [MyBatis](https://mybatis.org/mybatis-3/index.html) is a popular open-source Java ORM.

In this tutorial, you can learn how to use TiDB and MyBatis to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using MyBatis.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.

> **Note:**
>
> This tutorial works with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- **Java Development Kit (JDK) 17** or higher. You can choose [OpenJDK](https://openjdk.org/) or [Oracle JDK](https://www.oracle.com/hk/java/technologies/downloads/) based on your business and personal requirements.
- [Maven](https://maven.apache.org/install.html) **3.8** or higher.
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
git clone https://github.com/tidb-samples/tidb-java-mybatis-quickstart.git
cd tidb-java-mybatis-quickstart
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

5. Run the following command to copy `env.sh.example` and rename it to `env.sh`:

    ```shell
    cp env.sh.example env.sh
    ```

6. Copy and paste the corresponding connection string into the `env.sh` file. The example result is as follows:

    ```shell
    export TIDB_HOST='{host}'  # e.g. gateway01.ap-northeast-1.prod.aws.tidbcloud.com
    export TIDB_PORT='4000'
    export TIDB_USER='{user}'  # e.g. xxxxxx.root
    export TIDB_PASSWORD='{password}'
    export TIDB_DB_NAME='test'
    export USE_SSL='true'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters obtained from the connection dialog.

    {{{ .starter }}} requires a secure connection. Therefore, you need to set the value of `USE_SSL` to `true`.

7. Save the `env.sh` file.

</div>
<div label="TiDB Cloud Dedicated">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list, and then click **CA cert** to download the CA certificate.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidbcloud/configure-ip-access-list) to configure it before your first connection.

    In addition to the **Public** connection type, TiDB Cloud Dedicated supports **Private Endpoint** and **VPC Peering** connection types. For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).

4. Run the following command to copy `env.sh.example` and rename it to `env.sh`:

    ```shell
    cp env.sh.example env.sh
    ```

5. Copy and paste the corresponding connection string into the `env.sh` file. The example result is as follows:

    ```shell
    export TIDB_HOST='{host}'  # e.g. tidb.xxxx.clusters.tidb-cloud.com
    export TIDB_PORT='4000'
    export TIDB_USER='{user}'  # e.g. root
    export TIDB_PASSWORD='{password}'
    export TIDB_DB_NAME='test'
    export USE_SSL='false'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters obtained from the connection dialog.

6. Save the `env.sh` file.

</div>
<div label="TiDB Self-Managed">

1. Run the following command to copy `env.sh.example` and rename it to `env.sh`:

    ```shell
    cp env.sh.example env.sh
    ```

2. Copy and paste the corresponding connection string into the `env.sh` file. The example result is as follows:

    ```shell
    export TIDB_HOST='{host}'
    export TIDB_PORT='4000'
    export TIDB_USER='root'
    export TIDB_PASSWORD='{password}'
    export TIDB_DB_NAME='test'
    export USE_SSL='false'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters, and set `USE_SSL` to `false`. If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `env.sh` file.

</div>
### Step 3: Run the code and check the result

1. Execute the following command to run the sample code:

    ```shell
    make
    ```

2. Check the [Expected-Output.txt](https://github.com/tidb-samples/tidb-java-mybatis-quickstart/blob/main/Expected-Output.txt) to see if the output matches.
