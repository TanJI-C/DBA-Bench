# LlamaIndex setup, prerequisites, and sample document loading

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-llamaindex.md`
- Source Title: `Integrate Vector Search with LlamaIndex`
- Source Heading Path: `Integrate Vector Search with LlamaIndex | Integrate Vector Search with LlamaIndex > Prerequisites | Integrate Vector Search with LlamaIndex > Get started | Integrate Vector Search with LlamaIndex > Get started > Step 1. Create a new Jupyter Notebook file | Integrate Vector Search with LlamaIndex > Get started > Step 2. Install required dependencies | Integrate Vector Search with LlamaIndex > Get started > Step 3. Configure environment variables | Integrate Vector Search with LlamaIndex > Get started > Step 4. Load the sample document | Integrate Vector Search with LlamaIndex > Get started > Step 4. Load the sample document > Step 4.1 Download the sample document | Integrate Vector Search with LlamaIndex > Get started > Step 4. Load the sample document > Step 4.2 Load the document`
- Source Line Ranges: `5-118`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `vector-search`, `llamaindex`, `prerequisites`, `jupyter`, `python`, `dependencies`, `environment-variables`, `connection-string`, `openai`, `document-loading`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0314_4d8949143d`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-llamaindex.md#integrate-vector-search-with-llamaindex`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1761d0e4bca80c5b066b68f7641860bd60aee27cec5d259f778b41a89914d89b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-llamaindex#integrate-vector-search-with-llamaindex
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-llamaindex.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the prerequisite setup and initial notebook workflow to integrate TiDB Vector Search with LlamaIndex, including dependency installation, environment variables, connection string details, and loading the sample document.
- Retrieval Keywords: TiDB Vector Search with LlamaIndex, integrate_with_llamaindex.ipynb, pip install llama-index-vector-stores-tidbvector, pip install llama-index, SimpleDirectoryReader, StorageContext, VectorStoreIndex, TiDBVectorStore, TiDB Cloud Serverless cluster, Python 3.8 or higher, Jupyter Notebook, Git, OPENAI_API_KEY, TiDB Connection String, mysql+pymysql://<USER>:<PASSWORD>@<HOST>:4000/<DB>?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true, Connection Type Public, Branch main, Connect With SQLAlchemy, PyMySQL tab, data/paul_graham/, paul_graham_essay.txt, SimpleDirectoryReader("./data/paul_graham").load_data()
- Follow-up Guidance: The next steps in the source initialize a `TiDBVectorStore`, generate embeddings with `VectorStoreIndex.from_documents`, run semantic queries, apply `MetadataFilters`, and delete documents by `doc_id`.
- Classification Note: This chunk is classified as configuration because the official content focuses on prerequisites, installing packages, setting environment variables, obtaining the SQLAlchemy PyMySQL connection string, and loading the sample input document.

## Official Source Content

# Integrate Vector Search with LlamaIndex

This tutorial demonstrates how to integrate the [vector search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview) feature of TiDB with [LlamaIndex](https://www.llamaindex.ai).

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).

> **Tip**
>
> You can view the complete [sample code](https://github.com/run-llama/llama_index/blob/main/docs/docs/examples/vector_stores/TiDBVector.ipynb) on Jupyter Notebook, or run the sample code directly in the [Colab](https://colab.research.google.com/github/run-llama/llama_index/blob/main/docs/docs/examples/vector_stores/TiDBVector.ipynb) online environment.
## Prerequisites

To complete this tutorial, you need:

- [Python 3.8 or higher](https://www.python.org/downloads/) installed.
- [Jupyter Notebook](https://jupyter.org/install) installed.
- [Git](https://git-scm.com/downloads) installed.
- A TiDB Cloud Serverless cluster. Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create your own TiDB Cloud cluster if you don't have one.
## Get started

This section provides step-by-step instructions for integrating TiDB Vector Search with LlamaIndex to perform semantic searches.
### Step 1. Create a new Jupyter Notebook file

In the root directory, create a new Jupyter Notebook file named `integrate_with_llamaindex.ipynb`:

```shell
touch integrate_with_llamaindex.ipynb
```
### Step 2. Install required dependencies

In your project directory, run the following command to install the required packages:

```shell
pip install llama-index-vector-stores-tidbvector
pip install llama-index
```

Open the `integrate_with_llamaindex.ipynb` file in Jupyter Notebook and add the following code to import the required packages:

```python
import textwrap

from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.tidbvector import TiDBVectorStore
```
### Step 3. Configure environment variables

Take the following steps to obtain the cluster connection string and configure environment variables:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

   - **Connection Type** is set to `Public`.
   - **Branch** is set to `main`.
   - **Connect With** is set to `SQLAlchemy`.
   - **Operating System** matches your environment.

4. Click the **PyMySQL** tab and copy the connection string.

   > **Tip:**
   >
   > If you have not set a password yet, click **Generate Password** to generate a random password.

5. Configure environment variables.

   This document uses [OpenAI](https://platform.openai.com/docs/introduction) as the embedding model provider. In this step, you need to provide the connection string obtained from the previous step and your [OpenAI API key](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key).

   To configure the environment variables, run the following code. You will be prompted to enter your connection string and OpenAI API key:

   ```python
   # Use getpass to securely prompt for environment variables in your terminal.
   import getpass
   import os

   # Copy your connection string from the TiDB Cloud console.
   # Connection string format: "mysql+pymysql://<USER>:<PASSWORD>@<HOST>:4000/<DB>?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true"
   tidb_connection_string = getpass.getpass("TiDB Connection String:")
   os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
   ```
### Step 4. Load the sample document
#### Step 4.1 Download the sample document

In your project directory, create a directory named `data/paul_graham/` and download the sample document [`paul_graham_essay.txt`](https://github.com/run-llama/llama_index/blob/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt) from the [run-llama/llama_index](https://github.com/run-llama/llama_index) GitHub repository.

```shell
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
#### Step 4.2 Load the document

Load the sample document from `data/paul_graham/paul_graham_essay.txt` using the `SimpleDirectoryReader` class.

```python
documents = SimpleDirectoryReader("./data/paul_graham").load_data()
print("Document ID:", documents[0].doc_id)

for index, document in enumerate(documents):
   document.metadata = {"book": "paul_graham"}
```
