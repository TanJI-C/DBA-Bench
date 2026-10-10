# Spring Boot sample app prerequisites and connection setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-spring-boot.md`
- Source Title: `Connect to TiDB with Spring Boot`
- Source Heading Path: `Connect to TiDB with Spring Boot | Connect to TiDB with Spring Boot > Prerequisites | Connect to TiDB with Spring Boot > Run the sample app to connect to TiDB | Connect to TiDB with Spring Boot > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with Spring Boot > Run the sample app to connect to TiDB > Step 2: Configure connection information | Connect to TiDB with Spring Boot > Run the sample app to connect to TiDB > Step 3: Run the code and check the result`
- Source Line Ranges: `5-186`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `shared`
- Topic Tags: `spring-boot`, `java`, `hibernate`, `spring-data-jpa`, `prerequisites`, `sample-app`, `git-clone`, `connection-configuration`, `env-vars`, `ssl`, `cloud-connection`, `self-managed-connection`, `run-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0055_41946ce502`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-spring-boot.md#connect-to-tidb-with-spring-boot`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `62c7a31dcf1042d32f323b7f9a45efef62f2b4c752d52406734d6186e631b25e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-spring-boot#connect-to-tidb-with-spring-boot
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-spring-boot.md

## Retrieval Guidance

- Use When: Use this chunk when you need the prerequisites, repository clone commands, deployment-specific env.sh connection setup, or run verification steps for the Spring Boot sample application connecting to TiDB.
- Retrieval Keywords: Connect to TiDB with Spring Boot, Prerequisites, Java Development Kit (JDK) 17, Maven 3.8, Git, git clone https://github.com/tidb-samples/tidb-java-springboot-jpa-quickstart.git, env.sh.example, cp env.sh.example env.sh, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, USE_SSL, TiDB Cloud Dedicated, TiDB Self-Managed, Generate Password, CA cert, Configure IP Access List, make, make request, Expected-Output.txt
- Follow-up Guidance: The next step in the source is to run `make`, then `make request`, and compare the output with `Expected-Output.txt`.
- Classification Note: This chunk is classified as configuration because it provides prerequisite requirements and the exact connection environment variable setup and execution steps for the sample app.

## Official Source Content

# Connect to TiDB with Spring Boot

TiDB is a MySQL-compatible database, and [Spring](https://spring.io/) is a popular open-source container framework for Java. This document uses [Spring Boot](https://spring.io/projects/spring-boot) as the way to use Spring.

In this tutorial, you can learn how to use TiDB along with [Spring Data JPA](https://spring.io/projects/spring-data-jpa) and [Hibernate](https://hibernate.org/orm/) as the JPA provider to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using Hibernate and Spring Data JPA.
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
git clone https://github.com/tidb-samples/tidb-java-springboot-jpa-quickstart.git
cd tidb-java-springboot-jpa-quickstart
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

2. Run the request script in another terminal session:

    ```shell
    make request
    ```

3. Check the [Expected-Output.txt](https://github.com/tidb-samples/tidb-java-springboot-jpa-quickstart/blob/main/Expected-Output.txt) to see if the output matches.
