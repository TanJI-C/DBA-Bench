# Next.js mysql2 sample app setup and connection steps

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nextjs.md`
- Source Title: `Connect to TiDB with mysql2 in Next.js`
- Source Heading Path: `Connect to TiDB with mysql2 in Next.js | Connect to TiDB with mysql2 in Next.js > Prerequisites | Connect to TiDB with mysql2 in Next.js > Run the sample app to connect to TiDB | Connect to TiDB with mysql2 in Next.js > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with mysql2 in Next.js > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with mysql2 in Next.js > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with mysql2 in Next.js > Run the sample app to connect to TiDB > Step 4: Run the code and check the result`
- Source Line Ranges: `5-182`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `shared`
- Topic Tags: `next.js`, `mysql2`, `prerequisites`, `sample-app`, `git`, `npm`, `environment-variables`, `connection-string`, `tls`, `cloud-connectivity`, `self-managed`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0056_7682ce48f0`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nextjs.md#connect-to-tidb-with-mysql2-in-next-js`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b011a18373c1ad8cf357537c41725c8138aa8e88fe57ad3e9396fefdecf9b51b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nextjs#connect-to-tidb-with-mysql2-in-next-js
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nextjs.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official Next.js mysql2 sample app setup steps, prerequisites, .env connection variables, and connection verification flow for connecting to a TiDB cluster.
- Retrieval Keywords: Connect to TiDB with mysql2 in Next.js, tidb-nextjs-vercel-quickstart, Node.js 18 or later, git clone git@github.com:tidb-samples/tidb-nextjs-vercel-quickstart.git, npm install, cp .env.example .env, Copy-Item ".env.example" -Destination ".env", TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, Connection Type Public, Branch main, Connect With General, npm run dev, RUN SQL, Hello World
- Follow-up Guidance: If the user needs implementation examples after setup, the same source also provides sample code snippets for connect, insert, query, update, and delete operations with mysql2.
- Classification Note: This is classified as configuration because the content is a step-by-step setup guide covering prerequisites, repository cloning, dependency installation, environment variables, connection dialog settings, and run-time verification.

## Official Source Content

# Connect to TiDB with mysql2 in Next.js

TiDB is a MySQL-compatible database, and [mysql2](https://github.com/sidorares/node-mysql2) is a popular open-source driver for Node.js.

In this tutorial, you can learn how to use TiDB and mysql2 in Next.js to accomplish the following tasks:

- Set up your environment.
- Connect to your TiDB cluster using mysql2.
- Build and run your application. Optionally, you can find [sample code snippets](#sample-code-snippets) for basic CRUD operations.

> **Note**
>
> This tutorial works with {{{ .starter }}}, {{{ .essential }}}, and TiDB Self-Managed.
## Prerequisites

To complete this tutorial, you need:

- [Node.js **18**](https://nodejs.org/en/download/) or later.
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

> **Note**
>
> For complete code snippets and running instructions, refer to the [tidb-nextjs-vercel-quickstart](https://github.com/tidb-samples/tidb-nextjs-vercel-quickstart) GitHub repository.
### Step 1: Clone the sample app repository

Run the following commands in your terminal window to clone the sample code repository:

```bash
git clone git@github.com:tidb-samples/tidb-nextjs-vercel-quickstart.git
cd tidb-nextjs-vercel-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including `mysql2`) for the sample app:

```bash
npm install
```
### Step 3: Configure connection information

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters** page](https://tidbcloud.com/project/clusters), and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`
    - **Branch** is set to `main`
    - **Connect With** is set to `General`
    - **Operating System** matches your environment.

    > **Note**
    >
    > In Node.js applications, you do not have to provide an SSL CA certificate, because Node.js uses the built-in [Mozilla CA certificate](https://wiki.mozilla.org/CA/Included_Certificates) by default when establishing the TLS (SSL) connection.

4. Click **Generate Password** to create a random password.

    > **Tip**
    >
    > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

5. Run the following command to copy `.env.example` and rename it to `.env`:

    ```bash
    # Linux
    cp .env.example .env
    ```

    ```powershell
    # Windows
    Copy-Item ".env.example" -Destination ".env"
    ```

6. Copy and paste the corresponding connection string into the `.env` file. The example result is as follows:

    ```bash
    TIDB_HOST='{gateway-region}.aws.tidbcloud.com'
    TIDB_PORT='4000'
    TIDB_USER='{prefix}.root'
    TIDB_PASSWORD='{password}'
    TIDB_DB_NAME='test'
    ```

    Replace the placeholders in `{}` with the values obtained in the connection dialog.

7. Save the `.env` file.

</div>

<div label="TiDB Self-Managed">

1. Run the following command to copy `.env.example` and rename it to `.env`:

    ```bash
    # Linux
    cp .env.example .env
    ```

    ```powershell
    # Windows
    Copy-Item ".env.example" -Destination ".env"
    ```

2. Copy and paste the corresponding connection string into the `.env` file. The example result is as follows:

    ```bash
    TIDB_HOST='{tidb_server_host}'
    TIDB_PORT='4000'
    TIDB_USER='root'
    TIDB_PASSWORD='{password}'
    TIDB_DB_NAME='test'
    ```

    Replace the placeholders in `{}` with the values obtained in the **Connect** window. If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `.env` file.

</div>
### Step 4: Run the code and check the result

1. Start the application:

   ```bash
   npm run dev
   ```

2. Open your browser and visit `http://localhost:3000`. (Check your terminal for the actual port number, and the default is `3000`.)

3. Click **RUN SQL** to execute the sample code.

4. Check the output in the terminal. If the output is similar to the following, the connection is successful:

   ```json
   {
     "results": [
       {
         "Hello World": "Hello World"
       }
     ]
   }
   ```
