# Vector Search via SQL quickstart for TiDB Cloud Serverless

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-get-started-using-sql.md`
- Source Title: `Get Started with Vector Search via SQL`
- Source Heading Path: `Get Started with Vector Search via SQL | Get Started with Vector Search via SQL > Prerequisites | Get Started with Vector Search via SQL > Get started | Get Started with Vector Search via SQL > Get started > Step 1. Connect to the TiDB cluster | Get Started with Vector Search via SQL > Get started > Step 2. Create a vector table | Get Started with Vector Search via SQL > Get started > Step 3. Insert vector embeddings to the table | Get Started with Vector Search via SQL > Get started > Step 4. Query the vector table | Get Started with Vector Search via SQL > Get started > Step 5. Perform a vector search query | Get Started with Vector Search via SQL > See also`
- Source Line Ranges: `5-150`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `vector-search`, `sql`, `mysql-cli`, `prerequisites`, `cluster-connection`, `vector-table`, `vector-embeddings`, `data-insert`, `verification`, `query`, `cosine-distance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0440_283e6cad99`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-get-started-using-sql.md#get-started-with-vector-search-via-sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5524ea4d60c6721608066b64b7ee6e77c245f4ceb5182b8e76a05ef6916f11eb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-get-started-using-sql#get-started-with-vector-search-via-sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-get-started-using-sql.md

## Retrieval Guidance

- Use When: Use this chunk when someone wants a TiDB Cloud Serverless SQL quickstart for connecting with MySQL CLI, creating a VECTOR table, inserting vector embeddings, verifying rows, and running a cosine-distance vector search query.
- Retrieval Keywords: TiDB Cloud Serverless, Vector Search via SQL, MySQL command-line client, MySQL CLI, VECTOR(3), embedded_documents, CREATE TABLE embedded_documents, INSERT INTO embedded_documents, SELECT * FROM embedded_documents, vec_cosine_distance, ORDER BY distance LIMIT 3, mysql -u '<prefix>.root' -h '<host>' -P 4000 -D 'test', ssl-mode=VERIFY_IDENTITY, Generate Password, Connect With MySQL CLI, Connection Type Public, a swimming animal, [1,2,3], cosine distances
- Follow-up Guidance: The source also links to related documentation for Vector Data Types and Vector Search Index.
- Classification Note: This chunk is classified as an operation because it provides a step-by-step procedure using SQL statements and MySQL CLI to connect to a cluster, create a vector table, insert data, verify the data, and perform a vector search query.

## Official Source Content

# Get Started with Vector Search via SQL

TiDB extends MySQL syntax to support [Vector Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview) and introduce new [Vector data types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types) and several [vector functions](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-functions-and-operators).

This tutorial demonstrates how to get started with TiDB Vector Search just using SQL statements. You will learn how to use the [MySQL command-line client](https://dev.mysql.com/doc/refman/8.4/en/mysql.html) to complete the following operations:

- Connect to your TiDB cluster.
- Create a vector table.
- Store vector embeddings.
- Perform vector search queries.

> **Note**
>
> TiDB Vector Search is only available for TiDB Self-Managed (TiDB >= v8.4) and [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless). It is not available for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated).
## Prerequisites

To complete this tutorial, you need:

- [MySQL command-line client](https://dev.mysql.com/doc/refman/8.4/en/mysql.html) (MySQL CLI) installed on your machine.
- A TiDB Cloud Serverless cluster. Follow [creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless) to create your own TiDB Cloud cluster if you don't have one.
## Get started
### Step 1. Connect to the TiDB cluster

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **MySQL CLI** from the **Connect With** drop-down list and keep the default setting of the **Connection Type** as **Public**.

4. If you have not set a password yet, click **Generate Password** to generate a random password.

5. Copy the connection command and paste it into your terminal. The following is an example for macOS:

   ```bash
   mysql -u '<prefix>.root' -h '<host>' -P 4000 -D 'test' --ssl-mode=VERIFY_IDENTITY --ssl-ca=/etc/ssl/cert.pem -p'<password>'
   ```
### Step 2. Create a vector table

When creating a table, you can define a column as a [vector](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview#vector-embedding) column by specifying the `VECTOR` data type.

For example, to create a table `embedded_documents` with a three-dimensional `VECTOR` column, execute the following SQL statements using your MySQL CLI:

```sql
USE test;
CREATE TABLE embedded_documents (
    id        INT       PRIMARY KEY,
    -- Column to store the original content of the document.
    document  TEXT,
    -- Column to store the vector representation of the document.
    embedding VECTOR(3)
);
```

The expected output is as follows:

```text
Query OK, 0 rows affected (0.27 sec)
```
### Step 3. Insert vector embeddings to the table

Insert three documents with their [vector embeddings](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview#vector-embedding) into the `embedded_documents` table:

```sql
INSERT INTO embedded_documents
VALUES
    (1, 'dog', '[1,2,1]'),
    (2, 'fish', '[1,2,4]'),
    (3, 'tree', '[1,0,0]');
```

The expected output is as follows:

```
Query OK, 3 rows affected (0.15 sec)
Records: 3  Duplicates: 0  Warnings: 0
```

> **Note**
>
> This example simplifies the dimensions of the vector embeddings and uses only 3-dimensional vectors for demonstration purposes.
>
> In real-world applications, [embedding models](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview#embedding-model) often produce vector embeddings with hundreds or thousands of dimensions.
### Step 4. Query the vector table

To verify that the documents have been inserted correctly, query the `embedded_documents` table:

```sql
SELECT * FROM embedded_documents;
```

The expected output is as follows:

```sql
+----+----------+-----------+
| id | document | embedding |
+----+----------+-----------+
|  1 | dog      | [1,2,1]   |
|  2 | fish     | [1,2,4]   |
|  3 | tree     | [1,0,0]   |
+----+----------+-----------+
3 rows in set (0.15 sec)
```
### Step 5. Perform a vector search query

Similar to full-text search, users provide search terms to the application when using vector search.

In this example, the search term is "a swimming animal", and its corresponding vector embedding is assumed to be `[1,2,3]`. In practical applications, you need to use an embedding model to convert the user's search term into a vector embedding.

Execute the following SQL statement, and TiDB will identify the top three documents closest to `[1,2,3]` by calculating and sorting the cosine distances (`vec_cosine_distance`) between the vector embeddings in the table.

```sql
SELECT id, document, vec_cosine_distance(embedding, '[1,2,3]') AS distance
FROM embedded_documents
ORDER BY distance
LIMIT 3;
```

The expected output is as follows:

```plain
+----+----------+---------------------+
| id | document | distance            |
+----+----------+---------------------+
|  2 | fish     | 0.00853986601633272 |
|  1 | dog      | 0.12712843905603044 |
|  3 | tree     |  0.7327387580875756 |
+----+----------+---------------------+
3 rows in set (0.15 sec)
```

The three terms in the search results are sorted by their respective distance from the queried vector: the smaller the distance, the more relevant the corresponding `document`.

Therefore, according to the output, the swimming animal is most likely a fish, or a dog with a gift for swimming.
## See also

- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)
- [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index)
