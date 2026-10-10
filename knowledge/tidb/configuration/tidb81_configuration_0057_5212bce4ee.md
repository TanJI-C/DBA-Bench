# Prisma quickstart setup and sample app run steps

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-prisma.md`
- Source Title: `Connect to TiDB with Prisma`
- Source Heading Path: `Connect to TiDB with Prisma | Connect to TiDB with Prisma > Prerequisites | Connect to TiDB with Prisma > Run the sample app to connect to TiDB | Connect to TiDB with Prisma > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with Prisma > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with Prisma > Run the sample app to connect to TiDB > Step 3: Provide connection Parameters | Connect to TiDB with Prisma > Run the sample app to connect to TiDB > Step 4. Initialize the database schema | Connect to TiDB with Prisma > Run the sample app to connect to TiDB > Step 5: Run the code`
- Source Line Ranges: `5-279`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `sql`
- Topic Tags: `prisma`, `nodejs`, `prerequisites`, `repository-clone`, `dependency-installation`, `connection-string`, `tls`, `schema-migration`, `datasource-configuration`, `sample-app`, `crud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0057_5212bce4ee`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-prisma.md#connect-to-tidb-with-prisma`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1427bf96083796c63c97452620d35a21e6810859ffdad619765d0f7822c37669`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-prisma#connect-to-tidb-with-prisma
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-prisma.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official Prisma quickstart steps to connect a Node.js application to TiDB, including prerequisites, repository setup, DATABASE_URL configuration, Prisma schema datasource settings, migration, and running the sample app.
- Retrieval Keywords: Connect to TiDB with Prisma, Node.js >= 16.x, git clone https://github.com/tidb-samples/tidb-nodejs-prisma-quickstart.git, npm install, DATABASE_URL, cp .env.example .env, prisma/schema.prisma, provider = "mysql", url = env("DATABASE_URL"), npx prisma migrate dev, npm start, PrismaClient, sslaccept=strict, CA cert, TiDB Cloud Dedicated, TiDB Self-Managed
- Follow-up Guidance: This chunk also includes the expected output for `npx prisma migrate dev`, the `Player` and `Profile` models in `prisma.schema`, and the sample app output showing a successful connection to the TiDB cluster.
- Classification Note: It is classified as configuration because the content focuses on environment prerequisites, connection parameters, `.env` and `schema.prisma` setup, schema initialization, and execution steps for the sample application.

## Official Source Content

# Connect to TiDB with Prisma

TiDB is a MySQL-compatible database, and [Prisma](https://github.com/prisma/prisma) is a popular open-source ORM framework for Node.js.

In this tutorial, you can learn how to use TiDB and Prisma to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using Prisma.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.

> **Note:**
>
> This tutorial works with {{{ .starter }}}, {{{ .essential }}}, TiDB Cloud Dedicated, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [Node.js](https://nodejs.org/en) >= 16.x installed on your machine.
- [Git](https://git-scm.com/downloads) installed on your machine.
- A TiDB cluster running.

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
git clone https://github.com/tidb-samples/tidb-nodejs-prisma-quickstart.git
cd tidb-nodejs-prisma-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including `prisma`) for the sample app:

```shell
npm install
```

<details>
<summary><b>Install dependencies to existing project</b></summary>

For your existing project, run the following command to install the packages:

```shell
npm install prisma typescript ts-node @types/node --save-dev
```

</details>
### Step 3: Provide connection Parameters

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`.
    - **Branch** is set to `main`.
    - **Connect With** is set to `Prisma`.
    - **Operating System** matches the operating system where you run the application.

4. If you have not set a password yet, click **Generate Password** to generate a random password.

5. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

6. Edit the `.env` file, set up the environment variable `DATABASE_URL` as follows, and replace the corresponding placeholders `{}` with the connection string in the connection dialog:

    ```dotenv
    DATABASE_URL='{connection_string}'
    ```

    > **Note**
    >
    > For {{{ .starter }}}, you **MUST** enable TLS connection by setting `sslaccept=strict` when using public endpoint.

7. Save the `.env` file.
8. In the `prisma/schema.prisma`, set up `mysql` as the connection provider and `env("DATABASE_URL")` as the connection URL:

    ```prisma
    datasource db {
      provider = "mysql"
      url      = env("DATABASE_URL")
    }
    ```

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

