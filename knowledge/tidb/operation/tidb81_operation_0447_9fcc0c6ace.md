# SQLAlchemy vector search quickstart setup and demo run

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-sqlalchemy.md`
- Source Title: `Integrate TiDB Vector Search with SQLAlchemy`
- Source Heading Path: `Integrate TiDB Vector Search with SQLAlchemy | Integrate TiDB Vector Search with SQLAlchemy > Prerequisites | Integrate TiDB Vector Search with SQLAlchemy > Run the sample app | Integrate TiDB Vector Search with SQLAlchemy > Run the sample app > Step 1. Clone the repository | Integrate TiDB Vector Search with SQLAlchemy > Run the sample app > Step 2. Create a virtual environment | Integrate TiDB Vector Search with SQLAlchemy > Run the sample app > Step 3. Install the required dependencies | Integrate TiDB Vector Search with SQLAlchemy > Run the sample app > Step 4. Configure the environment variables | Integrate TiDB Vector Search with SQLAlchemy > Run the sample app > Step 5. Run the demo`
- Source Line Ranges: `5-111`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `sql`
- Topic Tags: `sqlalchemy`, `vector-search`, `python`, `prerequisites`, `repository`, `virtualenv`, `dependencies`, `environment-variables`, `connection-string`, `demo`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0447_9fcc0c6ace`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-sqlalchemy.md#integrate-tidb-vector-search-with-sqlalchemy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa7af13636571354abd5f04f42df8651e3034abc5a65154fff8e353966af5c77`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-sqlalchemy#integrate-tidb-vector-search-with-sqlalchemy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-sqlalchemy.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the prerequisite list and exact demo setup steps to run the SQLAlchemy TiDB Vector Search quickstart with a TiDB Cloud Serverless cluster.
- Retrieval Keywords: TiDB Vector Search with SQLAlchemy, Prerequisites, Python 3.8 or higher, Git, TiDB Cloud Serverless cluster, tidb-vector-python, git clone https://github.com/pingcap/tidb-vector-python.git, orm-sqlalchemy-quickstart, python3 -m venv .venv, pip install -r requirements.txt, pip install pymysql python-dotenv sqlalchemy tidb-vector, TIDB_DATABASE_URL, .env, Connect With SQLAlchemy, PyMySQL connection string, Connection Type Public, Branch main, python sqlalchemy-quickstart.py
- Follow-up Guidance: The chunk includes the sample output showing 3-nearest neighbor documents and documents within a certain distance after running `python sqlalchemy-quickstart.py`.
- Classification Note: This is classified as an operation chunk because the content provides prerequisites and a step-by-step procedure to configure environment variables and run the demo application.

## Official Source Content

# Integrate TiDB Vector Search with SQLAlchemy

This tutorial walks you through how to use [SQLAlchemy](https://www.sqlalchemy.org/) to interact with [TiDB Vector Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview), store embeddings, and perform vector search queries.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Prerequisites

To complete this tutorial, you need:

- [Python 3.8 or higher](https://www.python.org/downloads/) installed.
- [Git](https://git-scm.com/downloads) installed.
- A TiDB Cloud Serverless cluster. Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create your own TiDB Cloud cluster if you don't have one.
## Run the sample app

You can quickly learn about how to integrate TiDB Vector Search with SQLAlchemy by following the steps below.
### Step 1. Clone the repository

Clone the `tidb-vector-python` repository to your local machine:

```shell
git clone https://github.com/pingcap/tidb-vector-python.git
```
### Step 2. Create a virtual environment

Create a virtual environment for your project:

```bash
cd tidb-vector-python/examples/orm-sqlalchemy-quickstart
python3 -m venv .venv
source .venv/bin/activate
```
### Step 3. Install the required dependencies

Install the required dependencies for the demo project:

```bash
pip install -r requirements.txt
```

Alternatively, you can install the following packages for your project:

```bash
pip install pymysql python-dotenv sqlalchemy tidb-vector
```
### Step 4. Configure the environment variables

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your environment.

   - **Connection Type** is set to `Public`.
   - **Branch** is set to `main`.
   - **Connect With** is set to `SQLAlchemy`.
   - **Operating System** matches your environment.

   > **Tip:**
   >
   > If your program is running in Windows Subsystem for Linux (WSL), switch to the corresponding Linux distribution.

4. Click the **PyMySQL** tab and copy the connection string.

   > **Tip:**
   >
   > If you have not set a password yet, click **Generate Password** to generate a random password.

5. In the root directory of your Python project, create a `.env` file and paste the connection string into it.

   The following is an example for macOS:

   ```dotenv
   TIDB_DATABASE_URL="mysql+pymysql://<prefix>.root:<password>@gateway01.<region>.prod.aws.tidbcloud.com:4000/test?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true"
   ```
### Step 5. Run the demo

```bash
python sqlalchemy-quickstart.py
```

Example output:

```text
Get 3-nearest neighbor documents:
  - distance: 0.00853986601633272
    document: fish
  - distance: 0.12712843905603044
    document: dog
  - distance: 0.7327387580875756
    document: tree
Get documents within a certain distance:
  - distance: 0.00853986601633272
    document: fish
  - distance: 0.12712843905603044
    document: dog
```
