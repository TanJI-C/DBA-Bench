# Peewee vector search quickstart setup and demo run

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-peewee.md`
- Source Title: `Integrate TiDB Vector Search with peewee`
- Source Heading Path: `Integrate TiDB Vector Search with peewee | Integrate TiDB Vector Search with peewee > Prerequisites | Integrate TiDB Vector Search with peewee > Run the sample app | Integrate TiDB Vector Search with peewee > Run the sample app > Step 1. Clone the repository | Integrate TiDB Vector Search with peewee > Run the sample app > Step 2. Create a virtual environment | Integrate TiDB Vector Search with peewee > Run the sample app > Step 3. Install required dependencies | Integrate TiDB Vector Search with peewee > Run the sample app > Step 4. Configure the environment variables | Integrate TiDB Vector Search with peewee > Run the sample app > Step 5. Run the demo`
- Source Line Ranges: `5-123`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `vector-search`, `peewee`, `python`, `prerequisites`, `quickstart`, `environment-variables`, `connection`, `serverless`, `demo`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0446_58f5e23e2e`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-peewee.md#integrate-tidb-vector-search-with-peewee`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ff17f467bd4b20f01e42c1be2896a8c213db70a2fe46c11aaa9a2a9e7e96c6d7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-peewee#integrate-tidb-vector-search-with-peewee
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-peewee.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the peewee quickstart prerequisites, TiDB Cloud Serverless connection setup, environment variables, and demo execution steps for TiDB Vector Search.
- Retrieval Keywords: Integrate TiDB Vector Search with peewee, TiDB Vector Search, peewee, Python 3.8 or higher, Git, TiDB Cloud Serverless cluster, tidb-vector-python, orm-peewee-quickstart, python3 -m venv .venv, pip install -r requirements.txt, pip install peewee pymysql python-dotenv tidb-vector, .env, TIDB_HOST, TIDB_PORT, TIDB_USERNAME, TIDB_PASSWORD, TIDB_DATABASE, TIDB_CA_PATH, Connection Type Public, Branch main, Connect With General, Generate Password, python peewee-quickstart.py
- Follow-up Guidance: The source also shows example demo output for 3-nearest neighbor documents and documents within a certain distance.
- Classification Note: This is classified as an operation chunk because the official content provides prerequisites and step-by-step setup, connection configuration, and demo run instructions.

## Official Source Content

# Integrate TiDB Vector Search with peewee

This tutorial walks you through how to use [peewee](https://docs.peewee-orm.com/) to interact with the [TiDB Vector Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview), store embeddings, and perform vector search queries.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Prerequisites

To complete this tutorial, you need:

- [Python 3.8 or higher](https://www.python.org/downloads/) installed.
- [Git](https://git-scm.com/downloads) installed.
- A TiDB Cloud Serverless cluster. Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create your own TiDB Cloud cluster if you don't have one.
## Run the sample app

You can quickly learn about how to integrate TiDB Vector Search with peewee by following the steps below.
### Step 1. Clone the repository

Clone the [`tidb-vector-python`](https://github.com/pingcap/tidb-vector-python) repository to your local machine:

```shell
git clone https://github.com/pingcap/tidb-vector-python.git
```
### Step 2. Create a virtual environment

Create a virtual environment for your project:

```bash
cd tidb-vector-python/examples/orm-peewee-quickstart
python3 -m venv .venv
source .venv/bin/activate
```
### Step 3. Install required dependencies

Install the required dependencies for the demo project:

```bash
pip install -r requirements.txt
```

Alternatively, you can install the following packages for your project:

```bash
pip install peewee pymysql python-dotenv tidb-vector
```
### Step 4. Configure the environment variables

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

   - **Connection Type** is set to `Public`.
   - **Branch** is set to `main`.
   - **Connect With** is set to `General`.
   - **Operating System** matches your environment.

   > **Tip:**
   >
   > If your program is running in Windows Subsystem for Linux (WSL), switch to the corresponding Linux distribution.

4. Copy the connection parameters from the connection dialog.

   > **Tip:**
   >
   > If you have not set a password yet, click **Generate Password** to generate a random password.

5. In the root directory of your Python project, create a `.env` file and paste the connection parameters to the corresponding environment variables.

   - `TIDB_HOST`: The host of the TiDB cluster.
   - `TIDB_PORT`: The port of the TiDB cluster.
   - `TIDB_USERNAME`: The username to connect to the TiDB cluster.
   - `TIDB_PASSWORD`: The password to connect to the TiDB cluster.
   - `TIDB_DATABASE`: The database name to connect to.
   - `TIDB_CA_PATH`: The path to the root certificate file.

   The following is an example for macOS:

   ```dotenv
   TIDB_HOST=gateway01.****.prod.aws.tidbcloud.com
   TIDB_PORT=4000
   TIDB_USERNAME=********.root
   TIDB_PASSWORD=********
   TIDB_DATABASE=test
   TIDB_CA_PATH=/etc/ssl/cert.pem
   ```
### Step 5. Run the demo

```bash
python peewee-quickstart.py
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
