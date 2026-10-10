# Prepare environment and connect Python application to TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-amazon-bedrock.md`
- Source Title: `Integrate TiDB Vector Search with Amazon Bedrock`
- Source Heading Path: `Integrate TiDB Vector Search with Amazon Bedrock > Get started > Step 1. Set the environment variables | Integrate TiDB Vector Search with Amazon Bedrock > Get started > Step 2. Set up the Python virtual environment | Integrate TiDB Vector Search with Amazon Bedrock > Get started > Step 3. Import required libraries | Integrate TiDB Vector Search with Amazon Bedrock > Get started > Step 4. Configure the database connection`
- Source Line Ranges: `47-138`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `ecosystem`, `sql`
- Topic Tags: `environment-variables`, `python`, `virtualenv`, `dependencies`, `sqlalchemy`, `database-connection`, `serverless`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0313_b6186ac75f`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-amazon-bedrock.md#step-1-set-the-environment-variables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ef67e78f629289612183da92bba0781491d7589672b71367c77c8404909f2cc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-amazon-bedrock#step-1-set-the-environment-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-amazon-bedrock.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact environment variables, Python dependencies, imports, or SQLAlchemy connection code for connecting a Python application to a TiDB Cloud Serverless cluster.
- Retrieval Keywords: TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME, Connection Type Public, Branch main, Connect With General, Generate Password, Reset Password, python3 -m venv env, source env/bin/activate, SQLAlchemy==2.0.30, PyMySQL==1.1.0, tidb-vector==0.0.9, pydantic==2.7.1, boto3, from tidb_vector.sqlalchemy import VectorType, mysql+pymysql://, ssl_verify_cert=True, ssl_verify_identity=True, create_engine(get_db_url(), pool_recycle=300), declarative_base
- Follow-up Guidance: The following steps show how to invoke Amazon Bedrock models and create the vector table after the database connection is configured.
- Classification Note: This is configuration content because it gives exact console connection settings, shell environment variables, package versions, imports, and database URL construction used in the tutorial.

## Official Source Content

### Step 1. Set the environment variables

Get the TiDB connection information from the [TiDB Cloud console](https://tidbcloud.com/) and set the environment variables in your development environment as follows:

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

5. Run the following commands in your terminal to set the environment variables. You need to replace the placeholders in the commands with the corresponding connection parameters obtained from the connection dialog.

    ```shell
    export TIDB_HOST=<your-tidb-host>
    export TIDB_PORT=4000
    export TIDB_USER=<your-tidb-user>
    export TIDB_PASSWORD=<your-tidb-password>
    export TIDB_DB_NAME=test
    ```
### Step 2. Set up the Python virtual environment

1. Create a Python file named `demo.py`:

    ```shell
    touch demo.py
    ```

2. Create and activate a virtual environment to manage dependencies:

    ```shell
    python3 -m venv env
    source env/bin/activate  # On Windows, use env\Scripts\activate
    ```

3. Install the required dependencies:

    ```shell
    pip install SQLAlchemy==2.0.30 PyMySQL==1.1.0 tidb-vector==0.0.9 pydantic==2.7.1 boto3
    ```
### Step 3. Import required libraries

Add the following code to the beginning of `demo.py` to import the required libraries:

```python
import os
import json
import boto3
from sqlalchemy import Column, Integer, Text, create_engine
from sqlalchemy.orm import declarative_base, Session
from tidb_vector.sqlalchemy import VectorType
```
### Step 4. Configure the database connection

In `demo.py`, add the following code to configure the database connection:

```python
# ---- Configuration Setup ----
# Set environment variables: TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB_NAME
TIDB_HOST = os.environ.get("TIDB_HOST")
TIDB_PORT = os.environ.get("TIDB_PORT")
TIDB_USER = os.environ.get("TIDB_USER")
TIDB_PASSWORD = os.environ.get("TIDB_PASSWORD")
TIDB_DB_NAME = os.environ.get("TIDB_DB_NAME")

# ---- Database Setup ----
def get_db_url():
    """Build the database connection URL."""
    return f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DB_NAME}?ssl_verify_cert=True&ssl_verify_identity=True"

# Create engine
engine = create_engine(get_db_url(), pool_recycle=300)
Base = declarative_base()
```
