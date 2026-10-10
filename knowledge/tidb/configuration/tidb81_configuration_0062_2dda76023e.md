# Rails quickstart setup and connection workflow

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-ruby-rails.md`
- Source Title: `Connect to TiDB with Rails framework and ActiveRecord ORM`
- Source Heading Path: `Connect to TiDB with Rails Framework and ActiveRecord ORM | Connect to TiDB with Rails Framework and ActiveRecord ORM > Prerequisites | Connect to TiDB with Rails Framework and ActiveRecord ORM > Run the sample app to connect to TiDB | Connect to TiDB with Rails Framework and ActiveRecord ORM > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with Rails Framework and ActiveRecord ORM > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with Rails Framework and ActiveRecord ORM > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with Rails Framework and ActiveRecord ORM > Run the sample app to connect to TiDB > Step 4: Run the code and check the result`
- Source Line Ranges: `5-197`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `shared`
- Topic Tags: `rails`, `activerecord`, `ruby`, `prerequisites`, `sample-app`, `repository`, `dependencies`, `dotenv`, `database-url`, `tls`, `public-endpoint`, `ca-certificate`, `ip-access-list`, `migration`, `seed`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0062_2dda76023e`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-ruby-rails.md#connect-to-tidb-with-rails-framework-and-activerecord-orm`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bc5fa3cb34de83557a4153f6fef652d57f84dbf168b7946671cddf9811cdb75f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-ruby-rails#connect-to-tidb-with-rails-framework-and-activerecord-orm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-ruby-rails.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Rails quickstart workflow to clone the sample repository, install dependencies, configure DATABASE_URL for a TiDB cluster, and run migrations, seed data, and verification commands.
- Retrieval Keywords: tidb-ruby-rails-quickstart, git clone https://github.com/tidb-samples/tidb-ruby-rails-quickstart.git, bundle install, bundle add mysql2 dotenv, cp .env.example .env, DATABASE_URL, mysql2://{user}:{password}@{host}:{port}/{database_name}?ssl_mode=verify_identity, mysql2://{user}:{password}@{host}:{port}/{database}?ssl_mode=verify_identity&sslca=/path/to/ca.pem, mysql2://{user}:{password}@{host}:{port}/{database}, Rails, ActiveRecord ORM, Public, CA cert, Configure IP Access List, Private Endpoint, VPC Peering, bundle exec rails db:create, bundle exec rails db:migrate, bundle exec rails db:seed, bundle exec rails runner ./quickstart.rb, Connected to TiDB cluster
- Follow-up Guidance: The source also provides sample code snippets for ActiveRecord connection settings and basic CRUD operations.
- Classification Note: This chunk is classified as configuration because the official content focuses on prerequisites, connection string setup, TLS-related DATABASE_URL parameters, and the step-by-step commands to run the Rails sample app.

## Official Source Content

# Connect to TiDB with Rails Framework and ActiveRecord ORM

TiDB is a MySQL-compatible database, [Rails](https://github.com/rails/rails) is a popular web application framework written in Ruby, and [ActiveRecord ORM](https://github.com/rails/rails/tree/main/activerecord) is the object-relational mapping in Rails.

In this tutorial, you can learn how to use TiDB and Rails to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using Rails.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations using ActiveRecord ORM.

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
git clone https://github.com/tidb-samples/tidb-ruby-rails-quickstart.git
cd tidb-ruby-rails-quickstart
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

3. In the connection dialog, select `Rails` from the **Connect With** drop-down list and keep the default setting of the **Connection Type** as `Public`.

4. If you have not set a password yet, click **Generate Password** to generate a random password.

5. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

6. Edit the `.env` file, set up the `DATABASE_URL` environment variable as follows, and copy the connection string from the connection dialog as the variable value.

    ```dotenv
    DATABASE_URL='mysql2://{user}:{password}@{host}:{port}/{database_name}?ssl_mode=verify_identity'
    ```

   > **Note**
   >
   > For [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential), TLS connection **MUST** be enabled with the `ssl_mode=verify_identity` query parameter when using public endpoint.

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

5. Edit the `.env` file, set up the `DATABASE_URL` environment variable as follows, copy the connection string from the connection dialog as the variable value, and set the `sslca` query parameter to the file path of the CA certificate downloaded from the connection dialog:

    ```dotenv
    DATABASE_URL='mysql2://{user}:{password}@{host}:{port}/{database}?ssl_mode=verify_identity&sslca=/path/to/ca.pem'
    ```

   > **Note**
   >
   > It is recommended to enable TLS connection when using the public endpoint to connect to TiDB Cloud Dedicated.
   >
   > To enable TLS connection, modify the value of the `ssl_mode` query parameter to `verify_identity` and the value of  `sslca` to the file path of CA certificate downloaded from the connection dialog.

6. Save the `.env` file.

</div>
<div label="TiDB Self-Managed">

1. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

2. Edit the `.env` file, set up the `DATABASE_URL` environment variable as follows, and replace the `{user}`, `{password}`, `{host}`, `{port}`, and `{database}` with your own TiDB connection information:

    ```dotenv
    DATABASE_URL='mysql2://{user}:{password}@{host}:{port}/{database}'
    ```

   If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `.env` file.

</div>
### Step 4: Run the code and check the result

1. Create the database and table:

    ```shell
    bundle exec rails db:create
    bundle exec rails db:migrate
    ```

2. Seed the sample data:

    ```shell
    bundle exec rails db:seed
    ```

3. Run the following command to execute the sample code:

    ```shell
    bundle exec rails runner ./quickstart.rb
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
