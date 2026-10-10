# Django sample app setup and connection workflow

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-python-django.md`
- Source Title: `Connect to TiDB with Django`
- Source Heading Path: `Connect to TiDB with Django | Connect to TiDB with Django > Prerequisites | Connect to TiDB with Django > Run the sample app to connect to TiDB | Connect to TiDB with Django > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with Django > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with Django > Run the sample app to connect to TiDB > Step 2: Install dependencies > What is `django-tidb`? | Connect to TiDB with Django > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with Django > Run the sample app to connect to TiDB > Step 4: Initialize the database | Connect to TiDB with Django > Run the sample app to connect to TiDB > Step 5: Run the sample application`
- Source Line Ranges: `5-217`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `tiup`
- Topic Tags: `django`, `python`, `prerequisites`, `sample-app`, `repository-clone`, `dependency-installation`, `django-tidb`, `connection-configuration`, `environment-variables`, `tls`, `ca-certificate`, `ip-access-list`, `database-initialization`, `migration`, `runserver`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0058_a2e5edcc1b`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-python-django.md#connect-to-tidb-with-django`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `11a02aaefeb0adfdbf43a30284e5f2c91ba2ec09866004bef60e8b1439398a9f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-django#connect-to-tidb-with-django
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-python-django.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official Django quickstart workflow for connecting a sample app to TiDB, including prerequisites, repository cloning, dependency installation, .env connection setup, migrate, and runserver steps.
- Retrieval Keywords: Connect to TiDB with Django, tidb-python-django-quickstart, git clone https://github.com/tidb-samples/tidb-python-django-quickstart.git, pip install -r requirements.txt, django-tidb, mysqlclient, cp .env.example .env, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, CA_PATH, python manage.py migrate, python manage.py runserver, Configure IP Access List, CA cert, Public, Branch main, Connect With General
- Follow-up Guidance: It also shows deployment-specific connection details for Starter or Essential, TiDB Cloud Dedicated, and TiDB Self-Managed, including CA certificate and IP access list context where provided.
- Classification Note: This is classified as configuration because the content mainly describes environment prerequisites, package installation, connection variables, TLS-related settings in .env, and the startup workflow for the sample application.

## Official Source Content

# Connect to TiDB with Django

TiDB is a MySQL-compatible database, and [Django](https://www.djangoproject.com) is a popular web framework for Python, which includes a powerful Object Relational Mapper (ORM) library.

In this tutorial, you can learn how to use TiDB and Django to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using Django.
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
git clone https://github.com/tidb-samples/tidb-python-django-quickstart.git
cd tidb-python-django-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including Django, django-tidb, and mysqlclient) for the sample app:

```shell
pip install -r requirements.txt
```

If you encounter installation issues with mysqlclient, refer to the [mysqlclient official documentation](https://github.com/PyMySQL/mysqlclient#install).
#### What is `django-tidb`?

`django-tidb` is a TiDB dialect for Django that resolves compatibility issues between TiDB and Django.

To install `django-tidb`, choose a version that matches your Django version. For example, if you are using `django==4.2.*`, install `django-tidb==4.2.*`. The minor version does not need to be the same. It is recommended to use the latest minor version.

For more information, refer to [django-tidb repository](https://github.com/pingcap/django-tidb).
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

    {{{ .starter }}} requires a secure connection. Since the `ssl_mode` of mysqlclient defaults to `PREFERRED`, you don't need to manually specify `CA_PATH`. Just leave it empty. But if you have a special reason to specify `CA_PATH` manually, you can refer to the [TLS connections to {{{ .starter }}}](https://docs.pingcap.com/tidbcloud/secure-connections-to-serverless-clusters) to get the certificate paths for different operating systems.

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
### Step 4: Initialize the database

In the root directory of the project, run the following command to initialize the database:

```shell
python manage.py migrate
```
### Step 5: Run the sample application

1. Run the application in the development mode:

    ```shell
    python manage.py runserver
    ```

    The application runs on port `8000` by default. To use a different port, you can append the port number to the command. The following is an example:

    ```shell
    python manage.py runserver 8080
    ```

2. To access the application, open your browser and go to `http://localhost:8000/`. In the sample application, you can:

    - Create a new player.
    - Bulk create players.
    - View all players.
    - Update a player.
    - Delete a player.
    - Trade goods between two players.
