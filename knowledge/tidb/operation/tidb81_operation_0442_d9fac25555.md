# Django ORM vector search quickstart setup and demo run

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-django-orm.md`
- Source Title: `Integrate TiDB Vector Search with Django ORM`
- Source Heading Path: `Integrate TiDB Vector Search with Django ORM | Integrate TiDB Vector Search with Django ORM > Prerequisites | Integrate TiDB Vector Search with Django ORM > Run the sample app | Integrate TiDB Vector Search with Django ORM > Run the sample app > Step 1. Clone the repository | Integrate TiDB Vector Search with Django ORM > Run the sample app > Step 2. Create a virtual environment | Integrate TiDB Vector Search with Django ORM > Run the sample app > Step 3. Install required dependencies | Integrate TiDB Vector Search with Django ORM > Run the sample app > Step 3. Install required dependencies > What is `django-tidb` | Integrate TiDB Vector Search with Django ORM > Run the sample app > Step 4. Configure the environment variables | Integrate TiDB Vector Search with Django ORM > Run the sample app > Step 5. Run the demo`
- Source Line Ranges: `5-132`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `django`, `vector-search`, `python`, `prerequisites`, `repository-clone`, `virtualenv`, `dependencies`, `environment-variables`, `serverless`, `migration`, `demo-run`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0442_d9fac25555`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-django-orm.md#integrate-tidb-vector-search-with-django-orm`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `39d94f17acccc6ce19bb459e3adee1f081ec015ff287da109eb63da24c673d50`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-django-orm#integrate-tidb-vector-search-with-django-orm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-django-orm.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the Django ORM TiDB Vector Search quickstart prerequisites, repository setup, environment variable configuration, or demo run steps for a TiDB Cloud Serverless cluster.
- Retrieval Keywords: Integrate TiDB Vector Search with Django ORM, TiDB Cloud Serverless, Python 3.8 or higher, git clone https://github.com/pingcap/tidb-vector-python.git, orm-django-quickstart, python3 -m venv .venv, pip install -r requirements.txt, pip install Django django-tidb mysqlclient numpy python-dotenv, django-tidb, TIDB_HOST, TIDB_PORT, TIDB_USERNAME, TIDB_PASSWORD, TIDB_DATABASE, TIDB_CA_PATH, python manage.py migrate, python manage.py runserver, POST: /insert_documents, GET: /get_nearest_neighbors_documents, GET: /get_documents_within_distance
- Follow-up Guidance: The source also points to sample API paths for inserting documents, getting the 3-nearest neighbor documents, and getting documents within a certain distance.
- Classification Note: This is classified as an operation chunk because the content is a step-by-step tutorial for prerequisites, setup, configuration, migration, and running the demo application.

## Official Source Content

# Integrate TiDB Vector Search with Django ORM

This tutorial walks you through how to use [Django](https://www.djangoproject.com/) ORM to interact with the [TiDB Vector Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview), store embeddings, and perform vector search queries.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Prerequisites

To complete this tutorial, you need:

- [Python 3.8 or higher](https://www.python.org/downloads/) installed.
- [Git](https://git-scm.com/downloads) installed.
- A TiDB Cloud Serverless cluster. Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create your own TiDB Cloud cluster if you don't have one.
## Run the sample app

You can quickly learn about how to integrate TiDB Vector Search with Django ORM by following the steps below.
### Step 1. Clone the repository

Clone the `tidb-vector-python` repository to your local machine:

```shell
git clone https://github.com/pingcap/tidb-vector-python.git
```
### Step 2. Create a virtual environment

Create a virtual environment for your project:

```bash
cd tidb-vector-python/examples/orm-django-quickstart
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
pip install Django django-tidb mysqlclient numpy python-dotenv
```

If you encounter installation issues with mysqlclient, refer to the mysqlclient official documentation.
#### What is `django-tidb`

`django-tidb` is a TiDB dialect for Django, which enhances the Django ORM to support TiDB-specific features (for example, TiDB Vector Search) and resolves compatibility issues between TiDB and Django.

To install `django-tidb`, choose a version that matches your Django version. For example, if you are using `django==4.2.*`, install `django-tidb==4.2.*`. The minor version does not need to be the same. It is recommended to use the latest minor version.

For more information, refer to [django-tidb repository](https://github.com/pingcap/django-tidb).
### Step 4. Configure the environment variables

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

Migrate the database schema:

```bash
python manage.py migrate
```

Run the Django development server:

```bash
python manage.py runserver
```

Open your browser and visit `http://127.0.0.1:8000` to try the demo application. Here are the available API paths:

| API Path                                | Description                              |
| --------------------------------------- | ---------------------------------------- |
| `POST: /insert_documents`               | Insert documents with embeddings.        |
| `GET: /get_nearest_neighbors_documents` | Get the 3-nearest neighbor documents.    |
| `GET: /get_documents_within_distance`   | Get documents within a certain distance. |