5. Edit the `.env` file, set up the environment variable `DATABASE_URL` as follows, replace the corresponding placeholders `{}` with connection parameters on the connection dialog:

    ```dotenv
    DATABASE_URL='mysql://{user}:{password}@{host}:4000/test?sslaccept=strict&sslcert={downloaded_ssl_ca_path}'
    ```

    > **Note**
    >
    > For {{{ .starter }}}, It is **RECOMMENDED** to enable TLS connection by setting `sslaccept=strict` when using public endpoint. When you set up `sslaccept=strict` to enable TLS connection, you **MUST** specify the file path of the CA certificate downloaded from connection dialog via `sslcert=/path/to/ca.pem`.

6. Save the `.env` file.
7. In the `prisma/schema.prisma`, set up `mysql` as the connection provider and `env("DATABASE_URL")` as the connection URL:

    ```prisma
    datasource db {
      provider = "mysql"
      url      = env("DATABASE_URL")
    }
    ```

</div>
<div label="TiDB Self-Managed">

1. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

2. Edit the `.env` file, set up the environment variable `DATABASE_URL` as follows, replace the corresponding placeholders `{}` with connection parameters of your TiDB cluster:

    ```dotenv
    DATABASE_URL='mysql://{user}:{password}@{host}:4000/test'
    ```

   If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `.env` file.

4. In the `prisma/schema.prisma`, set up `mysql` as the connection provider and `env("DATABASE_URL")` as the connection URL:

    ```prisma
    datasource db {
      provider = "mysql"
      url      = env("DATABASE_URL")
    }
    ```

</div>
### Step 4. Initialize the database schema

Run following command to invoke [Prisma Migrate](https://www.prisma.io/docs/concepts/components/prisma-migrate) to initialize the database with the data models defined in `prisma/prisma.schema`.

```shell
npx prisma migrate dev
```

**Data models defined in `prisma.schema`:**

```prisma
// Define a Player model, which represents the `players` table.
model Player {
  id        Int      @id @default(autoincrement())
  name      String   @unique(map: "uk_player_on_name") @db.VarChar(50)
  coins     Decimal  @default(0)
  goods     Int      @default(0)
  createdAt DateTime @default(now()) @map("created_at")
  profile   Profile?

  @@map("players")
}

// Define a Profile model, which represents the `profiles` table.
model Profile {
  playerId  Int    @id @map("player_id")
  biography String @db.Text

  // Define a 1:1 relation between the `Player` and `Profile` models with foreign key.
  player    Player @relation(fields: [playerId], references: [id], onDelete: Cascade, map: "fk_profile_on_player_id")

  @@map("profiles")
}
```

To learn how to define data models in Prisma, please check the [Data model](https://www.prisma.io/docs/concepts/components/prisma-schema/data-model) documentation.

**Expected execution output:**

```
Your database is now in sync with your schema.

✔ Generated Prisma Client (5.1.1 | library) to ./node_modules/@prisma/client in 54ms
```

This command will also generate [Prisma Client](https://www.prisma.io/docs/concepts/components/prisma-client) for TiDB database accessing based on the `prisma/prisma.schema`.
### Step 5: Run the code

Run the following command to execute the sample code:

```shell
npm start
```

**Main logic in the sample code:**

```typescript
// Step 1. Import the auto-generated `@prisma/client` package.
import {Player, PrismaClient} from '@prisma/client';

async function main(): Promise<void> {
  // Step 2. Create a new `PrismaClient` instance.
  const prisma = new PrismaClient();
  try {

    // Step 3. Perform some CRUD operations with Prisma Client ...

  } finally {
    // Step 4. Disconnect Prisma Client.
    await prisma.$disconnect();
  }
}

void main();
```

**Expected execution output:**

If the connection is successful, the terminal will output the version of the TiDB cluster as follows:

```
🔌 Connected to TiDB cluster! (TiDB version: 8.0.11-TiDB-v8.1.2)
🆕 Created a new player with ID 1.
ℹ️ Got Player 1: Player { id: 1, coins: 100, goods: 100 }
🔢 Added 50 coins and 50 goods to player 1, now player 1 has 150 coins and 150 goods.
🚮 Player 1 has been deleted.
```
