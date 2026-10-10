# Run WordPress with TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/dev-guide-wordpress.md`
- Source Title: `Connect to TiDB Cloud Serverless with WordPress`
- Source Heading Path: `Connect to TiDB Cloud Serverless with WordPress | Connect to TiDB Cloud Serverless with WordPress > Prerequisites | Connect to TiDB Cloud Serverless with WordPress > Run WordPress with TiDB Cloud Serverless | Connect to TiDB Cloud Serverless with WordPress > Run WordPress with TiDB Cloud Serverless > Step 1: Clone the WordPress sample repository | Connect to TiDB Cloud Serverless with WordPress > Run WordPress with TiDB Cloud Serverless > Step 2: Install dependencies | Connect to TiDB Cloud Serverless with WordPress > Run WordPress with TiDB Cloud Serverless > Step 3: Configure connection information | Connect to TiDB Cloud Serverless with WordPress > Run WordPress with TiDB Cloud Serverless > Step 4: Start WordPress with TiDB Cloud Serverless | Connect to TiDB Cloud Serverless with WordPress > Run WordPress with TiDB Cloud Serverless > Step 5: Confirm the database connection | Connect to TiDB Cloud Serverless with WordPress > Need help?`
- Source Line Ranges: `5-108`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `wordpress`, `serverless`, `prerequisites`, `docker`, `docker-compose`, `repository-clone`, `submodule`, `connection-string`, `environment-variables`, `password-generation`, `public-connection`, `sql-editor`, `verification`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0232_f53b9fdbcc`
- Source ID: `tidb-docs-8.1:tidb-cloud/dev-guide-wordpress.md#connect-to-tidb-cloud-serverless-with-wordpress`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c344fbb13aed9a68f47ce44907419bb5b304d915510e6b7493996c3c656b7a70`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/dev-guide-wordpress#connect-to-tidb-cloud-serverless-with-wordpress
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/dev-guide-wordpress.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about connecting or running WordPress with TiDB Cloud Serverless, including prerequisites, Docker setup, connection dialog settings, .env configuration, and verifying WordPress tables in SQL Editor.
- Retrieval Keywords: Connect to TiDB Cloud Serverless with WordPress, Run WordPress with TiDB Cloud Serverless, TiDB Cloud Serverless, WordPress, Docker, Docker Compose, git clone https://github.com/Icemap/wordpress-tidb-docker.git, git submodule update --init --recursive, Connection Type Public, Connect With WordPress, Operating System Debian/Ubuntu/Arch, Generate Password, Reset Password, .env.example, .env, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, docker compose up -d, SQL Editor, Schemas, wp_posts, wp_comments, localhost
- Follow-up Guidance: If more help is needed, the source points to Discord, Slack, or submitting a support ticket.
- Classification Note: This is classified as configuration because the content centers on setting connection parameters, environment variables, and container startup settings for WordPress to use TiDB Cloud Serverless.

## Official Source Content

# Connect to TiDB Cloud Serverless with WordPress

TiDB is a MySQL-compatible database, TiDB Cloud Serverless is a fully managed TiDB offering, and [WordPress](https://github.com/WordPress) is a free, open-source content management system (CMS) that lets users create and manage websites. WordPress is written in PHP and uses a MySQL database.

In this tutorial, you can learn how to use TiDB Cloud Serverless to run WordPress for free.

> **Note:**
>
> In addition to TiDB Cloud Serverless, this tutorial works with TiDB Cloud Dedicated and TiDB Self-Managed clusters as well. However, it is highly recommended to run WordPress with TiDB Cloud Serverless for cost efficiency.
## Prerequisites

To complete this tutorial, you need:

- A TiDB Cloud Serverless cluster. Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create your own TiDB Cloud cluster if you don't have one.
## Run WordPress with TiDB Cloud Serverless

This section demonstrates how to run WordPress with TiDB Cloud Serverless.
### Step 1: Clone the WordPress sample repository

Run the following commands in your terminal window to clone the sample code repository:

```shell
git clone https://github.com/Icemap/wordpress-tidb-docker.git
cd wordpress-tidb-docker
```
### Step 2: Install dependencies

1. The sample repository requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to start WordPress. If you have them installed, you can skip this step. It is highly recommended to run your WordPress in a Linux environment (such as Ubuntu). Run the following command to install Docker and Docker Compose:

    ```shell
    sudo sh install.sh
    ```

2. The sample repository includes the [TiDB Compatibility Plugin](https://github.com/pingcap/wordpress-tidb-plugin) as a submodule. Run the following command to update the submodule:

    ```shell
    git submodule update --init --recursive
    ```
### Step 3: Configure connection information

Configure the WordPress database connection to TiDB Cloud Serverless.

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`.
    - **Connect With** is set to `WordPress`.
    - **Operating System** is set to `Debian/Ubuntu/Arch`.
    - **Database** is set to the database you want to use—for example, `test`.

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
    TIDB_HOST='{HOST}'  # e.g. gateway01.ap-northeast-1.prod.aws.tidbcloud.com
    TIDB_PORT='4000'
    TIDB_USER='{USERNAME}'  # e.g. xxxxxx.root
    TIDB_PASSWORD='{PASSWORD}'
    TIDB_DB_NAME='test'
    ```

    Be sure to replace the placeholders `{}` with the connection parameters obtained from the connection dialog. By default, your TiDB Cloud Serverless comes with a `test` database. If you have already created another database in your TiDB Cloud Serverless cluster, you can replace `test` with your database name.

7. Save the `.env` file.
### Step 4: Start WordPress with TiDB Cloud Serverless

1. Execute the following command to run WordPress as a Docker container:

    ```shell
    docker compose up -d
    ```

2. Set up your WordPress site by visiting [localhost](http://localhost/) if you start the container on your local machine or `http://<your_instance_ip>` if the WordPress is running on a remote machine.
### Step 5: Confirm the database connection

1. Close the connection dialog for your cluster on the TiDB Cloud console, and open the **SQL Editor** page.
2. Under the **Schemas** tab on the left, click the database you connected to Wordpress.
3. Confirm that you now see the Wordpress tables (such as `wp_posts` and `wp_comments`) in the list of tables for that database.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
