# Jina AI embeddings sample app setup and execution

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-jinaai-embedding.md`
- Source Title: `Integrate TiDB Vector Search with Jina AI Embeddings API`
- Source Heading Path: `Integrate TiDB Vector Search with Jina AI Embeddings API | Integrate TiDB Vector Search with Jina AI Embeddings API > Prerequisites | Integrate TiDB Vector Search with Jina AI Embeddings API > Run the sample app | Integrate TiDB Vector Search with Jina AI Embeddings API > Run the sample app > Step 1. Clone the repository | Integrate TiDB Vector Search with Jina AI Embeddings API > Run the sample app > Step 2. Create a virtual environment | Integrate TiDB Vector Search with Jina AI Embeddings API > Run the sample app > Step 3. Install required dependencies | Integrate TiDB Vector Search with Jina AI Embeddings API > Run the sample app > Step 4. Configure the environment variables | Integrate TiDB Vector Search with Jina AI Embeddings API > Run the sample app > Step 5. Run the demo`
- Source Line Ranges: `5-111`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`, `ecosystem`
- Topic Tags: `vector-search`, `jinaai`, `prerequisites`, `sample-app`, `environment-variables`, `connection-string`, `sqlalchemy`, `python`, `demo-run`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0443_57a12287da`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-jinaai-embedding.md#integrate-tidb-vector-search-with-jina-ai-embeddings-api`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `030687037263877df91b06bb65801a63258b2fd4bc173c80c95406b44547dec4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-jinaai-embedding#integrate-tidb-vector-search-with-jina-ai-embeddings-api
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-jinaai-embedding.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the prerequisites, environment variables, cluster connection dialog settings, repository path, and demo command for running the Jina AI embeddings sample app with TiDB Vector Search.
- Retrieval Keywords: TiDB Vector Search with Jina AI Embeddings API, Python 3.8 or higher, Git, TiDB Cloud Serverless cluster, tidb-vector-python, examples/jina-ai-embeddings-demo, python3 -m venv .venv, pip install -r requirements.txt, JINAAI_API_KEY, TIDB_DATABASE_URL, Connection Type Public, Branch main, Connect With SQLAlchemy, PyMySQL tab, python jina-ai-embeddings-demo.py
- Follow-up Guidance: The chunk also includes example demo output showing inserted texts and cosine distance search results for the query.
- Classification Note: The official content is operational because it provides prerequisites and step-by-step setup, configuration, and execution instructions for the sample app.

## Official Source Content

# Integrate TiDB Vector Search with Jina AI Embeddings API

This tutorial walks you through how to use [Jina AI](https://jina.ai/) to generate embeddings for text data, and then store the embeddings in TiDB vector storage and search similar texts based on embeddings.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Prerequisites

To complete this tutorial, you need:

- [Python 3.8 or higher](https://www.python.org/downloads/) installed.
- [Git](https://git-scm.com/downloads) installed.
- A TiDB Cloud Serverless cluster. Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create your own TiDB Cloud cluster if you don't have one.
## Run the sample app

You can quickly learn about how to integrate TiDB Vector Search with JinaAI Embedding by following the steps below.
### Step 1. Clone the repository

Clone the `tidb-vector-python` repository to your local machine:

```shell
git clone https://github.com/pingcap/tidb-vector-python.git
```
### Step 2. Create a virtual environment

Create a virtual environment for your project:

```bash
cd tidb-vector-python/examples/jina-ai-embeddings-demo
python3 -m venv .venv
source .venv/bin/activate
```
### Step 3. Install required dependencies

Install the required dependencies for the demo project:

```bash
pip install -r requirements.txt
```
### Step 4. Configure the environment variables

Get the Jina AI API key from the [Jina AI Embeddings API](https://jina.ai/embeddings/) page. Then, obtain the cluster connection string and configure environment variables as follows:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

   - **Connection Type** is set to `Public`
   - **Branch** is set to `main`
   - **Connect With** is set to `SQLAlchemy`
   - **Operating System** matches your environment.

   > **Tip:**
   >
   > If your program is running in Windows Subsystem for Linux (WSL), switch to the corresponding Linux distribution.

4. Switch to the **PyMySQL** tab and click the **Copy** icon to copy the connection string.

   > **Tip:**
   >
   > If you have not set a password yet, click **Create password** to generate a random password.

5. Set the Jina AI API key and the TiDB connection string as environment variables in your terminal, or create a `.env` file with the following environment variables:

   ```dotenv
   JINAAI_API_KEY="****"
   TIDB_DATABASE_URL="{tidb_connection_string}"
   ```

   The following is an example connection string for macOS:

   ```dotenv
   TIDB_DATABASE_URL="mysql+pymysql://<prefix>.root:<password>@gateway01.<region>.prod.aws.tidbcloud.com:4000/test?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true"
   ```
### Step 5. Run the demo

```bash
python jina-ai-embeddings-demo.py
```

Example output:

```text
- Inserting Data to TiDB...
  - Inserting: Jina AI offers best-in-class embeddings, reranker and prompt optimizer, enabling advanced multimodal AI.
  - Inserting: TiDB is an open-source MySQL-compatible database that supports Hybrid Transactional and Analytical Processing (HTAP) workloads.
- List All Documents and Their Distances to the Query:
  - distance: 0.3585317326132522
    content: Jina AI offers best-in-class embeddings, reranker and prompt optimizer, enabling advanced multimodal AI.
  - distance: 0.10858102967720984
    content: TiDB is an open-source MySQL-compatible database that supports Hybrid Transactional and Analytical Processing (HTAP) workloads.
- The Most Relevant Document and Its Distance to the Query:
  - distance: 0.10858102967720984
    content: TiDB is an open-source MySQL-compatible database that supports Hybrid Transactional and Analytical Processing (HTAP) workloads.
```
