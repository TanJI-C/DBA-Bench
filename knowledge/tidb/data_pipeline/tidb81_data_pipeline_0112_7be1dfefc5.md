# LangChain vector search quickstart in TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-langchain.md`
- Source Title: `Integrate Vector Search with LangChain`
- Source Heading Path: `Integrate Vector Search with LangChain | Integrate Vector Search with LangChain > Prerequisites | Integrate Vector Search with LangChain > Get started | Integrate Vector Search with LangChain > Get started > Step 1. Create a new Jupyter Notebook file | Integrate Vector Search with LangChain > Get started > Step 2. Install required dependencies | Integrate Vector Search with LangChain > Get started > Step 3. Set up your environment | Integrate Vector Search with LangChain > Get started > Step 4. Load the sample document | Integrate Vector Search with LangChain > Get started > Step 4. Load the sample document > Step 4.1 Download the sample document | Integrate Vector Search with LangChain > Get started > Step 4. Load the sample document > Step 4.2 Load and split the document | Integrate Vector Search with LangChain > Get started > Step 5. Embed and store document vectors | Integrate Vector Search with LangChain > Get started > Step 6. Perform a vector search | Integrate Vector Search with LangChain > Get started > Step 6. Perform a vector search > Option 1: Use `similarity_search_with_score()``
- Source Line Ranges: `5-204`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `sql`
- Topic Tags: `langchain`, `vector-search`, `jupyter-notebook`, `python`, `dependencies`, `environment-variables`, `openai`, `document-loading`, `text-splitting`, `embeddings`, `vector-store`, `similarity-search`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0112_7be1dfefc5`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-langchain.md#integrate-vector-search-with-langchain`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d9f1fc33ccf81d107922baf590c6745400d1b27b788666cd086476c483ab542`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-langchain#integrate-vector-search-with-langchain
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-langchain.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud Serverless LangChain vector search quickstart, including Jupyter setup, Python dependencies, OpenAI embeddings, TiDBVectorStore, and a similarity search example.
- Retrieval Keywords: Integrate Vector Search with LangChain, TiDB Cloud Serverless, Jupyter Notebook, integrate_with_langchain.ipynb, pip install langchain langchain-community, pip install langchain-openai, pip install pymysql, pip install tidb-vector, TextLoader, TiDBVectorStore, OpenAIEmbeddings, CharacterTextSplitter, mysql+pymysql connection string, OPENAI_API_KEY, state_of_the_union.txt, embedded_documents, distance_strategy="cosine", distance_strategy="l2", similarity_search_with_score(), What did the president say about Ketanji Brown Jackson
- Follow-up Guidance: The chunk also shows the connection dialog settings, the sample document download path `data/how_to/state_of_the_union.txt`, and the expected output pattern for `similarity_search_with_score(query, k=3)`.
- Classification Note: The classification is data_pipeline for the ecosystem component because the content walks through loading a document, splitting text, generating embeddings, storing vectors in TiDB, and querying them through the LangChain integration.

## Official Source Content

# Integrate Vector Search with LangChain

This tutorial demonstrates how to integrate the [vector search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview) feature in TiDB Cloud with [LangChain](https://python.langchain.com/).

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).

> **Tip**
>
> You can view the complete [sample code](https://github.com/langchain-ai/langchain/blob/master/docs/docs/integrations/vectorstores/tidb_vector.ipynb) on Jupyter Notebook, or run the sample code directly in the [Colab](https://colab.research.google.com/github/langchain-ai/langchain/blob/master/docs/docs/integrations/vectorstores/tidb_vector.ipynb) online environment.
## Prerequisites

To complete this tutorial, you need:

- [Python 3.8 or higher](https://www.python.org/downloads/) installed.
- [Jupyter Notebook](https://jupyter.org/install) installed.
- [Git](https://git-scm.com/downloads) installed.
- A TiDB Cloud Serverless cluster. Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create your own TiDB Cloud cluster if you don't have one.
## Get started

This section provides step-by-step instructions for integrating TiDB Vector Search with LangChain to perform semantic searches.
### Step 1. Create a new Jupyter Notebook file

In your preferred directory, create a new Jupyter Notebook file named `integrate_with_langchain.ipynb`:

```shell
touch integrate_with_langchain.ipynb
```
### Step 2. Install required dependencies

In your project directory, run the following command to install the required packages:

```shell
!pip install langchain langchain-community
!pip install langchain-openai
!pip install pymysql
!pip install tidb-vector
```

Open the `integrate_with_langchain.ipynb` file in Jupyter Notebook, and then add the following code to import the required packages:

```python
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import TiDBVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
```
### Step 3. Set up your environment

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

In your project directory, create a directory named `data/how_to/` and download the sample document [`state_of_the_union.txt`](https://github.com/langchain-ai/langchain/blob/master/docs/docs/how_to/state_of_the_union.txt) from the [langchain-ai/langchain](https://github.com/langchain-ai/langchain) GitHub repository.

```shell
!mkdir -p 'data/how_to/'
!wget 'https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/how_to/state_of_the_union.txt' -O 'data/how_to/state_of_the_union.txt'
```
#### Step 4.2 Load and split the document

Load the sample document from `data/how_to/state_of_the_union.txt` and split it into chunks of approximately 1,000 characters each using a `CharacterTextSplitter`.

```python
loader = TextLoader("data/how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
```
### Step 5. Embed and store document vectors

TiDB vector store supports both cosine distance (`consine`) and Euclidean distance (`l2`) for measuring similarity between vectors. The default strategy is cosine distance.

The following code creates a table named `embedded_documents` in TiDB, which is optimized for vector search.

```python
embeddings = OpenAIEmbeddings()
vector_store = TiDBVectorStore.from_documents(
    documents=docs,
    embedding=embeddings,
    table_name="embedded_documents",
    connection_string=tidb_connection_string,
    distance_strategy="cosine",  # default, another option is "l2"
)
```

Upon successful execution, you can directly view and access the `embedded_documents` table in your TiDB database.
### Step 6. Perform a vector search

This step demonstrates how to query "What did the president say about Ketanji Brown Jackson" from the document `state_of_the_union.txt`.

```python
query = "What did the president say about Ketanji Brown Jackson"
```
#### Option 1: Use `similarity_search_with_score()`

The `similarity_search_with_score()` method calculates the vector space distance between the documents and the query. This distance serves as a similarity score, determined by the chosen `distance_strategy`. The method returns the top `k` documents with the lowest scores. A lower score indicates a higher similarity between a document and your query.

```python
docs_with_score = vector_store.similarity_search_with_score(query, k=3)
for doc, score in docs_with_score:
   print("-" * 80)
   print("Score: ", score)
   print(doc.page_content)
   print("-" * 80)
```

<details>
   <summary><b>Expected output</b></summary>

```plain
--------------------------------------------------------------------------------
Score:  0.18472413652518527
Tonight. I call on the Senate to: Pass the Freedom to Vote Act. Pass the John Lewis Voting Rights Act. And while you’re at it, pass the Disclose Act so Americans can know who is funding our elections.

Tonight, I’d like to honor someone who has dedicated his life to serve this country: Justice Stephen Breyer—an Army veteran, Constitutional scholar, and retiring Justice of the United States Supreme Court. Justice Breyer, thank you for your service.

One of the most serious constitutional responsibilities a President has is nominating someone to serve on the United States Supreme Court.

And I did that 4 days ago, when I nominated Circuit Court of Appeals Judge Ketanji Brown Jackson. One of our nation’s top legal minds, who will continue Justice Breyer’s legacy of excellence.
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Score:  0.21757513022785557
A former top litigator in private practice. A former federal public defender. And from a family of public school educators and police officers. A consensus builder. Since she’s been nominated, she’s received a broad range of support—from the Fraternal Order of Police to former judges appointed by Democrats and Republicans.

And if we are to advance liberty and justice, we need to secure the Border and fix the immigration system.

We can do both. At our border, we’ve installed new technology like cutting-edge scanners to better detect drug smuggling.

We’ve set up joint patrols with Mexico and Guatemala to catch more human traffickers.

We’re putting in place dedicated immigration judges so families fleeing persecution and violence can have their cases heard faster.

We’re securing commitments and supporting partners in South and Central America to host more refugees and secure their own borders.
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Score:  0.22676987253721725
And for our LGBTQ+ Americans, let’s finally get the bipartisan Equality Act to my desk. The onslaught of state laws targeting transgender Americans and their families is wrong.

As I said last year, especially to our younger transgender Americans, I will always have your back as your President, so you can be yourself and reach your God-given potential.

While it often appears that we never agree, that isn’t true. I signed 80 bipartisan bills into law last year. From preventing government shutdowns to protecting Asian-Americans from still-too-common hate crimes to reforming military justice.

And soon, we’ll strengthen the Violence Against Women Act that I first wrote three decades ago. It is important for us to show the nation that we can come together and do big things.

So tonight I’m offering a Unity Agenda for the Nation. Four big things we can do together.

First, beat the opioid epidemic.
--------------------------------------------------------------------------------
```

</details>
